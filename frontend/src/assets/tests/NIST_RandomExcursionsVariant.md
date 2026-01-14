Wariant testu Random Excursions, który testuje więcej stanów (±1 do ±9) i używa innej statystyki testowej. Każdy stan ma osobną p-value.

## Jak działa

1. Podobnie jak Random Excursions: tworzy random walk
2. Testuje stany: ±1, ±2, ..., ±9 (18 stanów)
3. Dla każdego stanu oblicza osobną p-value
4. Test przechodzi gdy wszystkie p-values ≥ 0.01

## Wzory matematyczne

```
Dla stanu x:
statystyka = |wizyt - cykle| / √(2×cykle×(4|x|-2))

p-value(x) = erfc(statystyka/√2)

Test passed = wszystkie p-values ≥ 0.01
```

## Różnice od Random Excursions

- Więcej stanów (18 vs 8)
- Inna statystyka testowa
- Każdy stan testowany oddzielnie
- Bardziej rygorystyczny (wszystkie p-values muszą przejść)

## Implementacja

```python
def _nist_random_excursions_variant_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Konwersja do ±1 i oblicz sumy cząstkowe
    S = [0]
    for bit in bits:
        S.append(S[-1] + (1 if bit == 1 else -1))

    # Zlicz cykle
    cycles = sum(1 for i in range(1, len(S)) if S[i] == 0)

    if cycles < 500:
        return {
            'passed': False,
            'score': 0.0,
            'error': f'Need at least 500 cycles, got {cycles}',
            'statistics': {'cycles': cycles}
        }

    # Stany do testowania: ±1, ±2, ..., ±9
    states = list(range(-9, 0)) + list(range(1, 10))

    results = {}
    all_passed = True

    for state in states:
        # Zlicz wizyty w tym stanie
        visits = sum(1 for s in S if s == state)

        # Oblicz statystykę testową
        numerator = abs(visits - cycles)
        denominator = math.sqrt(2 * cycles * (4 * abs(state) - 2))

        if denominator > 0:
            test_stat = numerator / denominator
            p_value = erfc(test_stat / math.sqrt(2))
        else:
            p_value = 0.0

        results[f'state_{state}'] = {
            'p_value': p_value,
            'visits': visits,
            'expected': cycles,
            'passed': p_value >= 0.01
        }

        if p_value < 0.01:
            all_passed = False

    passed = all_passed
    score = min(1.0, min(r['p_value'] for r in results.values()))

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'cycles': cycles,
            'num_states_tested': len(states),
            'states_results': results
        }
    }
```

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_random_excursions_variant",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **cycles**: Liczba cykli
- **num_states_tested**: Liczba testowanych stanów (18)
- **states_results**: Wyniki dla każdego stanu
  - **visits**: Faktyczna liczba wizyt
  - **expected**: Oczekiwana liczba (równa liczbie cykli)
  - **p_value**: Musi być ≥ 0.01
- **Wszystkie stany muszą przejść**: Bardziej restrykcyjny niż podstawowy test

## Porównanie z Random Excursions

| Cecha          | Random Excursions | Random Excursions Variant |
| -------------- | ----------------- | ------------------------- |
| Liczba stanów  | 8 (±1 do ±4)      | 18 (±1 do ±9)             |
| Statystyka     | Chi-kwadrat       | Różnica/√variance         |
| Kryterium      | Każdy stan osobno | Każdy stan osobno         |
| Restrykcyjność | Średnia           | Wysoka                    |

## Parametry testu

- **Typ danych**: Bity
- **Minimalna liczba próbek**: ~10000 (dla 500 cykli)
- **Złożoność**: Bardzo wysoka
- **Co wykrywa**: Random walk (więcej stanów)
