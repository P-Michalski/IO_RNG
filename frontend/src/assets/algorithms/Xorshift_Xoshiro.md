Rodzina xorshift/xoshiro reprezentuje nowoczesne podejście do projektowania generatorów pseudolosowych, łącząc ekstremalną szybkość z doskonałą jakością statystyczną. **Xoshiro256\*\*** (xor-shift-rotate) to najnowsza ewolucja tej rodziny, zaprojektowana przez Davida Blackmana i Sebastiano Vignę, oferująca praktycznie najlepszy stosunek jakości do wydajności spośród wszystkich niekryptograficznych generatorów.

### Historia i ewolucja

#### Xorshift (Marsaglia, 2003)

Oryginalny **xorshift** zaproponowany przez George'a Marsaglię wykorzystywał tylko operacje XOR i przesunięcia:

$$x_{n+1} = x_n \oplus (x_n << a) \oplus (x_n >> b) \oplus (x_n << c)$$

**Zalety**: Ekstremalnie prosty i szybki\
**Wady**: Niepowodzenia w niektórych testach statystycznych, szczególnie dla małych stanów

#### Xorshift+ / Xorshift\* (2014-2015)

Vigna i Blackman wprowadzili **scrambler** – dodatkową funkcję permutacji wyjścia:

- **Xorshift+**: Dodawanie dwóch stanów
- **Xorshift\***: Mnożenie przez stałą

To znacznie poprawiło jakość statystyczną.

#### Xoshiro/Xoroshiro (2016-2018)

Najnowsza rodzina używa **rotacji** zamiast przesunięć + ulepszone schematy aktualizacji stanu:

- **xoroshiro128+**: 128-bitowy stan, + scrambler
- **xoshiro256\*\***: 256-bitowy stan, \*\* scrambler (najlepszy)
- **xoshiro512\*\***: 512-bitowy stan (dla najdłuższych symulacji)

### Wyjaśnienie matematyczne xoshiro256\*\*

Generator xoshiro256\*\* wykorzystuje stan złożony z czterech 64-bitowych słów i zaawansowany scrambler.

#### Stan generatora

Stan to cztery 64-bitowe liczby całkowite:

$$\text{state} = (s_0, s_1, s_2, s_3)$$

Całkowity rozmiar stanu: $4 \times 64 = 256$ bitów.

#### Funkcja wyjścia (scrambler "\*\*")

Wyjście 64-bitowe generowane jest przez podwójne operacje mnożenia i rotacji na $s_1$:

$$\text{output} = \text{rotl}(s_1 \times 5, 7) \times 9$$

gdzie $\text{rotl}(x, k)$ oznacza rotację bitową w lewo o $k$ pozycji.

**Dlaczego ten scrambler?**

- **Mnożenie × 5**: Propaguje zmiany przez całe słowo
- **Rotacja o 7**: Miesza pozycje bitów
- **Mnożenie × 9**: Druga warstwa dyfuzji
- Stałe (5, 7, 9) dobrane empirycznie dla maksymalnej avalanche

#### Aktualizacja stanu

Stan aktualizowany jest przez szereg operacji XOR i rotacji:

```
t ← s_1 << 17          // Przesunięcie pomocnicze
s_2 ← s_2 ⊕ s_0        // Mieszanie stanu
s_3 ← s_3 ⊕ s_1
s_1 ← s_1 ⊕ s_2
s_0 ← s_0 ⊕ s_3
s_2 ← s_2 ⊕ t          // Dodaj przesunięcie
s_3 ← rotl(s_3, 45)    // Rotacja finalna
```

**Analiza aktualizacji:**

- Każde słowo stanu jest funkcją co najmniej dwóch poprzednich słów
- XOR zapewnia odwracalność (pełny okres)
- Rotacja dodaje nieliniowość
- Liczby (17, 45) dobrane dla maksymalnej dyfuzji

#### Własności matematyczne

**Okres**: $2^{256} - 1$ – praktycznie niewyczerpany

- Wszystkie $2^{256}$ stanów z wyjątkiem stanu zerowego (0,0,0,0)
- Dla porównania: liczba atomów we wszechświecie $\approx 2^{265}$

**Liniowa złożoność**: 256 bitów (pełna)

**Reversible**: Można obliczyć poprzedni stan ze znanego stanu (ale nietrywialnie)

### Kluczowy fragment kodu

```csharp
public class Xoshiro256StarStar
{
    private ulong s0, s1, s2, s3;

    // Funkcja pomocnicza: rotacja w lewo
    private static ulong RotateLeft(ulong x, int k)
    {
        return (x << k) | (x >> (64 - k));
    }

    public ulong Next()
    {
        // Funkcja wyjścia (scrambler **)
        ulong result = RotateLeft(s1 * 5, 7) * 9;

        // Aktualizacja stanu
        ulong t = s1 << 17;

        s2 ^= s0;
        s3 ^= s1;
        s1 ^= s2;
        s0 ^= s3;

        s2 ^= t;
        s3 = RotateLeft(s3, 45);

        return result;
    }

    // Inicjalizacja (często z SplitMix64)
    public void Seed(ulong seed)
    {
        var sm = new SplitMix64(seed);
        s0 = sm.Next();
        s1 = sm.Next();
        s2 = sm.Next();
        s3 = sm.Next();
    }
}
```

Implementacja w C# wykorzystuje natywne typy `ulong` i efektywne operacje bitowe procesora.

### Warianty rodziny xoshiro

#### xoshiro256\*\* (implementowany)

- Stan: 256 bitów (4 × 64-bit)
- Scrambler: \*\* (podwójne mnożenie)
- **Najlepszy wybór ogólny**

#### xoshiro256+

- Scrambler: + (dodawanie s0 + s3)
- Szybszy, ale nieco słabszy statystycznie
- Dobry dla zmiennoprzecinkowych aplikacji

#### xoroshiro128\*\*

- Stan: 128 bitów (2 × 64-bit)
- Mniejszy footprint pamięciowy
- Wystarczający dla większości zastosowań

#### xoshiro512\*\*

- Stan: 512 bitów (8 × 64-bit)
- Jeszcze dłuższy okres ($2^{512}-1$)
- Dla ekstremalnie długich symulacji

### Zastosowania

**Zastosowania praktyczne:**

- **Symulacje naukowe** – fizyka cząstek, biologia obliczeniowa, Monte Carlo
- **Gry komputerowe** – proceduralna generacja, AI, systemy cząsteczek
- **Biblioteki standardowe** – Rust `rand` crate używa xoshiro domyślnie
- **Benchmarki wydajnościowe** – testowanie algorytmów na dużych zbiorach danych
- **Machine learning** – inicjalizacja wag, dropout, data augmentation

**Zalety nad Mersenne Twister:**

- **256 razy mniejsze zużycie pamięci**: 32 bajty vs 2.5 KB
- **Szybsza inicjalizacja**: Instant vs setki cykli
- **Lepsza jakość**: Przechodzi wszystkie testy (MT ma problemy w BigCrush)
- **Jump functions**: Łatwe tworzenie niezależnych strumieni

**Ograniczenia:**

- **Nie dla kryptografii**: Stan można odtworzyć z ~4 wyjść 64-bitowych
- **Wymaga dobrej inicjalizacji**: Stan zerowy (0,0,0,0) jest niepoprawny

### Jakość statystyczna

#### Testy statystyczne:

**TestU01 (L'Ecuyer i Simard):**

- **SmallCrush**: Zdany 100%
- **Crush**: Zdany 100%
- **BigCrush**: Zdany 100% (wszystkie 160 testów)

**PractRand (Doty-Humphrey):**

- Przechodzi testy do co najmniej **16 TB** danych bez anomalii
- Brak wykrytych wzorców czy korelacji

**DIEHARD Battery:**

- Zdane wszystkie testy

### Kontekst historyczny i ciekawostki

**Twórcy:**

- **Sebastiano Vigna** – informatyk, Università degli Studi di Milano, ekspert w generatorach PRNG
- **David Blackman** – współpracownik, specjalizacja w algorytmach numerycznych

**Publikacje:**

- 2018: "Scrambled Linear Pseudorandom Number Generators" (arXiv:1805.01407)
- Kompleksowa analiza wszystkich wariantów xoshiro/xoroshiro

**Adopcja:**

- **Rust** (2018+): `rand` crate używa xoshiro256++/xoshiro256\*\* jako domyślny
- **Lua** (5.4+): Używa xoshiro256\*\*
- **Julia**: Opcja dla aplikacji wymagających wydajności

**Ciekawostki:**

- Nazwa "xoshiro" to akronim: **XO**r/**SHI**ft/**RO**tate
- Autorzy przetestowali setki kombinacji parametrów (przesunięć, rotacji, stałych)
- xoshiro256** przeszedł **petabajty\*\* danych w testach PractRand
- "Jump functions" pozwalają przeskoczyć $2^{128}$ kroków w czasie stałym – użyteczne dla paralelizacji
- Implementacja sprzętowa (FPGA) osiąga prędkości > 100 Gbits/s

**Dlaczego "**" (podwójne mnożenie)?\*\*

- Pojedyncze mnożenie (\*) jest szybsze, ale daje słabszą jakość dla niektórych aplikacji
- Podwójne mnożenie (\*\*) osiąga perfekcyjną jakość przy minimalnym koszcie

### Złożoność obliczeniowa

- **Krok generacji**: $O(1)$ – stała liczba operacji bitowych
- **Pamięć**: $O(1)$ – 32 bajty (4 × 64-bit)
- **Inicjalizacja**: $O(1)$ – 4 wywołania SplitMix64

**Szczegółowa analiza operacji na krok:**

- 2× mnożenie 64-bitowe (scrambler)
- 7× XOR 64-bitowe
- 2× rotacja bitowa
- 1× przesunięcie bitowe

**Razem**: ~8-12 cykli CPU na 64 bity wyjścia (0.125-0.19 cykli/bit)

### Przykłady obliczeniowe

#### Przykład 1: Podstawowa iteracja

Stan początkowy: $s_0=1$, $s_1=2$, $s_2=3$, $s_3=4$

**Wyjście:**

```
result = rotl(2 * 5, 7) * 9
       = rotl(10, 7) * 9
       = 1280 * 9
       = 11520
```

**Aktualizacja stanu:**

```
t = 2 << 17 = 262144

s_2 = 3 ⊕ 1 = 2
s_3 = 4 ⊕ 2 = 6
s_1 = 2 ⊕ 2 = 0
s_0 = 1 ⊕ 6 = 7

s_2 = 2 ⊕ 262144 = 262146
s_3 = rotl(6, 45) = 12884901888

Nowy stan: (7, 0, 262146, 12884901888)
```

#### Przykład 2: Jump function

Xoshiro256\*\* oferuje funkcję "jump" przeskakującą $2^{128}$ kroków:

```csharp
public void Jump()
{
    // Implementacja używa mnożenia macierzowego
    // w GF(2) – poza zakresem tego przykładu
    // Wynik: stan po 2^128 iteracjach w O(1) czasie
}
```

Użyteczne dla paralelizacji – każdy wątek dostaje niezależny strumień.

#### Przykład 3: Porównanie scramblerów

Dla tego samego stanu (przed scramblerem) $s_1 = 12345$:

**Xoshiro256+**:

```
output = s0 + s3 = 1 + 4 = 5
```

**Xoshiro256\*\***:

```
output = rotl(12345 * 5, 7) * 9 = ... (znacznie bardziej "losowa" wartość)
```

Podwójne mnożenie daje lepszą avalanche.

#### Przykład 4: Inicjalizacja z SplitMix64

```python
seed = 42
sm = SplitMix64(seed)

s0 = sm.next()  # np. 0x5B2A3D847F6E91C2
s1 = sm.next()  # np. 0xA7C4E9F1D3B82056
s2 = sm.next()  # np. 0x3F8D6C2B91E54A73
s3 = sm.next()  # np. 0xE1A9C5D7F4B38062

xoshiro = Xoshiro256StarStar(s0, s1, s2, s3)
```

SplitMix64 zapewnia, że stan jest "dobry" (nie ma złych korelacji).

Xoshiro256\*\* reprezentuje szczyt nowoczesnego projektowania generatorów niekryptograficznych – perfekcyjna równowaga między prostotą, szybkością i jakością statystyczną. Jest to prawdopodobnie najlepszy wybór dla większości aplikacji niewymagających gwarancji kryptograficznych.
