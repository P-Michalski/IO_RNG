The Birthday Spacings test examines distances between "birthdays" (repeated values) in 24-bit words. Based on the birthday problem - for truly random sources, the distribution of distances between duplicates should follow a Poisson distribution.

## How it works
1. Converts bits into 24-bit words
2. Divides words into blocks of 512 elements
3. In each block, sorts words and finds duplicates
4. Measures the distance (spacing) between duplicates
5. Tests if the spacing distribution matches Poisson distribution

## Mathematical formula
```
Theoretical mean spacing = 2^24 / 512 ≈ 32,768

Chi-square test:
χ² = |mean_spacing - expected_mean| / (variance / n)^0.5

p-value = erfc(χ² / √2)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 262,144 bits (2^18)
- **Recommended**: 1,048,576 bits (2^20)
- **Minimum blocks**: 10

## Implementation
The test uses numpy optimizations for fast bit-to-word conversion. If few duplicates are found (< 10), the test considers this a sign of excellent randomness (score = 0.95).

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_birthday_spacings",
    "samples_count": 1048576,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect spacing distribution
- **score > 0.7**: Very good result
- **score = 0.95 (few duplicates)**: Excellent randomness
- **score < 0.5**: Weak generator, non-random pattern
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 262,144 bits
- **Complexity**: High (sorting, duplicate search)
- **Optimization**: Uses numpy for faster conversion
