The Squeeze test compresses random 32-bit integers by iteratively multiplying by random floats [0,1] until result < 1. It counts the number of iterations (multiplications) needed to "squeeze" the value below 1. The distribution of iteration counts should be characteristic.

## How it works

1. Converts bits into 32-bit integers
2. Also converts into floats [0,1] used as multipliers
3. For each integer, iteratively multiplies by successive floats
4. Counts how many multiplications needed until value < 1
5. Analyzes distribution of iteration counts (mean, deviation)

## Mathematical formula

```
Squeeze process for value v:
v₀ = integer (large value)
vᵢ₊₁ = vᵢ × floatᵢ

Count iterations until vₙ < 1

Theoretical mean: ≈ 47 iterations

Z-score:
z = |mean_count - 47| / std_count

p-value = erfc(z / √2)
```

## Critical value

- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements

- **Minimum**: 100,000 bits
- **Bits per integer**: 32

## Implementation

The test uses numpy to convert bits into 32-bit integers and floats [0,1]. Squeeze process is simulated iteratively for each (integer, float sequence) pair.

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_squeeze",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **score = 1.0**: Perfect iteration count distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect squeeze distribution
- **passed = false**: Generator failed the test

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 100,000 bits
- **Complexity**: Medium (iterative multiplication)
- **Optimization**: Uses numpy for conversion
