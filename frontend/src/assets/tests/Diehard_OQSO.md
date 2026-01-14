Test OQSO (Overlapping-Quadruples-Sparse-Occupancy) jest podobny do OPSO, ale analizuje 4-literowe słowa zamiast par. Dzieli 32-bitowe słowa na 5-bitowe "litery" (32 możliwe wartości), tworząc nakładające się czwórki liter i licząc singletons.

## Jak działa
1. Konwertuje bity na 32-bitowe słowa
2. Każde 32-bitowe słowo dzieli na 6 5-bitowych "liter"
3. Z 6 liter tworzy 3 nakładające się czwórki (pozycje 0-3, 1-4, 2-5)
4. Zlicza częstość każdej unikalnej czwórki
5. Liczy czwórki występujące dokładnie raz i porównuje z rozkładem Poissona

## Wzór matematyczny
```
Liczba możliwych czwórek: 32^4 = 1,048,576
(każda litera ma 32 możliwe wartości)

Parametr λ rozkładu Poissona:
λ = total_quadruples / 32^4

Oczekiwana liczba singletonów:
expected = 32^4 × λ × e^(-λ)

Test Chi-kwadrat:
χ² = (observed - expected)² / expected
p-value = erfc((χ² / 2)^0.5)
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 2,097,152 bitów (2^21)
- **Bity na słowo**: 32

## Implementacja
Test konwertuje bity na 32-bitowe słowa, następnie ekstrahuje 5-bitowe litery przez operacje bitowe (shift i mask). Tworzy nakładające się czwórki i analizuje ich sparse occupancy.

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_oqso",
    "samples_count": 2097152,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład singletonów
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowa sparse occupancy
- **passed = false**: Generator nie przeszedł testu

## Parametry testu
- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 2,097,152 bitów
- **Złożoność**: Średnia-wysoka
- **Optymalizacja**: Wykorzystuje numpy dla konwersji bitów
