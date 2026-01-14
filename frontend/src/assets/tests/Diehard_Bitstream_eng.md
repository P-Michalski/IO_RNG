The Bitstream test analyzes frequencies of 20-bit words in overlapping windows. It checks whether the count of the most and least frequent words is within norms for truly random generators.

## How it works
1. Creates overlapping 20-bit words from bit sequence
2. Counts occurrences of each unique word
3. Finds maximum and minimum occurrence frequencies
4. Compares with expected frequency (uniform distribution)
5. Calculates z-score for deviations and converts to p-value

## Mathematical formula
```
Number of possible 20-bit words: 2^20 = 1,048,576

Expected frequency for each word:
expected_count = total_words / 2^20

Z-score for deviations:
z = max(|max_count - expected| / √expected,
        |min_count - expected| / √expected)

p-value = erfc(z / √2)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 2,097,152 bits (2^21)
- **Word length**: 20 bits

## Implementation
The test uses numpy for efficient sliding window to integer conversion. Uses `np.unique` for fast frequency counting.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_bitstream",
    "samples_count": 2097152,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfectly uniform frequency distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, non-uniform distribution
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 2,097,152 bits
- **Complexity**: High (analysis of many overlapping windows)
- **Optimization**: Uses numpy for sliding window
