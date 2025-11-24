"""
Add-With-Carry (AWC) generator — implementacja "z palca".

Funkcja publiczna:
    awcg_bit_stream(seed, n_bits, r=24, s=10, base=2**32,
                    bits_per_value=None, msb_first=True, return_time=False)
Alias:
    lcg_bit_stream = awcg_bit_stream  # dla kompatybilności z testerem

Parametry:
    seed : int lub None       -- wartość początkowa dla prostego seeda (jeśli podano stan, użyj go)
    n_bits : int              -- liczba bitów do zwrócenia
    r : int                   -- główny lag (typowo 24)
    s : int                   -- mniejszy lag (typowo 10)
    base : int                -- baza (mod), zwykle 2**32
    bits_per_value : int      -- ile bitów pobrać z każdej wartości (domyślnie bit-length(base) lub -1 dla potęgi dwójki)
    msb_first : bool          -- True: MSB-first, False: LSB-first
    return_time : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Zwraca:
    lista intów 0/1 długości n_bits
    lub (lista intów, czas_w_sekundach) jeśli return_time=True
"""
from typing import List, Optional, Tuple, Union, Sequence
import time

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [(value >> i) & 1 for i in range(bits - 1, -1, -1)]
    else:
        return [(value >> i) & 1 for i in range(bits)]

def _simple_seed_state(seed: int, r: int, base: int) -> List[int]:
    """
    Prosty LCG do wygenerowania początkowego stanu długości r.
    Implementacja 'z palca' — tylko do inicjalizacji.
    """
    a = 1103515245
    c = 12345
    m = 2**31
    x = int(seed) & 0x7fffffff
    if x == 0:
        x = 1
    state: List[int] = []
    for _ in range(r):
        x = (a * x + c) % m
        # rozciągnij wartości do zakresu base (mogą być m < base; ok)
        state.append(x % base)
    return state

def awcg_bit_stream(seed: Optional[Union[int, Sequence[int]]],
                    n_bits: int,
                    r: int = 24,
                    s: int = 10,
                    base: int = 2**32,
                    bits_per_value: Optional[int] = None,
                    msb_first: bool = True,
                    return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:
    """
    Generuje strumień bitów korzystając z Add-With-Carry (AWC).
    - seed: jeśli int -> użyj prostego seeda do wygenerowania r wartości;
            jeśli sekwencja liczb -> użyj jej jako stanu (musi mieć >= r elementów),
            jeśli None -> użyj domyślnego seeda 1.
    """
    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []

    if r <= 0 or s <= 0 or s >= r:
        raise ValueError("Wymagane: r > s > 0")

    # przygotuj stan
    if seed is None:
        state = _simple_seed_state(1, r, base)
    elif isinstance(seed, int):
        state = _simple_seed_state(seed, r, base)
    else:
        # sekwencja liczb
        state = [int(x) % base for x in seed]
        if len(state) < r:
            # dopełnij przy użyciu prostego seeda
            extra = _simple_seed_state(1, r - len(state), base)
            state.extend(extra)
        # weź tylko pierwsze r
        state = state[:r]

    # dobór bits_per_value: jeśli base jest potęgą 2, wybierz base.bit_length()-1
    if bits_per_value is not None:
        bpv = int(bits_per_value)
    else:
        if base & (base - 1) == 0:
            bpv = base.bit_length() - 1
        else:
            bpv = base.bit_length()

    out: List[int] = []
    carry = 0
    p = 0  # wskaźnik miejsca w cyklicznym buforze
    start = time.perf_counter() if return_time else None

    while len(out) < n_bits:
        # x_n = x_{n-r} + x_{n-s} + carry (mod base), carry = 0/1 jeśli przekroczenie base
        idx_r = p % r                   # miejsce, które zostanie nadpisane
        idx_n_minus_r = (p - r) % r     # równoważne (p) - r
        idx_n_minus_s = (p - s) % r
        # użyj wartości historycznych:
        val = state[idx_n_minus_r] + state[idx_n_minus_s] + carry
        if val >= base:
            carry = 1
            val -= base
        else:
            carry = 0
        state[idx_r] = val
        p = (p + 1) % r

        bits = _int_to_bits(val, bpv, msb_first)
        rem = n_bits - len(out)
        if rem >= len(bits):
            out.extend(bits)
        else:
            out.extend(bits[:rem])

    if return_time:
        elapsed = time.perf_counter() - start  # type: ignore[operator]
        return out, elapsed
    return out

"""
if __name__ == "__main__":
    # Krótki przykład użycia
    seed = 123456789
    n_bits = 200
    bits, elapsed = awcg_bit_stream(seed, n_bits, r=24, s=10, base=2**32, bits_per_value=32, msb_first=True, return_time=True)
    print(f"Generated {len(bits)} bits in {elapsed:.6f} s")
    print(bits)
"""