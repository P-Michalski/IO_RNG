# Diehard Binary Rank Test

## Opis
Test Binary Rank sprawdza rangę (rank) macierzy binarnych 32x32 utworzonych z bitów. Dla prawdziwie losowych bitów, rozkład rang powinien być charakterystyczny - większość macierzy powinna mieć pełną rangę (32) lub rangę 31.

## Jak działa
1. Konwertuje bity na macierze binarne 32x32 (1024 bity każda)
2. Dla każdej macierzy oblicza rangę używając eliminacji Gaussa w GF(2)
3. Zlicza ile macierzy ma rangę 32, 31 lub mniejszą
4. Porównuje z teoretycznym rozkładem używając testu Chi-kwadrat

## Wzór matematyczny
```
Teoretyczne prawdopodobieństwa dla 32x32:
P(rank=32) ≈ 0.2888
P(rank=31) ≈ 0.5776
P(rank≤30) ≈ 0.1336

Test Chi-kwadrat:
χ² = Σ (observed - expected)² / expected

p-value = erfc((χ² / 4)^0.5)
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 10,240 bitów (10 macierzy)
- **Zalecane**: 100,000+ bitów
- **Bity na macierz**: 1024 (32×32)

## Implementacja
Test wykorzystuje numpy do szybkiego obliczania rangi macierzy za pomocą eliminacji Gaussa w ciele GF(2). Operacje XOR zastępują dodawanie i odejmowanie w standardowej eliminacji.

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_binary_rank",
    "samples_count": 100000,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład rang
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład rang
- **passed = false**: Generator nie przeszedł testu

## Parametry testu
- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 10,240 bitów
- **Złożoność**: Bardzo wysoka (eliminacja Gaussa dla wielu macierzy)
- **Optymalizacja**: Wykorzystuje numpy dla operacji macierzowych
