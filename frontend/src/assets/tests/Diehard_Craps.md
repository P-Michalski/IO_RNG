Test Craps symuluje grę w kości (craps) używając bitów jako źródła losowości dla rzutów kostką. Gra ma dobrze zdefiniowane prawdopodobieństwa wygranej (~49.3%), które powinny być osiągnięte przez prawdziwie losowy generator.

## Jak działa

1. Konwertuje trójki bitów na rzuty kostką (1-6)
2. Symuluje gry w craps według standardowych zasad
3. Zlicza wygrane i przegrane gry
4. Porównuje proporcję wygranych z teoretyczną wartością (~0.493)
5. Używa testu Chi-kwadrat do weryfikacji

## Zasady Craps

```
Pierwszy rzut (suma 2 kostek):
- 7 lub 11 → natychmiastowa wygrana
- 2, 3, lub 12 → natychmiastowa przegrana
- Inne sumy → "point", kontynuuj rzuty:
  - Jeśli suma = point → wygrana
  - Jeśli suma = 7 → przegrana
  - W przeciwnym razie → rzuć ponownie
```

## Wzór matematyczny

```
Teoretyczne prawdopodobieństwa:
P(wygrana) ≈ 0.493
P(przegrana) ≈ 0.507

Oczekiwane liczby:
expected_wins = total_games × 0.493
expected_losses = total_games × 0.507

Test Chi-kwadrat:
χ² = (wins - expected_wins)² / expected_wins +
     (losses - expected_losses)² / expected_losses

df = 1
p-value = erfc((χ² / 2)^0.5)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 200,000 bitów
- **Minimum gier**: 100
- **Bity na rzut**: 3 (z odrzuceniem 6,7)

## Implementacja

Test konwertuje trójki bitów na wartości 0-7 i odrzuca 6-7, używając wartości 0-5 jako rzuty 1-6. Symuluje pełne gry w craps według standardowych zasad.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_craps",
    "samples_count": 200000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny win rate ~49.3%
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład wyników
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 200,000 bitów
- **Złożoność**: Średnia (symulacja gier)
- **Optymalizacja**: Wykorzystuje numpy dla konwersji bitów
