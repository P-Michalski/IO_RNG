The DFT test detects periodic patterns in a bit sequence using Fourier transform. A random sequence should not have distinct peaks in the frequency spectrum.

## How it works
1. Converts bits to values +1/-1
2. Calculates discrete Fourier transform (DFT)
3. Counts peaks exceeding threshold
4. Compares with expected number of peaks

## Mathematical formulas
```
DFT: S(k) = Σ X(n)×e^(-2πikn/N)

Threshold: T = √(ln(1/0.05)×n)

Expected number of peaks below T:
N0 = 0.95×n/2

Statistic: d = (N1 - N0) / √(n×0.95×0.05/4)

P-value: p = erfc(|d|/√2)
```

## Implementation
```python
def _nist_dft_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc
    import numpy as np

    n = len(bits)

    if n < 100:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 100 bits'}

    # Convert to ±1
    X = [2*bit - 1 for bit in bits]

    # DFT
    S = np.fft.fft(X)
    M = np.abs(S[:n//2])

    # Threshold
    T = math.sqrt(math.log(1/0.05) * n)

    # Count peaks below threshold
    N1 = sum(1 for peak in M if peak < T)

    # Expected count
    N0 = 0.95 * n / 2

    # Test statistic
    d = (N1 - N0) / math.sqrt(n * 0.95 * 0.05 / 4)

    # P-value
    p_value = erfc(abs(d) / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'threshold': T,
            'peaks_below_threshold': N1,
            'expected_peaks': N0,
            'd': d
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_dft",
    "samples_count": 10000
  }'
```

## Result interpretation
- **Detects**: Periodic patterns, cyclicity
- **p-value > 0.5**: No detectable periodicities
- **peaks_below_threshold ≈ expected**: Correct spectrum
- **d**: The smaller the absolute value, the better

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 100
- **Complexity**: High
- **What it detects**: Periodic patterns
