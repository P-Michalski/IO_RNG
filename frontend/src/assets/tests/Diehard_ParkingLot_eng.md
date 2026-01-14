The Parking Lot test simulates "parking" circles on a unit square [0,1]×[0,1]. Each "circle" (point with radius) is randomly placed, and the test counts how many circles can be parked without collisions (overlapping). The number of parked circles should match theoretical distribution.

## How it works

1. Converts bits into (x, y) coordinates in range [0,1]
2. Each point represents the center of a circle with fixed radius r
3. Tries to "park" each circle, checking collisions with already parked ones
4. Counts how many circles were successfully parked without collisions
5. Compares with expected number of circles using z-score test

## Mathematical formula

```
Circle parked if distance > 2×radius from all others

Distance between points:
dist = √((x₁-x₂)² + (y₁-y₂)²)

Expected number of parked:
expected ≈ num_points × 0.3

Z-score:
z = |num_parked - expected| / √expected

p-value = erfc(z / √2)
```

## Critical value

- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements

- **Minimum**: 384,000 bits (12,000 attempts at 32 bits)
- **Bits per coordinate**: 16
- **Circle radius**: 0.01 (fixed)

## Implementation

The test converts 16-bit sequences into [0,1] coordinates and simulates parking process by checking collisions between circles. Uses numpy for fast bit-to-coordinate conversion.

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_parking_lot",
    "samples_count": 384000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **score = 1.0**: Perfect parked circle distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect spatial distribution
- **passed = false**: Generator failed the test

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 384,000 bits
- **Complexity**: High (N×M collision checking)
- **Optimization**: Uses numpy for coordinate conversion
