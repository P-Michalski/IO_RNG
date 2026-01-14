The uniformity test checks whether the mean and variance of generated numbers correspond to theoretical values for the uniform distribution U(0,1).

## How it works
1. Calculates the arithmetic mean of all numbers
2. Calculates the sample variance
3. Compares with expected values:
   - Mean should be ≈ 0.5
   - Variance should be ≈ 1/12 ≈ 0.0833

## Mathematical formulas
```
Mean: μ = (1/n) × Σ xi
Variance: σ² = (1/n) × Σ (xi - μ)²

For U(0,1):
- Expected mean: E[X] = 0.5
- Expected variance: Var[X] = 1/12 ≈ 0.0833
```

## Pass criteria
- **|mean - 0.5| < 0.05**
- **|variance - 0.0833| < 0.02**
- Both conditions must be satisfied

## Implementation
```python
def _uniformity_test(self, numbers: List[float]) -> Dict[str, Any]:
    n = len(numbers)

    # Calculate mean
    mean = sum(numbers) / n

    # Calculate variance
    variance = sum((x - mean) ** 2 for x in numbers) / n

    # Expected values for uniform distribution [0,1]
    expected_mean = 0.5
    expected_variance = 1.0 / 12.0  # ≈ 0.083

    # Differences
    mean_diff = abs(mean - expected_mean)
    var_diff = abs(variance - expected_variance)

    # Test passes if differences are small
    passed = mean_diff < 0.05 and var_diff < 0.02

    # Score based on differences
    score = max(0.0, min(1.0, 1 - (mean_diff * 10 + var_diff * 5)))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'mean': mean,
            'variance': variance,
            'expected_mean': expected_mean,
            'expected_variance': expected_variance,
            'mean_diff': mean_diff,
            'var_diff': var_diff
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "uniformity_test",
    "samples_count": 50000
  }'
```

## Result interpretation
- **mean ≈ 0.5**: Generator produces numbers symmetrically around the center
- **variance ≈ 0.083**: Data spread is correct
- **mean_diff > 0.05**: Generator may have bias
- **var_diff > 0.02**: Numbers are too clustered or too dispersed

## Test parameters
- **Data type**: Floating-point numbers
- **Minimum samples**: 100
- **Complexity**: Low
