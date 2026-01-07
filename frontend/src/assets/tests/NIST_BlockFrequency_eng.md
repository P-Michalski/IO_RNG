# NIST Block Frequency Test

## Description
The test checks whether the proportion of ones in individual blocks (subsequences) is close to 0.5. This is a more localized version of the Monobit test.

## How it works
1. Divides the bit sequence into blocks of size M (default 128 bits)
2. For each block, calculates the proportion of ones
3. Checks if proportions are close to 0.5 using Chi-square statistic
4. Calculates p-value

## Mathematical formulas
```
For each block i:
πi = (number of ones in block i) / M

Chi-square statistic:
χ² = 4M × Σ (πi - 0.5)²

P-value:
p = erfc(√(χ²/2))
```

## Parameters
- **Default block size**: M = 128 bits
- **Minimum sequence size**: 128 bits
- **Criterion**: p-value ≥ 0.01

## Implementation
```python
def _nist_block_frequency_test(self, bits: List[int], block_size: int = 128):
    import math
    from math import erfc

    n = len(bits)
    num_blocks = n // block_size

    if num_blocks == 0:
        return {
            'passed': False,
            'score': 0.0,
            'error': 'Not enough bits for block test'
        }

    # Chi-square statistic
    chi_square = 0.0
    proportions = []

    for i in range(num_blocks):
        block = bits[i * block_size:(i + 1) * block_size]
        proportion = sum(block) / block_size
        proportions.append(proportion)
        chi_square += (proportion - 0.5) ** 2

    chi_square *= 4 * block_size

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
            'num_blocks': num_blocks,
            'block_size': block_size,
            'proportions': proportions[:10]  # First 10 for example
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_block_frequency",
    "samples_count": 128000
  }'
```

## Result interpretation
- **p-value > 0.5**: All blocks have good balance
- **p-value ≈ 0.01**: Borderline result, some blocks may be unbalanced
- **num_blocks**: More blocks make the test more reliable
- **chi_square**: The smaller the value, the better

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 128
- **Complexity**: Medium
- **What it detects**: Local imbalance
