# Diehard Binary Rank Test

## Description
The Binary Rank test checks the rank of 32x32 binary matrices created from bits. For truly random bits, the rank distribution should be characteristic - most matrices should have full rank (32) or rank 31.

## How it works
1. Converts bits into 32x32 binary matrices (1024 bits each)
2. For each matrix, calculates rank using Gaussian elimination in GF(2)
3. Counts how many matrices have rank 32, 31, or less
4. Compares with theoretical distribution using Chi-square test

## Mathematical formula
```
Theoretical probabilities for 32x32:
P(rank=32) ≈ 0.2888
P(rank=31) ≈ 0.5776
P(rank≤30) ≈ 0.1336

Chi-square test:
χ² = Σ (observed - expected)² / expected

p-value = erfc((χ² / 4)^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 10,240 bits (10 matrices)
- **Recommended**: 100,000+ bits
- **Bits per matrix**: 1024 (32×32)

## Implementation
The test uses numpy for fast matrix rank calculation via Gaussian elimination in field GF(2). XOR operations replace addition and subtraction in standard elimination.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_binary_rank",
    "samples_count": 100000,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect rank distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect rank distribution
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 10,240 bits
- **Complexity**: Very high (Gaussian elimination for many matrices)
- **Optimization**: Uses numpy for matrix operations
