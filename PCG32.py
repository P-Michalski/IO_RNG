"""
PCG32 — implementacja (wariant 32-bitowy).

Funkcja publiczna:
    pcg32_bit_stream(seed, n_bits, bits_per_value=None, msb_first=True, return_time=False)

Parametry:
    seed : None | int | (int,int)
        - jeśli None -> użyty domyślny initstate=1, seq=1
        - jeśli int -> traktowane jako initstate, seq=1
        - jeśli krotka/lista (initstate, seq) -> użyj podanych wartości
    n_bits : int              -- liczba bitów do zwrócenia
    bits_per_value : int      -- ile bitów pobrać z każdej wartości (domyślnie 32)
    msb_first : bool          -- True: MSB-first, False: LSB-first
    return_time : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Zwraca:
    lista intów 0/1 długości n_bits
    lub (lista intów, czas_w_sekundach) jeśli return_time=True
"""
from typing import List, Optional, Tuple, Union, Sequence
import time

# Stałe PCG
_PCG_MULT = 6364136223846793005
_MASK64 = (1 << 64) - 1

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [ (value >> i) & 1 for i in range(bits - 1, -1, -1) ]
    else:
        return [ (value >> i) & 1 for i in range(bits) ]

def _pcg_step(state: int, inc: int) -> Tuple[int, int]:
    state = (state * _PCG_MULT + inc) & _MASK64
    x = state
    xorshifted = (((x >> 18) ^ x) >> 27) & 0xFFFFFFFF
    rot = (x >> 59) & 0x1F
    output = ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF
    return state, output

def pcg32_bit_stream(seed: Optional[Union[int, Sequence[int]]],
                     n_bits: int,
                     bits_per_value: Optional[int] = None,
                     msb_first: bool = True,
                     return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:
    """
    Generuje strumień bitów za pomocą PCG32.
    seed może być None, int (initstate) lub sekwencją (initstate, seq).
    """
    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []
    
    if seed is None:
        initstate = 1
        seq = 1
    elif isinstance(seed, int):
        initstate = int(seed)
        seq = 1
    else:
        seq_list = [int(x) for x in seed]
        if len(seq_list) >= 2:
            initstate, seq = seq_list[0], seq_list[1]
        elif len(seq_list) == 1:
            initstate, seq = seq_list[0], 1
        else:
            initstate, seq = 1, 1

    inc = ((int(seq) << 1) | 1) & _MASK64
    state = 0
    state = (state * _PCG_MULT + inc) & _MASK64
    state = (state + (int(initstate) & _MASK64)) & _MASK64
    state = (state * _PCG_MULT + inc) & _MASK64

    bpv = int(bits_per_value) if bits_per_value is not None else 32

    out: List[int] = []
    start = time.perf_counter() if return_time else None

    while len(out) < n_bits:
        state, val32 = _pcg_step(state, inc)
        rem = n_bits - len(out)
        bits = _int_to_bits(val32, bpv, msb_first)
        if rem >= len(bits):
            out.extend(bits)
        else:
            out.extend(bits[:rem])

    if return_time:
        elapsed = time.perf_counter() - start
        return out, elapsed
    return out

"""
if __name__ == "__main__":
    # Krótki przykład użycia
    seed = (42, 54)  # initstate, seq
    n_bits = 200
    bits, elapsed = pcg32_bit_stream(seed, n_bits, bits_per_value=32, msb_first=True, return_time=True)
    print(f"Generated {len(bits)} bits in {elapsed:.6f} s")
    print(bits)
"""