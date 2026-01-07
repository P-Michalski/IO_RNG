# NIST Linear Complexity Test

## Opis
Test mierzy długość najkrótszego rejestru przesuwnego ze sprzężeniem zwrotnym liniowym (LFSR), który może wygenerować daną sekwencję. Używa algorytmu Berlekamp-Massey.

## Jak działa
1. Dzieli sekwencję na bloki długości M
2. Dla każdego bloku oblicza złożoność liniową (algorytm Berlekamp-Massey)
3. Kategoryzuje odstępstwa od oczekiwanej złożoności
4. Test Chi-kwadrat na rozkładzie

## Wzory matematyczne
```
Oczekiwana złożoność:
μ = M/2 + (9+(-1)^(M+1))/36 - (M/3+2/9)/2^M

Kategorie Ti:
[-∞,-2.5], (-2.5,-1.5], ..., (2.5,+∞]

Prawdopodobieństwa:
π = [0.010417, 0.03125, 0.125, 0.5,
     0.25, 0.0625, 0.020833]
```

## Algorytm Berlekamp-Massey
```python
def berlekamp_massey(bits):
    n = len(bits)
    c = [0] * n
    b = [0] * n
    c[0] = b[0] = 1
    L = 0
    m = -1
    
    for i in range(n):
        d = bits[i]
        for j in range(1, L + 1):
            d ^= c[j] & bits[i - j]
        
        if d == 1:
            t = c[:]
            for j in range(len(b)):
                if i - m + j < n:
                    c[i - m + j] ^= b[j]
            if L <= i // 2:
                L = i + 1 - L
                m = i
                b = t
    
    return L
```

## Parametry
- **M**: 500 (domyślnie)
- **Minimum bloków**: 200 (minimum 100000 bitów)

## Implementacja
```python
def _nist_linear_complexity_test(self, bits: List[int], M: int = 500):
    import math
    from math import erfc

    n = len(bits)
    N = n // M

    if N < 200:
        return {'passed': False, 'score': 0.0,
                'error': 'Need at least 200 blocks (100000 bits)'}

    # Oczekiwana złożoność
    mu = M / 2.0 + (9.0 + (-1) ** (M + 1)) / 36.0 - \
         (M / 3.0 + 2.0 / 9.0) / (2 ** M)

    # Prawdopodobieństwa
    pi = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]
    
    frequencies = [0] * 7

    for i in range(N):
        block = bits[i * M:(i + 1) * M]
        L = berlekamp_massey(block)
        
        # Oblicz T
        T = (-1) ** M * (L - mu) + 2.0 / 9.0
        
        # Kategoryzuj
        if T <= -2.5:
            frequencies[0] += 1
        elif T <= -1.5:
            frequencies[1] += 1
        elif T <= -0.5:
            frequencies[2] += 1
        elif T <= 0.5:
            frequencies[3] += 1
        elif T <= 1.5:
            frequencies[4] += 1
        elif T <= 2.5:
            frequencies[5] += 1
        else:
            frequencies[6] += 1

    # Chi-square
    chi_square = sum(
        (frequencies[i] - N * pi[i]) ** 2 / (N * pi[i])
        for i in range(7)
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
            'block_size': M,
            'expected_complexity': mu
        }
    }
```

## Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_linear_complexity",
    "samples_count": 1000000
  }'
```

## Interpretacja wyników
- **expected_complexity**: Oczekiwana złożoność liniowa dla bloku
- **p-value > 0.1**: Prawidłowa złożoność liniowa
- **Niska złożoność**: Sekwencja może być generowana przez prosty LFSR

## Parametry testu
- **Typ danych**: Bity
- **Minimalna liczba próbek**: 100000
- **Złożoność**: Bardzo wysoka
- **Co wykrywa**: Złożoność LFSR
