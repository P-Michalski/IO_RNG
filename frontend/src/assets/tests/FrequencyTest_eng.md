The Chi-square frequency test checks whether the generated numbers are uniformly distributed across specified intervals (bins). This is a fundamental test for distribution uniformity.

## How it works
1. Divides the range [0, 1] into 10 equal intervals (bins)
2. Counts how many numbers fell into each interval
3. Compares observed frequencies with expected frequencies using Chi-square statistic
4. Calculates test score based on deviation from ideal distribution

## Mathematical formula
```
χ² = Σ ((Oi - Ei)² / Ei)

where:
- Oi = observed count in bin i
- Ei = expected count in bin i (n/10)
- n = total number of samples
```

## Critical value
- **Threshold**: χ² < 16.919 (for α=0.05, df=9)
- Test **passed** when χ² < critical value

## Implementation
```python
def _frequency_test(self, numbers: List[float]) -> Dict[str, Any]:
    num_bins = 10
    bins = [0] * num_bins

    # Count numbers in each bin
    for num in numbers:
        bin_idx = min(int(num * num_bins), num_bins - 1)
        bins[bin_idx] += 1

    # Chi-square test
    expected = len(numbers) / num_bins
    chi_square = sum(
        (observed - expected) ** 2 / expected
        for observed in bins
    )

    critical_value = 16.919
    passed = chi_square < critical_value
    score = max(0.0, min(1.0, 1 - (chi_square / critical_value)))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'chi_square': chi_square,
            'critical_value': critical_value,
            'bins': bins
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "frequency_test",
    "samples_count": 10000,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect uniform distribution
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, may not be random
- **passed = false**: Generator failed the test, non-uniform distribution

## Test parameters
- **Data type**: Floating-point numbers
- **Minimum samples**: 100
- **Complexity**: Low
