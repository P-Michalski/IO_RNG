"""
Funkcja publiczna:
    lcg_bit_stream(seed, a, c, m, n_bits, bits_per_value=None, msb_first=True, return_time=False) -> List[int] | (List[int], float)

Parametry:
    seed : int           -- wartość początkowa
    a : int              -- mnożnik
    c : int              -- przyrost
    m : int              -- moduł
    n_bits : int          -- liczba bitów do zwrócenia
    bits_per_value : int  -- ile bitów pobrać z każdej wartości (domyślnie bit-length(m))
    msb_first : bool      -- True: MSB-first, False: LSB-first
    return_time : bool    -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Zwraca:
    lista intów 0/1 długości n_bits
    lub (lista intów, czas_w_sekundach) jeśli return_time=True

Proponowane dobre parametry:

1) GLIBC-like (częste, 31-bit)
    seed = 123456789
    a = 1103515245
    c = 12345
    m = 2**31
    bits_per_value = 31
    msb_first = True

2) 32-bit (popularny, stosowany w przykładach; ma zastrzeżenia statystyczne)
    seed = 123456789
    a = 1664525
    c = 1013904223
    m = 2**32
    bits_per_value = 32
    msb_first = True

3) MSVC-like
    seed = 123456789
    a = 214013
    c = 2531011
    m = 2**32
    bits_per_value = 32
    msb_first = True

Wskazówki praktyczne:
- Zawsze jawnie ustaw bits_per_value (np. 31 albo 32) zamiast polegać na m.bit_length().
- Wybierz msb_first zgodnie z wymaganiami testów (domyślnie True).
"""
from typing import List, Optional, Tuple, Union
import time

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [ (value >> i) & 1 for i in range(bits - 1, -1, -1) ]
    else:
        return [ (value >> i) & 1 for i in range(bits) ]

def lcg_bit_stream(seed: int, a: int, c: int, m: int, n_bits: int,
                   bits_per_value: Optional[int] = None,
                   msb_first: bool = True,
                   return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:
    seed = int(seed)
    a = int(a)
    c = int(c)
    m = int(m)
    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []

    bpv = int(bits_per_value) if bits_per_value is not None else (m.bit_length() if m > 1 else 1)
    out: List[int] = []

    start = time.perf_counter() if return_time else None
    while len(out) < n_bits:
        seed = (a * seed + c) % m
        bits = _int_to_bits(seed, bpv, msb_first)
        rem = n_bits - len(out)
        if rem >= len(bits):
            out.extend(bits)
        else:
            out.extend(bits[:rem])
    if return_time:
        elapsed = time.perf_counter() - start  # type: ignore[operator]
        return out, elapsed
    return out

'''
# Przykład użycia LCG
if __name__ == "__main__":
    seed = 123456789
    a = 1103515245
    c = 12345
    m = 2**31
    n_bits = 1024
    bits_per_value = 31
    msb_first = True
    bits, elapsed = lcg_bit_stream(seed, a, c, m, n_bits, bits_per_value, msb_first, return_time=True)
    print(f"Generated {n_bits} bits in {elapsed:.6f} seconds:")
    print(bits)
'''
