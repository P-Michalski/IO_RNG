# Nowe funkcje - Quick Start

## 1. Kompresja bitów (oszczędza 94% miejsca)

```bash
# BEZ kompresji (30 KB)
POST /api/rngs/10/generate
{"count": 10000, "seed": 42}

# Z kompresją (2 KB)
POST /api/rngs/10/generate?compressed=true
{"count": 10000, "seed": 42}
```

## 2. Testy Diehard Suite (5 nowych testów)

```bash
POST /api/rngs/10/run_test
{
  "test_name": "diehard_birthday_spacings",
  "samples_count": 500000
}
```

Dostępne testy:
- `diehard_birthday_spacings` (min. 262K bitów)
- `diehard_overlapping_permutations` (min. 1M bitów)
- `diehard_binary_rank` (min. 10K bitów)
- `diehard_bitstream` (min. 2M bitów)
- `diehard_opso` (min. 2M bitów)

## 3. Testowanie własnych bitów (bez zapisu do bazy)

```bash
# Krok 1: Wygeneruj bity
POST /api/rngs/10/generate?compressed=true
{"count": 100000, "seed": 999}

# Krok 2: Testuj wielokrotnie (bez zapisywania w bazie)
POST /api/rngs/test-custom
{
  "bits_compressed": "base64string...",
  "bits_count": 100000,
  "test_name": "nist_monobit"
}
```

## 4. Generatory .exe

Dodaj do bazy:
```python
language = "executable"
code_path = "algorytmy/moj_generator/generator.exe"
```

Generator musi zwracać JSON:
```json
{"bits": [0,1,0,1,...], "time": 0.001}
```

## 5. Optymalizacja bazy danych

**Usunięto pole `generated_bits` z wyników testów:**
- Wyniki testów nie przechowują już surowych danych bitowych w bazie
- Zmniejsza to rozmiar bazy danych i przyspiesza zapytania
- Surowe bity można wygenerować w dowolnym momencie przez endpoint `/api/rngs/{id}/generate`

**Endpoint zwracający wszystkie wyniki testów:**
- `GET /api/test-results` - zwraca teraz **wszystkie** wyniki testów (wcześniej tylko 20)
- Brak limitu pozwala na pełną analizę historii testów
- Frontend może sam filtrować i paginować wyniki według potrzeb
