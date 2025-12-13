"""
Generator Blum-Blum-Shub (BBS) napisany w czystym Pythonie.

Funkcja publiczna:
    bbs_bit_stream(seed, n_bits, p=383, q=503, bits_per_value=1, msb_first=True, return_time=False)

Parametry:
    seed : int lub None       -- ziarno, musi być coprime z N = p*q; None -> losowy seed systemowy
    n_bits : int              -- liczba bitów do zwrócenia
    p, q : int                -- liczby pierwsze typu Blum (p%4 == 3, q%4 == 3); domyślnie: 383, 503
    bits_per_value : int      -- ile LSB pobrać z każdego kroku (domyślnie 1)
    msb_first : bool          -- True: MSB-first, False: LSB-first (rozpakowanie bloku)
    return_time : bool        -- jeśli True, zwraca (bity, sekundy)

Zwraca:
    listę intów (0/1) długości n_bits
    lub (listę, sekundy) jeśli return_time=True
"""
from typing import List, Optional, Tuple, Union
import random
import time
import math


def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [(value >> i) & 1 for i in range(bits - 1, -1, -1)]
    return [(value >> i) & 1 for i in range(bits)]


def _ensure_coprime(seed: int, modulus: int) -> int:
    seed = seed % modulus
    if seed == 0:
        seed = 1
    if math.gcd(seed, modulus) == 1:
        return seed
    candidate = seed + 1
    while math.gcd(candidate, modulus) != 1:
        candidate += 1
    return candidate


def bbs_bit_stream(seed: Optional[int],
                   n_bits: int,
                   p: int = 383,
                   q: int = 503,
                   bits_per_value: int = 1,
                   msb_first: bool = True,
                   return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:

    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []

    p = int(p)
    q = int(q)
    if p <= 3 or q <= 3 or p % 4 != 3 or q % 4 != 3:
        raise ValueError("p i q musza byc pierwsze oraz p%4==3, q%4==3")

    modulus = p * q
    bpv = int(bits_per_value) if bits_per_value is not None else 1
    if bpv <= 0:
        bpv = 1

    if seed is None:
        seed = random.randrange(2, modulus - 1)
    seed = _ensure_coprime(int(seed), modulus)

    state = (seed * seed) % modulus
    out: List[int] = []
    start = time.perf_counter() if return_time else None

    while len(out) < n_bits:
        state = pow(state, 2, modulus)
        chunk_value = state & ((1 << bpv) - 1) 
        bits = _int_to_bits(chunk_value, bpv, msb_first)
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
# Przykład użycia
if __name__ == "__main__":
    seed = 12345
    n_bits = 200
    bits_per_value = 4  # liczba bitów z każdego kroku BBS
    msb_first = True
    return_time = True
    p = 383
    q = 503

    bits, elapsed = bbs_bit_stream(seed, n_bits, p=p, q=q, bits_per_value=bits_per_value,
                                   msb_first=msb_first, return_time=return_time)
    print(f"Wygenerowano {len(bits)} bitów w {elapsed:.6f} s")
    print(bits)
"""
