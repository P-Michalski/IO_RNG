The Approximate Entropy test measures the frequency of all possible overlapping patterns of length m in a sequence. It detects whether the sequence is too regular or predictable.

## How it works

1. Selects pattern length m (default 10, adjusted to sequence length)
2. Counts all possible patterns of length m
3. Calculates entropy for patterns of length m and m+1
4. Compares these entropies - for random sequences they should be similar

## Mathematical formulas

```
For pattern of length m:
Φ(m) = Σ (pi × log(pi))

where pi = frequency of pattern i

Approximate Entropy:
ApEn(m) = Φ(m) - Φ(m+1)

Chi-square statistic:
χ² = 2n(log(2) - ApEn)

P-value:
p = erfc(√(χ²/2))
```

## Adaptive parameters

```python
# Adjust m to sequence size
m = min(m_requested, int(log2(n)) - 5)
if m < 2:
    m = 2
```

## Implementation

```python
def _nist_approximate_entropy_test(self, bits: List[int], m: int = 10):
    import math
    from math import erfc

    n = len(bits)

    if n < 100:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 100 bits'}

    # Adjust m if n is too small
    m = min(m, int(math.log2(n)) - 5)
    if m < 2:
        m = 2

    def compute_phi(m_local):
        patterns = {}
        for i in range(n):
            pattern = tuple(bits[i:i+m_local] + bits[:max(0, i+m_local-n)])
            patterns[pattern] = patterns.get(pattern, 0) + 1

        phi = 0.0
        for count in patterns.values():
            pi = count / n
            phi += pi * math.log(pi)
        return phi

    phi_m = compute_phi(m)
    phi_m_plus_1 = compute_phi(m + 1)

    apen = phi_m - phi_m_plus_1

    # Chi-square approximation
    chi_square = 2 * n * (math.log(2) - apen)

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'approximate_entropy': apen,
            'chi_square': chi_square,
            'm': m
        }
    }
```

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_approximate_entropy",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **approximate_entropy**: ApEn value
  - Closer to 0 means more random sequence
  - Large values suggest regularity
- **m**: Pattern length used in test
  - Larger m = more accurate test (requires more data)
- **p-value > 0.1**: No detectable patterns, good randomness
- **p-value < 0.01**: Regularity detected in patterns

## What it detects

- Repeating sequences
- Cyclic patterns
- Too predictable structure
- Lack of entropy in data

## Test parameters

- **Data type**: Bits
- **Minimum samples**: 100
- **Complexity**: High
- **What it detects**: Pattern regularity
