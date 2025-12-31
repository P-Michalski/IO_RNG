# NIST Non-Overlapping Template Matching Test

## Opis
Test szuka określonego wzorca (template) w sekwencji, gdzie wystąpienia nie nakładają się na siebie. Sprawdza czy liczba wystąpień jest zgodna z oczekiwaniami dla losowej sekwencji.

## Jak działa
1. Wybiera m-bitowy wzorzec (domyślnie 000000001)
2. Dzieli sekwencję na bloki wielkości M
3. W każdym bloku zlicza wystąpienia wzorca (non-overlapping)
4. Porównuje rozkład z oczekiwanym

## Wzory matematyczne
```
Oczekiwana liczba wystąpień w bloku:
μ = (M - m + 1) / 2^m

Wariancja:
σ² = M × [(1/2^m) - (2m-1)/2^(2m)]

Chi-square: χ² = Σ(Wi - μ)² / σ²

P-value: p = erfc(√(χ²/2))
```

## Parametry
- **Domyślny template**: [0,0,0,0,0,0,0,0,1]
- **Rozmiar bloku**: M = 1000
- **Minimum bitów**: 1000

## Implementacja
```python
def _nist_non_overlapping_template_test(self, bits: List[int], 
                                        template: List[int] = None) -> Dict[str, Any]:
    import math
    from math import erfc

    if template is None:
        template = [0, 0, 0, 0, 0, 0, 0, 0, 1]

    n = len(bits)
    m = len(template)
    M = 1000
    N = n // M

    if N == 0:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 1000 bits'}

    # Oczekiwana wartość i wariancja
    mu = (M - m + 1) / (2 ** m)
    sigma_sq = M * ((1 / (2 ** m)) - ((2 * m - 1) / (2 ** (2 * m))))

    counts = []
    for i in range(N):
        block = bits[i * M:(i + 1) * M]
        count = 0
        j = 0
        while j <= len(block) - m:
            if block[j:j+m] == template:
                count += 1
                j += m  # Non-overlapping
            else:
                j += 1
        counts.append(count)

    # Chi-square
    chi_square = sum((count - mu) ** 2 for count in counts) / sigma_sq

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
            'num_blocks': N,
            'template': template,
            'expected_matches': mu,
            'variance': sigma_sq
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_non_overlapping_template",
    "samples_count": 100000
  }'
```

## Interpretacja wyników
- **expected_matches**: Oczekiwana liczba wystąpień wzorca w bloku
- **p-value > 0.1**: Prawidłowa częstość występowania wzorca
- **chi_square**: Im mniejsza wartość, tym lepiej

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 1000
- **Złożoność**: Średnia
- **Co wykrywa**: Specyficzne wzorce
