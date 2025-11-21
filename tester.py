from typing import Optional, Tuple
from lcg import lcg_bit_stream

def measure_lcg(seed: int, a: int, c: int, m: int, n_bits: int,
                bits_per_value: Optional[int] = None,
                msb_first: bool = True) -> Tuple[float, float]:
    bits, elapsed = lcg_bit_stream(seed, a, c, m, n_bits,
                                   bits_per_value=bits_per_value,
                                   msb_first=msb_first,
                                   return_time=True)
    mean = (sum(bits) / len(bits)) if bits else 0.0
    return elapsed, mean

if __name__ == "__main__":
    seed = 123456789
    a = 1103515245
    c = 12345
    m = 2**31
    n_bits = 100000
    bits_per_value = 31
    elapsed, mean = measure_lcg(seed, a, c, m, n_bits, bits_per_value, msb_first=True)
    print(f"Elapsed (s): {elapsed:.6f}")
    print(f"Mean of bits: {mean:.6f}")