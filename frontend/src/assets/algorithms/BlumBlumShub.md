Blum–Blum–Shub (BBS) to kryptograficznie bezpieczny generator liczb pseudolosowych (CSPRNG) oparty na teorii liczb i trudności problemu faktoryzacji. Jest jednym z pierwszych generatorów z teoretycznie udowodnionym bezpieczeństwem, choć jego niska wydajność ogranicza praktyczne zastosowania. Generator BBS podniesiony do rangi "złotego standardu" w kryptografii teoretycznej ze względu na ścisłe podstawy matematyczne.

### Wyjaśnienie matematyczne

Generator BBS opiera się na iterowanym kwadratowaniu modulo iloczynu dwóch dużych liczb pierwszych o szczególnych własnościach.

#### Parametry i inicjalizacja

**Wybór modułu:**
Kluczowym krokiem jest wybór dwóch dużych liczb pierwszych $p$ i $q$ spełniających warunek:

$$p \equiv q \equiv 3 \pmod{4}$$

Liczby spełniające ten warunek nazywamy **liczbami pierwszymi Bluma** (_Blum primes_). Moduł generatora definiujemy jako:

$$M = p \cdot q$$

Dla zastosowań kryptograficznych $p$ i $q$ powinny być liczbami rzędu co najmniej $2^{512}$, co daje $M \approx 2^{1024}$ lub więcej.

**Warunki dla seeda:**
Wartość początkowa $x_0$ (seed) musi spełniać:

1. $\gcd(x_0, M) = 1$ – seed jest względnie pierwszy z $M$
2. $x_0 \in [2, M-1]$ – seed jest w odpowiednim zakresie

Stan początkowy ustawiamy jako:

$$x_1 = x_0^2 \bmod M$$

#### Aktualizacja stanu

W każdej iteracji stan aktualizowany jest przez podniesienie do kwadratu modulo $M$:

$$x_{n+1} = x_n^2 \bmod M$$

Ta prosta operacja jest sercem generatora BBS. Bezpieczeństwo opiera się na fakcie, że bez znajomości rozkładu $M = p \cdot q$ obliczenie poprzednich stanów z bieżącego jest obliczeniowo niewykonalne.

#### Ekstrakcja bitów wyjściowych

Z każdego stanu $x_n$ ekstrahujemy $k$ **najmniej znaczących bitów** (LSB):

$$\text{output}_n = x_n \bmod 2^k$$

Najczęściej $k=1$ (pojedynczy bit na iterację) gwarantuje najwyższe bezpieczeństwo teoretyczne. Dla lepszej wydajności można zwiększyć $k$, ale przy koszcie słabszych gwarancji bezpieczeństwa.

**Dlaczego LSB?**

- Bity najmniej znaczące są "najbardziej losowe" w kontekście reszty kwadratowej
- Bit parzystości ($x_n \bmod 2$) jest szczególnie trudny do przewidzenia bez znajomości faktoryzacji
- Ekstrahowanie MSB osłabiałoby własności kryptograficzne

#### Podstawy teoretyczne

Bezpieczeństwo BBS opiera się na **problemie reszty kwadratowej** (_Quadratic Residuosity Problem_, QRP):

**Problem QRP:** Dla danego $M = p \cdot q$ (gdzie $p, q$ są nieznane) i liczby $a \in \mathbb{Z}_M^*$, określ czy $a$ jest resztą kwadratową modulo $M$.

**Twierdzenie (Blum-Blum-Shub, 1986):**
Jeśli problem QRP jest trudny obliczeniowo, to przewidywanie następnego bitu generatora BBS (w dowolnym kierunku czasu) jest również trudne obliczeniowo.

Bezpieczeństwo BBS jest równoważne trudności faktoryzacji dużych liczb – problemu leżącego u podstaw kryptografii RSA.

### Własności matematyczne

#### Okres generatora

Maksymalny okres BBS dla modułu $M = p \cdot q$ wynosi:

$$T = \lambda(\lambda(M))$$

gdzie $\lambda$ jest funkcją Carmichaela. Dla liczb pierwszych Bluma:

$$\lambda(M) = \text{lcm}(p-1, q-1) = \frac{(p-1)(q-1)}{2}$$

Typowo okres jest rzędu $\frac{M}{4}$, co dla $M = 2^{1024}$ daje okres większy niż $2^{1022}$ – praktycznie niewyczerpany.

#### Nieprzewidywalność

**Forward security:** Znając $x_n$, obliczenie $x_{n+1}$ wymaga jednego kwadratowania modulo $M$ (łatwe).

**Backward security:** Znając $x_n$, obliczenie $x_{n-1}$ jest równoważne rozwiązaniu problemu pierwiastka kwadratowego modulo $M$ – wymaga znajomości faktoryzacji.

### Kluczowy fragment kodu

```python
def bbs_bit_stream(seed, n_bits, p=383, q=503, bits_per_value=1):
    """
    Generuje strumień bitów używając BBS.

    Args:
        seed: wartość początkowa (coprime z M)
        n_bits: liczba bitów do wygenerowania
        p, q: liczby pierwsze Bluma (p ≡ q ≡ 3 mod 4)
        bits_per_value: ile LSB ekstrahować z każdej wartości
    """
    # Sprawdź warunki dla liczb pierwszych Bluma
    if p % 4 != 3 or q % 4 != 3:
        raise ValueError("p i q muszą być ≡ 3 (mod 4)")

    M = p * q

    # Upewnij się że seed jest coprime z M
    seed = ensure_coprime(seed, M)

    # Inicjalizacja stanu
    state = pow(seed, 2, M)
    output = []

    while len(output) < n_bits:
        # Krok BBS: kwadratowanie modulo M
        state = pow(state, 2, M)

        # Ekstrakcja k LSB
        chunk_value = state & ((1 << bits_per_value) - 1)
        bits = int_to_bits(chunk_value, bits_per_value)

        output.extend(bits[:n_bits - len(output)])

    return output
```

Implementacja wykorzystuje funkcję `pow(x, 2, M)` Pythona, która efektywnie oblicza potęgowanie modularne z wykorzystaniem algorytmu szybkiego potęgowania.

### Zastosowania

**Zastosowania teoretyczne i badawcze:**

- **Protokoły zero-knowledge proof** – dowody bez ujawniania wiedzy (np. protokół Fiat-Shamira)
- **Bit commitment schemes** – kryptograficzne zobowiązania bitowe
- **Kryptografia teoretyczna** – konstrukcje wymagające udowodnialnego bezpieczeństwa
- **Badania naukowe** – analiza związków między trudnością obliczeniową a losowością
- **Materiały dydaktyczne** – przykład CSPRNG o formalnych gwarancjach bezpieczeństwa

**Ograniczenia praktyczne:**

- **Bardzo niska wydajność**: ~0.3 Mbits/s (Python) – około 10000× wolniejszy niż ChaCha20
- **Wysokie wymagania obliczeniowe**: Każdy bit wymaga potęgowania modularnego dużych liczb
- **Złożona inicjalizacja**: Generowanie dużych liczb pierwszych Bluma jest kosztowne
- **Nie stosowany w praktyce**: Współczesne systemy używają ChaCha20, AES-CTR, SHA-based DRBG

**Dlaczego BBS nie jest używany w praktyce?**

- Nowoczesne CSPRNG (ChaCha20, AES-CTR) oferują podobne lub lepsze bezpieczeństwo przy prędkości tysięcy razy wyższej
- Hardware acceleration (AES-NI, NEON) dodatkowo przyspiesza konkurencyjne algorytmy
- BBS wymaga dużych liczb pierwszych (>512 bitów), co komplikuje implementację
- Brak standaryzacji i wsparcia w bibliotekach kryptograficznych

### Jakość kryptograficzna

#### Zalety:

1. **Udowodnialne bezpieczeństwo**: Bezpieczeństwo redukowalne do problemu faktoryzacji
2. **Teoretyczna doskonałość**: Najbardziej "czysty" matematycznie CSPRNG
3. **Długi okres**: Praktycznie niewyczerpany dla dużych modułów
4. **Brak struktury**: Sekwencja nie wykazuje żadnych statystycznych korelacji wykrywalnych bez faktoryzacji

#### Wady praktyczne:

1. **Ekstremalna wolność**: Tysięce razy wolniejszy niż współczesne CSPRNG
2. **Wymaga dużych liczb**: Dla bezpieczeństwa potrzeba $M \geq 2^{1024}$
3. **Złożona implementacja**: Arytmetyka wieloprecyzyjna, generowanie liczb pierwszych
4. **Brak standaryzacji**: Nie ma standardów typu FIPS dla BBS

#### Analiza bezpieczeństwa:

- **Ataki known-plaintext**: Odporne – nawet znając wiele bitów wyjściowych nie można odtworzyć stanu bez faktoryzacji
- **Ataki timing**: Potencjalnie wrażliwe – implementacja musi być constant-time
- **Forward/backward prediction**: Obliczeniowo niewykonalne bez znajomości $p$ i $q$
- **Quantum computing**: Podatne – algorytm Shora łamie faktoryzację w czasie wielomianowym

### Kontekst historyczny i ciekawostki

**Historia:**

- Zaproponowany przez **Lenore Blum**, **Manuela Bluma** i **Michaela Shuba** w 1986 roku w pracy "A Simple Unpredictable Pseudo-Random Number Generator"
- Pierwszy PRNG z dowodem bezpieczeństwa opartym na dobrze poznanym problemie matematycznym
- Inspiracja dla późniejszych konstrukcji CSPRNG o udowodnialnym bezpieczeństwie

**Znaczenie teoretyczne:**

- **Dowód koncepcji**: Pokazał, że można zbudować CSPRNG z formalnym dowodem bezpieczeństwa
- **Most między teorią a praktyką**: Połączył teoretyczną informatykę z kryptografią stosowaną
- **Fundament badań**: Inspiracja dla konstrukcji takich jak Micali-Schnorr generator

**Ciekawostki:**

- Lenore Blum jest jedną z pionierek informatyki teoretycznej
- BBS był jednym z pierwszych algorytmów rozważanych do standaryzacji NIST (odrzucony ze względu na wydajność)
- Niektóre chipy kryptograficzne z lat 90. implementowały BBS sprzętowo
- W praktyce częściej stosuje się hybrydy: BBS do generacji seedu dla szybszego generatora

**Warianty i rozszerzenia:**

- **x²+1 generator**: Wariant $x_{n+1} = x_n^2 + 1 \bmod M$
- **Multiple-stream BBS**: Równoległe strumienie z różnymi seedami
- **BBS z przyspieszeniem**: Skipping ahead – generowanie $x_{n+k}$ bez obliczania stanów pośrednich

### Złożoność obliczeniowa

- **Krok generacji**: $O(\log^3 M)$ dla naiwnego mnożenia modularnego; $O(\log^2 M)$ z algorytmami Karatsuba/FFT
- **Pamięć**: $O(\log M)$ – przechowywany stan + moduł (typowo ~256 bajtów dla $M = 2^{1024}$)
- **Inicjalizacja**: $O(\log^4 M)$ – generowanie liczb pierwszych Bluma (testy pierwszości Miller-Rabin)

Dla porównania, ChaCha20 ma złożoność $O(1)$ per bit i wymaga stałej pamięci (64 bajty stanu).

### Przykłady obliczeniowe

#### Przykład 1: Małe liczby pierwsze Bluma

Dla $p=7$, $q=11$ (oba $\equiv 3 \bmod 4$):

- $M = 7 \cdot 11 = 77$
- Seed $x_0 = 3$ (coprime z 77)
- $x_1 = 3^2 \bmod 77 = 9$
- $x_2 = 9^2 \bmod 77 = 81 \bmod 77 = 4$
- $x_3 = 4^2 \bmod 77 = 16$
- $x_4 = 16^2 \bmod 77 = 256 \bmod 77 = 25$

Ekstrahując LSB: $\text{bit}_1 = 9 \bmod 2 = 1$, $\text{bit}_2 = 4 \bmod 2 = 0$, $\text{bit}_3 = 16 \bmod 2 = 0$, $\text{bit}_4 = 25 \bmod 2 = 1$

Sekwencja bitów: `1, 0, 0, 1, ...`

#### Przykład 2: Średnie liczby pierwsze

Dla $p=383$, $q=503$ (domyślne w implementacji testowej):

- $M = 383 \cdot 503 = 192649$
- Seed $x_0 = 12345$
- $x_1 = 12345^2 \bmod 192649 = 152399025 \bmod 192649 = 101112$
- $x_2 = 101112^2 \bmod 192649 = 10223636544 \bmod 192649 = 85665$
- $x_3 = 85665^2 \bmod 192649 = 7338490225 \bmod 192649 = 67201$

Ekstrahując 4 LSB z każdego: $101112 \bmod 16 = 8$, $85665 \bmod 16 = 1$, $67201 \bmod 16 = 1$

#### Przykład 3: Długoterminowa predykcja (niemożliwa bez faktoryzacji)

Znając $x_{100}$ nie można efektywnie obliczyć $x_{99}$ bez znajomości $p$ i $q$. To wymaga rozwiązania:

$$y^2 \equiv x_{100} \pmod{M}$$

Co jest równoważne faktoryzacji $M$ (problem trudny obliczeniowo).

BBS pozostaje fascynującym przykładem głębokiego związku między teorią liczb a kryptografią praktyczną, choć jego niska wydajność uczyniła go głównie obiektem studiów teoretycznych i materiałem edukacyjnym.
