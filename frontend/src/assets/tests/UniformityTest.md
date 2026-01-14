Test równomierności sprawdza, czy średnia i wariancja wygenerowanych liczb odpowiadają teoretycznym wartościom dla rozkładu jednostajnego U(0,1).

## Jak działa

1. Oblicza średnią arytmetyczną wszystkich liczb
2. Oblicza wariancję próbki
3. Porównuje z wartościami oczekiwanymi:
   - Średnia powinna ≈ 0.5
   - Wariancja powinna ≈ 1/12 ≈ 0.0833

## Wzory matematyczne

```
Średnia: μ = (1/n) × Σ xi
Wariancja: σ² = (1/n) × Σ (xi - μ)²

Dla U(0,1):
- Oczekiwana średnia: E[X] = 0.5
- Oczekiwana wariancja: Var[X] = 1/12 ≈ 0.0833
```

## Kryteria zdania

- **|średnia - 0.5| < 0.05**
- **|wariancja - 0.0833| < 0.02**
- Obie warunki muszą być spełnione

## Implementacja

```python
def _uniformity_test(self, numbers: List[float]) -> Dict[str, Any]:
    n = len(numbers)

    # Oblicz średnią
    mean = sum(numbers) / n

    # Oblicz wariancję
    variance = sum((x - mean) ** 2 for x in numbers) / n

    # Wartości oczekiwane dla rozkładu uniform [0,1]
    expected_mean = 0.5
    expected_variance = 1.0 / 12.0  # ≈ 0.083

    # Różnice
    mean_diff = abs(mean - expected_mean)
    var_diff = abs(variance - expected_variance)

    # Test przechodzi jeśli różnice są małe
    passed = mean_diff < 0.05 and var_diff < 0.02

    # Score bazujący na różnicach
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

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "uniformity_test",
    "samples_count": 50000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **mean ≈ 0.5**: Generator produkuje liczby symetrycznie wokół środka
- **variance ≈ 0.083**: Rozproszenie danych jest prawidłowe
- **mean_diff > 0.05**: Generator może mieć bias (skrzywienie)
- **var_diff > 0.02**: Liczby są zbyt skupione lub zbyt rozproszone

## Parametry testu

- **Typ danych**: Liczby zmiennoprzecinkowe (floats)
- **Minimalna liczba próbek**: 100
- **Złożoność**: Niska
