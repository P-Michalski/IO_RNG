ChaCha20 to szyfr strumieniowy zaprojektowany przez Daniela J. Bernsteina w 2008 roku jako ulepszona wersja Salsa20. Jako **kryptograficznie bezpieczny generator pseudolosowy (CSPRNG)**, ChaCha20 znalazł szerokie zastosowanie w protokołach sieciowych (TLS 1.3, WireGuard, SSH) i jest obecnie jednym z najpopularniejszych szyfrów strumieniowych na świecie. Strumień klucza generowany przez ChaCha20 może służyć jako źródło wysokiej jakości bitów pseudolosowych z gwarancjami kryptograficznymi.

### Wyjaśnienie matematyczne

ChaCha20 jest szyfrem strumieniowym opartym na konstrukcji **ARX** (Add-Rotate-XOR) – wykorzystuje tylko dodawanie modulo $2^{32}$, rotacje bitowe i XOR.

#### Stan wewnętrzny

Stan ChaCha20 to macierz $4 \times 4$ słów 32-bitowych (łącznie 512 bitów):

$$
\begin{bmatrix}
c_0 & c_1 & c_2 & c_3 \\
k_0 & k_1 & k_2 & k_3 \\
k_4 & k_5 & k_6 & k_7 \\
b & n_0 & n_1 & n_2
\end{bmatrix}
$$

gdzie:

- $c_0, c_1, c_2, c_3$ – **stałe ChaCha** ("expand 32-byte k" w ASCII): `0x61707865, 0x3320646e, 0x79622d32, 0x6b206574`
- $k_0 \ldots k_7$ – **256-bitowy klucz** (8 × 32-bit)
- $b$ – **32-bitowy licznik bloku**
- $n_0, n_1, n_2$ – **96-bitowy nonce** (3 × 32-bit)

#### Operacja quarter-round

Podstawową operacją ChaCha20 jest **quarter-round** – funkcja mieszająca działająca na 4 słowach 32-bitowych:

```
QUARTERROUND(a, b, c, d):
    a += b; d ^= a; d <<<= 16
    c += d; b ^= c; b <<<= 12
    a += b; d ^= a; d <<<= 8
    c += d; b ^= c; b <<<= 7
```

gdzie:

- += oznacza dodawanie modulo $2^{32}$
- ^= oznacza XOR
- <<<= oznacza rotację bitową w lewo

**Dlaczego te konkretne rotacje (16, 12, 8, 7)?**

- Dobrane empirycznie dla maksymalnej dyfuzji
- Każda rotacja miesza bity w inny sposób
- 4 rundy dają pełną avalanche effect (zmiana 1 bitu wejścia → zmienia średnio 16 bitów wyjścia)

#### Rundy mieszania

Jedna **double-round** ChaCha20 składa się z:

1. **Column rounds** – quarter-round na kolumnach:

   ```
   QUARTERROUND(0, 4,  8, 12)
   QUARTERROUND(1, 5,  9, 13)
   QUARTERROUND(2, 6, 10, 14)
   QUARTERROUND(3, 7, 11, 15)
   ```

2. **Diagonal rounds** – quarter-round na przekątnych:
   ```
   QUARTERROUND(0, 5, 10, 15)
   QUARTERROUND(1, 6, 11, 12)
   QUARTERROUND(2, 7,  8, 13)
   QUARTERROUND(3, 4,  9, 14)
   ```

**ChaCha20 wykonuje 10 double-rounds (20 quarter-rounds)** – stąd nazwa "ChaCha20".

#### Generacja bloku

Proces generacji 512-bitowego bloku strumienia klucza:

1. **Inicjalizacja**: Załaduj stan początkowy (stałe, klucz, licznik, nonce)
2. **Kopiuj stan**: $\text{working} \leftarrow \text{state}$
3. **20 rund mieszania**: Wykonaj 10 double-rounds na $\text{working}$
4. **Dodaj stan początkowy**: $\text{output} \leftarrow \text{working} + \text{state}$ (modulo $2^{32}$ per słowo)
5. **Inkrementuj licznik**: $b \leftarrow b + 1$
6. **Wynik**: 512 bitów strumienia klucza

**Dlaczego dodawać stan początkowy?**

- Zapobiega atakom typu "backward tracing"
- Każdy blok jest funkcją zarówno stanu przed jak i po mieszaniu
- Zwiększa bezpieczeństwo kryptograficzne

#### Jako CSPRNG

Gdy ChaCha20 używany jest jako CSPRNG:

- **Klucz**: 256 bitów entropii (np. z /dev/urandom)
- **Nonce**: 96 bitów entropii lub deterministyczna wartość
- **Licznik**: Zaczyna od 0, inkrementowany dla każdego bloku
- **Wyjście**: Strumień klucza traktowany jako pseudolosowe bity

Jeden seed (klucz + nonce) może wygenerować $2^{32} \times 512 = 2{,}199{,}023{,}255{,}552$ bitów (~2 terabity) przed wyczerpaniem licznika.

### Warianty ChaCha

#### ChaCha20 (standard)

- 20 rund (10 double-rounds)
- Pełne bezpieczeństwo kryptograficzne
- Standardowy wariant używany w TLS, WireGuard

#### ChaCha12

- 12 rund (6 double-rounds)
- Szybszy przy zachowaniu wysokiego bezpieczeństwa
- Używany w niektórych aplikacjach mobilnych

#### ChaCha8

- 8 rund (4 double-rounds)
- Najszybszy wariant
- Wciąż bardzo bezpieczny dla większości zastosowań

#### XChaCha20

- Rozszerzony nonce do 192 bitów (zamiast 96)
- Umożliwia losowy wybór nonce bez kolizji
- Używany w libsodium

### Kluczowy fragment kodu

```rust
use chacha20::ChaCha20;
use chacha20::cipher::{KeyIvInit, StreamCipher};

fn chacha20_bit_stream(seed: &[u8; 32], nonce: &[u8; 12],
                        n_bits: usize) -> Vec<u8> {
    // Inicjalizacja ChaCha20
    let mut cipher = ChaCha20::new(seed.into(), nonce.into());

    // Oblicz potrzebną liczbę bajtów
    let n_bytes = (n_bits + 7) / 8;
    let mut buffer = vec![0u8; n_bytes];

    // Generuj strumień klucza
    cipher.apply_keystream(&mut buffer);

    // Konwertuj na bity (jeśli potrzebne)
    buffer
}
```

Implementacja w Rust wykorzystuje dedykowaną bibliotekę `chacha20` zapewniającą constant-time operations (ochrona przed timing attacks).

### Zastosowania

**Zastosowania kryptograficzne:**

- **TLS 1.3** – ChaCha20-Poly1305 jako preferowany szyfr na urządzeniach bez AES-NI
- **WireGuard VPN** – używa ChaCha20 dla szyfrowania tuneli
- **SSH** – chacha20-poly1305@openssh.com cipher
- **Signal Protocol** – szyfrowanie wiadomości w komunikatorach (Signal, WhatsApp)
- **Tor** – szyfrowanie obwodów w sieci anonimizującej

**Jako CSPRNG:**

- **Generowanie kluczy kryptograficznych** – klucze AES, RSA, ECDSA
- **Inicjalizacyjne wektory (IV)** – dla szyfrów blokowych
- **Nonce generation** – wartości jednorazowe dla protokołów
- **Salts** – do hashowania haseł (bcrypt, Argon2)
- **Token generation** – tokeny sesji, CSRF tokens

**Zalety nad AES-CTR:**

- **Szybszy na CPU bez AES-NI** – urządzenia mobilne, embedded systems
- **Constant-time** – odporny na timing attacks bez specjalnego sprzętu
- **Prostszy** – łatwiejsza implementacja bez błędów
- **Brak słabych kluczy** – każdy 256-bitowy klucz jest równie dobry

**Ograniczenia:**

- **Wolniejszy niż AES-NI** – na procesorach z akceleracją sprzętową AES
- **Większy kod** – implementacja zajmuje więcej miejsca niż AES
- **Nonce reuse catastrophic** – użycie tego samego (klucz, nonce) dwukrotnie łamie szyfrowanie

### Jakość kryptograficzna

#### Analiza bezpieczeństwa:

**Bezpieczeństwo teoretyczne:**

- **Brak znanych ataków praktycznych** na ChaCha20 (20 rund)
- **7.5 rund ChaCha** łamanych w atakach teoretycznych (margines: 12.5 rund)
- **ChaCha8** wciąż uważany za bezpieczny (margines: 0.5 rund)

**Testy kryptanalityczne:**

- **Differential cryptanalysis**: Brak praktycznych ataków
- **Linear cryptanalysis**: Odporny
- **Algebraic attacks**: Brak postępów
- **Related-key attacks**: Nie dotyczy (brak powiązanych kluczy w praktyce)

**Zalety kryptograficzne:**

1. **256-bitowy klucz**: Odporny na brute-force (nawet dla komputerów kwantowych)
2. **ARX construction**: Prosta, dobrze zbadana konstrukcja
3. **No lookup tables**: Brak cache-timing vulnerabilities
4. **Parallelizable**: Każdy blok niezależny (SIMD, GPU)

### Kontekst historyczny i ciekawostki

**Historia:**

- **2005**: Daniel J. Bernstein projektuje **Salsa20**
- **2008**: **ChaCha** jako ulepszona wersja Salsa20
- **2014**: Google adoptuje ChaCha20-Poly1305 w Chrome/Android (brak AES-NI na ARM)
- **2018**: **RFC 8439** standaryzuje ChaCha20-Poly1305
- **2020**: TLS 1.3 preferuje ChaCha20 na urządzeniach mobilnych

**Motywacja powstania:**

- Potrzeba szybkiego szyfru strumieniowego dla urządzeń bez akceleracji AES
- Salsa20 był dobry, ale ChaCha poprawił dyfuzję (diagonal rounds)
- Alternatywa dla AES unikająca patentów i specjalizowanego sprzętu

**Daniel J. Bernstein:**

- Profesor matematyki i informatyki (University of Illinois Chicago)
- Twórca: Curve25519, Ed25519, NaCl/libsodium
- Znany z projektowania algorytmów odpornych na timing attacks

**Ciekawostki:**

- Nazwa "ChaCha" pochodzi od tańca latynoamerykańskiego (podobnie jak "Salsa")
- **ChaCha20-Poly1305** łączy szyfrowanie (ChaCha20) z uwierzytelnianiem (Poly1305) w AEAD
- Google zaimplementował ChaCha20 w BoringSSL (fork OpenSSL) i kontrybuował do standaryzacji
- WireGuard (Linus Torvalds: "dzieło sztuki") używa wyłącznie ChaCha20 dla szyfrowania
- ChaCha20 jest używany w **>80% połączeń mobilnych TLS** (Chrome, Android)
- Implementacja ChaCha20 w 100 liniach C jest bezpieczna i szybka

### Złożoność obliczeniowa

- **Krok generacji** (512-bitowy blok): $O(1)$ – 80 quarter-rounds × 4 operacje = 320 operacji
- **Pamięć**: $O(1)$ – 64 bajty stanu (16 × 32-bit)
- **Inicjalizacja**: $O(1)$ – ustawienie stanu początkowego

**Szczegółowa analiza:**

- Każdy quarter-round: 4 dodawania + 4 XOR + 4 rotacje = 12 operacji
- 80 quarter-rounds: 960 operacji na 512 bitów = ~1.9 operacji/bit
- Bardzo efektywne dla konstrukcji kryptograficznej

**Wydajność praktyczna:**

- Python (pure): ~10-20 MB/s
- Python (biblioteka C): ~100-200 MB/s
- C (optimized): ~500-800 MB/s
- Rust: ~400-700 MB/s
- Assembly (SIMD): ~2-4 GB/s

**Porównanie z AES:**

- Na CPU bez AES-NI: **ChaCha20 2-3× szybszy**
- Na CPU z AES-NI: **AES 3-4× szybszy**
- Na ARM/mobile: **ChaCha20 dominuje**

### Przykłady obliczeniowe

#### Przykład 1: Quarter-round

Dla wejścia $(a, b, c, d) = (0x11111111, 0x01020304, 0x9b8d6f43, 0x01234567)$:

```
Krok 1: a += b; d ^= a; d <<<= 16
    a = 0x11111111 + 0x01020304 = 0x12131415
    d = 0x01234567 ^ 0x12131415 = 0x13305172
    d = rotl(0x13305172, 16) = 0x51721330

Krok 2: c += d; b ^= c; b <<<= 12
    c = 0x9b8d6f43 + 0x51721330 = 0xecff8273
    b = 0x01020304 ^ 0xecff8273 = 0xedfd8177
    b = rotl(0xedfd8177, 12) = 0xd8177edf

... (2 kolejne kroki)
```

Wynik: Kompletnie zmienione wartości wszystkich 4 słów.

#### Przykład 2: Inicjalizacja stanu

Dla klucza `key = [0x03020100, ..., 0x1f1e1d1c]` i nonce `[0, 0, 0]`:

```
Stan początkowy:
[0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]  // Stałe
[0x03020100, 0x07060504, 0x0b0a0908, 0x0f0e0d0c]  // Klucz (część 1)
[0x13121110, 0x17161514, 0x1b1a1918, 0x1f1e1d1c]  // Klucz (część 2)
[0x00000000, 0x00000000, 0x00000000, 0x00000000]  // Licznik + Nonce
```

#### Przykład 3: Generowanie strumienia PRNG

```rust
// Seed (256-bit klucz)
let key = [0u8; 32];  // Wszystkie zera (tylko dla przykładu!)

// Nonce (96-bit)
let nonce = [0u8; 12];

// Generuj 1000 bitów
let stream = chacha20_rng(&key, &nonce, 1000);

// stream[0..125] zawiera 1000 bitów pseudolosowych
```

**Bezpieczeństwo**: Dla prawdziwego CSPRNG, key musi być 256 bitów entropii z /dev/urandom lub podobnego źródła.

#### Przykład 4: Przestrzeń stanów

- **Klucz**: $2^{256}$ możliwych wartości
- **Nonce**: $2^{96}$ możliwych wartości
- **Licznik**: $2^{32}$ bloków per (klucz, nonce)
- **Całkowita przestrzeń**: $2^{256} \times 2^{96} \times 2^{32} = 2^{384}$ bloków

To daje $2^{393}$ bitów możliwego strumienia.

ChaCha20 reprezentuje nowoczesne podejście do projektowania szyfrów strumieniowych: prostota konstrukcji, wysoka wydajność, udowodnione bezpieczeństwo i odporność na side-channel attacks. Jest to obecnie złoty standard dla szyfrowania na urządzeniach mobilnych i idealny wybór dla CSPRNG w aplikacjach wymagających gwarancji kryptograficznych.
