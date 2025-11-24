"""
Park-Miller "Minimal Standard" RNG — implementacja.
Funkcja publiczna:
    lcg_bit_stream(seed, n_bits, bits_per_value=None, msb_first=True, return_time=False)
(albo park_miller_bit_stream z tymi samymi parametrami)

Parametry:
    seed : int           -- wartość początkowa (0 < seed < 2147483647 zalecane)
    n_bits : int         -- liczba bitów do zwrócenia
    bits_per_value : int -- ile bitów pobrać z każdej wartości (domyślnie 31)
    msb_first : bool     -- True: MSB-first, False: LSB-first
    return_time : bool   -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Zwraca:
    lista intów 0/1 długości n_bits
    lub (lista intów, czas_w_sekundach) jeśli return_time=True
"""
from typing import List, Optional, Tuple, Union
import time

# Stałe Park-Millera (Minimal Standard)
_PM_A = 16807
_PM_M = 2147483647  # 2**31 - 1
_PM_Q = _PM_M // _PM_A  # 127773
_PM_R = _PM_M % _PM_A   # 2836

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [ (value >> i) & 1 for i in range(bits - 1, -1, -1) ]
    else:
        return [ (value >> i) & 1 for i in range(bits) ]

def park_miller_bit_stream(seed: int, n_bits: int,
                           bits_per_value: Optional[int] = None,
                           msb_first: bool = True,
                           return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:
    seed = int(seed)
    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []
    seed %= _PM_M
    if seed <= 0:
        seed = 1
    bpv = int(bits_per_value) if bits_per_value is not None else _PM_M.bit_length()  # domyślnie 31
    out: List[int] = []
    start = time.perf_counter() if return_time else None
    while len(out) < n_bits:
        hi = seed // _PM_Q
        lo = seed % _PM_Q
        t = _PM_A * lo - _PM_R * hi
        if t > 0:
            seed = t
        else:
            seed = t + _PM_M

        bits = _int_to_bits(seed, bpv, msb_first)
        rem = n_bits - len(out)
        if rem >= len(bits):
            out.extend(bits)
        else:
            out.extend(bits[:rem])

    if return_time:
        elapsed = time.perf_counter() - start
        return out, elapsed
    return out

lcg_bit_stream = park_miller_bit_stream

"""
# Krótki przykład użycia
if __name__ == "__main__":
    seed = 123456789
    n_bits = 100
    bits, elapsed = park_miller_bit_stream(seed, n_bits, bits_per_value=31, msb_first=True, return_time=True)
    print(f"Generated {len(bits)} bits in {elapsed:.6f} s")
    print(bits)
"""


