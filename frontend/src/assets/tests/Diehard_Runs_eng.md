The Runs test analyzes lengths of runs (sequences) of consecutive zeros or ones in bit sequence. For truly random generators, the run length distribution should match theoretical distribution - short runs are more frequent, long runs are rarer.

## How it works
1. Traverses bit sequence and identifies runs
2. Counts length of each run (sequence of consecutive 0s or 1s)
3. Groups runs by length: 1, 2, 3, 4, 5, 6, ≥7
4. Compares with theoretical distribution using Chi-square test

## Mathematical formula
```
Theoretical probability of run length k:
P(length = k) = 2 × (1/2)^(k+1)

For k ≥ 7: P(length ≥ 7) = 2 × (1/2)^8

Expected number of runs of length k:
expected[k] = P(k) × total_runs

Chi-square test:
χ² = Σ (observed[k] - expected[k])² / expected[k]
     k=1..7

Degrees of freedom: df = 6
p-value = erfc((χ² / (2×df))^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 100,000 bits
- **Length categories**: 7 (1-6, ≥7)

## Implementation
The test uses numpy and `np.diff` operation for fast detection of bit value changes. Runs are identified by change locations, and their lengths are grouped and analyzed.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_runs",
    "samples_count": 100000,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect run length distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect run distribution
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 100,000 bits
- **Complexity**: Low-medium
- **Optimization**: Uses numpy diff for change detection
