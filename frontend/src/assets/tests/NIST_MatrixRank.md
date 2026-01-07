# NIST Binary Matrix Rank Test

## Opis
Test analizuje rangę macierzy binarnych utworzonych z sekwencji bitowej. Sprawdza czy ranga macierzy odpowiada oczekiwanej dla losowych danych. Niska ranga wskazuje na zależności liniowe między bitami.

## Jak działa
1. Dzieli sekwencję na macierze 32×32 bity
2. Oblicza rangę każdej macierzy metodą eliminacji Gaussa
3. Klasyfikuje macierze według rangi (32, 31, lub mniej)
4. Porównuje rozkład z oczekiwanym za pomocą Chi-kwadrat

## Wzory matematyczne
```
Dla macierzy M×M binarnej:
Ranga = liczba liniowo niezależnych wierszy/kolumn

Prawdopodobieństwa dla M=32:
P(rank=32) = 0.2888
P(rank=31) = 0.5776
P(rank≤30) = 0.1336

Chi-square: χ² = Σ (Oi - Ei)² / Ei
```

## Parametry
- **Rozmiar macierzy**: 32×32
- **Minimum bitów**: 1024
- **Kryterium**: p-value ≥ 0.01

## Implementacja
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
        """Eliminacja Gaussa dla macierzy binarnej"""
        rows = len(matrix)
        cols = len(matrix[0])
        rank = 0
        
        for col in range(cols):
            # Znajdź pivot
            pivot_row = None
            for row in range(rank, rows):
                if matrix[row][col] == 1:
                    pivot_row = row
                    break
            
            if pivot_row is None:
                continue
            
            # Zamień wiersze
            matrix[rank], matrix[pivot_row] = matrix[pivot_row], matrix[rank]
            
            # Eliminacja
            for row in range(rows):
                if row != rank and matrix[row][col] == 1:
                    for c in range(cols):
                        matrix[row][c] ^= matrix[rank][c]
            
            rank += 1
        
        return rank

    rank_counts = {M: 0, M-1: 0, 'other': 0}

    for i in range(num_matrices):
        # Utwórz macierz M×M
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

    # Oczekiwane wartości
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

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_matrix_rank",
    "samples_count": 100000
  }'
```

## Interpretacja wyników
- **rank_full**: Liczba macierzy z pełną rangą (32)
- **rank_minus_1**: Liczba macierzy z rangą 31
- **rank_other**: Liczba macierzy z rangą ≤30
- **p-value > 0.1**: Prawidłowy rozkład rang
- **Niska ranga**: Zależności liniowe między bitami

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 1024
- **Złożoność**: Wysoka
- **Co wykrywa**: Zależności liniowe
