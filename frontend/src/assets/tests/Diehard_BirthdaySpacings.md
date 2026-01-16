Test Birthday Spacings zlicza ile wartości występuje więcej niż raz (duplikaty) w blokach 24-bitowych słów. Zgodnie z oryginalnym testem Diehard, liczba takich duplikatów j powinna mieć rozkład Poissona z λ = m³/(4n), gdzie m=512 (urodziny na blok) i n=2²⁴ (rozmiar przestrzeni).

## Jak działa

1. Konwertuje bity na 24-bitowe słowa
2. Dzieli słowa na bloki po 512 elementów (m = 512)
3. W każdym bloku zlicza ile wartości występuje więcej niż raz (j)
4. Testuje czy rozkład wartości j jest zgodny z Poisson(λ=2.0)
5. Używa testu chi-kwadrat do porównania obserwowanych vs oczekiwanych częstości

## Wzór matematyczny

```
Parametr lambda: λ = m³/(4n) = 512³/(4×2²⁴) = 2.0

Prawdopodobieństwo Poissona: P(j=k) = (λᵏ × e⁻ᵏ) / k!

Test Chi-kwadrat:
χ² = Σ (observed_k - expected_k)² / expected_k

p-value = gammaincc(df/2, χ²/2)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 262,144 bitów (2^18)
- **Zalecane**: 1,048,576 bitów (2^20)
- **Minimum bloków**: 10

## Implementacja

Test wykorzystuje optymalizacje numpy dla szybkiej konwersji bitów na słowa. Jeśli znaleziono mało duplikatów (< 10), test uznaje to za oznakę doskonałej losowości (score = 0.95).

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_birthday_spacings",
    "samples_count": 1048576,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny rozkład Poissona liczby duplikatów
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, rozkład liczby duplikatów nie jest Poissonem
- **passed = false**: Generator nie przeszedł testu

**Uwaga**: Test został poprawiony i teraz zgodnie z oryginalną specyfikacją Diehard testuje rozkład Poissona LICZBY wartości duplikujących się (j), a nie odległości między nimi.

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 262,144 bitów
- **Złożoność**: Wysoka (sortowanie, wyszukiwanie duplikatów)
- **Optymalizacja**: Wykorzystuje numpy dla szybszej konwersji
