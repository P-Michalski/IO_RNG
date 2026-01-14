The Count-the-1s test counts the number of ones in each byte and checks if the distribution of one-counts matches the theoretical binomial distribution B(8, 0.5). Each byte can have from 0 to 8 ones.

## How it works
1. Converts bits into bytes (8-bit sequences)
2. For each byte, counts the number of ones (0-8)
3. Creates frequency histogram for each possible one-count
4. Compares with theoretical binomial distribution
5. Uses Chi-square test for verification

## Mathematical formula
```
Binomial distribution B(8, 0.5):
P(k ones) = C(8,k) × 0.5^8

where C(8,k) = 8! / (k! × (8-k)!)

Expected number of bytes with k ones:
expected[k] = P(k ones) × num_bytes

Chi-square test:
χ² = Σ (observed[k] - expected[k])² / expected[k]
     k=0..8

Degrees of freedom: df = 8
p-value = erfc((χ² / (2×df))^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 256,000 bits (32,000 bytes)
- **Bits per byte**: 8

## Implementation
The test uses numpy for fast one-counting in each byte through `np.sum(axis=1)` operation on byte matrix. Binomial distribution is calculated using binomial coefficients.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_count_1s",
    "samples_count": 256000,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect binomial distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect one-count distribution
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 256,000 bits
- **Complexity**: Low
- **Optimization**: Uses numpy for one-counting
