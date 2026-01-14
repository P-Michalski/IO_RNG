Test sprawdza długość najdłuższego ciągu jedynek w sekwencji. Zbyt krótkie lub zbyt długie maksymalne serie mogą wskazywać na niełosowość.

## Jak działa
1. Dzieli sekwencję na bloki
2. W każdym bloku znajduje najdłuższy ciąg jedynek
3. Klasyfikuje bloki według długości najdłuższego run
4. Porównuje rozkład z oczekiwanym za pomocą Chi-kwadrat

## Parametry zależne od długości
```
n < 6,272:
  - M = 8 (rozmiar bloku)
  - K = 3 (liczba kategorii)
  - Kategorie długości: ≤1, 2, 3, ≥4

6,272 ≤ n < 750,000:
  - M = 128
  - K = 5
  - Kategorie: ≤4, 5, 6, 7, 8, ≥9

n ≥ 750,000:
  - M = 10,000
  - K = 6
  - Kategorie: ≤10, 11, 12, 13, 14, 15, ≥16
```

## Implementacja
```python
def _nist_longest_run_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    if n < 128:
        return {'passed': False, 'score': 0.0, 
                'error': 'Need at least 128 bits'}

    # Parametry dla różnych długości
    if n < 6272:
        K, M = 3, 8
        v_values = [1, 2, 3, 4]
        pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
    elif n < 750000:
        K, M = 5, 128
        v_values = [4, 5, 6, 7, 8, 9]
        pi_values = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    else:
        K, M = 6, 10000
        v_values = [10, 11, 12, 13, 14, 15, 16]
        pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

    num_blocks = n // M
    frequencies = [0] * (K + 1)

    # Dla każdego bloku znajdź najdłuższy run jedynek
    for i in range(num_blocks):
        block = bits[i * M:(i + 1) * M]
        max_run = 0
        current_run = 0
        
        for bit in block:
            if bit == 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        # Klasyfikuj
        for j, v in enumerate(v_values):
            if max_run <= v:
                frequencies[j] += 1
                break
        else:
            frequencies[K] += 1

    # Chi-square
    chi_square = sum(
        (frequencies[i] - num_blocks * pi_values[i]) ** 2 /
        (num_blocks * pi_values[i])
        for i in range(K + 1)
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
            'num_blocks': num_blocks,
            'block_size': M,
            'frequencies': frequencies
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_longest_run",
    "samples_count": 128000
  }'
```

## Interpretacja wyników
- **p-value > 0.1**: Rozkład długości runs jest prawidłowy
- **frequencies**: Pokazuje rozkład najdłuższych runs w blokach
- **chi_square**: Im mniejsza wartość, tym lepsze dopasowanie do oczekiwanego rozkładu

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 128
- **Złożoność**: Średnia
- **Co wykrywa**: Zbyt długie/krótkie serie
