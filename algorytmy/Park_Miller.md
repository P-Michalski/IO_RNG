# Park–Miller (Minimal Standard)

## Skrót

Park–Miller to szczególny LCG bez składowej addytywnej: \( x\_{n+1} = (a x_n) \bmod m \), gdzie \(a=16807\), \(m=2^{31}-1\). Znany jako „minimalny standard" generatora pseudolosowego.

## Wersja długa

### Wyjaśnienie matematyczne

- Wykorzystuje mnożnik \(a=16807=7^5\) i moduł \(m=2^{31}-1\) (liczba pierwsza Mersenne'a).
- Aktualizacja: \(x\_{n+1} = (16807 \cdot x_n) \bmod (2^{31}-1)\).
- Implementacja unika przepełnień dzięki arytmetyce Schrage'a lub odpowiednim trikom numerycznym.
- Z każdej wartości \(x_n\) pobiera się 31 najstarszych bitów.

### Kluczowy fragment kodu

```python
# Krok Park-Miller (uproszczony)
a = 16807
m = 2147483647  # 2^31 - 1
x = (a * x) % m
# Ekstrakcja bitów z x
output_bits = extract_bits(x, bits_per_value=31, msb_first=True)
```

### Zastosowania

- Referencyjny generator w badaniach naukowych i edukacji.
- Symulacje statystyczne o umiarkowanych wymaganiach jakościowych.
- Nie zalecany do zastosowań kryptograficznych.

### Kontekst i ciekawostki

- Zaproponowany przez Stephena K. Parka i Keitha W. Millera w 1988 roku jako „minimalny standard".
- Odpowiedź na rozpowszechnienie słabych LCG w bibliotekach standardowych lat 80.
- Spektralne testy potwierdzają średnią jakość; lepszy niż naiwne LCG, gorszy od nowoczesnych generatorów (PCG, xoshiro).

### Krótki przykład obliczeniowy

Dla \(x_0=1\):

- \(x_1 = 16807 \bmod (2^{31}-1) = 16807\)
- \(x_2 = (16807 \cdot 16807) \bmod (2^{31}-1) = 282475249\)
- \(x_3 = (16807 \cdot 282475249) \bmod (2^{31}-1) = 1622650073\)
