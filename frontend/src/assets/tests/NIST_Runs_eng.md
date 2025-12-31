# NIST Runs Test

## Description
The test checks whether the number of transitions (runs) between 0 and 1 is correct. A run is an uninterrupted sequence of identical bits. The test detects whether the sequence is too "smooth" or too "variable".

## How it works
1. Performs pre-test: proportion of ones must be close to 0.5
2. Counts the number of runs (transitions from 0→1 or 1→0)
3. Compares with expected number of runs
4. Calculates p-value

## Mathematical formulas
```
π = number of ones / n

Pre-test: |π - 0.5| < 2/√n

Number of runs: V_n (obs) = count transitions

Expected number of runs:
E[V_n] = 2nπ(1-π)

Test statistic:
T = |V_n(obs) - E[V_n]| / (2√(2n)π(1-π))

P-value:
p = erfc(T/√2)
```

## Example of runs
```
Sequence: 1 1 0 0 0 1 1 1 0 1
Runs:     [11][000][111][0][1]
Number of runs: 5
```

## Implementation
```python
def _nist_runs_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    # Pre-test: proportion of ones must be close to 0.5
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        return {
            'passed': False,
            'score': 0.0,
            'error': 'Pre-test failed: proportion of ones not close to 0.5',
            'statistics': {'pi': pi}
        }

    # Count runs
    runs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1

    # Expected value
    expected_runs = 2 * n * pi * (1 - pi)

    # Test statistic
    numerator = abs(runs - expected_runs)
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    test_stat = numerator / denominator if denominator != 0 else 0

    # P-value
    p_value = erfc(test_stat / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'runs': runs,
            'expected_runs': expected_runs,
            'pi': pi
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_runs",
    "samples_count": 100000
  }'
```

## Result interpretation
- **runs ≈ expected_runs**: Correct number of transitions
- **runs << expected_runs**: Sequence too "smooth", long runs of same bits
- **runs >> expected_runs**: Sequence too "variable", too many switches
- **Pre-test failed**: Sequence is not balanced (use Monobit test first)

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 100
- **Complexity**: Medium
- **What it detects**: Incorrect transitions
