# NIST Random Excursions Test

## Description
The test analyzes the number of cycles in a "random walk" created from the sequence. It checks whether the number of visits to each state of the random walk is correct.

## How it works
1. Converts bits to +1/-1
2. Calculates partial sums (random walk)
3. Counts cycles (returns to zero)
4. For each state (-4 to +4), counts visits
5. Compares with expected values

## Mathematical formulas
```
Xi = 2×biti - 1  (conversion to ±1)

Partial sum:
Sk = Σ(i=1 to k) Xi

Cycle: return of Sk to 0

States tested: ±1, ±2, ±3, ±4

For each state x:
χ²(x) = Σ (visits - expected)² / expected
```

## Requirements
- **Minimum cycles**: 500
- If < 500 cycles, test cannot be performed

## Geometric interpretation
```
Random walk:
  +4 |      *
  +3 |    *   *
  +2 |  *       *
  +1 |*           *
   0 |-------------  (return = cycle)
  -1 |
```

## Implementation
```python
def _nist_random_excursions_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Convert to ±1 and calculate partial sums
    S = [0]
    for bit in bits:
        S.append(S[-1] + (1 if bit == 1 else -1))

    # Count cycles (returns to 0)
    cycles = sum(1 for i in range(1, len(S)) if S[i] == 0)

    if cycles < 500:
        return {
            'passed': False,
            'score': 0.0,
            'error': f'Need at least 500 cycles, got {cycles}',
            'statistics': {'cycles': cycles}
        }

    # States to test
    states = [-4, -3, -2, -1, 1, 2, 3, 4]
    
    # Theoretical probabilities for each state
    pi = {
        1: [0.5000, 0.2500, 0.1250, 0.0625, 0.0312, 0.0312],
        2: [0.7500, 0.0625, 0.0469, 0.0352, 0.0264, 0.0791],
        3: [0.8333, 0.0278, 0.0231, 0.0193, 0.0161, 0.0804],
        4: [0.8750, 0.0156, 0.0137, 0.0120, 0.0105, 0.0733]
    }

    results = {}
    all_passed = True

    for state in states:
        abs_state = abs(state)
        
        # Count visits to this state in each cycle
        visits = []
        cycle_start = 0
        
        for i in range(1, len(S)):
            if S[i] == 0:
                # End of cycle
                count = sum(1 for j in range(cycle_start, i) if S[j] == state)
                visits.append(count)
                cycle_start = i

        # Classify visits
        frequencies = [0] * 6
        for v in visits:
            if v >= 5:
                frequencies[5] += 1
            else:
                frequencies[v] += 1

        # Chi-square for this state
        expected_probs = pi[abs_state]
        chi_square = sum(
            (frequencies[i] - cycles * expected_probs[i]) ** 2 / (cycles * expected_probs[i])
            for i in range(6) if expected_probs[i] > 0
        )

        # P-value
        p_value = erfc(math.sqrt(chi_square / 2))
        
        results[f'state_{state}'] = {
            'p_value': p_value,
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
            'states_results': results
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_random_excursions",
    "samples_count": 100000
  }'
```

## Result interpretation
- **cycles**: Number of cycles (returns to zero)
- **states_results**: Results for each state
- **p_value for each state**: Must be ≥ 0.01
- **All states**: Must pass the test

## Test parameters
- **Data type**: Bits
- **Minimum samples**: ~10000 (for 500 cycles)
- **Complexity**: Very high
- **What it detects**: Random walk properties
