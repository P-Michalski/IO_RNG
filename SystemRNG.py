"""
Systemowy CSPRNG — Windows BCryptGenRandom (fallback: os.urandom).

Funkcja publiczna:
    system_random_bit_stream(seed, n_bits, bits_per_value=None, msb_first=True, return_time=False)

Parametry:
    seed : ignored (dla kompatybilności z innymi generatorami)
    n_bits : int              -- liczba bitów do zwrócenia
    bits_per_value : int      -- ile bitów pobrać z każdej wartości (domyślnie 32)
    msb_first : bool          -- True: MSB-first, False: LSB-first
    return_time : bool        -- jeśli True, funkcja zwraca (bity, czas_w_sekundach)

Używa BCryptGenRandom na Windowsie; na innych platformach używa os.urandom.
"""
from typing import List, Optional, Tuple, Union
import sys
import os
import time

def _int_to_bits(value: int, bits: int, msb_first: bool = True) -> List[int]:
    if bits <= 0:
        return []
    if msb_first:
        return [ (value >> i) & 1 for i in range(bits - 1, -1, -1) ]
    else:
        return [ (value >> i) & 1 for i in range(bits) ]

_use_bcrypt = sys.platform.startswith("win")
if _use_bcrypt:
    import ctypes
    _bcrypt = ctypes.WinDLL("bcrypt")
    _BCryptGenRandom = _bcrypt.BCryptGenRandom
    _BCryptGenRandom.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]
    _BCryptGenRandom.restype = ctypes.c_ulong
    _BCRYPT_USE_SYSTEM_PREFERRED_RNG = 0x00000002

def system_random_bit_stream(seed: Optional[object],
                             n_bits: int,
                             bits_per_value: Optional[int] = None,
                             msb_first: bool = True,
                             return_time: bool = False) -> Union[List[int], Tuple[List[int], float]]:
    """
    Generuje bity korzystając z systemowego CSPRNG.
    'seed' jest ignorowany (dla kompatybilności interfejsu).
    """
    n_bits = int(n_bits)
    if n_bits <= 0:
        if return_time:
            return [], 0.0
        return []

    bpv = int(bits_per_value) if bits_per_value is not None else 32
    num_bytes = (bpv + 7) // 8

    out: List[int] = []
    start = time.perf_counter() if return_time else None

    while len(out) < n_bits:
        if _use_bcrypt:
            buf = ctypes.create_string_buffer(num_bytes)
            status = _BCryptGenRandom(None, buf, num_bytes, _BCRYPT_USE_SYSTEM_PREFERRED_RNG)
            if status != 0:
                raise OSError(f"BCryptGenRandom failed with NTSTATUS 0x{status:08X}")
            raw = buf.raw
        else:
            raw = os.urandom(num_bytes)

        val = int.from_bytes(raw, "big") & ((1 << bpv) - 1 if bpv < (8 * num_bytes) else (1 << (8 * num_bytes)) - 1)
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
# Krótki przykład użycia (Windows: BCryptGenRandom; inne: os.urandom)
if __name__ == "__main__":
    n_bits = 200
    bits, elapsed = system_random_bit_stream(None, n_bits, bits_per_value=32, msb_first=True, return_time=True)
    print(f"Generated {len(bits)} bits in {elapsed:.6f} s")
    print(bits)
"""
