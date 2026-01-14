Test analizuje liczbę cykli w "random walk" - spacerze losowym utworzonym z sekwencji. Sprawdza czy liczba wizyt w każdym stanie random walk jest prawidłowa.

## Jak działa
1. Konwertuje bity do +1/-1
2. Oblicza sumy cząstkowe (random walk)
3. Zlicza cykle (powroty do zera)
4. Dla każdego stanu (-4 do +4) zlicza wizyty
5. Porównuje z oczekiwanymi wartościami

## Wzory matematyczne
```
Xi = 2×biti - 1  (konwersja do ±1)

Suma cząstkowa:
Sk = Σ(i=1 do k) Xi

Cykl: powrót Sk do 0

Stany testowane: ±1, ±2, ±3, ±4

Dla każdego stanu x:
χ²(x) = Σ (wizyt - oczekiwane)² / oczekiwane
```

## Wymagania
- **Minimum cykli**: 500
- Jeśli < 500 cykli, test nie może być wykonany

## Interpretacja geometryczna
```
Random walk:
  +4 |      *
  +3 |    *   *
  +2 |  *       *
  +1 |*           *
   0 |-------------  (powrót = cykl)
  -1 |
```

## Implementacja
```python
def _nist_random_excursions_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Konwersja do ±1 i oblicz sumy cząstkowe
    S = [0]
    for bit in bits:
        S.append(S[-1] + (1 if bit == 1 else -1))

    # Zlicz cykle (powroty do 0)
    cycles = sum(1 for i in range(1, len(S)) if S[i] == 0)

    if cycles < 500:
        return {
            'passed': False,
            'score': 0.0,
            'error': f'Need at least 500 cycles, got {cycles}',
            'statistics': {'cycles': cycles}
        }

    # Stany do testowania
    states = [-4, -3, -2, -1, 1, 2, 3, 4]
    
    # Prawdopodobieństwa teoretyczne dla każdego stanu
    pi = {
        1: [0.5000, 0.2500, 0.1250, 0.0625, 0.0312, 0.0312],
        2: [0.7500, 0.0625, 0.0469, 0.0352, 0.0264, 0.0791],
        3: [0.8333, 0.0278, 0.0231, 0.0193, 0.0161, 0.0804],
        4: [0.8750, 0.0156, 0.0137, 0.0120, 0.0105, 0.0733]
    }

    results = {}
    all_passed = True

    for state in states:
        abs_state = abs(state)
        
        # Zlicz wizyty w tym stanie w każdym cyklu
        visits = []
        cycle_start = 0
        
        for i in range(1, len(S)):
            if S[i] == 0:
                # Koniec cyklu
                count = sum(1 for j in range(cycle_start, i) if S[j] == state)
                visits.append(count)
                cycle_start = i

        # Klasyfikuj wizyty
        frequencies = [0] * 6
        for v in visits:
            if v >= 5:
                frequencies[5] += 1
            else:
                frequencies[v] += 1

        # Chi-square dla tego stanu
        expected_probs = pi[abs_state]
        chi_square = sum(
            (frequencies[i] - cycles * expected_probs[i]) ** 2 / (cycles * expected_probs[i])
            for i in range(6) if expected_probs[i] > 0
        )

        # P-value
        p_value = erfc(math.sqrt(chi_square / 2))
        
        results[f'state_{state}'] = {
            'p_value': p_value,
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
            'states_results': results
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_random_excursions",
    "samples_count": 100000
  }'
```

## Interpretacja wyników
- **cycles**: Liczba cykli (powrotów do zera)
- **states_results**: Wyniki dla każdego stanu
- **p_value dla każdego stanu**: Musi być ≥ 0.01
- **Wszystkie stany**: Muszą przejść test

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: ~10000 (dla 500 cykli)
- **Złożoność**: Bardzo wysoka
- **Co wykrywa**: Właściwości random walk
