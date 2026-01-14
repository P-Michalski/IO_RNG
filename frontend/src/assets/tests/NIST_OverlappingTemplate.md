Podobny do poprzedniego testu, ale wystąpienia wzorca mogą się nakładać. Używa specyficznego wzorca 111111111 (9 jedynek).

## Jak działa

1. Używa stałego wzorca: 9 jedynek
2. W każdym bloku zlicza nakładające się wystąpienia
3. Kategoryzuje bloki według liczby wystąpień (0,1,2,3,4,5+)
4. Test Chi-kwadrat na rozkładzie

## Wzory matematyczne

```
λ = (M - m + 1) / 2^m
η = λ / 2

Prawdopodobieństwa teoretyczne:
π = [0.364091, 0.185659, 0.139381,
     0.100571, 0.0704323, 0.139865]
```

## Parametry

- **Wzorzec**: [1,1,1,1,1,1,1,1,1]
- **Rozmiar bloku**: M = 1032
- **Kategorie**: 0, 1, 2, 3, 4, ≥5

## Implementacja

```python
def _nist_overlapping_template_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    template = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    m = len(template)
    M = 1032
    n = len(bits)
    N = n // M

    if N == 0:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 1032 bits'}

    # Prawdopodobieństwa teoretyczne
    pi = [0.364091, 0.185659, 0.139381, 0.100571, 0.0704323, 0.139865]

    frequencies = [0] * 6

    for i in range(N):
        block = bits[i * M:(i + 1) * M]
        count = 0

        # Zlicz nakładające się wystąpienia
        for j in range(len(block) - m + 1):
            if block[j:j+m] == template:
                count += 1

        # Kategoryzuj
        if count >= 5:
            frequencies[5] += 1
        else:
            frequencies[count] += 1

    # Chi-square
    chi_square = sum(
        (frequencies[i] - N * pi[i]) ** 2 / (N * pi[i])
        for i in range(6)
    )

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
            'num_blocks': N,
            'template': template,
            'frequencies': frequencies
        }
    }
```

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_overlapping_template",
    "samples_count": 100000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **frequencies**: Rozkład liczby wystąpień wzorca w blokach
- **p-value > 0.1**: Prawidłowa częstość nakładających się wzorców
- **chi_square**: Im mniejsza wartość, tym lepiej

## Parametry testu

- **Typ danych**: Bity
- **Minimalna liczba próbek**: 1032
- **Złożoność**: Średnia
- **Co wykrywa**: Seryjne wzorce (111...1)
