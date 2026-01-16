The Birthday Spacings test counts how many values appear more than once (duplicates) in blocks of 24-bit words. According to the original Diehard test, the number of such duplicate values j should follow a Poisson distribution with λ = m³/(4n), where m=512 (birthdays per block) and n=2²⁴ (space size).

## How it works

1. Converts bits into 24-bit words
2. Divides words into blocks of 512 elements (m = 512)
3. In each block, counts how many values occur more than once (j)
4. Tests if the distribution of j values matches Poisson(λ=2.0)
5. Uses chi-square test to compare observed vs expected frequencies

## Mathematical formula

```
Lambda parameter: λ = m³/(4n) = 512³/(4×2²⁴) = 2.0

Poisson probability: P(j=k) = (λᵏ × e⁻ᵏ) / k!

Chi-square test:
χ² = Σ (observed_k - expected_k)² / expected_k

p-value = gammaincc(df/2, χ²/2)
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
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_birthday_spacings",
    "samples_count": 1048576,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **score = 1.0**: Perfect Poisson distribution of duplicate counts
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, non-Poisson pattern in duplicates
- **passed = false**: Generator failed the test

**Note**: This test now correctly implements the original Diehard specification by testing the Poisson distribution of the COUNT of duplicate values (j), not the spacing between them.

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 262,144 bits
- **Complexity**: High (sorting, duplicate search)
- **Optimization**: Uses numpy for faster conversion
