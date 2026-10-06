using MoonsecDeobfuscator.Bytecode.Models;
using MoonsecDeobfuscator.Deobfuscation.Utils;

namespace MoonsecDeobfuscator.Deobfuscation.Bytecode;

public enum ProtoStep
{
    Instructions,
    Constants,
    Functions,
    NumParams,

    StringConstant,
    NumberConstant,
    BooleanConstant
}

public class Deserializer(byte[] bytes, Context ctx) : BinaryReader(new MemoryStream(bytes))
{
    private const int MaxInstructionCount = 2_000_000;
    private const int MaxConstantCount = 1_000_000;
    private const int MaxPrototypeCount = 100_000;
    private const int MaxPrototypeDepth = 128;
    private const int MaxStringBytes = 16 * 1024 * 1024;

    private int ReadCount(string label, int maximum)
    {
        var count = ReadInt32();
        var remaining = BaseStream.Length - BaseStream.Position;
        if (count < 0 || count > maximum || count > remaining)
            throw new InvalidDataException($"Invalid MoonSec {label} count: {count}.");
        return count;
    }

    private List<Instruction> ReadInstructions(Function function)
    {
        var size = ReadCount("instruction", MaxInstructionCount);
        var instructions = new List<Instruction>(size);

        for (var i = 0; i < size; i++)
        {
            var descriptor = ReadByte();

            if (GetBits(descriptor, 1, 1) != 0)
                continue;

            var type = GetBits(descriptor, 2, 3);
            var mask = GetBits(descriptor, 4, 6);
            var instruction = new Instruction
            {
                OpNum = ReadInt16(),
                A = ReadInt16(),
                PC = i,
                Function = function
            };

            switch (type)
            {
                case 0:
                    instruction.B = ReadInt16();
                    instruction.C = ReadInt16();
                    break;
                case 1:
                    instruction.B = ReadInt32();
                    break;
                case 2:
                    instruction.B = ReadInt32() - (1 << 16);
                    break;
                case 3:
                    instruction.B = ReadInt32() - (1 << 16);
                    instruction.C = ReadInt16();
                    break;
            }

            instruction.IsKA = GetBits(mask, 1, 1) == 1;
            instruction.IsKB = GetBits(mask, 2, 2) == 1;
            instruction.IsKC = GetBits(mask, 3, 3) == 1;

            instructions.Add(instruction);
        }

        return instructions;
    }

    private List<Constant> ReadConstants()
    {
        var size = ReadCount("constant", MaxConstantCount);
        var constants = new List<Constant>(size);

        for (var i = 0; i < size; i++)
        {
            var typeFlag = ReadByte();

            if (!ctx.ConstantFormat.TryGetValue(typeFlag, out var type))
            {
                constants.Add(new NilConstant());
                continue;
            }

            switch (type)
            {
                case ProtoStep.BooleanConstant:
                    constants.Add(new BooleanConstant(ReadBoolean()));
                    break;
                case ProtoStep.NumberConstant:
                    constants.Add(new NumberConstant(ReadDouble()));
                    break;
                case ProtoStep.StringConstant:
                    var stringLength = ReadInt32();
                    if (stringLength < 0 || stringLength > MaxStringBytes ||
                        stringLength > BaseStream.Length - BaseStream.Position)
                        throw new InvalidDataException($"Invalid MoonSec string constant length: {stringLength}.");
                    var str = StringDecoding.DecodeConstant(ctx.ConstantKey, ReadBytes(stringLength));
                    constants.Add(new StringConstant(str));
                    break;
            }
        }

        return constants;
    }

    public Function ReadFunction() => ReadFunction(0);

    private Function ReadFunction(int depth)
    {
        if (depth > MaxPrototypeDepth)
            throw new InvalidDataException("MoonSec prototype nesting exceeds the analysis limit.");

        var function = new Function();

        foreach (var step in ctx.ProtoFormat)
        {
            switch (step)
            {
                case ProtoStep.Constants:
                    function.Constants = ReadConstants();
                    break;
                case ProtoStep.Instructions:
                    function.Instructions = ReadInstructions(function);
                    break;
                case ProtoStep.NumParams:
                    function.NumParams = ReadByte();
                    break;
                case ProtoStep.Functions:
                    function.Functions = ReadPrototypesAtDepth(depth + 1);
                    break;
            }
        }

        return function;
    }

    private List<Function> ReadPrototypesAtDepth(int depth)
    {
        var size = ReadCount("prototype", MaxPrototypeCount);
        var prototypes = new List<Function>(size);
        for (var i = 0; i < size; i++)
            prototypes.Add(ReadFunction(depth));
        return prototypes;
    }

    private static int GetBits(int source, int start, int end) =>
        (source >> (start - 1)) & ((1 << (end - start + 1)) - 1);
}
