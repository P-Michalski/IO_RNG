# Xorshift / Xoshiro256\*\*

## Skrót

Rodzina szybkich generatorów opartych o operacje XOR i przesunięcia (oraz rotacje). `xoshiro256**` (Vigna/Blackman) daje bardzo dobre własności statystyczne i wysoką szybkość.

## Wersja długa

### Wyjaśnienie matematyczne

- Stan generatora: cztery 64-bitowe słowa \(s_0, s_1, s_2, s_3\).
- Funkcja wyjścia (wariant `**`): \( \text{output} = \text{rotl}(s_1 \cdot 5, 7) \cdot 9 \)
- Aktualizacja stanu (per krok):
  ```
  t = s_1 << 17
  s_2 ^= s_0
  s_3 ^= s_1
  s_1 ^= s_2
  s_0 ^= s_3
  s_2 ^= t
  s_3 = rotl(s_3, 45)
  ```
- Operacje XOR i rotacje zapewniają dobre właściwości dyfuzji; okres \(2^{256}-1\).
- Zdaje testy statystyczne (TestU01 BigCrush, PractRand), ale nie jest kryptograficznie bezpieczny.

### Kluczowy fragment kodu

```csharp
// Krok xoshiro256** (C#)
ulong result = RotateLeft(s1 * 5, 7) * 9;
ulong t = s1 << 17;
s2 ^= s0;
s3 ^= s1;
s1 ^= s2;
s0 ^= s3;
s2 ^= t;
s3 = RotateLeft(s3, 45);
return result;
```

### Zastosowania

- **Symulacje naukowe**: fizyka, biologia, Monte Carlo (gdzie kryptografia nie jest wymagana).
- **Gry komputerowe**: proceduralna generacja poziomów, AI, efekty losowe.
- **Benchmarki i testy**: szybki generator do testów wydajnościowych.
- **Nie dla kryptografii**: brak odporności na predykcję stanu przy znanych wyjściach.

### Kontekst i ciekawostki

- Rodzina xoshiro/xoroshiro zaprojektowana przez Davida Blackmana i Sebastiano Vignę.
- xoshiro256\*\* (scrambled) wprowadza multiplikacje i rotacje dla lepszej jakości niż podstawowy xorshift.
- Poprzednikiem: xorshift (George Marsaglia, 2003), szybki ale słabszy statystycznie.
- Szeroko stosowany w implementacjach standardowych bibliotek (np. Rust `rand` crate, numpy do wersji PCG64).
- Bardzo szybki: ~72 Mbits/s w testowej implementacji C#, setki Gbits/s na nowoczesnych CPU z optymalizacjami.

### Krótki przykład obliczeniowy

Inicjalizacja: \(s_0=1, s_1=2, s_2=3, s_3=4\).

- Wyjście: \( \text{rotl}(2 \cdot 5, 7) \cdot 9 = \text{rotl}(10, 7) \cdot 9 = 1280 \cdot 9 = 11520 \)
- Po aktualizacji stanu:
  - \(t = 2 << 17 = 262144\)
  - \(s_2 = 3 \oplus 1 = 2\), \(s_3 = 4 \oplus 2 = 6\), itd.
- Kolejne wyjście zależy od nowego stanu (deterministyczna sekwencja).
