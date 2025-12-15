# LCG (Linear Congruential Generator)

## Skrót

LCG to klasyczny generator liniowy: $x_{n+1} = (a x_n + c) \bmod m$. Szybki i prosty, lecz podatny na korelacje oraz wrażliwy na dobór parametrów $a, c, m$.

## Wersja długa

### Wyjaśnienie matematyczne

- Stan to pojedyncza liczba całkowita $x_n$.
- Aktualizacja: $x_{n+1} = (a x_n + c) \bmod m$, gdzie $a$ to mnożnik, $c$ to przyrost, $m$ to moduł.
- Bity wyjściowe pozyskuje się zwykle z najistotniejszych bitów $x_n$ (np. 31 bitów przy $m=2^{31}$).
- Okres i własności statystyczne zależą od spełnienia klasycznych warunków dla $a, c, m$ (pełny okres wymaga odpowiednich relacji między tymi parametrami).

### Kluczowy fragment kodu

```python
# Krok LCG - aktualizacja stanu
x = (a * x + c) % m
# Ekstrakcja wysokich bitów
output_bits = extract_bits(x, bits_per_value, msb_first)
```

### Zastosowania

- Materiały dydaktyczne, proste symulacje Monte Carlo, szybkie generowanie danych testowych.
- Nie zalecany do kryptografii z uwagi na liniową strukturę i przewidywalność.
- Historycznie szeroko wykorzystywany w bibliotekach standardowych (np. glibc, MINSTD).

### Kontekst i ciekawostki

- Geneza LCG sięga prac D. H. Lehmera (lata 50. XX wieku).
- Liczne „minimalne standardy" (np. Park-Miller MINSTD) wynikają z potrzeby dobrego doboru parametrów w praktyce.
- Spektralne testy ujawniają słabości: punkty leżą na hiperpłaszczyznach w przestrzeni wielowymiarowej.

### Krótki przykład obliczeniowy

Dla $a=5$, $c=3$, $m=16$, $x_0=7$:

- $x_1 = (5 \cdot 7 + 3) \bmod 16 = 38 \bmod 16 = 6$
- $x_2 = (5 \cdot 6 + 3) \bmod 16 = 33 \bmod 16 = 1$
- $x_3 = (5 \cdot 1 + 3) \bmod 16 = 8$
