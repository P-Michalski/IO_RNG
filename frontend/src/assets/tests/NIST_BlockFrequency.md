Test sprawdza, czy proporcja jedynek w poszczególnych blokach (podciągach) jest bliska 0.5. Jest to bardziej lokalna wersja testu Monobit.

## Jak działa
1. Dzieli sekwencję bitów na bloki o wielkości M (domyślnie 128 bitów)
2. Dla każdego bloku oblicza proporcję jedynek
3. Sprawdza, czy proporcje są bliskie 0.5 za pomocą statystyki Chi-kwadrat
4. Oblicza p-value

## Wzory matematyczne
```
Dla każdego bloku i:
πi = (liczba jedynek w bloku i) / M

Statystyka Chi-kwadrat:
χ² = 4M × Σ (πi - 0.5)²

P-value:
p = erfc(√(χ²/2))
```

## Parametry
- **Domyślny rozmiar bloku**: M = 128 bitów
- **Minimalny rozmiar sekwencji**: 128 bitów
- **Kryterium**: p-value ≥ 0.01

## Implementacja
```python
def _nist_block_frequency_test(self, bits: List[int], block_size: int = 128):
    import math
    from math import erfc

    n = len(bits)
    num_blocks = n // block_size

    if num_blocks == 0:
        return {
            'passed': False,
            'score': 0.0,
            'error': 'Not enough bits for block test'
        }

    # Chi-square statistic
    chi_square = 0.0
    proportions = []

    for i in range(num_blocks):
        block = bits[i * block_size:(i + 1) * block_size]
        proportion = sum(block) / block_size
        proportions.append(proportion)
        chi_square += (proportion - 0.5) ** 2

    chi_square *= 4 * block_size

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': score,
        'statistics': {
            'p_value': p_value,
            'chi_square': chi_square,
            'num_blocks': num_blocks,
            'block_size': block_size,
            'proportions': proportions[:10]  # Pierwsze 10 dla przykładu
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_block_frequency",
    "samples_count": 128000
  }'
```

## Interpretacja wyników
- **p-value > 0.5**: Wszystkie bloki mają dobrą równowagę
- **p-value ≈ 0.01**: Graniczny wynik, niektóre bloki mogą być niezbalansowane
- **num_blocks**: Im więcej bloków, tym bardziej wiarygodny test
- **chi_square**: Im mniejsza wartość, tym lepiej

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 128
- **Złożoność**: Średnia
- **Co wykrywa**: Lokalne niezbalansowanie
