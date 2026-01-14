Test Parking Lot symuluje "parkowanie" kół na jednostkowym kwadracie [0,1]×[0,1]. Każde "koło" (punkt z promieniem) jest losowane, a test zlicza ile kół można zaparkować bez kolizji (nakładania się). Liczba zaparkowanych kół powinna być zgodna z rozkładem teoretycznym.

## Jak działa

1. Konwertuje bity na współrzędne (x, y) w zakresie [0,1]
2. Każdy punkt reprezentuje środek koła o stałym promieniu r
3. Próbuje "zaparkować" każde koło, sprawdzając kolizje z już zaparkowanymi
4. Liczy ile kół udało się zaparkować bez kolizji
5. Porównuje z oczekiwaną liczbą kół używając testu z-score

## Wzór matematyczny

```
Koło zaparkowane jeśli odległość > 2×radius od wszystkich innych

Odległość między punktami:
dist = √((x₁-x₂)² + (y₁-y₂)²)

Oczekiwana liczba zaparkowanych:
expected ≈ num_points × 0.3

Z-score:
z = |num_parked - expected| / √expected

p-value = erfc(z / √2)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 384,000 bitów (12,000 prób po 32 bity)
- **Bity na współrzędną**: 16
- **Promień koła**: 0.01 (stały)

## Implementacja

Test konwertuje 16-bitowe sekwencje na współrzędne [0,1] i symuluje proces parkowania sprawdzając kolizje między kołami. Używa numpy dla szybkiej konwersji bitów na współrzędne.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_parking_lot",
    "samples_count": 384000
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny rozkład zaparkowanych kół
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład przestrzenny
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 384,000 bitów
- **Złożoność**: Wysoka (sprawdzanie kolizji N×M)
- **Optymalizacja**: Wykorzystuje numpy dla konwersji współrzędnych
