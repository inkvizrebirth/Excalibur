using MoonsecDeobfuscator.Deobfuscation;
using MoonsecDeobfuscator.Deobfuscation.Bytecode;

namespace MoonsecDeobfuscator;

public static class Program
{
    /*
        Devirtualize and dump bytecode to file:
            -dev -i <path to input> -o <path to output>

        Devirtualize and dump bytecode disassembly to file:
            -dis -i <path to input> -o <path to output>
    */

    static void Main(string[] args)
    {
        if (args.Length == 1 && args[0] == "--version")
        {
            Console.WriteLine("MoonsecDeobfuscator Protez V3 adapter 0.1.0");
            return;
        }

        if (args.Length != 5 || args[1] != "-i" || args[3] != "-o")
        {
            Console.Error.WriteLine("Usage:");
            Console.WriteLine("Devirtualize and dump bytecode to file:\n\t-dev -i <input> -o <output>");
            Console.WriteLine("Devirtualize and dump bytecode disassembly to file:\n\t-dis -i <input> -o <output>");
            Environment.ExitCode = 2;
            return;
        }

        var command = args[0];
        var input = args[2];
        var output = args[4];

        if (!File.Exists(input))
        {
            Console.Error.WriteLine("Invalid input path!");
            Environment.ExitCode = 2;
            return;
        }

        if (command == "-dev")
        {
            var result = new Deobfuscator().Deobfuscate(File.ReadAllText(input));
            using var stream = new FileStream(output, FileMode.Create, FileAccess.Write);
            using var serializer = new Serializer(stream);

            serializer.Serialize(result);
        }
        else if (command == "-dis")
        {
            var result = new Deobfuscator().Deobfuscate(File.ReadAllText(input));
            File.WriteAllText(output, new Disassembler(result).Disassemble());
        }
        else
        {
            Console.Error.WriteLine("Invalid command!");
            Environment.ExitCode = 2;
        }
    }
}
