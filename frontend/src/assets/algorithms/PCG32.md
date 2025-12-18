PCG32 (Permuted Congruential Generator) to nowoczesny generator pseudolosowy łączący prostotę i szybkość klasycznego LCG z zaawansowaną funkcją permutacji wyjścia. Zaprojektowany przez Melissę O'Neill około 2014 roku, PCG szybko zyskał popularność jako "następca" Mersenne Twistera, oferując lepszą jakość statystyczną przy znacznie mniejszym zużyciu pamięci i wyższej wydajności.

### Wyjaśnienie matematyczne

Generator PCG32 składa się z dwóch głównych komponentów: prostego generatora stanu (LCG) oraz zaawansowanej funkcji permutacji wyjścia.

#### Aktualizacja stanu (LCG)

Stan wewnętrzny to 64-bitowa liczba całkowita aktualizowana według klasycznej formuły LCG:

$$\text{state}_{n+1} = (a \cdot \text{state}_n + c) \bmod 2^{64}$$

gdzie:

- $a = 6364136223846793005$ – starannie dobrany mnożnik zapewniający maksymalny okres
- $c = \text{inc}$ – increment, wartość nieparzysta wybierana podczas inicjalizacji
- Moduł $2^{64}$ zapewnia pełny okres $2^{64}$ (wszystkie 64-bitowe wartości)

**Increment $c$ (inc):**
Wartość increment obliczana jest ze sparametryzowanej sekwencji (_sequence_):

$$\text{inc} = (\text{seq} << 1) | 1$$

Operacja `<< 1` przesuwa bity w lewo, a `| 1` zapewnia nieparzystość. Różne sekwencje generują niezależne strumienie pseudolosowe.

#### Funkcja permutacji: XSH RR (xorshift high, random rotate)

Kluczową innowacją PCG jest zaawansowana funkcja permutacji przekształcająca 64-bitowy stan w 32-bitowe wyjście:

1. **Xorshift wysokich bitów**:
   $$\text{xorshifted} = ((\text{state} >> 18) \oplus \text{state}) >> 27$$

   Ta operacja:

   - Przesuwa stan o 18 bitów w prawo
   - XOR-uje z oryginalnym stanem (miesza bity)
   - Przesuwa wynik o 27 bitów (wybiera 32 górne bity)

2. **Losowa rotacja**:
   $$\text{rot} = \text{state} >> 59$$

   Górne 5 bitów stanu determinują wielkość rotacji (0-31).

3. **Rotacja w prawo**:
   $$\text{output} = (\text{xorshifted} >> \text{rot}) | (\text{xorshifted} << (32 - \text{rot}))$$

   Rotacja bitowa w prawo o `rot` pozycji.

**Dlaczego to działa?**

- **Xorshift**: Miesza skorelowane bity z LCG, redukując liniowe zależności
- **Rotacja zależna od stanu**: Dodaje nieliniowość – różne stany mają różne permutacje
- **Wybór górnych bitów**: Górne bity LCG mają lepsze własności statystyczne niż dolne
- **32-bitowe wyjście z 64-bitowego stanu**: Zapewnia dodatkową ochronę przed odtworzeniem stanu

#### Inicjalizacja

Proces inicjalizacji PCG32 jest dwuetapowy:

```python
state = 0
inc = (seq << 1) | 1  # Zapewnij nieparzystość

# Krok 1: "Rozgrzanie" generatora
state = (state * a + inc) % 2**64

# Krok 2: Dodanie initstate
state = (state + initstate) % 2**64
state = (state * a + inc) % 2**64
```

To zapewnia, że różne seedy prowadzą do nieskorelowanych sekwencji.

### Warianty PCG

Rodzina PCG oferuje wiele wariantów dostosowanych do różnych potrzeb:

#### 1. **PCG32** (implementowany tutaj)

- Stan: 64 bity
- Wyjście: 32 bity
- Permutacja: XSH RR
- Najbardziej popularny, dobry balans

#### 2. **PCG64**

- Stan: 128 bitów
- Wyjście: 64 bity
- Dłuższy okres, lepsze własności dla 64-bitowych aplikacji

#### 3. **PCG32-fast**

- Uproszczona permutacja (XSH RS)
- Szybsza, ale nieznacznie gorsza statystycznie

#### 4. **PCG-unique**

- Każda instancja ma unikalny inc generowany z adresu obiektu
- Zapewnia niezależne strumienie bez ręcznej konfiguracji

### Kluczowy fragment kodu

```python
def pcg32_bit_stream(seed, n_bits, bits_per_value=32, msb_first=True):
    """
    Generuje strumień bitów używając PCG32.

    Args:
        seed: int (initstate) lub (initstate, seq)
        n_bits: liczba bitów do wygenerowania
        bits_per_value: ile bitów ekstrahować (domyślnie 32)
        msb_first: czy brać bity od najstarszych
    """
    # Stałe PCG
    MULT = 6364136223846793005
    MASK64 = (1 << 64) - 1

    # Parsowanie seeda
    if isinstance(seed, int):
        initstate, seq = seed, 1
    else:
        initstate, seq = seed[0], seed[1]

    # Oblicz inc (musi być nieparzysty)
    inc = ((seq << 1) | 1) & MASK64

    # Inicjalizacja stanu
    state = 0
    state = (state * MULT + inc) & MASK64
    state = (state + initstate) & MASK64
    state = (state * MULT + inc) & MASK64

    output = []

    while len(output) < n_bits:
        # Krok 1: Aktualizacja stanu (LCG)
        state = (state * MULT + inc) & MASK64

        # Krok 2: Permutacja XSH RR
        xorshifted = (((state >> 18) ^ state) >> 27) & 0xFFFFFFFF
        rot = (state >> 59) & 0x1F
        output_val = ((xorshifted >> rot) |
                      (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF

        # Ekstrakcja bitów
        bits = extract_bits(output_val, bits_per_value, msb_first)
        output.extend(bits[:n_bits - len(output)])

    return output
```

Implementacja wykorzystuje 64-bitową arytmetykę dostępną w nowoczesnym Pythonie, z maskowaniem zapewniającym poprawne zachowanie modulo $2^{64}$.

### Zastosowania

**Zastosowania praktyczne:**

- **Gry komputerowe** – proceduralna generacja światów, AI, systemy cząsteczek, animacje
- **Symulacje Monte Carlo** – badania naukowe, modelowanie finansowe, fizyka
- **Testy jednostkowe** – deterministyczne generowanie danych testowych
- **Generowanie proceduralnych treści** – tekstury, dźwięki, poziomy gier
- **Biblioteki naukowe** – numpy (od wersji 1.17+ jako domyślny generator PCG64)
- **Animacje i efekty wizualne** – szumy Perlina, systemy cząsteczek

**Zalety nad Mersenne Twister:**

- **Szybsza inicjalizacja**: Instant vs setki cykli CPU
- **Mniejsze zużycie pamięci**: 8 bajtów vs 2.5 KB
- **Lepsza jakość w niskich wymiarach**: Przechodzi więcej testów statystycznych
- **Wiele niezależnych strumieni**: Łatwa paralelizacja przez różne sekwencje
- **Przewidywalna wydajność**: Brak "warming up" jak MT

**Ograniczenia:**

- **Nie dla kryptografii**: Stan można odtworzyć z kilku wyjść (64 bity wyjścia to < 64 bity stanu)
- **Nie jest CSPRNG**: Brak własności kryptograficznych

### Jakość statystyczna

#### Testy statystyczne:

**TestU01 (L'Ecuyer i Simard):**

- **SmallCrush**: Zdany w 100%
- **Crush**: Zdany w 100%
- **BigCrush**: Zdany w 100% (wszystkie 160 testów)

**PractRand (Doty-Humphrey):**

- Przechodzi testy do co najmniej 32 TB danych
- Brak wykrytych anomalii dla standardowych parametrów

**DIEHARD Battery:**

- Zdane wszystkie testy
- Znacznie lepszy wynik niż LCG, Park-Miller

#### Zalety jakościowe:

1. **Brak struktury kratowej**: Eliminuje problem hiperpłaszczyzn charakterystyczny dla LCG
2. **Równomierna dystrybucja**: Wartości równomiernie rozłożone w przestrzeni wielowymiarowej
3. **Długie sekwencje**: Przechodzi testy na terabajtach danych bez wykrytych wzorców
4. **Niska korelacja**: Wartości kolejne i odległe są statystycznie niezależne

### Kontekst historyczny i ciekawostki

**Historia:**

- Zaprojektowany przez **Melissę O'Neill** na Harvey Mudd College (~2014)
- Pierwsza publikacja: artykuł "PCG: A Family of Simple Fast Space-Efficient Statistically Good Algorithms for Random Number Generation" (2014)
- Oficjalna strona: www.pcg-random.org z pełną dokumentacją i implementacjami

**Motywacja powstania:**

- Odpowiedź na słabości Mersenne Twistera (duża pamięć, słabe w niskich wymiarach)
- Potrzeba szybkiego, jakościowego generatora dla gier i symulacji
- Chęć stworzenia generatora "lepszego niż MT we wszystkim poza okresem"

**Adopcja w przemyśle:**

- **NumPy** (Python): PCG64 jako domyślny od wersji 1.17 (2019)
- **Rust**: Crate rand_pcg szeroko używany
- **C++**: Implementacje w bibliotekach takich jak pcg-cpp
- **Gry**: Używany w Unity, Unreal Engine (przez integracje)

**Ciekawostki:**

- Nazwa "Permuted Congruential Generator" podkreśla kluczową innowację – permutację wyjścia LCG
- Melissa O'Neill napisała **256-stronicowy raport techniczny** dokumentujący wszystkie aspekty PCG
- PCG ma ponad 20 wariantów (różne rozmiary stanu, funkcje permutacji)
- Generator był testowany na **petabajtach** danych w testach PractRand
- PCG-unique używa adresu w pamięci do generowania unikalnego inc – każda instancja ma inny strumień

### Złożoność obliczeniowa

- **Krok generacji**: $O(1)$ – stała liczba operacji (mnożenie, dodawanie, xor, przesunięcia, rotacja)
- **Pamięć**: $O(1)$ – 8 bajtów stanu + 8 bajtów inc (16 bajtów razem)
- **Inicjalizacja**: $O(1)$ – dwa kroki LCG

**Szczegółowa analiza operacji na krok:**

- 1× mnożenie 64-bitowe
- 2× dodawanie 64-bitowe
- 3× przesunięcie bitowe
- 1× XOR
- 1× rotacja bitowa (2 przesunięcia + OR)

**Razem**: ~8-10 instrukcji CPU na 32 bity wyjścia (≈0.3 instrukcji/bit)

**Wydajność praktyczna:**

- Python (CPython): ~50-100 MB/s
- C/C++ (optimized): ~400-800 MB/s
- Rust: ~500-1000 MB/s
- SIMD (AVX2): ~2-4 GB/s (równoległe strumienie)

### Przykłady obliczeniowe

#### Przykład 1: Podstawowa inicjalizacja

Dla `initstate = 42`, `seq = 54`:

**Krok inicjalizacji:**

```
inc = (54 << 1) | 1 = 109 (binarne: 1101101, nieparzyste ✓)

state = 0
state = (0 * 6364136223846793005 + 109) % 2^64 = 109
state = (109 + 42) % 2^64 = 151
state = (151 * 6364136223846793005 + 109) % 2^64
      = 960784502091959864
```

Stan początkowy: `960784502091959864`

#### Przykład 2: Pierwsza iteracja

Stan: `state = 960784502091959864`

**Aktualizacja stanu:**

```
state_new = (960784502091959864 * 6364136223846793005 + 109) % 2^64
          = 15295219558163128549 % 2^64
          = 15295219558163128549  (już w zakresie 64-bit)
```

**Permutacja XSH RR:**

```
xorshifted = ((state >> 18) ^ state) >> 27
state >> 18 = 3653889584...
(state >> 18) ^ state = ...
xorshifted = ... (32 bity)

rot = state >> 59 = 0 (górne 5 bitów)

output = (xorshifted >> 0) | (xorshifted << 32)
       = xorshifted  (brak rotacji dla rot=0)
```

Wynik: 32-bitowa wartość pseudolosowa.

#### Przykład 3: Przestrzeń stanów i okresy

- **Pełny okres**: $2^{64} = 18{,}446{,}744{,}073{,}709{,}551{,}616$ wartości stanu
- **Liczba niezależnych strumieni**: $2^{63}$ (różne wartości seq)
- **Całkowita przestrzeń**: $2^{64} \times 2^{63} = 2^{127}$ unikalnych sekwencji

To oznacza, że można wygenerować $2^{63}$ równoległych strumieni, każdy o okresie $2^{64}$.

#### Przykład 4: Porównanie z LCG (wizualizacja 2D)

Jeśli narysować punkty $(x_n, x_{n+1})$:

- **LCG**: Widoczne równoległe linie (struktura kratowa)
- **PCG32**: Równomierne rozłożenie bez widocznej struktury

Permutacja XSH RR efektywnie niszczy liniową strukturę LCG.

PCG32 reprezentuje nowoczesne podejście do projektowania generatorów PRNG: wykorzystanie prostych, dobrze zrozumianych komponentów (LCG) z inteligentną permutacją dającą doskonałe własności statystyczne przy minimalnym koszcie. Jest to idealny wybór dla większości aplikacji niewymagających gwarancji kryptograficznych.
