# Diehard OQSO Test

## Description
The OQSO (Overlapping-Quadruples-Sparse-Occupancy) test is similar to OPSO but analyzes 4-letter words instead of pairs. It divides 32-bit words into 5-bit "letters" (32 possible values), creating overlapping quadruples of letters and counting singletons.

## How it works
1. Converts bits into 32-bit words
2. Each 32-bit word is divided into 6 5-bit "letters"
3. From 6 letters, creates 3 overlapping quadruples (positions 0-3, 1-4, 2-5)
4. Counts frequency of each unique quadruple
5. Counts quadruples occurring exactly once and compares with Poisson distribution

## Mathematical formula
```
Number of possible quadruples: 32^4 = 1,048,576
(each letter has 32 possible values)

Poisson distribution parameter λ:
λ = total_quadruples / 32^4

Expected number of singletons:
expected = 32^4 × λ × e^(-λ)

Chi-square test:
χ² = (observed - expected)² / expected
p-value = erfc((χ² / 2)^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 2,097,152 bits (2^21)
- **Bits per word**: 32

## Implementation
The test converts bits into 32-bit words, then extracts 5-bit letters through bit operations (shift and mask). Creates overlapping quadruples and analyzes their sparse occupancy.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_oqso",
    "samples_count": 2097152,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect singleton distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect sparse occupancy
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 2,097,152 bits
- **Complexity**: Medium-high
- **Optimization**: Uses numpy for bit conversion
