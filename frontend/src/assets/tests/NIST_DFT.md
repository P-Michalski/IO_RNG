# NIST Discrete Fourier Transform (Spectral) Test

## Opis
Test DFT wykrywa okresowe wzorce w sekwencji bitowej używając transformaty Fouriera. Losowa sekwencja nie powinna mieć wyraźnych pików w spektrum częstotliwości.

## Jak działa
1. Konwertuje bity do wartości +1/-1
2. Oblicza dyskretną transformatę Fouriera (DFT)
3. Liczy piki przekraczające próg
4. Porównuje z oczekiwaną liczbą pików

## Wzory matematyczne
```
DFT: S(k) = Σ X(n)×e^(-2πikn/N)

Próg: T = √(ln(1/0.05)×n)

Oczekiwana liczba pików poniżej T:
N0 = 0.95×n/2

Statystyka: d = (N1 - N0) / √(n×0.95×0.05/4)

P-value: p = erfc(|d|/√2)
```

## Implementacja
```python
def _nist_dft_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc
    import numpy as np

    n = len(bits)

    if n < 100:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 100 bits'}

    # Konwersja do ±1
    X = [2*bit - 1 for bit in bits]

    # DFT
    S = np.fft.fft(X)
    M = np.abs(S[:n//2])

    # Próg
    T = math.sqrt(math.log(1/0.05) * n)

    # Zlicz piki poniżej progu
    N1 = sum(1 for peak in M if peak < T)

    # Oczekiwana liczba
    N0 = 0.95 * n / 2

    # Statystyka testowa
    d = (N1 - N0) / math.sqrt(n * 0.95 * 0.05 / 4)

    # P-value
    p_value = erfc(abs(d) / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'threshold': T,
            'peaks_below_threshold': N1,
            'expected_peaks': N0,
            'd': d
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_dft",
    "samples_count": 10000
  }'
```

## Interpretacja wyników
- **Wykrywa**: Okresowe wzorce, cykliczność
- **p-value > 0.5**: Brak wykrywalnych okresowości
- **peaks_below_threshold ≈ expected**: Prawidłowe spektrum
- **d**: Im mniejsza wartość bezwzględna, tym lepiej

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 100
- **Złożoność**: Wysoka
- **Co wykrywa**: Okresowe wzorce
