# Python `random` (Mersenne Twister)

## Skrót

Wbudowany generator Pythona bazuje na Mersenne Twister (MT19937). Charakteryzuje się bardzo długim okresem i dobrymi własnościami statystycznymi, lecz nie jest przeznaczony do zastosowań kryptograficznych.

## Wersja długa

### Wyjaśnienie matematyczne

- MT19937 operuje na wektorze 624 32-bitowych słów (stan wewnętrzny).
- Rekurencja liniowa nad \(GF(2)\): nowe słowo powstaje z XOR-ów przesuniętych starszych słów i operacji na bitach.
- Wyjście jest dodatkowo „temperowane" (seria XOR-ów i przesunięć) dla poprawy dystrybucji:
  ```
  y = state[index]
  y ^= (y >> 11)
  y ^= (y << 7) & 0x9D2C5680
  y ^= (y << 15) & 0xEFC60000
  y ^= (y >> 18)
  ```
- Okres wynosi \(2^{19937}-1\), co jest wyjątkowo długie.

### Kluczowy fragment kodu

```python
import random
# Inicjalizacja seeda
random.seed(seed)
# Generowanie 32-bitowej wartości
value = random.getrandbits(32)
# Ekstrakcja bitów
output_bits = extract_bits(value, bits_per_value, msb_first)
```

### Zastosowania

- Domyślny generator w bibliotece standardowej Pythona – szeroko stosowany w symulacjach, naukowych obliczeniach, prototypowaniu.
- Nie zalecany do kryptografii (przewidywalny po zaobserwowaniu 624 wartości wyjściowych).
- Używany w numpy (do wersji 1.17), scipy i innych bibliotekach naukowych.

### Kontekst i ciekawostki

- Zaprojektowany przez Makoto Matsumoto i Takuji Nishimurę w 1997 roku.
- Nazwa „Mersenne Twister" pochodzi od wykorzystania liczb pierwszych Mersenne'a w konstrukcji.
- Nowsze wersje numpy przeszły na PCG64 jako domyślny generator z uwagi na lepszą jakość i wydajność.
- MT ma długi stan (2496 bajtów), co może być problemem w aplikacjach z ograniczoną pamięcią.

### Krótki przykład obliczeniowy

MT korzysta z liniowej rekurencji: dla stanu \(x*0, x_1, \ldots, x*{623}\):

- \(x\_{624} = x_397 \oplus ((x_0 \& \text{UPPER}) | (x_1 \& \text{LOWER})) \gg 1) \oplus A\)
- Gdzie \(A\) to stała macierzowa zależna od najmłodszego bitu.
