# NIST Maurer's Universal Statistical Test

## Description
Maurer's universal test measures sequence compressibility. A random sequence should be difficult to compress. The test measures distance between repetitions of L-bit patterns.

## How it works
1. Divides sequence into L-bit blocks
2. Initialization phase: first Q blocks build the table
3. Test phase: next K blocks test distances
4. Calculates average logarithm of distance

## Mathematical formulas
```
fn = (1/K) × Σ log2(i - T[blocki])

where T[block] = last position of block

Adaptive parameters:
L=6, Q=640   for n < 387840
L=7, Q=1280  for n < 904960
L=8, Q=2560  for n ≥ 904960
```

## Implementation
```python
def _nist_universal_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Select parameters L, Q
    if n < 387840:
        L, Q = 6, 640
        expected = 5.2177052
        variance = 2.954
    elif n < 904960:
        L, Q = 7, 1280
        expected = 6.1962507
        variance = 3.125
    else:
        L, Q = 8, 2560
        expected = 7.1836656
        variance = 3.238

    K = (n // L) - Q

    if K <= 0:
        return {'passed': False, 'score': 0.0,
                'error': f'Need at least {(Q + 1) * L} bits for L={L}'}

    T = {}  # Block position table

    # Initialization phase
    for i in range(1, Q + 1):
        block = tuple(bits[(i-1)*L:i*L])
        T[block] = i

    # Test phase
    sum_log = 0.0
    for i in range(Q + 1, Q + K + 1):
        block = tuple(bits[(i-1)*L:i*L])
        if block in T:
            distance = i - T[block]
            sum_log += math.log2(distance)
        T[block] = i

    fn = sum_log / K

    # Test statistic
    test_stat = abs(fn - expected) / math.sqrt(variance / K)

    # P-value
    p_value = erfc(test_stat / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'fn': fn,
            'expected': expected,
            'L': L,
            'Q': Q,
            'K': K
        }
    }
```

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_universal",
    "samples_count": 500000
  }'
```

## Result interpretation
- **fn ≈ expected**: Good compressibility (high entropy)
- **fn significantly different**: Sequence too regular or too chaotic
- **L**: Block length used in test

## Test parameters
- **Data type**: Bits
- **Minimum samples**: 387840
- **Complexity**: High
- **What it detects**: Compressibility
