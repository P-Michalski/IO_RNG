The Cumulative Sums (CUSUM) test detects deviations from randomness by tracking the maximum deviation of the cumulative sum from zero.

## How it works
1. Converts bits to +1/-1
2. Calculates cumulative sum at each point
3. Finds maximum deviation (forward mode)
4. Calculates p-value based on this deviation

## Mathematical formulas
```
For each biti ∈ {0,1}:
Xi = 2×biti - 1  (conversion to ±1)

Cumulative sum:
Sk = Σ(i=1 to k) Xi

Maximum deviation:
z = max|Sk|

P-value: complex formula with erfc function
```

## Geometric interpretation
The test observes a "random walk" - if the sequence is random, the cumulative sum should oscillate around zero without excessive deviations.

## Implementation
```python
def _nist_cumulative_sums_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Forward cumulative sum
    s = [0]
    for bit in bits:
        s.append(s[-1] + (1 if bit == 1 else -1))

    z_forward = max(abs(val) for val in s)

    # Test statistic (simplified formula)
    sum_val = 0.0
    for k in range(int((-n / z_forward + 1) / 4),
                   int((n / z_forward - 1) / 4) + 1):
        term1 = erfc((4 * k + 1) * z_forward / math.sqrt(n))
        term2 = erfc((4 * k - 1) * z_forward / math.sqrt(n))
        sum_val += term1 - term2

    p_value = 1 - sum_val

    passed = p_value >= 0.01
    score = min(1.0, max(0.0, p_value))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'max_excursion': z_forward,
            'n': n
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_cumulative_sums",
    "samples_count": 100000
  }'
```

## Result interpretation
- **max_excursion**: Maximum deviation from zero
  - The smaller, the better balanced the sequence
  - Large values indicate bias
- **p-value > 0.5**: Very good balance
- **p-value < 0.01**: Systematic bias detected

## Visualization
```
Good sequence (random):
  Sum   |     /\    /\
        |    /  \  /  \

Bad sequence (bias):
  Sum   |          /
        |         /
```

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 100
- **Complexity**: High
- **What it detects**: Systematic bias
