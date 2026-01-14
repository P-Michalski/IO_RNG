Test Squeeze kompresuje losowe 32-bitowe integery poprzez iteracyjne mnożenie przez losowe liczby zmiennoprzecinkowe [0,1] aż wynik będzie < 1. Zlicza liczbę iteracji (mnożeń) potrzebnych do "ściśnięcia" wartości poniżej 1. Rozkład liczby iteracji powinien być charakterystyczny.

## Jak działa

1. Konwertuje bity na 32-bitowe integery
2. Konwertuje też na floaty [0,1] używane jako mnożniki
3. Dla każdego integera, iteracyjnie mnoży przez kolejne floaty
4. Liczy ile mnożeń potrzeba aby wartość < 1
5. Analizuje rozkład liczby iteracji (średnia, odchylenie)

## Wzór matematyczny

```
Proces squeeze dla wartości v:
v₀ = integer (duża wartość)
vᵢ₊₁ = vᵢ × floatᵢ

Liczymy iteracje aż vₙ < 1

Teoretyczna średnia: ≈ 47 iteracji

Z-score:
z = |mean_count - 47| / std_count

p-value = erfc(z / √2)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 100,000 bitów
- **Bity na integer**: 32

## Implementacja

Test wykorzystuje numpy do konwersji bitów na 32-bitowe integery i floaty [0,1]. Proces squeeze jest symulowany iteracyjnie dla każdej pary (integer, sequence of floats).

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_squeeze",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny rozkład liczby iteracji
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład squeeze
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 100,000 bitów
- **Złożoność**: Średnia (iteracyjne mnożenie)
- **Optymalizacja**: Wykorzystuje numpy dla konwersji
