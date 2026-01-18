# RNG Testing Platform - Backend API

Django REST API dla systemu testowania generatorów liczb losowych (RNG). Projekt implementuje Clean Architecture z wyraźnym podziałem na warstwy: core (domain), infrastructure, i API.

## 📋 Spis Treści

- [Architektura](#architektura)
- [Szybki Start](#szybki-start)
- [API Endpoints](#api-endpoints)
- [Testy Statystyczne](#testy-statystyczne)
- [Generatory RNG](#generatory-rng)
- [Nowe Funkcje](#nowe-funkcje)
- [Konfiguracja](#konfiguracja)

---

## 🏗️ Architektura

### Clean Architecture - 3 Warstwy

#### 1. Core Layer (`io_rng/core/`)
**Domain models i business logic**

- `entities/` - Domain models (RNG, TestResult, DataType enum)
- `interfaces/` - Abstract interfaces (IRNGRunner, IRNGRepository, ITestResultRepository)
- `use_cases/` - Business logic (RunRNGTestUseCase, CompareRNGsUseCase, GetTestResultsUseCase)

#### 2. Infrastructure Layer (`io_rng/infrastructure/`)
**Implementacje techniczne**

- `models.py` - Django ORM models (RNGModel, TestResultModel)
- `repositories/` - Concrete repository implementations
- `runners/` - RNG runner implementations (Python, C++, Java, Executable)
- `runners/universal_adapter.py` - Auto-detects generator functions

#### 3. API Layer (`io_rng/api/`)
**REST API interface**

- `views.py` - Django REST Framework ViewSets
- `serializers.py` - DRF serializers
- `urls.py` - API routes

### Design Patterns

- **Dependency Injection** - ViewSets instantiate dependencies and pass to use cases
- **Repository Pattern** - All database access through repository interfaces
- **Adapter Pattern** - UniversalRNGAdapter detects generator signatures automatically
- **Use Case Pattern** - Business logic isolated in use cases

---

## 🚀 Szybki Start

### Instalacja

```bash
# 1. Utworz virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# lub
venv\Scripts\activate     # Windows

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Wykonaj migracje
python manage.py migrate

# 4. Uruchom serwer deweloperski
python manage.py runserver
```

API dostępne pod: `http://localhost:8000/api/`

### Podstawowe Komendy

```bash
# Serwer deweloperski
python manage.py runserver

# Migracje bazy danych
python manage.py makemigrations
python manage.py migrate

# Django shell (testowanie)
python manage.py shell

# Utworzenie superusera
python manage.py createsuperuser
```

---

## 📡 API Endpoints

**Uwaga**: URLs działają z i bez trailing slash (`/api/rngs/1` i `/api/rngs/1/`)

### RNG Management

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `GET` | `/api/rngs` | Lista wszystkich generatorów |
| `POST` | `/api/rngs` | Utworzenie nowego generatora |
| `GET` | `/api/rngs/{id}` | Szczegóły generatora |
| `PUT` | `/api/rngs/{id}` | Aktualizacja generatora |
| `DELETE` | `/api/rngs/{id}` | Usunięcie generatora |
| `POST` | `/api/rngs/{id}/generate` | Generowanie surowych bitów |
| `POST` | `/api/rngs/{id}/run_test` | Uruchomienie testu statystycznego |
| `GET` | `/api/rngs/{id}/test_results` | Wyniki testów dla generatora |

### Test Results

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `GET` | `/api/test-results` | Wszystkie wyniki testów |
| `GET` | `/api/test-results/{id}` | Konkretny wynik testu |
| `DELETE` | `/api/test-results/{id}` | Usunięcie wyniku |

### Custom Testing

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `POST` | `/api/rngs/test-custom` | Testowanie własnych bitów (bez zapisu) |

---

## 📊 Testy Statystyczne

### Implementacja NIST SP800-22

**Wszystkie testy NIST używają profesjonalnej biblioteki `nistrng` v1.2.3**

- ✅ Certyfikowana implementacja NIST SP800-22
- ✅ Wszystkie 15 testów z oryginalnej specyfikacji
- ✅ Automatyczna detekcja typów danych (bits/integers/floats)
- ✅ P-values i szczegółowe statystyki

### Basic Tests (operate on floats)

1. **frequency_test** - Chi-square test sprawdzający równomierny rozkład
2. **uniformity_test** - Test średniej i wariancji (mean ≈ 0.5, var ≈ 1/12)

### NIST Test Suite (15 tests - operate on bits)

| # | Test Name | Opis | Min. Bity |
|---|-----------|------|-----------|
| 3 | `nist_monobit` | Balans 0s i 1s | 100 |
| 4 | `nist_block_frequency` | Lokalna balans w blokach | 100 |
| 5 | `nist_runs` | Liczba przejść | 100 |
| 6 | `nist_longest_run` | Najdłuższe sekwencje 1s | 128 |
| 7 | `nist_matrix_rank` | Niezależność liniowa | 1,024 |
| 8 | `nist_dft` | Wykrywanie wzorców okresowych | 100 |
| 9 | `nist_non_overlapping_template` | Wyszukiwanie wzorców | 1,000 |
| 10 | `nist_overlapping_template` | Nakładające się wzorce 111...1 | 1,032 |
| 11 | `nist_universal` | Kompresowność (Maurer) | 387,840 |
| 12 | `nist_linear_complexity` | Złożoność LFSR (Berlekamp-Massey) | 100,000 |
| 13 | `nist_serial` | Częstość m-bitowych wzorców | 100 |
| 14 | `nist_approximate_entropy` | Przewidywalność wzorców | 100 |
| 15 | `nist_cumulative_sums` | Systematyczny bias | 100 |
| 16 | `nist_random_excursions` | Analiza cykli random walk | 10,000+ |
| 17 | `nist_random_excursions_variant` | Random walk - więcej stanów | 10,000+ |

**Uwaga**: Testy 16-17 wymagają ~10,000+ bitów dla minimum 500 cykli.

### Diehard Test Suite (15 tests)

| # | Test Name | Opis | Min. Bity |
|---|-----------|------|-----------|
| 18 | `diehard_birthday_spacings` | Kolizje wartości | 262,144 |
| 19 | `diehard_overlapping_permutations` | Permutacje 5 wartości | 1,048,576 |
| 20 | `diehard_binary_rank` | Ranga macierzy 32×32 | 10,240 |
| 21 | `diehard_bitstream` | Nakładające się 20-bitowe słowa | 2,097,152 |
| 22 | `diehard_opso` | Overlapping-Pairs-Sparse-Occupancy | 2,097,152 |
| 23 | `diehard_oqso` | Overlapping-Quadruples-Sparse-Occupancy | 2,097,152 |
| 24 | `diehard_dna` | Wzorce 10-literowych słów DNA | 2,097,152 |
| 25 | `diehard_count_1s` | Test zliczania jedynek w bajtach | 2,097,152 |
| 26 | `diehard_parking_lot` | Test parkowania na siatce 100×100 | 98,304 |
| 27 | `diehard_squeeze` | Test "ściskania" liczb | 100,000 |
| 28 | `diehard_runs` | Test sekwencji rosnących/malejących | 100,000 |
| 29 | `diehard_craps` | Symulacja gry w craps | 200,000 |
| 30 | `diehard_minimum_distance` | Minimalna odległość między punktami | 8,000 |
| 31 | `diehard_3dspheres` | Minimalna odległość w 3D | 1,000,000 |
| 32 | `diehard_overlapping_sums` | Sumy nakładających się bajtów | 100,000 |

### Format Wyników

Każdy wynik testu zawiera:
```json
{
  "passed": true,
  "score": 0.8542,
  "statistics": {
    "p_value": 0.854278,
    "threshold": 0.01,
    "chi_square": 12.45,
    ...
  }
}
```

- `passed` (bool) - Czy test przeszedł próg krytyczny
- `score` (0-1) - Ocena jakości, 1.0 = doskonały
- `statistics` (dict) - Szczegółowe metryki (p-value, statystyki specyficzne dla testu)

---

## 🎲 Generatory RNG

### System Runnerów

Runners odpowiadają za wykonywanie kodu generatora w różnych językach:

| Runner | Język | Status | Opis |
|--------|-------|--------|------|
| `PythonRNGRunner` | Python | ✅ | Dynamiczne importowanie modułów |
| `ExeRNGRunner` | Executable | ✅ | Prekompilowane binaria (.exe/native) |
| `CppRNGRunner` | C++ | 🚧 | TODO: Kompilacja i wykonanie |
| `JavaRNGRunner` | Java | 🚧 | TODO: Kompilacja i wykonanie |

### Executable Generators (Cross-Platform)

**Automatyczna konfiguracja ścieżek** przez migrację `0006_fix_executable_paths_for_os.py`:

- **Windows**: Używa `.exe` plików z `bin/` lub `target/release/`
- **Linux/macOS**: Używa natywnych executable (bez `.exe`)

Aktualnie skonfigurowane generatory:
- **ChaCha20** (Rust): `algorytmy/chacha20_rng/target/release/chacha20_rng[.exe]`
- **Xoshiro256** (C# .NET 9.0): `algorytmy/Xorshift256/bin/[Release/net9.0/]Xoshiro256[.exe]`

Migracja uruchamia się automatycznie podczas `python manage.py migrate`.

### Universal Adapter

`UniversalRNGAdapter` automatycznie wykrywa:
- Funkcje `generate()` lub `*_bit_stream()`
- Typy danych (bits, integers, floats)
- Generatory parametryczne (LCG, AWCG) z custom parametrami

### Dodawanie Własnego Generatora

#### Python Generator

```python
# algorytmy/moj_generator.py
def generate(seed=None):
    """Generator function"""
    if seed:
        random.seed(seed)
    while True:
        yield random.random()
```

Dodaj do bazy:
```json
{
  "name": "Moj Generator",
  "language": "python",
  "code_path": "algorytmy/moj_generator.py",
  "description": "Opis generatora"
}
```

#### Executable Generator

Generator musi zwracać JSON na stdout:
```json
{"bits": [0,1,0,1,...], "time": 0.001}
```

Dodaj do bazy:
```json
{
  "name": "Custom Generator",
  "language": "executable",
  "code_path": "algorytmy/custom/generator.exe"
}
```

---

## 🆕 Nowe Funkcje

### 1. Kompresja Bitów (oszczędza 94% miejsca)

```bash
# BEZ kompresji (30 KB)
POST /api/rngs/10/generate
{"count": 10000, "seed": 42}

# Z kompresją base64 (2 KB)
POST /api/rngs/10/generate?compressed=true
{"count": 10000, "seed": 42}
```

Zwraca:
```json
{
  "bits_compressed": "base64string...",
  "bits_count": 10000,
  "compression_ratio": 0.94
}
```

### 2. Testowanie Własnych Bitów (bez zapisu w bazie)

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

Przydatne do:
- Eksperymentowania z różnymi testami
- Analizy zewnętrznych danych
- Walidacji bez zanieczyszczania bazy

### 3. Optymalizacja Bazy Danych

**Usunięto pole `generated_bits` z wyników testów:**
- Wyniki nie przechowują już surowych bitów
- Zmniejsza rozmiar bazy i przyspiesza zapytania
- Surowe bity można wygenerować w każdej chwili przez `/api/rngs/{id}/generate`

**Endpoint zwracający wszystkie wyniki:**
- `GET /api/test-results` - zwraca **wszystkie** wyniki (wcześniej tylko 20)
- Brak limitu pozwala na pełną analizę historii
- Frontend może sam filtrować i paginować

### 4. Rozszerzony Test Suite

**Diehard Suite** - 15 dodatkowych testów:
- Birthday Spacings
- Overlapping Permutations
- Binary Rank (31x31 i 32x32)
- Bitstream
- OPSO/OQSO/DNA
- Count 1s Stream
- Parking Lot
- Squeeze
- Runs (up/down)
- Craps
- Minimum Distance (2D/3D)
- Overlapping Sums

### 5. Generate Endpoint

Generowanie surowych bitów bez testowania:

**Request:**
```json
{
  "count": 10000,
  "seed": 42,
  "parameters": {"a": 1103515245, "c": 12345}
}
```

**Response:**
```json
{
  "bits": [0, 1, 1, 0, ...],
  "count": 10000,
  "execution_time_ms": 15.3,
  "rng_id": 1,
  "rng_name": "LCG",
  "seed": 42
}
```

Przydatne do:
- Pobierania surowych sekwencji bitów
- Benchmarkingu wydajności
- Zbierania danych do wizualizacji

---

## ⚙️ Konfiguracja

### Baza Danych

- **SQLite** (`db.sqlite3`)
- Dwie główne tabele: `rngs` i `test_results`
- Ścieżki RNG przechowywane jako względne nazwy plików

### Frontend Integration

CORS skonfigurowane dla Vite dev server:
- `localhost:5173`
- `127.0.0.1:5173`

### Wymagania

```
Django==5.2.8
djangorestframework==3.15.2
django-cors-headers==4.6.0
nistrng==1.2.3
numpy>=1.24.0
scipy>=1.10.0
```

### Environment Variables

Opcjonalne zmienne środowiskowe:

```bash
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (domyślnie SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## 📈 Wydajność

### Benchmarki Testów (100,000 bitów)

| Generator | Typ | Średni Czas | Ocena |
|-----------|-----|-------------|-------|
| ChaCha20 | Rust | ~36ms | ⚡ Bardzo szybki |
| Python Random | Python | ~16ms | ⚡ Bardzo szybki |
| Xoshiro256 | C# .NET | ~215ms | 🐢 Wolniejszy |
| LCG | Python | ~17ms | ⚡ Bardzo szybki |

### Statystyki Kodu

| Metryka | Wartość |
|---------|---------|
| Linie kodu (backend) | ~2,500 |
| Testy statystyczne | 32 |
| Supported RNG types | 4 (Python, C++, Java, Executable) |
| API endpoints | 10 |

---

## 🔍 Ważne Uwagi

- Generator `code_path` przechowywany jako względna nazwa pliku (np. `lcg.py`)
- Parametry dla generatorów parametrycznych (LCG: a/c/m, AWCG: r/s/base) można przekazać w POST request lub w `RNG.parameters`
- Wszystka generacja liczb przechodzi przez `UniversalRNGAdapter.generate_raw()` który zwraca `(data, DataType)`
- Testy podstawowe (frequency, uniformity) operują na floatach
- Testy NIST i Diehard operują bezpośrednio na bitach
- Endpoint DELETE dostępny dla czyszczenia starych wyników testów

---

## 📚 Dodatkowe Zasoby

- [NIST SP 800-22 Specification](https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final)
- [Diehard Tests Description](https://en.wikipedia.org/wiki/Diehard_tests)
- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---



