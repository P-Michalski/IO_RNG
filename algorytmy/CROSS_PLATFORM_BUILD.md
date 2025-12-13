# Kompilacja Generatorów RNG dla Różnych Platform

## Status Kompilacji

### ✅ Xorshift256 (C#) - Gotowy na obie platformy

**Windows:**

```bash
Xorshift256\bin\Release\net9.0\win-x64\publish\Xoshiro256.exe <seed> <n_bits>
```

**Linux:**

```bash
Xorshift256/bin/Release/net9.0/linux-x64/publish/Xoshiro256 <seed> <n_bits>
```

### ✅ ChaCha20 (Rust) - Windows gotowy, Linux: instrukcje poniżej

**Windows:**

```bash
chacha20_rng\target\release\chacha20_rng.exe <seed> <n_bits>
```

**Linux - Instrukcje kompilacji:**

Kolega na Linux'ie powinien wykonać w folderze `chacha20_rng/`:

```bash
# 1. Zainstaluj Rust (jeśli nie masz)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 2. Zainstaluj kompilator C (na Debian/Ubuntu)
sudo apt-get install build-essential

# 3. Skompiluj
cargo build --release

# 4. Użyj
./target/release/chacha20_rng 1000000 32 true
```

## Alternatywa: GitHub Actions CI/CD

Aby zautomatyzować builda na Linux'ie, mogę dodać GitHub Actions workflow.
Wymagane: pushuj projekt na GitHub, a workflow sam będzie budować dla Linux'a i uploaddować artefakty.

## Testowanie Kompilowanych Binariów

Po skompilowaniu, wszystkie generatory mogą być testowane przy użyciu:

```bash
python tester.py --benchmark 10000000
```

Zaktualizuj ścieżkę do `chacha20_rng` w `tester.py` jeśli uruchamiasz na Linux'ie.
