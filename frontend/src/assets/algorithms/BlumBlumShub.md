# Blum–Blum–Shub (BBS)

## Skrót

BBS to kryptograficzny generator oparty na trudności rozkładu liczb (RSA-like). Stan aktualizuje się przez $x_{n+1} = x_n^2 \bmod M$, gdzie $M=p\cdot q$ to iloczyn dwóch liczb pierwszych Blum'a ($p \equiv q \equiv 3 \bmod 4$).

## Wersja długa

### Wyjaśnienie matematyczne

- Wybierz dwie duże liczby pierwsze $p$ i $q$, gdzie $p \equiv q \equiv 3 \pmod{4}$ (tzw. Blum primes).
- Moduł: $M = p \cdot q$.
- Inicjalizacja: wybierz seed $x_0$ taki, że $\gcd(x_0, M) = 1$, następnie ustaw $x \leftarrow x_0^2 \bmod M$.
- Aktualizacja stanu: $x_{n+1} = x_n^2 \bmod M$.
- Ekstrakcja wyjścia: z każdego $x_n$ pobierane jest $k$ najmniej znaczących bitów (LSB).
- Bezpieczeństwo opiera się na założeniu trudności problemu reszty kwadratowej (Quadratic Residuosity Problem), powiązanym z trudnością faktoryzacji $M$.

### Kluczowy fragment kodu

```python
# Inicjalizacja
M = p * q  # p, q to Blum primes
x = pow(seed, 2, M)

# Każdy krok generacji
x = pow(x, 2, M)
output_bits = x & ((1 << k) - 1)  # k najniższych bitów
```

### Zastosowania

- **Kryptografia teoretyczna**: protokoły zero-knowledge proof, protokoły bit commitment.
- **Zastosowania niszowe**: scenariusze wymagające udowodnionego bezpieczeństwa na poziomie teoretycznym (rzadko w praktyce).
- **Nie zalecany do zastosowań praktycznych**: bardzo wolny w porównaniu do ChaCha20, AES-CTR, czy innych nowoczesnych CSPRNG.

### Kontekst i ciekawostki

- Zaproponowany przez Lenore Blum, Manuela Bluma i Michaela Shuba w 1986 roku.
- Jeden z pierwszych generatorów z udowodnionym bezpieczeństwem w modelu obliczeniowym (zakładając trudność faktoryzacji).
- Każda iteracja wymaga potęgowania modularnego, co czyni algorytm bardzo powolnym (~0.3 Mbits/s w implementacji testowej).
- W praktycznych zastosowaniach kryptograficznych wypiera go ChaCha20, AES-CTR i inne szyfry strumieniowe.
- Historycznie ważny jako dowód koncepcji dla CSPRNG o udowodnialnym bezpieczeństwie.

### Krótki przykład obliczeniowy

Dla $p=11, q=19$ (uproszczony przykład, nie prawdziwe Blum primes):

- $M = 11 \cdot 19 = 209$
- Seed $x_0 = 3$, więc $x = 3^2 \bmod 209 = 9$
- $x_1 = 9^2 \bmod 209 = 81$ → LSB (4 bity): `0001`
- $x_2 = 81^2 \bmod 209 = 6561 \bmod 209 = 136$ → LSB: `1000`
- $x_3 = 136^2 \bmod 209 = 18496 \bmod 209 = 102$ → LSB: `0110`
