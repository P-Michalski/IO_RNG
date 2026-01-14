Test sum kumulatywnych (CUSUM) wykrywa odchylenia od losowości poprzez śledzenie maksymalnego odchylenia skumulowanej sumy od zera.

## Jak działa

1. Konwertuje bity na +1/-1
2. Oblicza sumę kumulatywną w każdym punkcie
3. Znajduje maksymalne odchylenie (forward mode)
4. Oblicza p-value na podstawie tego odchylenia

## Wzory matematyczne

```
Dla każdego biti ∈ {0,1}:
Xi = 2×biti - 1  (konwersja do ±1)

Suma kumulatywna:
Sk = Σ(i=1 do k) Xi

Maksymalne odchylenie:
z = max|Sk|

P-value: złożony wzór z funkcją erfc
```

## Interpretacja geometryczna

Test obserwuje "random walk" - jeśli sekwencja jest losowa, suma kumulatywna powinna oscylować wokół zera bez zbyt dużych odchyleń.

## Implementacja

```python
def _nist_cumulative_sums_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Forward cumulative sum
    s = [0]
    for bit in bits:
        s.append(s[-1] + (1 if bit == 1 else -1))

    z_forward = max(abs(val) for val in s)

    # Test statistic (uproszczony wzór)
    sum_val = 0.0
    for k in range(int((-n / z_forward + 1) / 4),
                   int((n / z_forward - 1) / 4) + 1):
        term1 = erfc((4 * k + 1) * z_forward / math.sqrt(n))
        term2 = erfc((4 * k - 1) * z_forward / math.sqrt(n))
        sum_val += term1 - term2

    p_value = 1 - sum_val

    passed = p_value >= 0.01
    score = min(1.0, max(0.0, p_value))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'max_excursion': z_forward,
            'n': n
        }
    }
```

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_cumulative_sums",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **max_excursion**: Maksymalne odchylenie od zera
  - Im mniejsze, tym lepiej zbalansowana sekwencja
  - Duże wartości wskazują na bias
- **p-value > 0.5**: Bardzo dobra równowaga
- **p-value < 0.01**: Wykryto systematyczny bias

## Wizualizacja

```
Dobra sekwencja (losowa):
  Suma  |     /\    /\
        |    /  \  /  \

Zła sekwencja (bias):
  Suma  |          /
        |         /
```

## Parametry testu

- **Typ danych**: Bity
- **Minimalna liczba próbek**: 100
- **Złożoność**: Wysoka
- **Co wykrywa**: Systematyczny bias
