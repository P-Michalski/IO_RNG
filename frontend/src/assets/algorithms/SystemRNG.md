# System RNG (OS entropy)

## Skrót

SystemRNG korzysta z systemowego źródła losowości (np. `/dev/urandom` na Linux, CryptoAPI na Windows). Zapewnia kryptograficzną jakość, ale wydajność zależy od systemu.

## Wersja długa

### Wyjaśnienie matematyczne

- SystemRNG nie jest deterministycznym generatorem pseudolosowym, lecz interfejsem do entropii systemowej.
- Na systemach Unix/Linux wykorzystuje `/dev/urandom` (nieblokujący generator oparty o CSPRNG jądra).
- Na Windows wykorzystuje CryptoAPI lub BCryptGenRandom.
- Każde wywołanie zwraca niezależne, kryptograficznie silne dane losowe pochodzące z puli entropii systemu.
- Brak wzoru rekurencyjnego; źródło wykorzystuje zdarzenia sprzętowe (przerwania, szum termiczny, itp.) do budowy entropii.

### Kluczowy fragment kodu

```python
import os
# Pobranie n bajtów z systemowego źródła entropii
random_bytes = os.urandom(n_bytes)
# Konwersja bajtów na liczby/bity
value = int.from_bytes(random_bytes, 'big')
bits = extract_bits(value, bits_per_value, msb_first)
```

### Zastosowania

- **Kluczowanie kryptograficzne**: generowanie kluczy AES, RSA, salts dla haseł.
- **Nonce i IV**: unikalne wartości inicjalizacyjne w protokołach kryptograficznych (TLS, IPsec).
- **Bezpieczeństwo aplikacji**: tokeny sesji, identyfikatory CSRF.
- Python udostępnia moduł `secrets` (wrapper nad os.urandom) jako zalecane API do celów bezpieczeństwa.

### Kontekst i ciekawostki

- Jakość zależy od implementacji systemu operacyjnego; Linux `/dev/urandom` jest uznawany za bezpieczny od wersji jądra 4.8+.
- Starsze wersje `/dev/random` blokowały wywołania przy niskiej entropii; `/dev/urandom` nigdy nie blokuje, ale po wyczerpaniu puli entropii stosuje CSPRNG (kryptograficznie silny pseudogenerator).
- Na Windows CryptoAPI wykorzystuje wiele źródeł entropii: liczniki wydajności, ID procesów, sygnatury czasowe, szum sprzętowy.
- Wydajność jest zazwyczaj niższa niż dedykowanych generatorów (Mersenne Twister, PCG), ale jakość kryptograficzna jest gwarantowana.

### Krótki przykład obliczeniowy

Wywołanie `os.urandom(4)` może zwrócić bajty `[0xA3, 0x5F, 0x12, 0xC8]`.

- Interpretacja jako 32-bitowa liczba big-endian: $0xA35F12C8 = 2741949128$.
- Ekstrakcja bitów (MSB-first): `10100011 01011111 00010010 11001000`.
