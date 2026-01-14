The 3D Spheres test randomly places points in 3D space in cube [0,1]³ and counts points inside a sphere with radius r = 0.5 centered at (0.5, 0.5, 0.5). The number of inside points should match the volume ratio of sphere to cube.

## How it works

1. Converts bits into 3D points in cube [0,1]³
2. For each point, calculates distance from center (0.5, 0.5, 0.5)
3. Counts points with distance ≤ 0.5 (inside sphere)
4. Compares proportion with theoretical value (sphere/cube volume ratio)
5. Uses z-score test for verification

## Mathematical formula

```
Distance from center:
dist = √((x-0.5)² + (y-0.5)² + (z-0.5)²)

Point inside sphere if: dist ≤ 0.5

Theoretical proportion:
V_sphere / V_cube = (4/3 × π × 0.5³) / 1 ≈ 0.5236

Z-score:
z = |inside_count - expected_inside| /
    √(expected_inside × (1 - expected_ratio))

p-value = erfc(z / √2)
```

## Critical value

- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements

- **Minimum**: 150,000 bits
- **Minimum points**: 100
- **Bits per coordinate**: 10
- **Sphere radius**: 0.5

## Implementation

The test uses numpy for bit-to-3D-coordinate conversion and distance calculation from sphere center. Checks if points fit inside sphere inscribed in unit cube.

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_3dspheres",
    "samples_count": 150000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **score = 1.0**: Perfect inside/outside point ratio
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect 3D distribution
- **passed = false**: Generator failed the test

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 150,000 bits
- **Complexity**: Medium (3D distance calculation)
- **Optimization**: Uses numpy for vectorized calculations
