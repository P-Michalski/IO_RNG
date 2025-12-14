# SplitMix64

## Skrót

SplitMix64 to szybki generator 64-bitowy oparty o mieszanie bitów (dodawanie stałej \(\gamma\) i funkcje mieszające). Często używany do inicjalizacji stanów innych generatorów (np. xoshiro, xorshift).

## Wersja długa

### Wyjaśnienie matematyczne

- Stan \(x\) zwiększany o stałą \(\gamma = 0x9E3779B97F4A7C15\) (złoty kąt w reprezentacji 64-bit).
- Wyjście 64-bitowe powstaje przez sekwencję operacji mieszających:
  1. \(z = x\)
  2. \(z = (z \oplus (z \gg 30)) \cdot 0xBF58476D1CE4E5B9\)
  3. \(z = (z \oplus (z \gg 27)) \cdot 0x94D049BB133111EB\)
  4. \(z = z \oplus (z \gg 31)\)
- Zapewnia dobrą dystrybucję bitów przy minimalnym koszcie obliczeniowym.

### Kluczowy fragment kodu

```python
# Aktualizacja stanu
x += 0x9E3779B97F4A7C15
# Mieszanie (MurmurHash3 finalizer)
z = x
z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
z = (z ^ (z >> 27)) * 0x94D049BB133111EB
output = z ^ (z >> 31)
# Ekstrakcja bitów z output
```

### Zastosowania

- Inicjalizacja (seeding) innych generatorów wymagających wielu niezależnych wartości początkowych.
- Szybkie generowanie liczb losowych w aplikacjach, gdzie nie jest wymagana kryptografia.
- Często używany jako domyślny generator do tworzenia stanów xoshiro/xorshift.

### Kontekst i ciekawostki

- Zaprojektowany przez Sebastiano Vignę (~2015) jako efektywna alternatywa dla Java'owej funkcji `SplittableRandom`.
- Funkcja mieszająca oparta na MurmurHash3 finalizer – sprawdzony mechanizm z hashowania.
- Bardzo szybki (kilka operacji arytmetycznych), ale nie przechodzi wszystkich testów statystycznych dla długich sekwencji.

### Krótki przykład obliczeniowy

Dla \(x_0 = 0\), \(\gamma = 0x9E3779B97F4A7C15\):

- Krok 1: \(x_1 = 0 + \gamma = 0x9E3779B97F4A7C15\)
- Następnie aplikacja funkcji mieszającej daje \(z_1\) jako wyjście 64-bitowe.
