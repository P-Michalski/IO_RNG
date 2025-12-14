# PCG32 (Permuted Congruential Generator)

## Skrót

PCG32 to nowoczesny generator łączący prosty LCG dla stanu z permutacją wyjścia (XSH RR – xorshift + rotacja). Oferuje lepszą jakość statystyczną niż klasyczne LCG przy zachowaniu wysokiej wydajności.

## Wersja długa

### Wyjaśnienie matematyczne

- Stan 64-bitowy aktualizowany jak w LCG: \( state = state \cdot a + inc \bmod 2^{64} \).
- Wyjście 32-bitowe powstaje przez permutację XSH RR (xorshift high rotate right):
  - Wybór bitów ze stanu poprzez xorshift.
  - Rotacja wynikowej wartości w prawo o liczbę pozycji zależną od stanu.
- Eliminuje typowe artefakty LCG (korelacje w niskowymiarowych projekcjach).

### Kluczowy fragment kodu

```python
# Aktualizacja stanu (LCG)
state = (state * multiplier + increment) % (2**64)
# Permutacja XSH RR
xorshifted = ((state >> 18) ^ state) >> 27
rot = state >> 59
output = (xorshifted >> rot) | (xorshifted << (32 - rot))
# Ekstrakcja bitów z output
```

### Zastosowania

- Gry komputerowe, symulacje Monte Carlo, generowanie proceduralnych treści.
- Szybkie testy statystyczne i aplikacje wymagające dobrych własności losowych bez kryptografii.
- Popularny w nowoczesnych silnikach gier i bibliotekach naukowych (np. numpy).

### Kontekst i ciekawostki

- Zaprojektowany przez Melissę O'Neill (~2014) jako odpowiedź na słabości klasycznych LCG.
- Rodzina PCG oferuje różne warianty (PCG32, PCG64, rozszerzone stany) z elastycznym doborem parametrów.
- Zdaje testy statystyczne (TestU01, PractRand) znacznie lepiej niż Mersenne Twister w niskich wymiarach.

### Krótki przykład obliczeniowy

Dla uproszczonych parametrów: permutacja XSH RR miesza bity poprzez xorshift i rotację, redukując liniowe zależności typowe dla LCG.
