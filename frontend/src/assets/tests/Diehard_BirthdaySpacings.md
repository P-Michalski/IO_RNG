Test Birthday Spacings bada odległości między "urodzinami" (powtórzeniami wartości) w 24-bitowych słowach. Bazuje na problemie urodzin - dla prawdziwie losowego źródła, rozkład odległości między duplikatami powinien być zgodny z rozkładem Poissona.

## Jak działa
1. Konwertuje bity na 24-bitowe słowa
2. Dzieli słowa na bloki po 512 elementów
3. W każdym bloku sortuje słowa i znajduje duplikaty
4. Mierzy odległość (spacing) między duplikatami
5. Testuje zgodność rozkładu spacingów z rozkładem Poissona

## Wzór matematyczny
```
Teoretyczna średnia spacing = 2^24 / 512 ≈ 32,768

Test Chi-kwadrat:
χ² = |mean_spacing - expected_mean| / (variance / n)^0.5

p-value = erfc(χ² / √2)
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 262,144 bitów (2^18)
- **Zalecane**: 1,048,576 bitów (2^20)
- **Minimum bloków**: 10

## Implementacja
Test wykorzystuje optymalizacje numpy dla szybkiej konwersji bitów na słowa. Jeśli znaleziono mało duplikatów (< 10), test uznaje to za oznakę doskonałej losowości (score = 0.95).

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_birthday_spacings",
    "samples_count": 1048576,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład spacingów
- **score > 0.7**: Bardzo dobry wynik
- **score = 0.95 (mało duplikatów)**: Doskonała losowość
- **score < 0.5**: Słaby generator, nieprzypadkowy wzorzec
- **passed = false**: Generator nie przeszedł testu

## Parametry testu
- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 262,144 bitów
- **Złożoność**: Wysoka (sortowanie, wyszukiwanie duplikatów)
- **Optymalizacja**: Wykorzystuje numpy dla szybszej konwersji
