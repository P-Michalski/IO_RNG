SystemRNG (System Random Number Generator) to interfejs do kryptograficznie bezpiecznych źródeł losowości udostępnianych przez system operacyjny. W przeciwieństwie do deterministycznych generatorów pseudolosowych, SystemRNG czerpie entropię z rzeczywistych źródeł fizycznych i zdarzeń systemowych, zapewniając najwyższą jakość kryptograficzną. Jest to **złoty standard** dla wszystkich zastosowań wymagających nieprzewidywalności i bezpieczeństwa.

### Wyjaśnienie działania

SystemRNG nie jest algorytmem w tradycyjnym sensie – jest to abstrakcja nad mechanizmami zbierania i dostarczania entropii implementowanymi przez jądro systemu operacyjnego.

#### Źródła entropii systemowej

Systemy operacyjne zbierają entropię z wielu źródeł:

**Zdarzenia sprzętowe:**

- Timing przerwań (interrupts) – moment wystąpienia przerwania sprzętowego
- Szum termiczny z urządzeń – fluktuacje napięcia w elementach elektronicznych
- Timing operacji dyskowych – mikro-opóźnienia w operacjach I/O
- Ruch myszy i kliknięcia – timing i pozycje
- Timing naciśnięć klawiszy
- Pakiety sieciowe – timing przybycia, jitter

**Zdarzenia systemowe:**

- Process IDs nowych procesów
- Thread IDs
- Liczniki wydajności CPU (performance counters)
- Timestamp wysoko-rozdzielczy (TSC, RDTSC)
- Identyfikatory obiektów jądra

**Dedykowane źródła sprzętowe:**

- **RDRAND** (Intel/AMD) – instrukcja CPU generująca losowość z DRNG (Digital Random Number Generator)
- **RDSEED** – instrukcja CPU czerpająca z ENRNG (Enhanced NRBG)
- **TPM** (Trusted Platform Module) – dedykowany chip kryptograficzny
- **Hardware RNG** – dedykowane urządzenia (np. /dev/hwrng na Linux)

#### Implementacje systemowe

**Linux/Unix (/dev/urando, /dev/random):**

Jądro Linuxa utrzymuje **entropy pool** – bufor entropii zebranej z różnych źródeł.

**/dev/random** (blocking):

- Blokuje gdy pula entropii jest "wyczerpana"
- Używany historycznie dla krytycznych operacji
- Od Linux 5.6+ zachowanie zmienione

**/dev/urandom** (non-blocking):

- **Nigdy nie blokuje** – zawsze zwraca dane
- Po inicjalizacji: kryptograficznie bezpieczny CSPRNG (ChaCha20 od 5.17+)
- **Zalecany dla wszystkich zastosowań** (włącznie z kluczami)

**Windows (CryptGenRandom, BCryptGenRandom):**

Windows używa **Cryptographic Service Provider (CSP)** / **Cryptography API: Next Generation (CNG)**.

**CryptGenRandom** (stare API):

- Część CryptoAPI
- Używa AES-CTR z seedem z puli entropii

**BCryptGenRandom** (nowoczesne API):

- Część CNG (Cryptography Next Generation)
- Szybszy, bezpieczniejszy
- Domyślnie używa `BCRYPT_USE_SYSTEM_PREFERRED_RNG`

**Źródła entropii Windows:**

- Performance counters (QueryPerformanceCounter)
- Timestamp systemowy
- Process/Thread IDs
- Memory allocations
- CPU thermal noise (jeśli dostępne)
- TPM (jeśli dostępny)

#### Interfejs w Pythonie

Python udostępnia os.urandom() jako międzyplatformowy interfejs:

```python
import os

# Pobierz n bajtów kryptograficznie bezpiecznych
random_bytes = os.urandom(32)  # 256 bitów
```

**Mapowanie per platforma:**

- Linux: `/dev/urandom` lub `getrandom()` syscall
- Windows: `BCryptGenRandom()`
- macOS: `/dev/urandom`

### Kluczowy fragment kodu

```python
def system_random_bit_stream(seed, n_bits, bits_per_value=32):
    """
    Generuje strumień bitów używając systemowego CSPRNG.
    Parametr 'seed' jest ignorowany (dla kompatybilności).
    """
    import os

    # Oblicz potrzebną liczbę bajtów
    num_bytes = (bits_per_value + 7) // 8
    output = []

    while len(output) < n_bits:
        # Pobierz bajty z systemowego źródła
        if sys.platform.startswith('win'):
            # Windows: BCryptGenRandom (przez ctypes)
            raw = bcrypt_gen_random(num_bytes)
        else:
            # Linux/macOS: /dev/urandom
            raw = os.urandom(num_bytes)

        # Konwertuj bajty na liczbę
        val = int.from_bytes(raw, 'big')
        val &= (1 << bits_per_value) - 1

        # Ekstrakcja bitów
        bits = extract_bits(val, bits_per_value, msb_first=True)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Moduł `secrets` – wysokopoziomowe API

Python 3.6+ oferuje `secrets` module – **zalecany interfejs dla aplikacji bezpieczeństwa**:

```python
import secrets

# Generowanie tokenów
token_hex = secrets.token_hex(16)      # 32-znakowy hex
token_urlsafe = secrets.token_urlsafe(32)  # Base64 URL-safe

# Liczby losowe
rand_int = secrets.randbelow(100)       # [0, 100)
rand_bits = secrets.randbits(256)       # 256-bitowa liczba

# Wybór z sekwencji
choice = secrets.choice(['a', 'b', 'c'])
```

Wszystko oparte na `os.urandom()` – gwarancja kryptograficzna.

### Zastosowania

**Zastosowania kryptograficzne:**

- **Generowanie kluczy** – AES, RSA, ECDSA, ChaCha20
- **Inicjalizacyjne wektory (IV)** – dla szyfrów blokowych (AES-CBC, AES-GCM)
- **Nonce generation** – wartości jednorazowe dla protokołów (TLS, IPsec)
- **Salt dla haseł** – bcrypt, scrypt, Argon2, PBKDF2
- **Tokeny sesji** – web applications, authentication tokens
- **CSRF tokens** – ochrona przed cross-site request forgery
- **API keys** – generowanie unikalnych identyfikatorów

**Inne zastosowania:**

- **Gambling/kasyna online** – losowanie gdzie regulacje wymagają "prawdziwej losowości"
- **Losowanie na żywo** – konkursy, loterie
- **Seeding innych generatorów** – inicjalizacja PCG, xoshiro dla deterministycznych symulacji

**Kiedy ZAWSZE używać SystemRNG:**

- Jakiekolwiek zastosowanie kryptograficzne
- Generowanie tajnych wartości (klucze, hasła)
- Bezpieczeństwo aplikacji webowych (tokeny, sesje)
- Gdy nieprzewidywalność jest krytyczna

**Kiedy można użyć PRNG (PCG, MT):**

- Symulacje naukowe (Monte Carlo)
- Gry (nie-gambling)
- Proceduralna generacja treści
- Testy statystyczne

### Jakość i bezpieczeństwo

#### Zalety:

1. **Kryptograficznie bezpieczny** – nieprzewidywalny nawet dla atakującego z wiedzą o systemie
2. **Non-deterministic seed** – wykorzystuje rzeczywiste źródła entropii
3. **Forward secrecy** – stare wartości nie pozwalają przewidzieć nowych
4. **Backward secrecy** – nowe wartości nie pozwalają odtworzyć starych
5. **Standardy FIPS 140-2/3** – implementacje systemowe często certyfikowane

#### Gwarancje bezpieczeństwa:

**Nieprzewidywalność:**

- Atakujący znający algorytm CSPRNG + wszystkie dotychczasowe wyjścia **nie może** przewidzieć następnego bitu z prawdopodobieństwem > 50%
- Wymaga łamania kryptografii (np. ChaCha20, AES)

**Odporność na ataki:**

- **State compromise resilience**: Nawet jeśli atakujący zdobędzie pełny stan CSPRNG, nowa entropię z systemu "naprawia" generator
- **Backtracking resistance**: Kompromitacja stanu nie ujawnia przeszłych wyjść

**Certyfikacje:**

- Linux /dev/urandom: Zgodny z wymaganiami FIPS 140-2
- Windows BCryptGenRandom: Certyfikowany FIPS 140-2 Level 1
- Apple SecRandomCopyBytes: Spełnia Common Criteria EAL4+

### Wydajność

SystemRNG jest **wolniejszy** niż dedykowane PRNG, ale **wystarczająco szybki** dla większości zastosowań.

**Dlaczego wolniejszy?**

- Syscall overhead – przejście user→kernel space
- Operacje na puli entropii
- Synchronizacja wielowątkowa
- Sprawdzanie stanu inicjalizacji

**Optymalizacje:**

- Pobieranie większych buforów (np. 1024 bajtów) zamiast po 4 bajty
- Buforowanie w userspace dla częstych małych żądań
- Dla symulacji: używanie SystemRNG do seeda, potem PRNG

### Kontekst historyczny i ciekawostki

**Ewolucja Linux /dev/random:**

- **1994**: Theodore Ts'o wprowadza /dev/random do Linux 1.3.30
- **2006**: Yarrow algorithm (Bruce Schneier) zastąpiony przez własny design
- **2016**: Kontrowersje o "blokowanie" /dev/random vs /dev/urandom
- **2017-2020**: Seria ulepszeń, migracja na ChaCha20
- **2022**: Linux 5.17 – pełna przepisana implementacja, ChaCha20-based

**Kontrowersja /dev/random vs /dev/urandom:**

- **Mit**: "/dev/random jest bezpieczniejszy"
- **Prawda**: Od ~2013 /dev/urandom jest równie bezpieczny po inicjalizacji
- **Konsensus (2016+)**: **Używaj /dev/urandom dla wszystkiego**
- Linus Torvalds osobiście zalecał /dev/urandom

**Windows CryptoAPI historia:**

- **1996**: CryptoAPI (CryptGenRandom) w Windows NT 4.0
- **2007**: CNG (BCryptGenRandom) w Windows Vista
- **2015**: NSA backdoor w Dual_EC_DRBG (nie używany w Windows, ale wzbudził obawy)
- **2018**: Windows 10 RS5 – улучшения wydajności BCryptGenRandom

**Ciekawostki:**

- FreeBSD używa **Fortuna** (Ferguson & Schneier, 2003) – teoretycznie doskonały CSPRNG
- OpenBSD pionierem **pledge() + unveil()** – ograniczenie dostępu do /dev/urandom
- Android używa /dev/urandom + dodatkowa entropia z sensorów
- iPhone zbiera entropię z **Secure Enclave** – dedykowany koprocesor kryptograficzny
- Niektóre servery mają **hardware RNG PCI cards** dla dodatkowej entropii

**Incydenty bezpieczeństwa:**

- **2006**: Debian OpenSSL bug – słaba entropia przez błąd w kodzie (CVE-2008-0166)
- **2012**: Android Bitcoin wallets – słaba losowość na niektórych urządzeniach, kradzież bitcoinów
- **2013**: Snowden reveals – NSA ingerencja w standardy DRBG (Dual_EC_DRBG)

**Lessons learned:**

- Nigdy nie implementuj własnego CSPRNG
- Zawsze używaj systemowego API
- Sprawdź inicjalizację (szczególnie w early boot / embedded)

### Przykłady użycia

#### Przykład 1: Generowanie klucza AES

```python
import secrets

# 256-bitowy klucz AES
aes_key = secrets.token_bytes(32)
print(aes_key.hex())  # np. '3f7a...'
```

#### Przykład 2: Token sesji

```python
import secrets

# 256-bitowy token (base64 URL-safe)
session_token = secrets.token_urlsafe(32)
print(session_token)  # np. 'dGhlIHNhb...'
```

#### Przykład 3: Salt dla hasła

```python
import secrets
import hashlib

password = "user_password"
salt = secrets.token_bytes(16)  # 128-bitowy salt

# PBKDF2 z solą
hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
```

#### Przykład 4: Seed dla PRNG (deterministyczne symulacje)

```python
import secrets
import random

# Użyj SystemRNG do wygenerowania seeda
seed = secrets.randbits(64)

# Zasil deterministyczny PRNG
rng = random.Random(seed)
# Teraz symulacja jest reprodukowalna z tym seedem
```

#### Przykład 5: Losowanie z listy (kryptograficzne)

```python
import secrets

# Wybór elementu (uniform, cryptographically secure)
items = ['option1', 'option2', 'option3']
chosen = secrets.choice(items)
```

SystemRNG reprezentuje najwyższy poziom jakości losowości dostępny w systemach komputerowych – łączy fizyczne źródła entropii z kryptograficznie bezpiecznymi algorytmami. Jest absolutnie niezbędny dla wszystkich zastosowań związanych z bezpieczeństwem i powinien być domyślnym wyborem gdy nieprzewidywalność jest krytyczna. Zalecane jest unikanie własnych implementacji PRNG na rzecz sprawdzonych, systemowych rozwiązań.
