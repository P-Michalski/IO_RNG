from typing import Tuple, Optional
import time

import lcg
import park_miller
import AWCG
import PCG32
import SplitMix64
import PythonRNG
import SystemRNG

def _mean(bits: list) -> float:
    return (sum(bits) / len(bits)) if bits else 0.0

def measure_lcg(n_bits: int) -> Tuple[float, float]:
    seed = 123456789
    a = 1103515245
    c = 12345
    m = 2**31
    bits, elapsed = lcg.lcg_bit_stream(seed, a, c, m, n_bits, bits_per_value=31, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def measure_park_miller(n_bits: int) -> Tuple[float, float]:
    seed = 123456789
    bits, elapsed = park_miller.park_miller_bit_stream(seed, n_bits, bits_per_value=31, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def measure_awcg(n_bits: int) -> Tuple[float, float]:
    seed = 123456789
    bits, elapsed = AWCG.awcg_bit_stream(seed, n_bits, r=24, s=10, base=2**32, bits_per_value=32, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def measure_pcg32(n_bits: int) -> Tuple[float, float]:
    seed = (42, 54)
    bits, elapsed = PCG32.pcg32_bit_stream(seed, n_bits, bits_per_value=32, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def measure_splitmix64(n_bits: int) -> Tuple[float, float]:
    seed = 123456789
    bits, elapsed = SplitMix64.splitmix64_bit_stream(seed, n_bits, bits_per_value=64, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def measure_python_random(n_bits: int) -> Tuple[float, float]:
    seed = 12345
    bits, elapsed = PythonRNG.python_random_bit_stream(seed, n_bits, bits_per_value=32, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def measure_system_rng(n_bits: int) -> Tuple[float, float]:
    bits, elapsed = SystemRNG.system_random_bit_stream(None, n_bits, bits_per_value=32, msb_first=True, return_time=True)
    return elapsed, _mean(bits)

def run_all(n_bits: int = 100000) -> None:
    testers = [
        ("LCG (glibc-like)", measure_lcg),
        ("Park-Miller", measure_park_miller),
        ("AWCG", measure_awcg),
        ("PCG32", measure_pcg32),
        ("SplitMix64", measure_splitmix64),
        ("Python random (MT)", measure_python_random),
        ("System CSPRNG", measure_system_rng),
    ]

    print(f"Running each generator for {n_bits} bits\n")
    for name, fn in testers:
        try:
            start = time.perf_counter()
            elapsed, mean = fn(n_bits)
            total_elapsed = time.perf_counter() - start
            rate = n_bits / elapsed if elapsed > 0 else float("inf")
            print(f"{name}: elapsed={elapsed:.6f}s  mean={mean:.6f}  bits/s={rate:.0f}")
        except Exception as e:
            print(f"{name}: ERROR -> {e}")

if __name__ == "__main__":
    run_all(100000)