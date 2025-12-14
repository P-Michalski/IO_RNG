# ChaCha20 (CSPRNG z szyfru strumieniowego)

## Skrót

ChaCha20 to szyfr strumieniowy Daniela J. Bernsteina (2008), powszechnie stosowany w TLS, SSH. Strumień klucza może służyć jako wysokiej jakości CSPRNG.

## Wersja długa

### Wyjaśnienie matematyczne

- ChaCha20 to szyfr strumieniowy oparty o funkcję mieszającą ARX (Add-Rotate-XOR).
- Stan wewnętrzny: macierz 4×4 słów 32-bitowych (512 bitów).
- Inicjalizacja stanu: stałe ChaCha, 256-bitowy klucz, 32-bitowy licznik bloku, 96-bitowy nonce.
- Każdy blok: 20 rund mieszania (po 4 operacje quarter-round na kolumnach i przekątnych).
- Wyjście: XOR stanu początkowego z finalnym stanem → 512 bitów strumienia klucza.
- Do generacji pseudolosowych bitów: strumień klucza traktowany jako źródło entropii, kryptograficznie silne dzięki konstrukcji szyfru.

### Kluczowy fragment kodu

```rust
use chacha20::ChaCha20;
// Inicjalizacja generatora
let key = [0u8; 32];  // 256-bitowy klucz
let nonce = [0u8; 12]; // 96-bitowy nonce
let mut cipher = ChaCha20::new(&key.into(), &nonce.into());
// Generacja strumienia
let mut buffer = vec![0u8; n_bytes];
cipher.apply_keystream(&mut buffer);
// Konwersja na bity
```

### Zastosowania

- **Protokoły kryptograficzne**: TLS 1.3 (ChaCha20-Poly1305), WireGuard VPN, SSH.
- **Kryptografia mobilna**: preferowany na urządzeniach bez akceleracji AES-NI (ARM).
- **CSPRNG**: strumień klucza jako źródło wysokiej jakości pseudolosowości dla kluczy, IV, nonce.
- Szybkość: ~488 Mbits/s w implementacji testowej (Rust), przewyższa AES na CPU bez AES-NI.

### Kontekst i ciekawostki

- Zaprojektowany przez Daniela J. Bernsteina w 2008 roku jako ulepszona wersja Salsa20.
- Redukcja liczby rund z 20 do 8 (ChaCha8) lub 12 (ChaCha12) zwiększa wydajność przy zachowaniu bezpieczeństwa dla większości zastosowań.
- Przyjęty przez Google w 2014 jako alternatywa dla AES w TLS na urządzeniach mobilnych.
- W 2018 standaryzowany w RFC 8439 wraz z AEAD konstrukcją ChaCha20-Poly1305.
- Odporny na ataki typu timing i cache-timing (constant-time implementacje).

### Krótki przykład obliczeniowy

Przykładowa operacja quarter-round (jedna z 80 w pełnym bloku):

```
a += b; d ^= a; d <<<= 16;
c += d; b ^= c; b <<<= 12;
a += b; d ^= a; d <<<= 8;
c += d; b ^= c; b <<<= 7;
```

Dla wejścia \(a=0x11111111, b=0x01020304, c=0x9b8d6f43, d=0x01234567\):

- Po operacjach mieszania wartości ulegają nieodwracalnym transformacjom (diffusion).
