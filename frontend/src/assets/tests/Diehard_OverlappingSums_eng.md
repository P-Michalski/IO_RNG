The Overlapping Sums test converts bits into floating-point numbers [0,1] and calculates sums of overlapping windows. The sum distribution should be normal according to the central limit theorem. The test checks mean and standard deviation of sums.

## How it works
1. Converts bit groups (8 bits) into numbers [0,1]
2. Creates overlapping windows of size 10 values
3. Calculates sum for each window
4. Analyzes mean and standard deviation of sums
5. Compares with theoretical values using z-score

## Mathematical formula
```
For uniform [0,1], sum of n values:
- Theoretical mean: n/2
- Theoretical deviation: √(n/12)

For window size 10:
expected_mean = 10/2 = 5.0
expected_std = √(10/12) ≈ 0.913

Z-scores:
z_mean = |mean_sum - expected_mean| / (expected_std / √num_sums)
z_std = |std_sum - expected_std| / (expected_std / √(2×num_sums))

Combined test:
χ² = z_mean² + z_std²
p-value = erfc(√(χ² / 2))
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 100,000 bits
- **Bits per value**: 8
- **Window size**: 10 values

## Implementation
The test uses numpy for bit-to-[0,1] conversion and overlapping window sum calculation. Central limit theorem guarantees normal sum distribution for truly random data.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_overlapping_sums",
    "samples_count": 100000,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect normal sum distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect sum distribution
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 100,000 bits
- **Complexity**: Low-medium
- **Optimization**: Uses numpy for sliding window sums
