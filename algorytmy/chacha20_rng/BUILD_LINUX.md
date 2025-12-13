# ChaCha20 RNG - Kompilacja na Linux

## Wymagania

- Rust 1.92.0 lub nowszy (zainstaluj z https://rustup.rs/)
- Kompilator C (gcc/clang) - zazwyczaj preinstalowany na Linux'ie

## Instalacja na Ubuntu/Debian

```bash
# Zainstaluj Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Zainstaluj kompilator C (jeśli nie masz)
sudo apt-get update
sudo apt-get install build-essential
```

## Kompilacja

```bash
# Przejdź do folderu projektu
cd chacha20_rng

# Zbuduj release (zoptymalizowany)
cargo build --release

# Plik wykonywalny będzie w:
# ./target/release/chacha20_rng
```

## Użycie

```bash
# Domyślnie: 200 bitów, 32 bity na wartość, MSB-first
./target/release/chacha20_rng

# Z parametrami: nBits=1000000 bitsPerValue=32 msbFirst=true
./target/release/chacha20_rng 1000000 32 true

# Wynik: JSON z bitami i czasem wykonania
# {"bits":[1,0,1,1,0,1,0,1,...],"time":0.001234}
```

## Cross-platform

Możesz też zbudować dla Android, ARM, itd. używając:

```bash
# Przykład: ARM64 (np. Raspberry Pi 4)
rustup target add aarch64-unknown-linux-gnu
cargo build --release --target aarch64-unknown-linux-gnu
# Wynik: ./target/aarch64-unknown-linux-gnu/release/chacha20_rng
```
