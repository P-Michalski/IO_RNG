using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text.Json;
using System.Linq;

// Klasa do serializacji wyniku
public class RngResult
{
    public List<int> bits { get; set; }
    public double time { get; set; }
}

/*
Xoshiro256** — wbudowany generator w .NET 6+

Funkcja publiczna:
    Xoshiro256BitStream(seed, nBits, bitsPerValue=null, msbFirst=true, returnTime=false)

Parametry:
    seed : object            -- seed do inicjalizacji Random (jeśli null, używa Random.Shared)
    nBits : int              -- liczba bitów do zwrócenia
    bitsPerValue : int       -- ile bitów pobrać z każdej wartości (domyślnie 32)
    msbFirst : bool          -- True: MSB-first, False: LSB-first
    returnTime : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Używa wbudowanego Random (xoshiro256**) w .NET 6+.
*/
public class Xoshiro256
{
    private static List<int> IntToBits(ulong value, int bits, bool msbFirst = true)
    {
        var result = new List<int>();
        
        if (bits <= 0)
            return result;

        if (msbFirst)
        {
            for (int i = bits - 1; i >= 0; i--)
            {
                result.Add((int)((value >> i) & 1));
            }
        }
        else
        {
            for (int i = 0; i < bits; i++)
            {
                result.Add((int)((value >> i) & 1));
            }
        }

        return result;
    }

    public static (List<int> bits, double time)? Xoshiro256BitStream(
        object seed,
        int nBits,
        int? bitsPerValue = null,
        bool msbFirst = true,
        bool returnTime = false)
    {
        if (nBits <= 0)
        {
            if (returnTime)
                return (new List<int>(), 0.0);
            throw new ArgumentException("nBits must be positive");
        }

        int bpv = bitsPerValue ?? 32;
        
        // Inicjalizuj Random z seedem (lub Random.Shared jeśli seed == null)
        Random rng = seed is int seedInt ? new Random(seedInt) : new Random();

        var output = new List<int>();
        var stopwatch = returnTime ? Stopwatch.StartNew() : null;

        while (output.Count < nBits)
        {
            // Generuj ulong (64-bity) z Random
            ulong val;
            if (bpv <= 32)
            {
                val = (ulong)rng.Next();
            }
            else
            {
                val = ((ulong)rng.NextInt64() & 0xFFFFFFFFFFFFFFFFUL);
            }

            // Mask to bitsPerValue
            if (bpv < 64)
            {
                val = val & ((1UL << bpv) - 1);
            }

            var bits = IntToBits(val, bpv, msbFirst);
            int remaining = nBits - output.Count;

            if (remaining >= bits.Count)
            {
                output.AddRange(bits);
            }
            else
            {
                output.AddRange(bits.GetRange(0, remaining));
            }
        }

        if (returnTime)
        {
            stopwatch?.Stop();
            return (output, stopwatch?.Elapsed.TotalSeconds ?? 0.0);
        }

        return (output, 0.0);
    }

    public static List<int> Xoshiro256BitStream(
        object seed,
        int nBits,
        int? bitsPerValue = null,
        bool msbFirst = true)
    {
        var result = Xoshiro256BitStream(seed, nBits, bitsPerValue, msbFirst, false);
        return result?.bits ?? new List<int>();
    }
}

class Program
{
    static void Main(string[] args)
    {
        try
        {
            // Domyślne parametry
            int nBits = 200;
            int bitsPerValue = 32;
            bool msbFirst = true;
            int? seedValue = null;

            // Parsowanie argumentów z linii poleceń
            if (args.Length > 0 && int.TryParse(args[0], out int bits))
                nBits = bits;
            if (args.Length > 1 && int.TryParse(args[1], out int bpv))
                bitsPerValue = bpv;
            if (args.Length > 2)
                msbFirst = args[2].ToLower() != "false";
            if (args.Length > 3 && int.TryParse(args[3], out int seed))
                seedValue = seed;

            // Generuj bity z pomiarem czasu
            var result = Xoshiro256.Xoshiro256BitStream(seedValue, nBits, bitsPerValue, msbFirst, true);
            
            if (result.HasValue)
            {
                var (bits_list, elapsed) = result.Value;
                
                // Utwórz obiekt wyniku
                var rngResult = new RngResult
                {
                    bits = bits_list,
                    time = elapsed
                };

                // Zwróć JSON z bitami i czasem
                var json = JsonSerializer.Serialize(rngResult);
                Console.WriteLine(json);
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error: {ex.Message}");
            System.Environment.Exit(1);
        }
    }
}

/*
Krótki przykład użycia z terminala:

# Domyślnie: 200 bitów, 32 bity na wartość, MSB-first
.\bin\Release\net8.0\Xoshiro256.exe

# Z parametrami: nBits=1000000 bitsPerValue=32 msbFirst=true seed=12345
.\bin\Release\net8.0\Xoshiro256.exe 1000000 32 true 12345

# Wynik: JSON z bitami i czasem wykonania
{"bits":[1,0,1,1,0,1,0,1,...],"time":0.001234}

Korzysta z wbudowanego Random (xoshiro256**) w .NET 6+
*/ 