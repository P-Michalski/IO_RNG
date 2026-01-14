The simplest NIST test. It checks whether the number of ones and zeros in a bit sequence is approximately equal. This is a fundamental test for bit balance.

## How it works

1. Converts bits to values +1 (for 1) and -1 (for 0)
2. Sums all values
3. The smaller the absolute sum, the better balanced the sequence
4. Calculates p-value using the complementary error function (erfc)

## Mathematical formulas

```
S = Σ (2×biti - 1)  where bit ∈ {0,1}

Test statistic:
s_obs = |S| / √n

P-value:
p = erfc(s_obs / √2)
```

## Pass criterion

- **p-value ≥ 0.01**
- Test passed when p-value is sufficiently large

## Implementation

```python
def _nist_monobit_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)
    # S = sum of bits (as +1/-1)
    s = sum(1 if bit == 1 else -1 for bit in bits)

    # Test statistic
    s_obs = abs(s) / math.sqrt(n)

    # P-value
    p_value = erfc(s_obs / math.sqrt(2))

    # Test passes if p-value >= 0.01
    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            's_obs': s_obs,
            'ones': sum(bits),
            'zeros': n - sum(bits),
            'threshold': 0.01
        }
    }
```

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_monobit",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **p-value ≈ 1.0**: Perfect balance between 0 and 1
- **p-value > 0.5**: Very good balance
- **p-value < 0.01**: Test failed, non-random sequence
- **ones ≈ zeros**: Good sign of balance

## Example result

```json
{
  "passed": true,
  "score": 0.8234,
  "statistics": {
    "p_value": 0.823412,
    "s_obs": 0.223,
    "ones": 50112,
    "zeros": 49888,
    "threshold": 0.01
  },
  "generated_bits": [0, 1, 1, 0, ...]
}
```

## Test parameters

- **Data type**: Bits
- **Minimum samples**: 100
- **Complexity**: Low
- **What it detects**: Imbalance between 0/1
