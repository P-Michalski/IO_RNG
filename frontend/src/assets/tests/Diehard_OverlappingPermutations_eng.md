The Overlapping Permutations test analyzes frequencies of permutations of 5 consecutive values in overlapping windows. For 5 values, there are 5! = 120 possible permutations. The test checks if the permutation distribution is uniform.

## How it works

1. Converts bits into bytes (8-bit values)
2. Creates overlapping windows of 5 bytes
3. For each window, calculates the rank (permutation) of values
4. Counts occurrences of each permutation
5. Uses Chi-square test to check distribution uniformity

## Mathematical formula

```
Number of possible permutations: 5! = 120

Expected count for each permutation:
expected_count = total_windows / 120

Chi-square test:
χ² = Σ (observed - expected)² / expected

p-value = erfc((χ² / (2 * df))^0.5)
where df = 119 (degrees of freedom)
```

## Critical value

- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements

- **Minimum**: 1,048,576 bits (2^20)
- **Window**: 5 bytes (overlapping)

## Implementation

The test uses numpy for fast bit-to-byte conversion. Permutation rank is calculated by comparing each value with others in the window.

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_overlapping_permutations",
    "samples_count": 1048576,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **score = 1.0**: Perfectly uniform permutation distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, non-uniform distribution
- **passed = false**: Generator failed the test

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 1,048,576 bits
- **Complexity**: High (permutation analysis)
- **Optimization**: Uses numpy for bit conversion
