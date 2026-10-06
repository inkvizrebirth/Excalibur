using System.Text;
using MoonsecDeobfuscator.Ast;
using MoonsecDeobfuscator.Ast.Expressions;
using MoonsecDeobfuscator.Ast.Literals;
using MoonsecDeobfuscator.Ast.Statements;
using MoonsecDeobfuscator.Bytecode.Models;
using MoonsecDeobfuscator.Deobfuscation.Bytecode;
using MoonsecDeobfuscator.Deobfuscation.Rewriters;
using MoonsecDeobfuscator.Deobfuscation.Utils;
using MoonsecDeobfuscator.Deobfuscation.Walkers;
using System;
using Function = MoonsecDeobfuscator.Bytecode.Models.Function;

namespace MoonsecDeobfuscator.Deobfuscation;

public class Deobfuscator
{
    private Context _ctx = new();
    private Block _root = null!;

    public Function Deobfuscate(string code, bool antiTamper = false)
    {
        _root = Block.FromString(code);

        new Renamer().Walk(_root);
        new ConstantReplacer(DecodeConstants()).Rewrite(_root, Order.PreOrder);
        new ConstantFolder().Rewrite(_root, Order.PostOrder);
        new Analyzer(_ctx).Walk(_root, symbols: true);

        if (_root.Statements.Count > 3 && !antiTamper)
            return Deobfuscate(HandleAntiTamper(), true);

        new ControlFlowSolver().Rewrite(_ctx.Wrapper, Order.PostOrder);
        new Renamer(_ctx.IdentifiedNames).Walk(_root);

        var function = DeserializeBytecode();
        var bytecodeDeobfuscator = new BytecodeDeobfuscator(function, _ctx);

        function = bytecodeDeobfuscator.Deobfuscate();

        return function;
    }

    private Dictionary<string, string[]> DecodeConstants()
    {
        var constants = StringCollector.Collect(_root);

        return constants
            .Select(it => it.Item1 != null
                ? StringDecoding.Decode(it.Item2, (int) it.Item1)
                : StringDecoding.DecodeEscape(it.Item2))
            .Select(StringDecoding.DecodeConstants)
            .SelectMany(map => map)
            .ToDictionary(entry => entry.Key, entry => entry.Value);
    }

    private string HandleAntiTamper()
    {
        var function = DeserializeBytecode();
        var instructions = function.Instructions
            .Where(instr => instr is { IsKA: false, IsKB: true, IsKC: false })
            .ToList();

        // why tf is this static
        var constant = function.Constants[instructions[^2].B - 1];
        var key = ((NumberConstant) constant).Value;

        var bytecodeString = ((StringLiteral) ((Assign) _root.Statements[2]).Values[0]).Value[1..^1];
        var scriptString = ((StringLiteral) ((Assign) _root.Statements[3]).Values[0]).Value[1..^1];

        _ctx = new Context
        {
            BytecodeString = bytecodeString
        };

        return Encoding.UTF8.GetString(StringDecoding.Decode(scriptString, (int) key));
    }

    private Function DeserializeBytecode()
    {
        SolveKeys();

        var bytecode = StringDecoding.Decode(_ctx.BytecodeString, _ctx.BytecodeKey);
        var deserializer = new Deserializer(bytecode, _ctx);

        return deserializer.ReadFunction();
    }

    private void SolveKeys()
    {
        if (_ctx.KeyExpressions.Count == 2)
        {
            _ctx.ConstantKey = EvaluateKey(_ctx.KeyExpressions.First());
        }

        _ctx.BytecodeKey = EvaluateKey(_ctx.KeyExpressions.Last());
    }

    private static int EvaluateKey(Expression expression)
    {
        var value = EvaluateStaticExpression(expression, new StaticEnvironment(null), 0, new StaticBudget());
        if (value is not double number || !double.IsFinite(number))
            throw new NotSupportedException("MoonSec key expression did not resolve to a finite number.");
        if (number < int.MinValue || number > int.MaxValue)
            throw new NotSupportedException("MoonSec key expression resolved outside the supported integer range.");
        return Convert.ToInt32(number);
    }

    private const int MaxKeyExpressionDepth = 256;
    private const int MaxKeyFunctionStatements = 64;
    private const int MaxKeyFunctionArguments = 32;
    private const int MaxStaticLoopIterations = 4096;
    private const int MaxStaticInstructions = 100_000;
    private const int MaxStaticFunctionCalls = 256;

    private static object? EvaluateStaticExpression(
        Expression expression,
        StaticEnvironment scope,
        int depth,
        StaticBudget budget)
    {
        budget.Consume();
        if (depth > MaxKeyExpressionDepth)
            throw new NotSupportedException("MoonSec key expression exceeds the static evaluation depth limit.");

        return expression switch
        {
            NumberLiteral number => number.Value,
            BooleanLiteral boolean => boolean.Value,
            Name name => scope.Get(name.Value),
            UnaryExpression unary => EvaluateUnary(unary, scope, depth + 1, budget),
            BinaryExpression binary => EvaluateBinary(binary, scope, depth + 1, budget),
            Call call => EvaluateStaticCall(call, scope, depth + 1, budget),
            AnonymousFunction function => new StaticClosure(function, scope),
            _ => throw new NotSupportedException(
                $"MoonSec key expression uses unsupported syntax `{expression.GetType().Name}`; it was not executed."),
        };
    }

    private static object? EvaluateUnary(
        UnaryExpression expression,
        StaticEnvironment scope,
        int depth,
        StaticBudget budget)
    {
        var operand = EvaluateStaticExpression(expression.Operand, scope, depth + 1, budget);
        return expression.Operator switch
        {
            UnaryOperator.Negate => -RequireNumber(operand, "unary minus"),
            UnaryOperator.Not => !IsTruthy(operand),
            _ => throw new NotSupportedException("MoonSec key expression uses an unsupported unary operator."),
        };
    }

    private static object? EvaluateBinary(
        BinaryExpression expression,
        StaticEnvironment scope,
        int depth,
        StaticBudget budget)
    {
        var leftValue = EvaluateStaticExpression(expression.Left, scope, depth + 1, budget);
        if (expression.Operator == BinaryOperator.And)
            return IsTruthy(leftValue)
                ? EvaluateStaticExpression(expression.Right, scope, depth + 1, budget)
                : leftValue;
        if (expression.Operator == BinaryOperator.Or)
            return IsTruthy(leftValue)
                ? leftValue
                : EvaluateStaticExpression(expression.Right, scope, depth + 1, budget);

        var rightValue = EvaluateStaticExpression(expression.Right, scope, depth + 1, budget);
        var left = RequireNumber(leftValue, "left operand");
        var right = RequireNumber(rightValue, "right operand");
        return expression.Operator switch
        {
            BinaryOperator.Add => left + right,
            BinaryOperator.Sub => left - right,
            BinaryOperator.Mul => left * right,
            BinaryOperator.Div when right != 0 => left / right,
            BinaryOperator.Mod when right != 0 => left % right,
            BinaryOperator.Pow => Math.Pow(left, right),
            BinaryOperator.Equals => left == right,
            BinaryOperator.NotEquals => left != right,
            BinaryOperator.LessThan => left < right,
            BinaryOperator.GreaterThan => left > right,
            BinaryOperator.LessThanOrEquals => left <= right,
            BinaryOperator.GreaterThanOrEquals => left >= right,
            _ => throw new NotSupportedException(
                "MoonSec key expression uses an unsupported or unsafe operator."),
        };
    }

    private static object? EvaluateStaticCall(
        Call call,
        StaticEnvironment scope,
        int depth,
        StaticBudget budget)
    {
        if (call.Arguments.Count > MaxKeyFunctionArguments)
            throw new NotSupportedException("MoonSec key call exceeds the bounded argument limit.");

        if (call.Function is MemberAccess
            {
                Table: Name { Value: "math" },
                Key.Value: var functionName
            })
        {
            var arguments = call.Arguments
                .Select(argument => RequireNumber(
                    EvaluateStaticExpression(argument, scope, depth + 1, budget),
                    $"math.{functionName} argument"))
                .ToArray();
            return EvaluateWhitelistedMathCall(functionName, arguments);
        }

        var target = EvaluateStaticExpression(call.Function, scope, depth + 1, budget);
        var values = call.Arguments
            .Select(argument => EvaluateStaticExpression(argument, scope, depth + 1, budget))
            .ToArray();
        if (target is not StaticClosure closure)
            throw new NotSupportedException(
                "MoonSec key expression attempted to call a non-static function; it was not executed.");
        return InvokeStaticClosure(closure, values, depth + 1, budget);
    }

    private static double EvaluateWhitelistedMathCall(string functionName, double[] arguments)
    {
        double One(Func<double, double> function) => arguments.Length == 1
            ? function(arguments[0])
            : throw new NotSupportedException($"math.{functionName} expects one numeric argument.");
        double Two(Func<double, double, double> function) => arguments.Length == 2
            ? function(arguments[0], arguments[1])
            : throw new NotSupportedException($"math.{functionName} expects two numeric arguments.");

        var result = functionName switch
        {
            "abs" => One(Math.Abs),
            "ceil" => One(Math.Ceiling),
            "floor" => One(Math.Floor),
            "sqrt" => One(Math.Sqrt),
            "sin" => One(Math.Sin),
            "cos" => One(Math.Cos),
            "tan" => One(Math.Tan),
            "asin" => One(Math.Asin),
            "acos" => One(Math.Acos),
            "atan" => One(Math.Atan),
            "exp" => One(Math.Exp),
            "log" => arguments.Length switch
            {
                1 => Math.Log(arguments[0]),
                2 => Math.Log(arguments[0], arguments[1]),
                _ => throw new NotSupportedException("math.log expects one or two numeric arguments."),
            },
            "deg" => One(value => value * (180d / Math.PI)),
            "rad" => One(value => value * (Math.PI / 180d)),
            "fmod" => Two((left, right) => right == 0
                ? throw new NotSupportedException("math.fmod divisor is zero.")
                : left % right),
            "pow" => Two(Math.Pow),
            "atan2" => Two(Math.Atan2),
            "min" when arguments.Length > 0 => arguments.Min(),
            "max" when arguments.Length > 0 => arguments.Max(),
            _ => throw new NotSupportedException(
                $"MoonSec key expression calls unsupported math.{functionName}; it was not executed."),
        };
        if (!double.IsFinite(result))
            throw new NotSupportedException($"math.{functionName} produced a non-finite value.");
        return result;
    }

    private static object? InvokeStaticClosure(
        StaticClosure closure,
        object?[] arguments,
        int depth,
        StaticBudget budget)
    {
        if (depth > MaxKeyExpressionDepth || closure.Function.Parameters.IsVarArg ||
            closure.Function.Parameters.Names.Count != arguments.Length ||
            arguments.Length > MaxKeyFunctionArguments ||
            closure.Function.Body.Statements.Count > MaxKeyFunctionStatements)
            throw new NotSupportedException("MoonSec key function is outside the bounded static subset.");

        var scope = new StaticEnvironment(closure.Captured);
        for (var index = 0; index < arguments.Length; index++)
            scope.Declare(closure.Function.Parameters.Names[index].Value, arguments[index]);

        budget.EnterFunction();
        try
        {
            // Expression depth is reset at a function boundary. Recursive key
            // functions have their own explicit call-depth and instruction caps.
            var flow = ExecuteStaticBlock(closure.Function.Body, scope, 0, budget);
            if (flow.Broken)
                throw new NotSupportedException("MoonSec key function contains a break outside a static loop.");
            if (!flow.Returned)
                return null; // Lua functions without an explicit return yield nil.
            return flow.Value;
        }
        finally
        {
            budget.ExitFunction();
        }
    }

    private static StaticFlow ExecuteStaticBlock(
        Block block,
        StaticEnvironment scope,
        int depth,
        StaticBudget budget)
    {
        if (depth > MaxKeyExpressionDepth || block.Statements.Count > MaxKeyFunctionStatements)
            throw new NotSupportedException("MoonSec key function exceeds the bounded static block limit.");

        foreach (var statement in block.Statements)
        {
            budget.Consume();
            var flow = ExecuteStaticStatement(statement, scope, depth + 1, budget);
            if (flow.Returned || flow.Broken)
                return flow;
        }
        return StaticFlow.Continue;
    }

    private static StaticFlow ExecuteStaticStatement(
        Statement statement,
        StaticEnvironment scope,
        int depth,
        StaticBudget budget)
    {
        if (statement is Return returned)
        {
            if (returned.Values.Count == 0)
                return StaticFlow.Return(null);
            if (returned.Values.Count != 1)
                throw new NotSupportedException("MoonSec key function must return exactly one static value.");
            return StaticFlow.Return(EvaluateStaticExpression(returned.Values[0], scope, depth + 1, budget));
        }

        if (statement is LocalDeclare local)
        {
            if (local.Names.Count > MaxKeyFunctionArguments || local.Values.Count != local.Names.Count)
                throw new NotSupportedException("MoonSec key function has an unsupported local declaration shape.");
            // Lua evaluates all right-hand values before binding the locals.
            var values = local.Values
                .Select(value => EvaluateStaticExpression(value, scope, depth + 1, budget))
                .ToArray();
            for (var index = 0; index < local.Names.Count; index++)
                scope.Declare(local.Names[index].Value, values[index]);
            return StaticFlow.Continue;
        }

        if (statement is Assign assignment)
        {
            if (assignment.Variables.Count == 0 ||
                assignment.Variables.Count != assignment.Values.Count ||
                assignment.Variables.Count > MaxKeyFunctionArguments ||
                assignment.Variables.Any(variable => variable is not Name))
                throw new NotSupportedException("MoonSec key function has an unsupported assignment shape.");
            var values = assignment.Values
                .Select(value => EvaluateStaticExpression(value, scope, depth + 1, budget))
                .ToArray();
            for (var index = 0; index < assignment.Variables.Count; index++)
                scope.Assign(((Name)assignment.Variables[index]).Value, values[index]);
            return StaticFlow.Continue;
        }

        if (statement is If conditional)
        {
            if (IsTruthy(EvaluateStaticExpression(conditional.IfClause.Condition, scope, depth + 1, budget)))
                return ExecuteStaticBlock(conditional.IfClause.Body, new StaticEnvironment(scope), depth + 1, budget);
            foreach (var clause in conditional.ElseIfClauses)
                if (IsTruthy(EvaluateStaticExpression(clause.Condition, scope, depth + 1, budget)))
                    return ExecuteStaticBlock(clause.Body, new StaticEnvironment(scope), depth + 1, budget);
            return conditional.ElseBody is null
                ? StaticFlow.Continue
                : ExecuteStaticBlock(conditional.ElseBody, new StaticEnvironment(scope), depth + 1, budget);
        }

        if (statement is NumericFor numericFor)
            return ExecuteStaticNumericFor(numericFor, scope, depth + 1, budget);

        if (statement is While whileLoop)
        {
            for (var iteration = 0; iteration < MaxStaticLoopIterations; iteration++)
            {
                budget.Consume();
                if (!IsTruthy(EvaluateStaticExpression(whileLoop.Condition, scope, depth + 1, budget)))
                    return StaticFlow.Continue;
                var flow = ExecuteStaticBlock(whileLoop.Body, new StaticEnvironment(scope), depth + 1, budget);
                if (flow.Returned)
                    return flow;
                if (flow.Broken)
                    return StaticFlow.Continue;
            }
            throw new NotSupportedException("MoonSec key loop exceeded the static iteration limit.");
        }

        if (statement is Repeat repeatLoop)
        {
            for (var iteration = 0; iteration < MaxStaticLoopIterations; iteration++)
            {
                budget.Consume();
                var iterationScope = new StaticEnvironment(scope);
                var flow = ExecuteStaticBlock(repeatLoop.Body, iterationScope, depth + 1, budget);
                if (flow.Returned)
                    return flow;
                if (!flow.Broken && IsTruthy(EvaluateStaticExpression(repeatLoop.Condition, iterationScope, depth + 1, budget)))
                    return StaticFlow.Continue;
                if (flow.Broken)
                    return StaticFlow.Continue;
            }
            throw new NotSupportedException("MoonSec key loop exceeded the static iteration limit.");
        }

        if (statement is ExpressionStatement expressionStatement)
        {
            _ = EvaluateStaticExpression(expressionStatement.Expression, scope, depth + 1, budget);
            return StaticFlow.Continue;
        }

        if (statement is Break)
            return StaticFlow.Break;

        var statementText = PrettyPrinter.AsString(statement).Replace('\r', ' ').Replace('\n', ' ');
        if (statementText.Length > 240)
            statementText = statementText[..240] + "…";
        throw new NotSupportedException(
            $"MoonSec key function contains unsupported statement `{statementText}`; it was not executed.");
    }

    private static StaticFlow ExecuteStaticNumericFor(
        NumericFor loop,
        StaticEnvironment parent,
        int depth,
        StaticBudget budget)
    {
        var current = RequireNumber(EvaluateStaticExpression(loop.InitialValue, parent, depth + 1, budget), "for start");
        var limit = RequireNumber(EvaluateStaticExpression(loop.FinalValue, parent, depth + 1, budget), "for limit");
        var step = loop.Step is null
            ? 1d
            : RequireNumber(EvaluateStaticExpression(loop.Step, parent, depth + 1, budget), "for step");
        if (step == 0 || !double.IsFinite(current) || !double.IsFinite(limit) || !double.IsFinite(step))
            throw new NotSupportedException("MoonSec key numeric loop has an invalid range.");

        var loopScope = new StaticEnvironment(parent);
        loopScope.Declare(loop.IteratorName.Value, current);
        for (var iteration = 0; iteration < MaxStaticLoopIterations && (step > 0 ? current <= limit : current >= limit); iteration++)
        {
            budget.Consume();
            loopScope.Assign(loop.IteratorName.Value, current);
            var flow = ExecuteStaticBlock(loop.Body, new StaticEnvironment(loopScope), depth + 1, budget);
            if (flow.Returned)
                return flow;
            if (flow.Broken)
                return StaticFlow.Continue;
            current += step;
            if (!double.IsFinite(current))
                throw new NotSupportedException("MoonSec key numeric loop exceeded the supported range.");
        }
        if (step > 0 ? current <= limit : current >= limit)
            throw new NotSupportedException("MoonSec key loop exceeded the static iteration limit.");
        return StaticFlow.Continue;
    }

    private static double RequireNumber(object? value, string description) => value is double number
        ? number
        : throw new NotSupportedException($"MoonSec key {description} is not a static number.");

    private static bool IsTruthy(object? value) => value is not null && value is not false;

    private sealed class StaticEnvironment(StaticEnvironment? parent)
    {
        private readonly Dictionary<string, object?> _values = new(StringComparer.Ordinal);
        private readonly StaticEnvironment? _parent = parent;

        public object? Get(string name)
        {
            if (_values.TryGetValue(name, out var value))
                return value;
            if (_parent is not null)
                return _parent.Get(name);
            throw new NotSupportedException(
                $"MoonSec key expression references unbound name `{name}`; it was not executed.");
        }

        public void Declare(string name, object? value) => _values[name] = value;

        public void Assign(string name, object? value)
        {
            if (_values.ContainsKey(name))
            {
                _values[name] = value;
                return;
            }
            if (_parent is not null)
            {
                _parent.Assign(name, value);
                return;
            }
            throw new NotSupportedException(
                $"MoonSec key function assigns unbound name `{name}`; global assignment was not executed.");
        }
    }

    private sealed record StaticClosure(AnonymousFunction Function, StaticEnvironment Captured);

    private sealed class StaticBudget
    {
        private int _remaining = MaxStaticInstructions;
        private int _activeFunctions;

        public void EnterFunction()
        {
            if (++_activeFunctions > MaxStaticFunctionCalls)
            {
                _activeFunctions--;
                throw new NotSupportedException("MoonSec key expression exceeded the static function-call depth limit.");
            }
        }

        public void ExitFunction() => _activeFunctions--;

        public void Consume()
        {
            if (--_remaining < 0)
                throw new NotSupportedException("MoonSec key expression exceeded the static instruction budget.");
        }
    }

    private readonly record struct StaticFlow(bool Returned, bool Broken, object? Value)
    {
        public static StaticFlow Continue => new(false, false, null);
        public static StaticFlow Break => new(false, true, null);
        public static StaticFlow Return(object? value) => new(true, false, value);
    }
}
