A variant of the Random Excursions test that tests more states (±1 to ±9) and uses a different test statistic. Each state has a separate p-value.

## How it works
1. Similar to Random Excursions: creates random walk
2. Tests states: ±1, ±2, ..., ±9 (18 states)
3. For each state, calculates separate p-value
4. Test passes when all p-values ≥ 0.01

## Mathematical formulas
```
For state x:
statistic = |visits - cycles| / √(2×cycles×(4|x|-2))

p-value(x) = erfc(statistic/√2)

Test passed = all p-values ≥ 0.01
```

## Differences from Random Excursions
- More states (18 vs 8)
- Different test statistic
- Each state tested separately
- More rigorous (all p-values must pass)

## Implementation
```python
def _nist_random_excursions_variant_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Convert to ±1 and calculate partial sums
    S = [0]
    for bit in bits:
        S.append(S[-1] + (1 if bit == 1 else -1))

    # Count cycles
    cycles = sum(1 for i in range(1, len(S)) if S[i] == 0)

    if cycles < 500:
        return {
            'passed': False,
            'score': 0.0,
            'error': f'Need at least 500 cycles, got {cycles}',
            'statistics': {'cycles': cycles}
        }

    # States to test: ±1, ±2, ..., ±9
    states = list(range(-9, 0)) + list(range(1, 10))
    
    results = {}
    all_passed = True

    for state in states:
        # Count visits to this state
        visits = sum(1 for s in S if s == state)
        
        # Calculate test statistic
        numerator = abs(visits - cycles)
        denominator = math.sqrt(2 * cycles * (4 * abs(state) - 2))
        
        if denominator > 0:
            test_stat = numerator / denominator
            p_value = erfc(test_stat / math.sqrt(2))
        else:
            p_value = 0.0

        results[f'state_{state}'] = {
            'p_value': p_value,
            'visits': visits,
            'expected': cycles,
            'passed': p_value >= 0.01
        }
        
        if p_value < 0.01:
            all_passed = False

    passed = all_passed
    score = min(1.0, min(r['p_value'] for r in results.values()))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'cycles': cycles,
            'num_states_tested': len(states),
            'states_results': results
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_random_excursions_variant",
    "samples_count": 100000
  }'
```

## Result interpretation
- **cycles**: Number of cycles
- **num_states_tested**: Number of states tested (18)
- **states_results**: Results for each state
  - **visits**: Actual number of visits
  - **expected**: Expected number (equal to number of cycles)
  - **p_value**: Must be ≥ 0.01
- **All states must pass**: More restrictive than basic test

## Comparison with Random Excursions
| Feature | Random Excursions | Random Excursions Variant |
|---------|-------------------|---------------------------|
| Number of states | 8 (±1 to ±4) | 18 (±1 to ±9) |
| Statistic | Chi-square | Difference/√variance |
| Criterion | Each state separately | Each state separately |
| Strictness | Medium | High |

## Test parameters
- **Data type**: Bits
- **Minimum samples**: ~10000 (for 500 cycles)
- **Complexity**: Very high
- **What it detects**: Random walk (more states)
