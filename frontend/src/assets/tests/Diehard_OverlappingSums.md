# Diehard Overlapping Sums Test

## Opis
Test Overlapping Sums konwertuje bity na liczby zmiennoprzecinkowe [0,1] i oblicza sumy nakładających się okien. Rozkład sum powinien być normalny zgodnie z centralnym twierdzeniem granicznym. Test sprawdza średnią i odchylenie standardowe sum.

## Jak działa
1. Konwertuje grupy bitów (8 bitów) na liczby [0,1]
2. Tworzy nakładające się okna o rozmiarze 10 wartości
3. Oblicza sumę dla każdego okna
4. Analizuje średnią i odchylenie standardowe sum
5. Porównuje z teoretycznymi wartościami używając z-score

## Wzór matematyczny
```
Dla uniform [0,1], suma n wartości:
- Teoretyczna średnia: n/2
- Teoretyczne odchylenie: √(n/12)

Dla okna rozmiaru 10:
expected_mean = 10/2 = 5.0
expected_std = √(10/12) ≈ 0.913

Z-scores:
z_mean = |mean_sum - expected_mean| / (expected_std / √num_sums)
z_std = |std_sum - expected_std| / (expected_std / √(2×num_sums))

Test łączny:
χ² = z_mean² + z_std²
p-value = erfc(√(χ² / 2))
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 100,000 bitów
- **Bity na wartość**: 8
- **Rozmiar okna**: 10 wartości

## Implementacja
Test wykorzystuje numpy do konwersji bitów na wartości [0,1] i obliczania sum nakładających się okien. Centralne twierdzenie graniczne gwarantuje normalność rozkładu sum dla prawdziwie losowych danych.

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_overlapping_sums",
    "samples_count": 100000,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład normalny sum
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład sum
- **passed = false**: Generator nie przeszedł testu

## Parametry testu
- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 100,000 bitów
- **Złożoność**: Niska-średnia
- **Optymalizacja**: Wykorzystuje numpy dla sum sliding window
