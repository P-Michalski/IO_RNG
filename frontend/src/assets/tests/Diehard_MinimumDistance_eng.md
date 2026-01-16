The Minimum Distance test (original Diehard specification) randomly places 8000 points in a 10000×10000 square, finds the minimum distance d between ALL pairs, then tests if d² follows an exponential distribution with mean 0.995. This is repeated 100 times and a Kolmogorov-Smirnov test checks uniformity.

## How it works

1. Converts bits into (x, y) coordinates in [0, 10000)² square
2. Generates 8000 random points per sample
3. Finds minimum distance d between ALL pairs of points
4. Computes d² (square of minimum distance)
5. Converts d² to uniform value: u = 1 - exp(-d²/0.995)
6. Repeats 100 times and applies KS test to u values
7. Tests if u values are uniformly distributed in [0,1)

## Mathematical formula

```
For 8000 points in 10000×10000, find minimum distance:
d_min = min(√((xᵢ-xⱼ)² + (yᵢ-yⱼ)²)) for all pairs i≠j

Theoretical: d² ~ Exponential(mean = 0.995)

CDF transform to uniform [0,1):
u = 1 - exp(-d²/0.995)

Kolmogorov-Smirnov statistic:
D = max|F_empirical(u) - F_theoretical(u)|

p-value ≈ 2 × exp(-2 × n × D²)
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

- **score = 1.0**: Perfect exponential distribution of d²
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, d² does not follow Exponential(0.995)
- **passed = false**: Generator failed the test

**Note**: Now correctly implements the original Diehard specification by testing d² ~ Exponential(mean=0.995) using 100 samples and KS test, not the naive approximation that was previously used.

## Test parameters

- **Data type**: Bits (binary)
- **Minimum samples**: 200,000 bits (adjusts based on available data)
- **Standard parameters**: 8000 points, 100 samples
- **Complexity**: Very high (N² distance calculation per sample)
- **Optimization**: Limited to prevent timeout
