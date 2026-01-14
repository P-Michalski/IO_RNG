Test Bitstream analizuje częstości 20-bitowych słów w nakładających się oknach. Sprawdza, czy liczba wystąpień najbardziej i najmniej częstego słowa jest w normie dla prawdziwie losowego generatora.

## Jak działa

1. Tworzy nakładające się 20-bitowe słowa z ciągu bitów
2. Zlicza wystąpienia każdego unikalnego słowa
3. Znajduje maksymalną i minimalną częstość wystąpień
4. Porównuje z oczekiwaną częstością (rozkład równomierny)
5. Oblicza z-score dla odchyleń i konwertuje na p-value

## Wzór matematyczny

```
Liczba możliwych 20-bitowych słów: 2^20 = 1,048,576

Oczekiwana częstość każdego słowa:
expected_count = total_words / 2^20

Z-score dla odchyleń:
z = max(|max_count - expected| / √expected,
        |min_count - expected| / √expected)

p-value = erfc(z / √2)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 2,097,152 bitów (2^21)
- **Długość słowa**: 20 bitów

## Implementacja

Test wykorzystuje numpy do efektywnej konwersji sliding windows na wartości całkowite. Używa `np.unique` do szybkiego zliczania częstości.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_bitstream",
    "samples_count": 2097152,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealnie równomierny rozkład częstości
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nierównomierny rozkład
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 2,097,152 bitów
- **Złożoność**: Wysoka (analiza wielu nakładających się okien)
- **Optymalizacja**: Wykorzystuje numpy dla sliding window
