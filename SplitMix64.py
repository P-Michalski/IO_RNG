"""
SplitMix64 — implementacja "z palca".

Funkcja publiczna:
    splitmix64_bit_stream(seed, n_bits, bits_per_value=None, msb_first=True, return_time=False)

Parametry:
    seed : None | int
        - jeśli None -> użyty domyślny seed=1
        - jeśli int -> traktowane jako początkowy stan (64-bit)
    n_bits : int              -- liczba bitów do zwrócenia
    bits_per_value : int      -- ile bitów pobrać z każdej wartości (domyślnie 64)
    msb_first : bool          -- True: MSB-first, False: LSB-first
    return_time : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)
"""
from typing import List, Optional, Tuple, Union
import time

_MASK64 = (1 << 64) - 1

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [ (value >> i) & 1 for i in range(bits - 1, -1, -1) ]
    else:
        return [ (value >> i) & 1 for i in range(bits) ]

def _splitmix64_next(state: int) -> Tuple[int, int]:
    state = (state + 0x9E3779B97F4A7C15) & _MASK64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK64
    out = (z ^ (z >> 31)) & _MASK64
    return state, out

def splitmix64_bit_stream(seed: Optional[int], n_bits: int,
                          bits_per_value: Optional[int] = None,
                          msb_first: bool = True,
                          return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:
    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []

    state = (int(seed) & _MASK64) if seed is not None else 1
    bpv = int(bits_per_value) if bits_per_value is not None else 64

    out: List[int] = []
    start = time.perf_counter() if return_time else None
    while len(out) < n_bits:
        state, val64 = _splitmix64_next(state)
        bits = _int_to_bits(val64, bpv, msb_first)
        rem = n_bits - len(out)
        if rem >= len(bits):
            out.extend(bits)
        else:
            out.extend(bits[:rem])

    if return_time:
        elapsed = time.perf_counter() - start
        return out, elapsed
    return out

"""
# Krótki przykład użycia
if __name__ == "__main__":
    seed = 123456789
    n_bits = 200
    bits, elapsed = splitmix64_bit_stream(seed, n_bits, bits_per_value=64, msb_first=True, return_time=True)
    print(f"Generated {len(bits)} bits in {elapsed:.6f} s")
    print(bits)
"""