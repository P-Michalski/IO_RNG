# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Backend Django REST API dla systemu testowania generatorów liczb losowych (RNG). Projekt implementuje Clean Architecture z wyraźnym podziałem na warstwy: core (domain), infrastructure, i API.

## Architecture

### Clean Architecture Layers

1. **Core Layer** (`io_rng/core/`)
   - `entities/` - Domain models (RNG, TestResult, DataType enum)
   - `interfaces/` - Abstract interfaces (IRNGRunner, IRNGRepository, ITestResultRepository)
   - `use_cases/` - Business logic (RunRNGTestUseCase, CompareRNGsUseCase, GetTestResultsUseCase)

2. **Infrastructure Layer** (`io_rng/infrastructure/`)
   - `models.py` - Django ORM models (RNGModel, TestResultModel)
   - `repositories/` - Concrete repository implementations (DjangoRNGRepository, DjangoTestResultRepository)
   - `runners/` - RNG runner implementations (PythonRNGRunner, CppRNGRunner, JavaRNGRunner)
   - `runners/universal_adapter.py` - Auto-detects generator functions and handles different generator signatures

3. **API Layer** (`io_rng/api/`)
   - `views.py` - Django REST Framework ViewSets (RNGViewSet, TestResultViewSet)
   - `serializers.py` - DRF serializers
   - `urls.py` - API routes

### Key Design Patterns

**Dependency Injection**: ViewSets instantiate repositories and runners, passing them to use cases. This allows easy testing and swapping implementations.

**Repository Pattern**: All database access goes through repository interfaces defined in core layer.

**Adapter Pattern**: `UniversalRNGAdapter` detects generator function signatures automatically:
- Handles `generate()` or `*_bit_stream()` functions
- Auto-detects data types (bits, integers, floats)
- Supports parametric generators (LCG, AWCG) with custom parameters

**Use Case Pattern**: Business logic isolated in use cases (e.g., `RunRNGTestUseCase`):
1. Fetch RNG from repository
2. Find appropriate runner for language
3. Generate numbers using runner
4. Perform statistical test
5. Save result to repository

## Database

- **SQLite** database (`db.sqlite3`)
- Two main tables: `rngs` and `test_results`
- RNG paths are stored as relative filenames, resolved at runtime by runners

## Common Commands

### Development Server
```bash
python manage.py runserver
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Update RNG Paths (after moving generator files)
```bash
python update_paths.py
```

### Django Shell (for testing)
```bash
python manage.py shell
```

### Create Superuser
```bash
python manage.py createsuperuser
```

## API Endpoints

**Note**: URLs work both with and without trailing slash (e.g., `/api/rngs/1` and `/api/rngs/1/` are both valid).

### RNG Management
- `GET /api/rngs` - List all RNGs
- `POST /api/rngs` - Create new RNG
- `GET /api/rngs/{id}` - Get RNG details
- `PUT /api/rngs/{id}` - Update RNG
- `DELETE /api/rngs/{id}` - Delete RNG
- `POST /api/rngs/{id}/generate` - **NEW**: Generate raw bits without testing (returns bits array + execution time)
- `POST /api/rngs/{id}/run_test` - Run statistical test on RNG
- `GET /api/rngs/{id}/test_results` - Get test results for RNG

### Test Results
- `GET /api/test-results` - List recent test results (paginated)
- `GET /api/test-results/{id}` - Get specific test result
- `DELETE /api/test-results/{id}` - **NEW**: Delete test result

## RNG Runner System

Runners are responsible for executing generator code in different languages:

1. **PythonRNGRunner** - Dynamically imports Python generator modules
2. **CppRNGRunner** - Compiles and executes C++ generators (TODO)
3. **JavaRNGRunner** - Compiles and executes Java generators (TODO)

Each runner:
- Implements `IRNGRunner` interface
- Uses `UniversalRNGAdapter` to handle different generator signatures
- Converts raw data (bits/integers) to floats [0,1] for statistical tests
- Resolves relative `code_path` to absolute path based on language conventions

## Statistical Tests

Implemented in `RunRNGTestUseCase`:

### Basic Tests (operate on floats)
1. **frequency_test** - Chi-square test checking uniform distribution across bins
2. **uniformity_test** - Mean and variance test (mean ≈ 0.5, variance ≈ 1/12)

### Complete NIST Test Suite (15 tests - all operate on bits)
3. **nist_monobit** - Monobit Test - checks balance of 0s and 1s
4. **nist_block_frequency** - Block Frequency - checks local balance in blocks
5. **nist_runs** - Runs Test - checks number of transitions
6. **nist_longest_run** - Longest Run - checks longest sequences of 1s
7. **nist_matrix_rank** - Binary Matrix Rank - checks linear independence
8. **nist_dft** - Spectral (DFT) - detects periodic patterns
9. **nist_non_overlapping_template** - Non-Overlapping Template - searches for specific patterns
10. **nist_overlapping_template** - Overlapping Template - searches for overlapping 111...1 patterns
11. **nist_universal** - Maurer's Universal - measures compressibility
12. **nist_linear_complexity** - Linear Complexity - measures LFSR complexity (Berlekamp-Massey)
13. **nist_serial** - Serial Test - checks m-bit pattern frequencies
14. **nist_approximate_entropy** - Approximate Entropy - measures pattern predictability
15. **nist_cumulative_sums** - Cumulative Sums - checks systematic bias
16. **nist_random_excursions** - Random Excursions - analyzes random walk cycles
17. **nist_random_excursions_variant** - Random Excursions Variant - random walk with more states

All NIST tests return p-values and use 0.01 significance level.

**Note**: Tests 16-17 (Random Excursions) require ~10,000+ bits to achieve minimum 500 cycles.

Results include:
- `passed` (bool) - Whether test passed critical threshold
- `score` (0-1) - Quality score, 1.0 = perfect
- `statistics` (dict) - Detailed test metrics (p-value, test-specific stats)
- `generated_bits` (list) - **NEW**: Raw bit sequence used in test

## Generate Endpoint

The `/api/rngs/{id}/generate/` endpoint allows generating raw bits without running statistical tests:

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

This is useful for:
- Getting raw bit sequences for external analysis
- Benchmarking generator performance
- Collecting data for visualization

## Frontend Integration

CORS configured for Vite dev server at `localhost:5173` and `127.0.0.1:5173`.

## Important Notes

- Generator `code_path` is stored as relative filename only (e.g., `lcg.py`), resolved by runner implementations
- Parameters for parametric generators (LCG: a/c/m, AWCG: r/s/base) can be passed in POST request or stored in RNG.parameters
- All number generation flows through `UniversalRNGAdapter.generate_raw()` which returns `(data, DataType)`
- **Test results now include `generated_bits` field** containing the raw bit sequence used in the test
- Statistical tests: Basic tests (frequency, uniformity) operate on floats; NIST tests operate directly on bits
- Delete endpoint available for cleaning up old test results
