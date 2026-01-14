Test OPSO (Overlapping-Pairs-Sparse-Occupancy) sprawdza jak często 10-bitowe "słowa" pojawiają się dokładnie 1 raz w strumieniu. Zlicza "sparse occupancy" - słowa występujące pojedynczo, co jest charakterystyczne dla prawdziwie losowego źródła.

## Jak działa
1. Tworzy nakładające się 10-bitowe słowa z ciągu bitów
2. Zlicza częstość wystąpień każdego słowa
3. Liczy ile słów wystąpiło dokładnie raz (singletons)
4. Porównuje z teoretyczną liczbą singletonów z rozkładu Poissona
5. Używa testu Chi-kwadrat do weryfikacji

## Wzór matematyczny
```
Liczba możliwych 10-bitowych słów: 2^10 = 1,024

Parametr λ rozkładu Poissona:
λ = total_words / 1024

Oczekiwana liczba singletonów:
expected = 1024 × λ × e^(-λ)

Test Chi-kwadrat:
χ² = (observed - expected)² / expected
p-value = erfc((χ² / 2)^0.5)
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 2,097,152 bitów (2^21)
- **Długość słowa**: 10 bitów

## Implementacja
Test wykorzystuje numpy do szybkiej konwersji sliding windows na integery oraz `np.unique` do zliczania częstości. Rozkład Poissona modeluje prawdopodobieństwo pojedynczych wystąpień.

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_opso",
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
- **Złożoność**: Średnia
- **Optymalizacja**: Wykorzystuje numpy dla sliding window
