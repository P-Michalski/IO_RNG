Test częstości Chi-kwadrat sprawdza, czy wygenerowane liczby są równomiernie rozłożone w zadanych przedziałach (binach). Jest to podstawowy test równomierności rozkładu.

## Jak działa
1. Dzieli zakres [0, 1] na 10 równych przedziałów (binów)
2. Zlicza ile liczb wpadło do każdego przedziału
3. Porównuje obserwowane częstości z oczekiwanymi za pomocą statystyki Chi-kwadrat
4. Oblicza wynik testu na podstawie odchylenia od idealnego rozkładu

## Wzór matematyczny
```
χ² = Σ ((Oi - Ei)² / Ei)

gdzie:
- Oi = obserwowana liczba w binie i
- Ei = oczekiwana liczba w binie i (n/10)
- n = całkowita liczba próbek
```

## Wartość krytyczna
- **Próg**: χ² < 16.919 (dla α=0.05, df=9)
- Test **zaliczony** gdy χ² < wartość krytyczna

## Implementacja
```python
def _frequency_test(self, numbers: List[float]) -> Dict[str, Any]:
    num_bins = 10
    bins = [0] * num_bins

    # Zlicz liczby w każdym binie
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

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "frequency_test",
    "samples_count": 10000,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład równomierny
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, może nie być losowy
- **passed = false**: Generator nie przeszedł testu, rozkład niejednostajny

## Parametry testu
- **Typ danych**: Liczby zmiennoprzecinkowe (floats)
- **Minimalna liczba próbek**: 100
- **Złożoność**: Niska
