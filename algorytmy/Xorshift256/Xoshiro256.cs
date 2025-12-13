using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Linq;

// Klasa do serializacji wyniku
public class RngResult
{
    public List<int> bits { get; set; }
    public double time { get; set; }
}

/*
Systemowy CSPRNG — Windows RNGCryptoServiceProvider (ekwiwalent BCryptGenRandom).

Funkcja publiczna:
    SystemRandomBitStream(seed, nBits, bitsPerValue=null, msbFirst=true, returnTime=false)

Parametry:
    seed : ignorowany (dla kompatybilności z innymi generatorami)
    nBits : int              -- liczba bitów do zwrócenia
    bitsPerValue : int       -- ile bitów pobrać z każdej wartości (domyślnie 32)
    msbFirst : bool          -- True: MSB-first, False: LSB-first
    returnTime : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Używa RNGCryptoServiceProvider na Windowsie do operacji CSPRNG.
*/
public class SystemRNG
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

    public static (List<int> bits, double time)? SystemRandomBitStream(
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
        int numBytes = (bpv + 7) / 8;

        var output = new List<int>();
        var stopwatch = returnTime ? Stopwatch.StartNew() : null;

        while (output.Count < nBits)
        {
            byte[] buffer = new byte[numBytes];
            RandomNumberGenerator.Fill(buffer);

                // Convert bytes to ulong (big-endian)
                ulong val = 0;
                for (int i = 0; i < numBytes; i++)
                {
                    val = (val << 8) | buffer[i];
                }

                // Mask to bitsPerValue
                int maxBits = 8 * numBytes;
                if (bpv < maxBits)
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

    public static List<int> SystemRandomBitStream(
        object seed,
        int nBits,
        int? bitsPerValue = null,
        bool msbFirst = true)
    {
        var result = SystemRandomBitStream(seed, nBits, bitsPerValue, msbFirst, false);
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

            // Parsowanie argumentów z linii poleceń
            if (args.Length > 0 && int.TryParse(args[0], out int bits))
                nBits = bits;
            if (args.Length > 1 && int.TryParse(args[1], out int bpv))
                bitsPerValue = bpv;
            if (args.Length > 2)
                msbFirst = args[2].ToLower() != "false";

            // Generuj bity z pomiarem czasu
            var result = SystemRNG.SystemRandomBitStream(null, nBits, bitsPerValue, msbFirst, true);
            
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
.\bin\Xoshiro256.exe

# Z parametrami: nBits=100 bitsPerValue=16 msbFirst=true
.\bin\Xoshiro256.exe 100 16 true

# Wynik: JSON z bitami i czasem wykonania
{"bits":[1,0,1,1,0,1,0,1,...],"time":0.001234}
*/

/// 