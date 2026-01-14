Test Minimum Distance losuje punkty w przestrzeni 2D ([0,1]×[0,1]) i oblicza minimalną odległość między każdym punktem a jego najbliższym sąsiadem. Rozkład minimalnych odległości powinien być zgodny z rozkładem teoretycznym zależnym od gęstości punktów.

## Jak działa

1. Konwertuje bity na punkty 2D w jednostkowym kwadracie [0,1]×[0,1]
2. Dla każdego punktu oblicza odległość do najbliższego sąsiada
3. Zbiera rozkład minimalnych odległości
4. Analizuje średnią i odchylenie standardowe minimalnych odległości
5. Porównuje z teoretyczną średnią używając z-score

## Wzór matematyczny

```
Odległość euklidesowa:
dist = √((x₁-x₂)² + (y₁-y₂)²)

Teoretyczna średnia odległość:
expected_mean ≈ √(1 / num_points)

Z-score:
z = |mean_distance - expected_mean| / std_distance

p-value = erfc(z / √2)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 200,000 bitów
- **Minimum punktów**: 100
- **Bity na współrzędną**: 10

## Implementacja

Test wykorzystuje numpy do konwersji bitów na współrzędne i obliczania odległości euklidesowych między punktami. Dla wydajności, analizuje tylko pierwsze 500 punktów.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_minimum_distance",
    "samples_count": 200000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny rozkład minimalnych odległości
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład przestrzenny
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 200,000 bitów
- **Złożoność**: Wysoka (obliczanie N×N odległości)
- **Optymalizacja**: Wykorzystuje numpy dla obliczeń wektorowych
