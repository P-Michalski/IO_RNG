Test Overlapping Permutations analizuje częstości permutacji 5 kolejnych wartości w nakładających się oknach. Dla 5 wartości istnieje 5! = 120 możliwych permutacji. Test sprawdza, czy rozkład permutacji jest równomierny.

## Jak działa

1. Konwertuje bity na bajty (8-bitowe wartości)
2. Tworzy nakładające się okna po 5 bajtów
3. Dla każdego okna oblicza rangę (permutację) wartości
4. Zlicza wystąpienia każdej permutacji
5. Używa testu Chi-kwadrat do sprawdzenia równomierności rozkładu

## Wzór matematyczny

```
Liczba możliwych permutacji: 5! = 120

Oczekiwana liczba każdej permutacji:
expected_count = total_windows / 120

Test Chi-kwadrat:
χ² = Σ (observed - expected)² / expected

p-value = erfc((χ² / (2 * df))^0.5)
gdzie df = 119 (stopnie swobody)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 1,048,576 bitów (2^20)
- **Okno**: 5 bajtów (nakładające się)

## Implementacja

Test wykorzystuje numpy do szybkiej konwersji bitów na bajty. Rangę permutacji oblicza się porównując każdą wartość z pozostałymi w oknie.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_overlapping_permutations",
    "samples_count": 1048576,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealnie równomierny rozkład permutacji
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nierównomierny rozkład
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 1,048,576 bitów
- **Złożoność**: Wysoka (analiza permutacji)
- **Optymalizacja**: Wykorzystuje numpy dla konwersji bitów
