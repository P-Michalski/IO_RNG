The DNA test treats bits as a DNA sequence with a 4-letter alphabet (A, C, G, T). Each letter is encoded by 2 bits: 00=A, 01=C, 10=G, 11=T. The test analyzes overlapping 10-letter DNA "words" and checks sparse occupancy.

## How it works
1. Converts bit pairs (2 bits) into DNA letters (0-3)
2. Creates overlapping 10-letter DNA words
3. Counts frequency of each unique word
4. Counts words occurring exactly once (singletons)
5. Compares with theoretical number of singletons from Poisson distribution

## Mathematical formula
```
DNA alphabet: 4 letters (A, C, G, T)
Number of possible 10-letter words: 4^10 = 1,048,576

Poisson distribution parameter λ:
λ = total_words / 4^10

Expected number of singletons:
expected = 4^10 × λ × e^(-λ)

Chi-square test:
χ² = (observed - expected)² / expected
p-value = erfc((χ² / 2)^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 2,097,152 bits (2^21)
- **Bits per letter**: 2
- **Word length**: 10 DNA letters (20 bits)

## Implementation
The test uses numpy to convert bit pairs into DNA letters (values 0-3). Overlapping 10-letter words are analyzed for sparse occupancy similarly to OPSO/OQSO tests.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_dna",
    "samples_count": 2097152,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect DNA singleton distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect sparse occupancy
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 2,097,152 bits
- **Complexity**: Medium
- **Optimization**: Uses numpy for bit pair conversion
