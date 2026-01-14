Test Runs analizuje długości ciągów (runs) kolejnych zer lub jedynek w sekwencji bitowej. Dla prawdziwie losowego generatora, rozkład długości runs powinien być zgodny z rozkładem teoretycznym - krótkie runy są częstsze, długie rzadsze.

## Jak działa

1. Przechodzi przez sekwencję bitów i identyfikuje ciągi (runs)
2. Zlicza długość każdego runa (ciągu kolejnych 0 lub 1)
3. Grupuje runy według długości: 1, 2, 3, 4, 5, 6, ≥7
4. Porównuje z teoretycznym rozkładem używając testu Chi-kwadrat

## Wzór matematyczny

```
Teoretyczne prawdopodobieństwo runa długości k:
P(długość = k) = 2 × (1/2)^(k+1)

Dla k ≥ 7: P(długość ≥ 7) = 2 × (1/2)^8

Oczekiwana liczba runów długości k:
expected[k] = P(k) × total_runs

Test Chi-kwadrat:
χ² = Σ (observed[k] - expected[k])² / expected[k]
     k=1..7

Stopnie swobody: df = 6
p-value = erfc((χ² / (2×df))^0.5)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 100,000 bitów
- **Kategorie długości**: 7 (1-6, ≥7)

## Implementacja

Test wykorzystuje numpy i operację `np.diff` do szybkiego wykrywania zmian wartości bitów. Runy są identyfikowane przez miejsca zmiany, a ich długości są grupowane i analizowane.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_runs",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny rozkład długości runów
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład runów
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 100,000 bitów
- **Złożoność**: Niska-średnia
- **Optymalizacja**: Wykorzystuje numpy diff dla wykrywania zmian
