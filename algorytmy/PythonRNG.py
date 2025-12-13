"""
Generator oparty o domyślny generator modułu `random` Pythona (Mersenne Twister).

Funkcja publiczna:
    python_random_bit_stream(seed, n_bits, bits_per_value=None, msb_first=True, return_time=False)

Parametry:
    seed : dowolna wartość akceptowana przez random.Random(seed) (None -> losowy seed systemowy)
    n_bits : int              -- liczba bitów do zwrócenia
    bits_per_value : int      -- ile bitów pobrać z każdej wartości (domyślnie 32)
    msb_first : bool          -- True: MSB-first, False: LSB-first
    return_time : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Zwraca:
    lista intów 0/1 długości n_bits
    lub (lista intów, czas_w_sekundach) jeśli return_time=True
"""
from typing import List, Optional, Tuple, Union
import random
import time

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [ (value >> i) & 1 for i in range(bits - 1, -1, -1) ]
    else:
        return [ (value >> i) & 1 for i in range(bits) ]

def python_random_bit_stream(seed: Optional[object],
                             n_bits: int,
                             bits_per_value: Optional[int] = None,
                             msb_first: bool = True,
                             return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:

    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []

    bpv = int(bits_per_value) if bits_per_value is not None else 32

    rnd = random.Random(seed)
    out: List[int] = []
    start = time.perf_counter() if return_time else None

    while len(out) < n_bits:
        val = rnd.getrandbits(bpv)
        bits = _int_to_bits(val, bpv, msb_first)
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
    seed = 12345
    n_bits = 200
    bits, elapsed = python_random_bit_stream(seed, n_bits, bits_per_value=32, msb_first=True, return_time=True)
    print(f"Generated {len(bits)} bits in {elapsed:.6f} s")
    print(bits)
"""

