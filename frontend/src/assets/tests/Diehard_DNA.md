# Diehard DNA Test

## Opis
Test DNA traktuje bity jako sekwencję DNA z 4-literowym alfabetem (A, C, G, T). Każda litera jest kodowana przez 2 bity: 00=A, 01=C, 10=G, 11=T. Test analizuje nakładające się 10-literowe "słowa" DNA i sprawdza sparse occupancy.

## Jak działa
1. Konwertuje pary bitów (2 bity) na litery DNA (0-3)
2. Tworzy nakładające się 10-literowe słowa DNA
3. Zlicza częstość każdego unikalnego słowa
4. Liczy słowa występujące dokładnie raz (singletons)
5. Porównuje z teoretyczną liczbą singletonów z rozkładu Poissona

## Wzór matematyczny
```
Alfabet DNA: 4 litery (A, C, G, T)
Liczba możliwych 10-literowych słów: 4^10 = 1,048,576

Parametr λ rozkładu Poissona:
λ = total_words / 4^10

Oczekiwana liczba singletonów:
expected = 4^10 × λ × e^(-λ)

Test Chi-kwadrat:
χ² = (observed - expected)² / expected
p-value = erfc((χ² / 2)^0.5)
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 2,097,152 bitów (2^21)
- **Bity na literę**: 2
- **Długość słowa**: 10 liter DNA (20 bitów)

## Implementacja
Test wykorzystuje numpy do konwersji par bitów na litery DNA (wartości 0-3). Nakładające się 10-literowe słowa są analizowane pod kątem sparse occupancy podobnie jak w testach OPSO/OQSO.

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_dna",
    "samples_count": 2097152,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład singletonów DNA
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowa sparse occupancy
- **passed = false**: Generator nie przeszedł testu

## Parametry testu
- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 2,097,152 bitów
- **Złożoność**: Średnia
- **Optymalizacja**: Wykorzystuje numpy dla konwersji par bitów
