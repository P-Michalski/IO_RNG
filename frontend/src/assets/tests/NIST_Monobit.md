Najprostszy test NIST. Sprawdza, czy liczba jedynek i zer w sekwencji bitowej jest w przybliżeniu równa. Jest to fundamentalny test równowagi bitów.

## Jak działa
1. Konwertuje bity na wartości +1 (dla 1) i -1 (dla 0)
2. Sumuje wszystkie wartości
3. Im mniejsza suma bezwzględna, tym lepiej zbalansowana sekwencja
4. Oblicza p-value za pomocą funkcji komplementarnej błędu (erfc)

## Wzory matematyczne
```
S = Σ (2×biti - 1)  gdzie bit ∈ {0,1}

Statystyka testowa:
s_obs = |S| / √n

P-value:
p = erfc(s_obs / √2)
```

## Kryterium zdania
- **p-value ≥ 0.01**
- Test zaliczony gdy p-value jest wystarczająco duże

## Implementacja
```python
def _nist_monobit_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)
    # S = suma bitów (jako +1/-1)
    s = sum(1 if bit == 1 else -1 for bit in bits)

    # Test statistic
    s_obs = abs(s) / math.sqrt(n)

    # P-value
    p_value = erfc(s_obs / math.sqrt(2))

    # Test passes if p-value >= 0.01
    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            's_obs': s_obs,
            'ones': sum(bits),
            'zeros': n - sum(bits),
            'threshold': 0.01
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_monobit",
    "samples_count": 100000
  }'
```

## Interpretacja wyników
- **p-value ≈ 1.0**: Idealna równowaga między 0 i 1
- **p-value > 0.5**: Bardzo dobra równowaga
- **p-value < 0.01**: Test niezaliczony, sekwencja nielosowa
- **ones ≈ zeros**: Dobry znak równowagi

## Przykład wyniku
```json
{
  "passed": true,
  "score": 0.8234,
  "statistics": {
    "p_value": 0.823412,
    "s_obs": 0.223,
    "ones": 50112,
    "zeros": 49888,
    "threshold": 0.01
  },
  "generated_bits": [0, 1, 1, 0, ...]
}
```

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 100
- **Złożoność**: Niska
- **Co wykrywa**: Niezbalansowanie 0/1
