The OPSO (Overlapping-Pairs-Sparse-Occupancy) test checks how often 10-bit "words" appear exactly once in the stream. It counts "sparse occupancy" - words occurring singly, which is characteristic of truly random sources.

## How it works
1. Creates overlapping 10-bit words from bit sequence
2. Counts occurrence frequency of each word
3. Counts how many words occurred exactly once (singletons)
4. Compares with theoretical number of singletons from Poisson distribution
5. Uses Chi-square test for verification

## Mathematical formula
```
Number of possible 10-bit words: 2^10 = 1,024

Poisson distribution parameter λ:
λ = total_words / 1024

Expected number of singletons:
expected = 1024 × λ × e^(-λ)

Chi-square test:
χ² = (observed - expected)² / expected
p-value = erfc((χ² / 2)^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 2,097,152 bits (2^21)
- **Word length**: 10 bits

## Implementation
The test uses numpy for fast sliding window to integer conversion and `np.unique` for frequency counting. Poisson distribution models the probability of single occurrences.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_opso",
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
- **Complexity**: Medium
- **Optimization**: Uses numpy for sliding window
