The test analyzes the rank of binary matrices created from a bit sequence. It checks whether the matrix rank corresponds to what's expected for random data. Low rank indicates linear dependencies between bits.

## How it works

1. Divides sequence into 32×32 bit matrices
2. Calculates rank of each matrix using Gaussian elimination
3. Classifies matrices by rank (32, 31, or less)
4. Compares distribution with expected using Chi-square

## Mathematical formulas

```
For M×M binary matrix:
Rank = number of linearly independent rows/columns

Probabilities for M=32:
P(rank=32) = 0.2888
P(rank=31) = 0.5776
P(rank≤30) = 0.1336

Chi-square: χ² = Σ (Oi - Ei)² / Ei
```

## Parameters

- **Matrix size**: 32×32
- **Minimum bits**: 1024
- **Criterion**: p-value ≥ 0.01

## Implementation

```python
def _nist_matrix_rank_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    M = Q = 32
    n = len(bits)
    num_matrices = n // (M * Q)

    if num_matrices == 0:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 1024 bits'}

    def compute_rank(matrix):
        """Gaussian elimination for binary matrix"""
        rows = len(matrix)
        cols = len(matrix[0])
        rank = 0

        for col in range(cols):
            # Find pivot
            pivot_row = None
            for row in range(rank, rows):
                if matrix[row][col] == 1:
                    pivot_row = row
                    break

            if pivot_row is None:
                continue

            # Swap rows
            matrix[rank], matrix[pivot_row] = matrix[pivot_row], matrix[rank]

            # Elimination
            for row in range(rows):
                if row != rank and matrix[row][col] == 1:
                    for c in range(cols):
                        matrix[row][c] ^= matrix[rank][c]

            rank += 1

        return rank

    rank_counts = {M: 0, M-1: 0, 'other': 0}

    for i in range(num_matrices):
        # Create M×M matrix
        matrix = []
        for row in range(M):
            start = i * M * Q + row * M
            matrix.append(bits[start:start+M])

        rank = compute_rank([row[:] for row in matrix])

        if rank == M:
            rank_counts[M] += 1
        elif rank == M - 1:
            rank_counts[M-1] += 1
        else:
            rank_counts['other'] += 1

    # Expected values
    p_32 = 0.2888
    p_31 = 0.5776
    p_other = 0.1336

    # Chi-square
    chi_square = (
        (rank_counts[M] - num_matrices * p_32) ** 2 / (num_matrices * p_32) +
        (rank_counts[M-1] - num_matrices * p_31) ** 2 / (num_matrices * p_31) +
        (rank_counts['other'] - num_matrices * p_other) ** 2 / (num_matrices * p_other)
    )

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'chi_square': chi_square,
            'num_matrices': num_matrices,
            'rank_full': rank_counts[M],
            'rank_minus_1': rank_counts[M-1],
            'rank_other': rank_counts['other']
        }
    }
```

## API usage example

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_matrix_rank",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Result interpretation

- **rank_full**: Number of matrices with full rank (32)
- **rank_minus_1**: Number of matrices with rank 31
- **rank_other**: Number of matrices with rank ≤30
- **p-value > 0.1**: Correct rank distribution
- **Low rank**: Linear dependencies between bits

## Test parameters

- **Data type**: Bits
- **Minimum samples**: 1024
- **Complexity**: High
- **What it detects**: Linear dependencies
