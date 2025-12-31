# NIST Overlapping Template Matching Test

## Description
Similar to the previous test, but pattern occurrences may overlap. Uses a specific pattern 111111111 (9 ones).

## How it works
1. Uses fixed pattern: 9 ones
2. In each block, counts overlapping occurrences
3. Categorizes blocks by number of occurrences (0,1,2,3,4,5+)
4. Chi-square test on distribution

## Mathematical formulas
```
λ = (M - m + 1) / 2^m
η = λ / 2

Theoretical probabilities:
π = [0.364091, 0.185659, 0.139381,
     0.100571, 0.0704323, 0.139865]
```

## Parameters
- **Pattern**: [1,1,1,1,1,1,1,1,1]
- **Block size**: M = 1032
- **Categories**: 0, 1, 2, 3, 4, ≥5

## Implementation
```python
def _nist_overlapping_template_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    template = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    m = len(template)
    M = 1032
    n = len(bits)
    N = n // M

    if N == 0:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 1032 bits'}

    # Theoretical probabilities
    pi = [0.364091, 0.185659, 0.139381, 0.100571, 0.0704323, 0.139865]
    
    frequencies = [0] * 6

    for i in range(N):
        block = bits[i * M:(i + 1) * M]
        count = 0
        
        # Count overlapping occurrences
        for j in range(len(block) - m + 1):
            if block[j:j+m] == template:
                count += 1
        
        # Categorize
        if count >= 5:
            frequencies[5] += 1
        else:
            frequencies[count] += 1

    # Chi-square
    chi_square = sum(
        (frequencies[i] - N * pi[i]) ** 2 / (N * pi[i])
        for i in range(6)
    )

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'chi_square': chi_square,
            'num_blocks': N,
            'template': template,
            'frequencies': frequencies
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_overlapping_template",
    "samples_count": 100000
  }'
```

## Result interpretation
- **frequencies**: Distribution of pattern occurrences in blocks
- **p-value > 0.1**: Correct frequency of overlapping patterns
- **chi_square**: The smaller the value, the better

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 1032
- **Complexity**: Medium
- **What it detects**: Serial patterns (111...1)
