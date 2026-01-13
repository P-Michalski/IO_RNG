# Diehard Count-the-1s Test

## Opis
Test Count-the-1s zlicza liczbę jedynek w każdym bajcie i sprawdza, czy rozkład liczby jedynek zgadza się z teoretycznym rozkładem dwumianowym B(8, 0.5). Każdy bajt może mieć od 0 do 8 jedynek.

## Jak działa
1. Konwertuje bity na bajty (8-bitowe sekwencje)
2. Dla każdego bajtu zlicza liczbę jedynek (0-8)
3. Tworzy histogram częstości dla każdej możliwej liczby jedynek
4. Porównuje z teoretycznym rozkładem dwumianowym
5. Używa testu Chi-kwadrat do weryfikacji

## Wzór matematyczny
```
Rozkład dwumianowy B(8, 0.5):
P(k jedynek) = C(8,k) × 0.5^8

gdzie C(8,k) = 8! / (k! × (8-k)!)

Oczekiwana liczba bajtów z k jedynkami:
expected[k] = P(k jedynek) × num_bytes

Test Chi-kwadrat:
χ² = Σ (observed[k] - expected[k])² / expected[k]
     k=0..8

Stopnie swobody: df = 8
p-value = erfc((χ² / (2×df))^0.5)
```

## Wartość krytyczna
- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania
- **Minimum**: 256,000 bitów (32,000 bajtów)
- **Bity na bajt**: 8

## Implementacja
Test wykorzystuje numpy do szybkiego zliczania jedynek w każdym bajcie przez operację `np.sum(axis=1)` na macierzy bajtów. Rozkład dwumianowy oblicza się używając współczynników dwumianowych.

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_count_1s",
    "samples_count": 256000,
    "seed": 42
  }'
```

## Interpretacja wyników
- **score = 1.0**: Idealny rozkład dwumianowy
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład jedynek
- **passed = false**: Generator nie przeszedł testu

## Parametry testu
- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 256,000 bitów
- **Złożoność**: Niska
- **Optymalizacja**: Wykorzystuje numpy dla zliczania jedynek
