use chacha20::ChaCha20;
use chacha20::cipher::{KeyIvInit, StreamCipher};
use std::time::Instant;
use serde_json::json;

/*
ChaCha20 CSPRNG — Algorytm szyfrowania strumienia do generacji liczb losowych.

Funkcja publiczna:
    chacha20_bit_stream(nBits, bitsPerValue=32, msbFirst=true) -> {"bits": [...], "time": 0.001234}

Parametry:
    nBits : usize            -- liczba bitów do zwrócenia
    bitsPerValue : usize     -- ile bitów pobrać z każdej wartości (domyślnie 32)
    msbFirst : bool          -- True: MSB-first, False: LSB-first

Zwraca JSON z tablicą bitów binarnych i czasem wykonania w sekundach.
*/

fn int_to_bits(value: u64, bits: usize, msb_first: bool) -> Vec<u8> {
    if bits == 0 {
        return Vec::new();
    }

    let mut result = Vec::with_capacity(bits);
    
    if msb_first {
        for i in (0..bits).rev() {
            result.push(((value >> i) & 1) as u8);
        }
    } else {
        for i in 0..bits {
            result.push(((value >> i) & 1) as u8);
        }
    }

    result
}

fn chacha20_bit_stream(
    n_bits: usize,
    bits_per_value: Option<usize>,
    msb_first: bool,
) -> (Vec<u8>, f64) {
    let start = Instant::now();

    if n_bits == 0 {
        return (Vec::new(), 0.0);
    }

    let bpv = bits_per_value.unwrap_or(32);
    let num_bytes = (bpv + 7) / 8;

    // Klucz i nonce dla ChaCha20 (mogą być dowolne dla CSPRNG)
    let key = [0u8; 32]; // 256-bit key
    let nonce = [0u8; 12]; // 96-bit nonce
    
    let mut cipher = ChaCha20::new(key.as_ref().into(), nonce.as_ref().into());
    
    let mut output = Vec::new();
    let mut buffer = vec![0u8; num_bytes];

    while output.len() < n_bits {
        // Generuj liczby losowe
        cipher.apply_keystream(&mut buffer);

        // Konwertuj bytes do u64 (big-endian)
        let mut val: u64 = 0;
        for byte in &buffer {
            val = (val << 8) | (*byte as u64);
        }

        // Maskuj do bitsPerValue
        let max_bits = (num_bytes * 8) as u32;
        if (bpv as u32) < max_bits {
            val = val & ((1u64 << bpv) - 1);
        }

        let bits = int_to_bits(val, bpv, msb_first);
        let remaining = n_bits - output.len();

        if remaining >= bits.len() {
            output.extend(&bits);
        } else {
            output.extend(&bits[..remaining]);
        }
    }

    let elapsed = start.elapsed().as_secs_f64();
    (output, elapsed)
}

fn main() {
    // Parsuj argumenty z linii poleceń
    let args: Vec<String> = std::env::args().collect();

    let mut n_bits = 200usize;
    let mut bits_per_value = 32usize;
    let mut msb_first = true;

    if args.len() > 1 {
        if let Ok(n) = args[1].parse::<usize>() {
            n_bits = n;
        }
    }

    if args.len() > 2 {
        if let Ok(n) = args[2].parse::<usize>() {
            bits_per_value = n;
        }
    }

    if args.len() > 3 {
        msb_first = args[3].to_lowercase() != "false";
    }

    // Generuj bity
    let (bits, elapsed) = chacha20_bit_stream(n_bits, Some(bits_per_value), msb_first);

    // Konwertuj na liczby (0 i 1)
    let bits_as_ints: Vec<i32> = bits.iter().map(|&b| b as i32).collect();

    // Utwórz JSON
    let result = json!({
        "bits": bits_as_ints,
        "time": elapsed
    });

    println!("{}", result.to_string());
}

/*
Krótki przykład użycia z terminala:

# Domyślnie: 200 bitów, 32 bity na wartość, MSB-first
.\chacha20_rng.exe

# Z parametrami: nBits=100 bitsPerValue=16 msbFirst=true
.\chacha20_rng.exe 100 16 true

# Wynik: JSON z bitami i czasem wykonania
{"bits":[1,0,1,1,0,1,0,1,...],"time":0.001234}
*/
