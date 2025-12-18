AWCG (Add-With-Carry Generator) to rozszerzona wersja klasycznego generatora LCG, która wprowadza dodatkowy mechanizm przeniesienia (_carry bit_). Ten prosty dodatek znacząco poprawia własności statystyczne generatora, wydłuża okres i redukuje korelacje charakterystyczne dla prostych LCG. AWCG stanowi ważny krok w ewolucji generatorów pseudolosowych, łącząc prostotę implementacji z lepszą jakością statystyczną.

### Wyjaśnienie matematyczne

Generator AWCG rozszerza klasyczny LCG o dodatkowy bit stanu — przeniesienie (_carry_), który przechowuje informację o "przepełnieniu" z poprzedniej iteracji.

#### Podstawowa formuła

Stan generatora składa się z dwóch komponentów:

- $x_n$ – główna wartość stanu (liczba całkowita z zakresu $[0, m-1]$)
- $\text{carry}_n$ – bit przeniesienia (zazwyczaj 0 lub 1, ale może być większy)

Aktualizacja stanu przebiega następująco:

$$s = a \cdot x_n + c + \text{carry}_n$$

$$x_{n+1} = s \bmod m$$

$$\text{carry}_{n+1} = \lfloor s / m \rfloor$$

gdzie:

- $a$ – mnożnik (multiplier)
- $c$ – przyrost (increment)
- $m$ – moduł, definiuje zakres wartości
- $s$ – wartość pośrednia przed zastosowaniem modulo

#### Mechanizm carry

Kluczowa różnica względem LCG polega na tym, że informacja o "przepełnieniu" (części całkowitej $s/m$) nie jest tracona, lecz jest przenoszona do następnej iteracji. To wprowadza zależność między kolejnymi krokami wykraczającą poza prosty schemat Markowa pierwszego rzędu.

**Efekty mechanizmu carry:**

- **Wydłużenie okresu**: Carry może znacznie wydłużyć okres generatora względem czystego LCG
- **Redukcja korelacji**: Nieliniowa zależność między stanami redukuje typowe dla LCG korelacje
- **Lepsza dystrybucja**: Wartości są bardziej równomiernie rozłożone w przestrzeni wielowymiarowej

#### Wariant z tablicą stanów

W pełnej implementacji AWCG często wykorzystuje się tablicę stanów zamiast pojedynczej wartości. Popularny wariant używa dwóch parametrów opóźnienia (_lags_):

$$x_n = (x_{n-r} + x_{n-s} + \text{carry}_{n-1}) \bmod m$$

gdzie $r > s > 0$ (typowo $r=24$, $s=10$). Ta wersja nazywana jest też **lagged Fibonacci generator with carry**.

#### Parametry testowe

Standardowe parametry używane w testach to adaptacja parametrów GLIBC:

- $a = 1103515245$
- $c = 12345$
- $m = 2^{32}$
- Seed: dowolna wartość początkowa $x_0$
- Carry początkowe: $\text{carry}_0 = 0$

#### Ekstrakcja bitów

Podobnie jak w LCG, bity wyjściowe najczęściej pobierane są z najstarszych (MSB) bitów wartości $x_n$:

- Dla $m = 2^{32}$: ekstrahuje się zazwyczaj 32 bity
- Implementacja: `(x >> (bits_total - bits_needed))` dla MSB-first
- LSB-first jest również dostępne, choć rzadziej używane

### Popularne konfiguracje parametrów

#### 1. AWCG-GLIBC (32-bit)

- $a = 1103515245$
- $c = 12345$
- $m = 2^{32}$
- Carry: standardowe przeniesienie binarne
- Podstawa dla wielu implementacji testowych

#### 2. Lagged Fibonacci with Carry

- $r = 24$, $s = 10$
- $m = 2^{32}$
- Tablica 24 wartości stanu
- Długi okres: około $2^{768}$

### Kluczowy fragment kodu

```python
def awcg_bit_stream(seed, n_bits, r=24, s=10, base=2**32,
                    bits_per_value=None, msb_first=True):
    """
    Generuje strumień bitów używając AWCG.

    Args:
        seed: wartość początkowa lub tablica stanów
        n_bits: liczba bitów do wygenerowania
        r: główny lag (długość tablicy stanów)
        s: mniejszy lag
        base: moduł (baza)
        bits_per_value: ile bitów ekstrahować z każdej wartości
        msb_first: czy brać bity od najstarszych
    """
    # Inicjalizacja tablicy stanów
    state = initialize_state(seed, r, base)
    carry = 0
    output = []
    p = 0  # wskaźnik pozycji w tablicy cyklicznej

    while len(output) < n_bits:
        # Indeksy w tablicy cyklicznej
        idx_r = p % r
        idx_n_minus_r = (p - r) % r
        idx_n_minus_s = (p - s) % r

        # Krok AWCG z carry
        val = state[idx_n_minus_r] + state[idx_n_minus_s] + carry

        # Oblicz nową wartość i carry
        if val >= base:
            carry = 1
            val -= base
        else:
            carry = 0

        state[idx_r] = val
        p = (p + 1) % r

        # Ekstrakcja bitów
        bits = extract_bits(val, bits_per_value, msb_first)
        output.extend(bits[:n_bits - len(output)])

    return output
```

Implementacja w Pythonie wykorzystuje tablicę cykliczną do przechowywania stanów oraz naturalną arytmetykę wieloprecyzyjną dla bezpieczeństwa obliczeń.

### Zastosowania

**Zastosowania praktyczne:**

- **Symulacje Monte Carlo** – gdy wymagana jest lepsza jakość niż LCG, ale bez konieczności najwyższej klasy generatorów
- **Modelowanie stochastyczne** – systemy wymagające umiarkowanych własności statystycznych
- **Materiały edukacyjne** – demonstracja wpływu mechanizmu carry na jakość sekwencji pseudolosowych
- **Badania naukowe** – analiza generatorów z pamięcią międzystanową
- **Prototypowanie algorytmów** – szybkie testy przed implementacją produkcyjną

**Ograniczenia:**

- **Kryptografia**: Absolutnie nie zalecany – przewidywalny przy znajomości parametrów i kilku wyjść
- **Aplikacje bezpieczeństwa**: Liniowa struktura umożliwia ataki analityczne
- **Symulacje wymagające najwyższej jakości**: Nowoczesne generatory (PCG, xoshiro) oferują lepszą jakość przy podobnej lub wyższej wydajności
- **Systemy z ograniczoną pamięcią**: Warianty z tablicą stanów wymagają więcej pamięci niż prosty LCG

### Jakość statystyczna i problemy

#### Zalety względem LCG:

1. **Dłuższy okres**: Carry może wydłużyć okres maksymalny znacznie powyżej $m$
2. **Lepsza dystrybucja wielowymiarowa**: Redukcja efektu "hiperpłaszczyzn" charakterystycznego dla LCG
3. **Słabsze korelacje**: Mechanizm carry redukuje korelacje między kolejnymi wartościami
4. **Przejście większości podstawowych testów**: DIEHARD, niektóre testy z TestU01

#### Wady:

1. **Nadal przewidywalny**: Liniowa natura (z nieliniowym carry) pozwala na rekonstrukcję stanu
2. **Wolniejszy niż LCG**: Dodatkowe operacje (sprawdzanie carry) obniżają wydajność
3. **Nie przechodzi zaawansowanych testów**: BigCrush z TestU01 ujawnia słabości
4. **Złożoność implementacji**: Trudniejszy w implementacji niż prosty LCG, szczególnie warianty z opóźnieniami

#### Testy statystyczne:

- **DIEHARD Battery**: Większość testów przechodzi pomyślnie (lepiej niż LCG)
- **TestU01 SmallCrush**: Przechodzi
- **TestU01 Crush**: Przechodzi częściowo
- **TestU01 BigCrush**: Wykrywa anomalie statystyczne
- **PractRand**: Ujawnia problemy przy długich sekwencjach (> 1TB)

### Kontekst historyczny i ciekawostki

**Historia:**

- AWCG jest częścią rodziny generatorów **with-carry** zaprojektowanej przez **George'a Marsaglię i Arimę Zaman** w latach 90. XX wieku
- Pierwsza publikacja opisująca Multiply-With-Carry (MWC) ukazała się w 1991 roku
- AWCG powstał jako wariant addytywny MWC, prostszy w analizie teoretycznej

**Warianty i rozwój:**

- **MWC (Multiply-With-Carry)**: $x_n = (a \cdot x_{n-1} + \text{carry}_{n-1}) \bmod b$
- **CMWC (Complementary MWC)**: $x_n = (a \cdot x_{n-r} + \text{carry}_{n-1}) \bmod b$, gdzie carry jest duże
- **Lagged Fibonacci with carry**: wykorzystuje dwa parametry opóźnienia

**Znaczenie historyczne:**

- Most między prostymi LCG a zaawansowanymi generatorami lat 90./2000.
- Inspiracja dla późniejszych konstrukcji łączących prostotę z lepszą jakością
- Dowód koncepcji, że prosty mechanizm (carry) może znacząco poprawić własności statystyczne

**Ciekawostki:**

- Marsaglia nazywał generatory with-carry "mother of all RNGs" (matka wszystkich generatorów)
- Mechanizm carry jest analogiczny do cyfrowego przeniesienia w arytmetyce
- AWCG z dobrymi parametrami może osiągnąć okres rzędu $2^{1000}$ i więcej
- Niektóre implementacje sprzętowe używają wariantów AWCG ze względu na prostotę obwodów

### Złożoność obliczeniowa

- **Krok generacji**: $O(1)$ – dodawanie, sprawdzenie carry, modulo (prostsze niż mnożenie w LCG)
- **Pamięć**:
  - Wersja podstawowa: $O(1)$ – stan + carry
  - Wersja z opóźnieniami: $O(r)$ – tablica $r$ wartości + carry
- **Inicjalizacja**: $O(r)$ – inicjalizacja tablicy stanów (jeśli używana)

Dla wariantu podstawowego AWCG jest nieznacznie wolniejszy niż LCG (dodatkowe sprawdzenie carry), ale wciąż bardzo szybki. Warianty z opóźnieniami są wolniejsze i wymagają więcej pamięci.

### Przykłady obliczeniowe

#### Przykład 1: Prosty AWCG z małym modułem

Dla $a=5$, $c=3$, $m=16$, $x_0=1$, $\text{carry}_0=0$:

- **Krok 1**:

  - $s = 5 \cdot 1 + 3 + 0 = 8$
  - $x_1 = 8 \bmod 16 = 8$
  - $\text{carry}_1 = \lfloor 8/16 \rfloor = 0$

- **Krok 2**:

  - $s = 5 \cdot 8 + 3 + 0 = 43$
  - $x_2 = 43 \bmod 16 = 11$
  - $\text{carry}_2 = \lfloor 43/16 \rfloor = 2$

- **Krok 3**:

  - $s = 5 \cdot 11 + 3 + 2 = 60$
  - $x_3 = 60 \bmod 16 = 12$
  - $\text{carry}_3 = \lfloor 60/16 \rfloor = 3$

- **Krok 4**:
  - $s = 5 \cdot 12 + 3 + 3 = 66$
  - $x_4 = 66 \bmod 16 = 2$
  - $\text{carry}_4 = \lfloor 66/16 \rfloor = 4$

Zauważ, że carry rośnie, co wydłuża okres względem czystego LCG.

#### Przykład 2: AWCG-GLIBC

Dla $a=1103515245$, $c=12345$, $m=2^{32}$, $x_0=1$, $\text{carry}_0=0$:

- **Krok 1**:

  - $s = 1103515245 \cdot 1 + 12345 + 0 = 1103527590$
  - $x_1 = 1103527590$
  - $\text{carry}_1 = 0$ (brak przepełnienia)

- **Krok 2**:
  - $s = 1103515245 \cdot 1103527590 + 12345 + 0 = 1217656738076457950$
  - $x_2 = 1217656738076457950 \bmod 2^{32} = 2524885598$
  - $\text{carry}_2 = \lfloor 1217656738076457950 / 2^{32} \rfloor = 283473826$

W tym przypadku duży carry wpływa na następne iteracje, zwiększając złożoność sekwencji.

#### Przykład 3: Lagged Fibonacci with Carry

Dla $r=5$, $s=2$, $m=10$, stan początkowy $[1,2,3,4,5]$, $\text{carry}_0=0$:

- **Krok 1** ($n=5$):

  - $x_5 = (x_0 + x_3 + 0) \bmod 10 = (1 + 4 + 0) \bmod 10 = 5$
  - $\text{carry} = 0$

- **Krok 2** ($n=6$):

  - $x_6 = (x_1 + x_4 + 0) \bmod 10 = (2 + 5 + 0) \bmod 10 = 7$
  - $\text{carry} = 0$

- **Krok 3** ($n=7$):
  - $x_7 = (x_2 + x_5 + 0) \bmod 10 = (3 + 5 + 0) \bmod 10 = 8$
  - $\text{carry} = 0$

AWCG pozostaje użyteczny głównie w kontekście edukacyjnym oraz jako generator o umiarkowanej jakości dla prostych symulacji. Jest to dobry kompromis między prostotą LCG a wymaganiami jakościowymi, choć nowoczesne generatory (PCG32, xoshiro256\*\*) oferują lepsze właściwości przy podobnej lub wyższej wydajności.
