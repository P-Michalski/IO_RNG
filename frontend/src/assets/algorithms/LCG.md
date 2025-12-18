LCG (Linear Congruential Generator) to klasyczny generator pseudolosowy oparty na prostej relacji rekurencyjnej: $x_{n+1} = (a x_n + c) \bmod m$. Jest jednym z najstarszych i najczęściej stosowanych algorytmów generowania liczb pseudolosowych ze względu na swoją prostotę i wydajność obliczeniową. Mimo zalet, generator jest podatny na korelacje statystyczne oraz bardzo wrażliwy na dobór parametrów $a$, $c$ i $m$.

### Wyjaśnienie matematyczne

Generator LCG opiera się na iteracyjnej funkcji liniowej z operacją modulo:

$$x_{n+1} = (a \cdot x_n + c) \bmod m$$

gdzie:

- $x_n$ – bieżący stan generatora (liczba całkowita z zakresu $[0, m-1]$)
- $x_0$ – wartość początkowa (seed), determinuje całą sekwencję
- $a$ – mnożnik (multiplier), wpływa na rozproszenie wartości
- $c$ – przyrost (increment), może być 0 dla tzw. generatorów multiplikatywnych
- $m$ – moduł, definiuje maksymalny okres oraz zakres wartości

#### Warunki pełnego okresu

Aby generator osiągnął maksymalny okres równy $m$, muszą być spełnione następujące warunki (twierdzenie Hull-Dobell):

1. $\gcd(c, m) = 1$ – $c$ i $m$ są względnie pierwsze
2. $a - 1$ jest podzielne przez wszystkie dzielniki pierwsze $m$
3. Jeśli $m$ jest podzielne przez 4, to $a - 1$ także musi być podzielne przez 4

Dla generatorów multiplikatywnych ($c = 0$) warunki są bardziej restrykcyjne, a maksymalny okres wynosi $m/4$ przy $m = 2^k$.

#### Ekstrakcja bitów

Bity wyjściowe pozyskuje się najczęściej z najstarszych (najbardziej znaczących) bitów wartości $x_n$, ponieważ młodsze bity wykazują słabsze własności statystyczne:

- Dla $m = 2^{31}$: ekstrahuje się zazwyczaj 31 bitów (poza bitem znaku)
- Dla $m = 2^{32}$: można ekstrahować wszystkie 32 bity
- Implementacja: `(x >> (bits_total - bits_needed))` dla MSB-first

W praktyce implementacji pozwala się na wybór między ekstrakcją MSB-first (najbardziej znaczące bity pierwsze) lub LSB-first, przy czym pierwsza opcja jest standardem ze względu na lepszą jakość statystyczną starszych bitów.

### Popularne zestawy parametrów

#### 1. GLIBC (31-bit)

- $a = 1103515245$
- $c = 12345$
- $m = 2^{31}$
- Używany w bibliotece standardowej C (glibc)
- Dobra równowaga między prostotą a jakością

#### 2. Numerical Recipes (32-bit)

- $a = 1664525$
- $c = 1013904223$
- $m = 2^{32}$
- Popularny w literaturze, choć ma pewne wady statystyczne

#### 3. MSVC (Microsoft Visual C++)

- $a = 214013$
- $c = 2531011$
- $m = 2^{32}$
- Stosowany w kompilatorze MSVC

### Kluczowy fragment kodu

```python
def lcg_bit_stream(seed, a, c, m, n_bits, bits_per_value=None, msb_first=True):
    """
    Generuje strumień bitów używając LCG.

    Args:
        seed: wartość początkowa x_0
        a, c, m: parametry LCG
        n_bits: liczba bitów do wygenerowania
        bits_per_value: ile bitów ekstrahować z każdej wartości
        msb_first: czy brać bity od najstarszych
    """
    x = seed
    output = []

    while len(output) < n_bits:
        # Krok LCG - aktualizacja stanu
        x = (a * x + c) % m

        # Ekstrakcja bitów (domyślnie MSB-first)
        bits = extract_bits(x, bits_per_value, msb_first)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Zastosowania

**Zastosowania praktyczne:**

- Materiały edukacyjne i dydaktyczne – doskonały przykład generatora PRNG do nauki
- Proste symulacje Monte Carlo – gdy nie są wymagane zaawansowane własności statystyczne
- Generowanie danych testowych – szybkie tworzenie powtarzalnych sekwencji
- Gry komputerowe (starsze) – generowanie map, pozycji przeciwników
- Biblioteki standardowe języków programowania – np. rand() w C

**Ograniczenia:**

- **Kryptografia**: Absolutnie nie zalecany do zastosowań kryptograficznych z uwagi na całkowitą przewidywalność – znając kilka kolejnych wartości można odtworzyć parametry i przewidzieć całą sekwencję
- **Symulacje wymagające wysokiej jakości losowości**: Korelacje między wartościami mogą prowadzić do błędnych wyników
- **Aplikacje bezpieczeństwa**: Liniowa struktura umożliwia łatwe ataki kryptoanalityczne

### Jakość statystyczna i problemy

#### Wady strukturalne:

1. **Korelacje liniowe**: Wartości $x_n$ i $x_{n+1}$ są ze sobą skorelowane
2. **Test spektralny**: Punkty $(x_n, x_{n+1}, ..., x_{n+k})$ leżą na hiperpłaszczyznach w przestrzeni $k$-wymiarowej
3. **Słabość młodszych bitów**: Najmłodsze bity mają bardzo krótkie okresy (np. ostatni bit ma okres 2)
4. **Przewidywalność**: Całkowicie deterministyczny – seed determinuje całą sekwencję

#### Testy statystyczne:

- Marsaglia's Spectral Test – ujawnia strukturę kratową
- Birthday Spacings Test – wykrywa korelacje
- DIEHARD Battery – generatory LCG często nie przechodzą wszystkich testów

### Kontekst historyczny i ciekawostki

**Historia:**

- Geneza LCG sięga prac **Derricka Henry'ego Lehmera** z 1949 roku, opublikowanych w artykule opisującym metodę dla maszyny ENIAC
- W latach 50-70. XX wieku był de facto standardem generatorów pseudolosowych
- Pierwsze implementacje sprzętowe pojawiły się w kalkulatorach naukowych lat 60.

**Ciekawostki:**

- Funkcja rand() w wielu implementacjach C++ do dziś używa LCG (choć nowsze standardy zalecają Mersenne Twister)
- Generator był używany w systemie IBM System/360 (1964)
- Donald Knuth poświęcił cały rozdział LCG w "The Art of Computer Programming" (Vol. 2)
- Spektralny test wizualizacyjny: gdy narysujemy pary $(x_n, x_{n+1})$, widoczne są linie równoległe zamiast równomiernego rozłożenia punktów

### Złożoność obliczeniowa

- **Krok generacji**: $O(1)$ – jedno mnożenie, jedno dodawanie, jedno modulo
- **Pamięć**: $O(1)$ – przechowywany tylko bieżący stan $x_n$
- **Inicjalizacja**: $O(1)$ – ustawienie seeda

Dzięki ekstremalnej prostocie LCG jest jednym z najszybszych generatorów, co czyni go atrakcyjnym dla zastosowań wymagających ogromnej liczby wartości pseudolosowych przy niewielkich wymaganiach co do jakości.

### Przykłady obliczeniowe

#### Przykład 1: Mały moduł

Dla $a=5$, $c=3$, $m=16$, $x_0=7$:

- $x_1 = (5 \cdot 7 + 3) \bmod 16 = 38 \bmod 16 = 6$
- $x_2 = (5 \cdot 6 + 3) \bmod 16 = 33 \bmod 16 = 1$
- $x_3 = (5 \cdot 1 + 3) \bmod 16 = 8 \bmod 16 = 8$
- $x_4 = (5 \cdot 8 + 3) \bmod 16 = 43 \bmod 16 = 11$

#### Przykład 2: Generator MINSTD

Dla $a=16807$, $c=0$, $m=2^{31}-1=2147483647$, $x_0=1$:

- $x_1 = (16807 \cdot 1) \bmod 2147483647 = 16807$
- $x_2 = (16807 \cdot 16807) \bmod 2147483647 = 282475249$
- $x_3 = (16807 \cdot 282475249) \bmod 2147483647 = 1622650073$

Ten generator ma pełny okres $2^{31} - 2$ (wszystkie wartości z wyjątkiem 0).

LCG pozostaje użyteczny przede wszystkim jako generator dydaktyczny oraz w zastosowaniach gdzie prostota implementacji i szybkość są ważniejsze niż najwyższa jakość statystyczna.
