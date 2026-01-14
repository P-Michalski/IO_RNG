The test checks the length of the longest sequence of ones in a bit sequence. Excessively short or long maximum runs may indicate non-randomness.

## How it works
1. Divides the sequence into blocks
2. In each block, finds the longest run of ones
3. Classifies blocks according to the length of the longest run
4. Compares distribution with expected using Chi-square

## Length-dependent parameters
```
n < 6,272:
  - M = 8 (block size)
  - K = 3 (number of categories)
  - Length categories: ≤1, 2, 3, ≥4

6,272 ≤ n < 750,000:
  - M = 128
  - K = 5
  - Categories: ≤4, 5, 6, 7, 8, ≥9

n ≥ 750,000:
  - M = 10,000
  - K = 6
  - Categories: ≤10, 11, 12, 13, 14, 15, ≥16
```

## Implementation
```python
def _nist_longest_run_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    if n < 128:
        return {'passed': False, 'score': 0.0, 
                'error': 'Need at least 128 bits'}

    # Parameters for different lengths
    if n < 6272:
        K, M = 3, 8
        v_values = [1, 2, 3, 4]
        pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
    elif n < 750000:
        K, M = 5, 128
        v_values = [4, 5, 6, 7, 8, 9]
        pi_values = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    else:
        K, M = 6, 10000
        v_values = [10, 11, 12, 13, 14, 15, 16]
        pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

    num_blocks = n // M
    frequencies = [0] * (K + 1)

    # For each block, find the longest run of ones
    for i in range(num_blocks):
        block = bits[i * M:(i + 1) * M]
        max_run = 0
        current_run = 0
        
        for bit in block:
            if bit == 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        # Classify
        for j, v in enumerate(v_values):
            if max_run <= v:
                frequencies[j] += 1
                break
        else:
            frequencies[K] += 1

    # Chi-square
    chi_square = sum(
        (frequencies[i] - num_blocks * pi_values[i]) ** 2 /
        (num_blocks * pi_values[i])
        for i in range(K + 1)
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
            'num_blocks': num_blocks,
            'block_size': M,
            'frequencies': frequencies
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_longest_run",
    "samples_count": 128000
  }'
```

## Result interpretation
- **p-value > 0.1**: Distribution of run lengths is correct
- **frequencies**: Shows distribution of longest runs in blocks
- **chi_square**: The smaller the value, the better the fit to expected distribution

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 128
- **Complexity**: Medium
- **What it detects**: Excessively long/short runs
