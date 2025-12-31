# NIST Serial Test

## Description
The test checks the frequency of all possible overlapping m-bit patterns. It is an extension of the Approximate Entropy test, calculating two test statistics.

## How it works
1. Calculates ψ² function for m, m-1, and m-2
2. Calculates delta1 and delta2
3. For each delta, calculates p-value
4. Test passes when both p-values ≥ 0.01

## Mathematical formulas
```
ψ²(m) = (2^m/n)×Σvi² - n

where vi = number of occurrences of pattern i

Δ1 = ψ²(m) - ψ²(m-1)
Δ2 = ψ²(m) - 2ψ²(m-1) + ψ²(m-2)

p-value1 = erfc(√(|Δ1|/2))
p-value2 = erfc(√(|Δ2|/2))
```

## Implementation
```python
def _nist_serial_test(self, bits: List[int], m: int = 16) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Adjust m if n is too small
    m = min(m, int(math.log2(n)) - 2)
    if m < 2:
        return {'passed': False, 'score': 0.0,
                'error': 'Sequence too short for serial test'}

    def compute_psi_squared(m_local):
        if m_local == 0:
            return 0.0
        
        patterns = {}
        for i in range(n):
            # Cyclic patterns
            pattern = tuple(bits[i:i+m_local] if i+m_local <= n 
                          else bits[i:] + bits[:i+m_local-n])
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        psi_sq = 0.0
        for count in patterns.values():
            psi_sq += count ** 2
        
        psi_sq = (psi_sq * (2 ** m_local) / n) - n
        return psi_sq

    psi_m = compute_psi_squared(m)
    psi_m1 = compute_psi_squared(m - 1)
    psi_m2 = compute_psi_squared(m - 2)

    delta1 = psi_m - psi_m1
    delta2 = psi_m - 2 * psi_m1 + psi_m2

    # P-values
    p_value1 = erfc(math.sqrt(abs(delta1) / 2))
    p_value2 = erfc(math.sqrt(abs(delta2) / 2))

    passed = (p_value1 >= 0.01) and (p_value2 >= 0.01)
    score = min(1.0, min(p_value1, p_value2))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value1': p_value1,
            'p_value2': p_value2,
            'delta1': delta1,
            'delta2': delta2,
            'm': m
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_serial",
    "samples_count": 100000
  }'
```

## Result interpretation
- **p_value1, p_value2**: Both must be ≥ 0.01
- **delta1, delta2**: Differences in pattern distribution
- **m**: Pattern length used in test

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 100
- **Complexity**: High
- **What it detects**: Frequency of m-bit patterns
