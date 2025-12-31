# NIST Approximate Entropy Test

## Opis
Test entropii aproksymacyjnej mierzy częstotliwość wszystkich możliwych nakładających się wzorców (patternów) długości m w sekwencji. Wykrywa, czy sekwencja jest zbyt regularna lub przewidywalna.

## Jak działa
1. Wybiera długość wzorca m (domyślnie 10, dostosowywane do długości sekwencji)
2. Liczy wszystkie możliwe wzorce długości m
3. Oblicza entropię dla wzorców długości m i m+1
4. Porównuje te entropie - dla losowej sekwencji powinny być podobne

## Wzory matematyczne
```
Dla wzorca długości m:
Φ(m) = Σ (pi × log(pi))

gdzie pi = częstość wzorca i

Approximate Entropy:
ApEn(m) = Φ(m) - Φ(m+1)

Statystyka Chi-kwadrat:
χ² = 2n(log(2) - ApEn)

P-value:
p = erfc(√(χ²/2))
```

## Parametry adaptacyjne
```python
# Dopasowanie m do rozmiaru sekwencji
m = min(m_requested, int(log2(n)) - 5)
if m < 2:
    m = 2
```

## Implementacja
```python
def _nist_approximate_entropy_test(self, bits: List[int], m: int = 10):
    import math
    from math import erfc

    n = len(bits)

    if n < 100:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 100 bits'}

    # Dopasuj m jeśli n jest za małe
    m = min(m, int(math.log2(n)) - 5)
    if m < 2:
        m = 2

    def compute_phi(m_local):
        patterns = {}
        for i in range(n):
            pattern = tuple(bits[i:i+m_local] + bits[:max(0, i+m_local-n)])
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        phi = 0.0
        for count in patterns.values():
            pi = count / n
            phi += pi * math.log(pi)
        return phi

    phi_m = compute_phi(m)
    phi_m_plus_1 = compute_phi(m + 1)

    apen = phi_m - phi_m_plus_1

    # Chi-square approximation
    chi_square = 2 * n * (math.log(2) - apen)

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'approximate_entropy': apen,
            'chi_square': chi_square,
            'm': m
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_approximate_entropy",
    "samples_count": 100000
  }'
```

## Interpretacja wyników
- **approximate_entropy**: Wartość ApEn
  - Im bliżej 0, tym bardziej losowa sekwencja
  - Duże wartości sugerują regularność
- **m**: Długość wzorca użyta w teście
  - Większe m = dokładniejszy test (wymaga więcej danych)
- **p-value > 0.1**: Brak wykrywalnych wzorców, dobra losowość
- **p-value < 0.01**: Wykryto regularność we wzorcach

## Co wykrywa
- Powtarzające się sekwencje
- Cykliczne wzorce
- Zbyt przewidywalną strukturę
- Brak entropii w danych

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 100
- **Złożoność**: Wysoka
- **Co wykrywa**: Regularność wzorców
