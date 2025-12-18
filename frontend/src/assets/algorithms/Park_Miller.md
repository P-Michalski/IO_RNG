Park–Miller, znany również jako **MINSTD** (Minimal Standard), to szczególny przypadek generatora multiplikatywnego LCG bez składowej addytywnej. Zaproponowany w 1988 roku jako odpowiedź na problematyczne implementacje funkcji rand() w bibliotekach standardowych, stał się punktem odniesienia dla oceny jakości prostych generatorów pseudolosowych. Wykorzystuje staranne dobranie parametrów matematycznych zapewniających maksymalny okres i relatywnie dobre własności statystyczne.

### Wyjaśnienie matematyczne

Generator Park-Miller jest multiplikatywnym generatorem liniowym kongruencyjnym, co oznacza brak składowej addytywnej:

$$x_{n+1} = (a \cdot x_n) \bmod m$$

gdzie:

- $a = 16807 = 7^5$ – mnożnik (primitive root modulo $m$)
- $m = 2^{31} - 1 = 2{,}147{,}483{,}647$ – moduł (liczba pierwsza Mersenne'a)
- $x_0$ – seed, wartość początkowa z zakresu $[1, m-1]$

#### Dlaczego te konkretne parametry?

**Mnożnik $a = 16807 = 7^5$:**

- Jest **pierwiastkiem pierwotnym** modulo $m$ – generuje wszystkie elementy $\mathbb{Z}_m^*$
- Zapewnia pełny okres $m-1 = 2{,}147{,}483{,}646$ (wszystkie wartości z wyjątkiem 0)
- Potęga 7 została wybrana po ekstensywnych testach spektralnych

**Moduł $m = 2^{31} - 1$:**

- **Liczba pierwsza Mersenne'a** – ma specjalne własności ułatwiające efektywne obliczenia modulo
- Maksymalizuje okres dla 31-bitowych liczb całkowitych
- Umożliwia implementację bez przepełnień na 32-bitowych architekturach

#### Problem przepełnienia i arytmetyka Schrage'a

Naiwne obliczenie $(a \cdot x_n) \bmod m$ może prowadzić do przepełnienia, ponieważ:

$$16807 \times 2{,}147{,}483{,}646 = 36{,}028{,}797{,}018{,}963{,}968 > 2^{31}$$

**Schrage's method** rozwiązuje ten problem przez dekompozycję:

$$m = a \cdot q + r$$

gdzie:

- $q = \lfloor m / a \rfloor = 127{,}773$
- $r = m \bmod a = 2{,}836$

Algorytm Schrage'a:

```
hi = x / q
lo = x % q
t = a * lo - r * hi
if t > 0:
    x = t
else:
    x = t + m
```

To zapewnia, że wszystkie pośrednie obliczenia mieszczą się w 32 bitach.

### Kluczowy fragment kodu

```python
def park_miller_bit_stream(seed, n_bits, bits_per_value=31):
    """
    Generuje strumień bitów używając Park-Miller MINSTD.
    """
    A = 16807
    M = 2147483647  # 2^31 - 1
    Q = M // A      # 127773
    R = M % A       # 2836

    x = seed % M
    if x <= 0:
        x = 1

    output = []

    while len(output) < n_bits:
        # Arytmetyka Schrage'a
        hi = x // Q
        lo = x % Q
        t = A * lo - R * hi

        if t > 0:
            x = t
        else:
            x = t + M

        # Ekstrakcja bitów
        bits = extract_bits(x, bits_per_value, msb_first=True)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Zastosowania

**Zastosowania praktyczne:**

- **Materiały edukacyjne** – prosty, dobrze udokumentowany generator do nauki
- **Badania naukowe** – punkt odniesienia dla porównań jakościowych
- **Symulacje statystyczne** – gdy wystarczą umiarkowane wymagania jakościowe
- **Reprodukcja starszych badań** – kompatybilność z publikacjami z lat 80-90
- **Embedded systems** – mały footprint pamięciowy (4 bajty)

**Ograniczenia:**

- **Kryptografia**: Absolutnie nie zalecany – przewidywalny, łatwy do złamania
- **Wymagające symulacje**: Korelacje wielowymiarowe, niepowodzenia w zaawansowanych testach
- **Nowoczesne aplikacje**: PCG32, xoshiro oferują lepszą jakość przy podobnej szybkości

### Jakość statystyczna

#### Testy statystyczne:

- **DIEHARD**: Przechodzi większość testów (lepiej niż słabe LCG)
- **TestU01 SmallCrush**: Zdany
- **TestU01 Crush**: Częściowe niepowodzenia
- **TestU01 BigCrush**: Niepowodzenia w kilku testach
- **Spectral test**: Rank 3-4 (umiarkowany dla 31-bitowego generatora)

### Kontekst historyczny i ciekawostki

**Historia:**

- Zaproponowany przez **Stephena K. Parka** i **Keitha W. Millera** w 1988 w artykule "Random Number Generators: Good Ones Are Hard To Find"
- Reakcja na wysyp słabych generatorów w bibliotekach standardowych
- Tytuł "Minimal Standard" miał podnieść poprzeczkę dla implementacji bibliotecznych

**Ewolucja:**

- **1988**: Oryginalny MINSTD ($a=16807$)
- **1993**: MINSTD Revised ($a=48271$) po dodatkowych testach
- **Obecnie**: Głównie znaczenie historyczne i edukacyjne

**Ciekawostki:**

- Artykuł Park-Miller był cytowany ponad 3000 razy
- Mnożnik $16807 = 7^5$ został wybrany po przetestowaniu setek kandydatów
- Liczba $2^{31}-1$ to 8. liczba pierwsza Mersenne'a
- Generator był używany w MATLAB do wersji R2007b

### Złożoność obliczeniowa

- **Krok generacji**: $O(1)$ – jedno mnożenie, dzielenie, sprawdzenie warunku
- **Pamięć**: $O(1)$ – 4 bajty (stan $x_n$)
- **Inicjalizacja**: $O(1)$ – ustawienie seeda

### Przykłady obliczeniowe

#### Przykład 1: Podstawowa sekwencja

Dla $x_0 = 1$:

- $x_1 = (16807 \cdot 1) \bmod (2^{31}-1) = 16{,}807$
- $x_2 = (16807 \cdot 16807) \bmod (2^{31}-1) = 282{,}475{,}249$
- $x_3 = (16807 \cdot 282475249) \bmod (2^{31}-1) = 1{,}622{,}650{,}073$
- $x_4 = (16807 \cdot 1622650073) \bmod (2^{31}-1) = 984{,}943{,}658$

Park-Miller pozostaje ważnym punktem odniesienia w historii generatorów pseudolosowych – reprezentuje "minimalny akceptowalny standard" z końca lat 80., obecnie zastąpiony przez lepsze algorytmy (PCG, xoshiro), ale wciąż użyteczny edukacyjnie i do replikacji historycznych badań.
