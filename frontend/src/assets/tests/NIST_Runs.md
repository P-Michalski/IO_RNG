# NIST Runs Test

## Opis
Test sprawdza, czy liczba przejść (runs) między 0 a 1 jest prawidłowa. Run to nieprzerwany ciąg identycznych bitów. Test wykrywa czy sekwencja nie jest zbyt "gładka" lub zbyt "zmienna".

## Jak działa
1. Sprawdza pre-test: proporcja jedynek musi być bliska 0.5
2. Zlicza liczbę runs (przejść z 0→1 lub 1→0)
3. Porównuje z oczekiwaną liczbą runs
4. Oblicza p-value

## Wzory matematyczne
```
π = liczba jedynek / n

Pre-test: |π - 0.5| < 2/√n

Liczba runs: V_n (obs) = liczenie przejść

Oczekiwana liczba runs:
E[V_n] = 2nπ(1-π)

Statystyka testowa:
T = |V_n(obs) - E[V_n]| / (2√(2n)π(1-π))

P-value:
p = erfc(T/√2)
```

## Przykład runs
```
Sekwencja: 1 1 0 0 0 1 1 1 0 1
Runs:      [11][000][111][0][1]
Liczba runs: 5
```

## Implementacja
```python
def _nist_runs_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    # Pre-test: proporcja jedynek musi być bliska 0.5
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        return {
            'passed': False,
            'score': 0.0,
            'error': 'Pre-test failed: proportion of ones not close to 0.5',
            'statistics': {'pi': pi}
        }

    # Zlicz runs
    runs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1

    # Expected value
    expected_runs = 2 * n * pi * (1 - pi)

    # Test statistic
    numerator = abs(runs - expected_runs)
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    test_stat = numerator / denominator if denominator != 0 else 0

    # P-value
    p_value = erfc(test_stat / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'runs': runs,
            'expected_runs': expected_runs,
            'pi': pi
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_runs",
    "samples_count": 100000
  }'
```

## Interpretacja wyników
- **runs ≈ expected_runs**: Prawidłowa liczba przejść
- **runs << expected_runs**: Sekwencja zbyt "gładka", długie serie tych samych bitów
- **runs >> expected_runs**: Sekwencja zbyt "zmienna", za dużo przełączeń
- **Pre-test failed**: Sekwencja nie jest zbalansowana (użyj najpierw Monobit)

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 100
- **Złożoność**: Średnia
- **Co wykrywa**: Nieprawidłowe przejścia
