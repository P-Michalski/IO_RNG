The Minimum Distance test randomly places points in 2D space ([0,1]×[0,1]) and calculates the minimum distance between each point and its nearest neighbor. The minimum distance distribution should match theoretical distribution dependent on point density.

## How it works

1. Converts bits into 2D points in unit square [0,1]×[0,1]
2. For each point, calculates distance to nearest neighbor
3. Collects minimum distance distribution
4. Analyzes mean and standard deviation of minimum distances
5. Compares with theoretical mean using z-score

## Mathematical formula

```
Euclidean distance:
dist = √((x₁-x₂)² + (y₁-y₂)²)

Theoretical mean distance:
expected_mean ≈ √(1 / num_points)

Z-score:
z = |mean_distance - expected_mean| / std_distance

p-value = erfc(z / √2)
```

## Critical value

- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements

- **Minimum**: 200,000 bits
- **Minimum points**: 100
- **Bits per coordinate**: 10

## Implementation

The test uses numpy for bit-to-coordinate conversion and Euclidean distance calculations between points. For efficiency, analyzes only first 500 points.

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_minimum_distance",
    "samples_count": 200000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **score = 1.0**: Perfect minimum distance distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect spatial distribution
- **passed = false**: Generator failed the test

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 200,000 bits
- **Complexity**: High (N×N distance calculation)
- **Optimization**: Uses numpy for vectorized calculations
