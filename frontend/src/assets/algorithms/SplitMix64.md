SplitMix64 to szybki, nowoczesny generator 64-bitowy wykorzystujący sekwencję prostych operacji mieszających do przekształcania liniowo rosnącego stanu w wysokiej jakości pseudolosowe wyjście. Zaprojektowany przez Sebastiano Vignę około 2015 roku, SplitMix64 znalazł szerokie zastosowanie głównie jako **generator inicjalizacyjny** (_splitter_) dla bardziej zaawansowanych generatorów wymagających wielu wartości początkowych, takich jak xoshiro i xoroshiro.

### Wyjaśnienie matematyczne

Generator SplitMix64 składa się z dwóch prostych komponentów: prostej aktualizacji stanu i zaawansowanej funkcji mieszającej.

#### Aktualizacja stanu

Stan generatora to pojedyncza 64-bitowa liczba całkowita $x$, aktualizowana przez dodawanie stałej:

$$x_{n+1} = x_n + \gamma$$

gdzie $\gamma = \text{0x9E3779B97F4A7C15}$ jest starannie dobraną stałą reprezentującą **złoty kąt w reprezentacji 64-bitowej**.

**Dlaczego ta stała?**

Stała $\gamma$ pochodzi od **złotego współczynnika** $\phi = \frac{1 + \sqrt{5}}{2} \approx 1.618033988749$:

$$\gamma = \lfloor 2^{64} / \phi \rfloor = 11400714819323198485_{10} = \text{0x9E3779B97F4A7C15}_{16}$$

Własność złotego kąta zapewnia, że kolejne wartości $x_n$ są "maksymalnie rozrzucone" w przestrzeni 64-bitowej.

#### Funkcja mieszająca

Kluczowa innowacja SplitMix64 to funkcja mieszająca przekształcająca liniowo rosnący stan w pseudolosowe wyjście. Jest to adaptacja **finalizera MurmurHash3**:

```
z ← x
z ← (z ⊕ (z >> 30)) × 0xBF58476D1CE4E5B9
z ← (z ⊕ (z >> 27)) × 0x94D049BB133111EB
output ← z ⊕ (z >> 31)
```

**Analiza kroków:**

1. Xorshift + mnożenie (pierwsza warstwa dyfuzji)
2. Xorshift + mnożenie (druga warstwa dyfuzji)
3. Finalne xorshift (równomierna dystrybucja)

### Kluczowy fragment kodu

```python
def splitmix64_bit_stream(seed, n_bits, bits_per_value=64):
    """
    Generuje strumień bitów używając SplitMix64.
    """
    GAMMA = 0x9E3779B97F4A7C15
    MASK64 = (1 << 64) - 1

    state = seed & MASK64
    output = []

    while len(output) < n_bits:
        # Aktualizacja stanu
        state = (state + GAMMA) & MASK64

        # Funkcja mieszająca
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        output_val = (z ^ (z >> 31)) & MASK64

        # Ekstrakcja bitów
        bits = extract_bits(output_val, bits_per_value, msb_first=True)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Zastosowania

**Zastosowania praktyczne:**

- **Inicjalizacja generatorów** – główne zastosowanie: tworzenie stanów dla xoshiro, xoroshiro, xorshift
- **Hash functions** – jako komponent funkcji hashujących
- **Szybkie generowanie** – aplikacje wymagające prostego, szybkiego generatora
- **Seeding** – konwersja pojedynczego seeda na wiele niezależnych wartości

**Dlaczego popularny jako splitter?**

- **Prostota**: Tylko kilka linii kodu
- **Szybkość**: Jedna z najszybszych funkcji mieszających (~5-10 cykli CPU na 64 bity)
- **Złoty kąt**: Zapewnia dobrą niezależność kolejnych wartości

**Ograniczenia:**

- **Nie dla długich sekwencji**: Nie przechodzi wszystkich testów PractRand dla bardzo długich strumieni (> 256 GB)
- **Nie dla kryptografii**: Stan łatwy do odtworzenia
- **Jakość średnia**: Dobry jako splitter, gorszy niż xoshiro/PCG jako samodzielny generator

### Jakość statystyczna

#### Testy statystyczne:

- **TestU01 SmallCrush**: Zdany
- **TestU01 Crush**: Częściowe niepowodzenia
- **TestU01 BigCrush**: Niepowodzenia w kilku testach
- **PractRand**: Przechodzi do ~256 GB, potem anomalie
- **Jako splitter**: Doskonały – generowane stany przechodzą wszystkie testy

### Kontekst historyczny i ciekawostki

**Historia:**

- Zaprojektowany przez **Sebastiano Vignę** (Università degli Studi di Milano) około 2015 roku
- Inspiracja: Java 8: SplittableRandom (Guy Steele, Doug Lea)
- Opublikowany jako część badań nad generatorami xoshiro/xoroshiro

**Ciekawostki:**

- Złoty kąt ($\gamma$) zapewnia **równomierny rozkład Weyla** – sekwencja $x \bmod 1$ jest równomiernie rozłożona w $[0,1]$
- SplitMix64 jest używany wewnętrznie w implementacjach xoshiro w Rust (rand crate)
- Funkcja mieszająca jest tak dobra, że używana jest również w non-cryptographic hash functions

### Złożoność obliczeniowa

- **Krok generacji**: $O(1)$ – 1 dodawanie + 3 xor + 3 przesunięcia + 2 mnożenia (~5-10 cykli CPU)
- **Pamięć**: $O(1)$ – 8 bajtów (stan 64-bitowy)
- **Inicjalizacja**: $O(1)$ – ustawienie seeda

### Przykład obliczeniowy

Dla $x_0 = 0$, $\gamma = \text{0x9E3779B97F4A7C15}$:

```
x_1 = 0 + 0x9E3779B97F4A7C15 = 0x9E3779B97F4A7C15
(aplikacja funkcji mieszającej)
output_1 = ... (64-bit pseudolosowa wartość)

x_2 = 0x9E3779B97F4A7C15 + 0x9E3779B97F4A7C15 = 0x3C6EF372FE94F82A
(aplikacja funkcji mieszającej)
output_2 = ... (inna pseudolosowa wartość)
```

SplitMix64 udowadnia, że prosta koncepcja (licznik + dobra funkcja mieszająca) może dać użyteczny generator, szczególnie w roli generatora seedów dla bardziej zaawansowanych generatorów.
