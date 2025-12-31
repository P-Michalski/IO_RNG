# NIST Maurer's Universal Statistical Test

## Opis
Test uniwersalny Maurera mierzy kompresowność sekwencji. Losowa sekwencja powinna być trudna do skompresowania. Test mierzy dystans między powtórzeniami L-bitowych wzorców.

## Jak działa
1. Dzieli sekwencję na L-bitowe bloki
2. Faza inicjalizacji: Q pierwszych bloków buduje tabelę
3. Faza testowa: K kolejnych bloków testuje dystanse
4. Oblicza średni logarytm dystansu

## Wzory matematyczne
```
fn = (1/K) × Σ log2(i - T[blocki])

gdzie T[block] = ostatnia pozycja bloku

Parametry adaptacyjne:
L=6, Q=640   dla n < 387840
L=7, Q=1280  dla n < 904960
L=8, Q=2560  dla n ≥ 904960
```

## Implementacja
```python
def _nist_universal_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Wybierz parametry L, Q
    if n < 387840:
        L, Q = 6, 640
        expected = 5.2177052
        variance = 2.954
    elif n < 904960:
        L, Q = 7, 1280
        expected = 6.1962507
        variance = 3.125
    else:
        L, Q = 8, 2560
        expected = 7.1836656
        variance = 3.238

    K = (n // L) - Q

    if K <= 0:
        return {'passed': False, 'score': 0.0,
                'error': f'Need at least {(Q + 1) * L} bits for L={L}'}

    T = {}  # Tabela pozycji bloków

    # Faza inicjalizacji
    for i in range(1, Q + 1):
        block = tuple(bits[(i-1)*L:i*L])
        T[block] = i

    # Faza testowa
    sum_log = 0.0
    for i in range(Q + 1, Q + K + 1):
        block = tuple(bits[(i-1)*L:i*L])
        if block in T:
            distance = i - T[block]
            sum_log += math.log2(distance)
        T[block] = i

    fn = sum_log / K

    # Statystyka testowa
    test_stat = abs(fn - expected) / math.sqrt(variance / K)

    # P-value
    p_value = erfc(test_stat / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'fn': fn,
            'expected': expected,
            'L': L,
            'Q': Q,
            'K': K
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_universal",
    "samples_count": 500000
  }'
```

## Interpretacja wyników
- **fn ≈ expected**: Dobra kompresowność (wysoka entropia)
- **fn znacznie różne**: Sekwencja zbyt regularna lub zbyt chaotyczna
- **L**: Długość bloku użyta w teście

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 387840
- **Złożoność**: Wysoka
- **Co wykrywa**: Kompresowność
