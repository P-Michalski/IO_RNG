The test searches for a specific pattern (template) in the sequence, where occurrences do not overlap. It checks whether the number of occurrences matches expectations for a random sequence.

## How it works

1. Selects an m-bit pattern (default 000000001)
2. Divides sequence into blocks of size M
3. In each block, counts pattern occurrences (non-overlapping)
4. Compares distribution with expected

## Mathematical formulas

```
Expected number of occurrences in block:
μ = (M - m + 1) / 2^m

Variance:
σ² = M × [(1/2^m) - (2m-1)/2^(2m)]

Chi-square: χ² = Σ(Wi - μ)² / σ²

P-value: p = erfc(√(χ²/2))
```

## Parameters

- **Default template**: [0,0,0,0,0,0,0,0,1]
- **Block size**: M = 1000
- **Minimum bits**: 1000

## Implementation

```python
def _nist_non_overlapping_template_test(self, bits: List[int],
                                        template: List[int] = None) -> Dict[str, Any]:
    import math
    from math import erfc

    if template is None:
        template = [0, 0, 0, 0, 0, 0, 0, 0, 1]

    n = len(bits)
    m = len(template)
    M = 1000
    N = n // M

    if N == 0:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 1000 bits'}

    # Expected value and variance
    mu = (M - m + 1) / (2 ** m)
    sigma_sq = M * ((1 / (2 ** m)) - ((2 * m - 1) / (2 ** (2 * m))))

    counts = []
    for i in range(N):
        block = bits[i * M:(i + 1) * M]
        count = 0
        j = 0
        while j <= len(block) - m:
            if block[j:j+m] == template:
                count += 1
                j += m  # Non-overlapping
            else:
                j += 1
        counts.append(count)

    # Chi-square
    chi_square = sum((count - mu) ** 2 for count in counts) / sigma_sq

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
            'expected_matches': mu,
            'variance': sigma_sq
        }
    }
```

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_non_overlapping_template",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **expected_matches**: Expected number of pattern occurrences in block
- **p-value > 0.1**: Correct pattern occurrence frequency
- **chi_square**: The smaller the value, the better

## Test parameters

- **Data type**: Bits
- **Minimum samples**: 1000
- **Complexity**: Medium
- **What it detects**: Specific patterns
