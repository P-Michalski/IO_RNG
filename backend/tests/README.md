# Testy Backend IO_RNG

System testów dla backendu aplikacji IO_RNG.

## Struktura

```
tests/
├── unit/              # Testy jednostkowe (encje, pure functions)
├── integration/       # Testy integracyjne (use cases, repozytoria)
└── api/              # Testy endpointów REST API
```

## Uruchomienie testów

### Instalacja zależności

```bash
pip install -r requirements-dev.txt
```

### Podstawowe komendy

```bash
# Wszystkie testy
pytest

# Tylko testy jednostkowe
pytest tests/unit/

# Tylko testy API
pytest tests/api/

# Z coverage
pytest --cov=io_rng --cov-report=html

# Parallel execution
pytest -n 4

# Verbose mode
pytest -v

# Stop na pierwszym błędzie
pytest -x
```

## Markery

Testy można oznaczać markerami:

- `@pytest.mark.unit` - Testy jednostkowe
- `@pytest.mark.integration` - Testy integracyjne
- `@pytest.mark.api` - Testy API
- `@pytest.mark.slow` - Wolne testy

Przykład użycia:

```bash
pytest -m unit  # Tylko testy jednostkowe
pytest -m "not slow"  # Pomijaj wolne testy
```

## Pokrycie testami

Cel: **>80% pokrycia kodu**

Obecny stan: **89.4%**

## Zasady pisania testów

### F.I.R.S.T.

- **F**ast - Szybkie wykonanie (<100ms)
- **I**ndependent - Niezależne od siebie
- **R**epeatable - Powtarzalne w każdym środowisku
- **S**elf-validating - Automatyczne sprawdzanie
- **T**imely - Pisane przed/z kodem

### Konwencje nazewnictwa

- Pliki: `test_*.py` lub `*_test.py`
- Klasy: `Test*` (np. `TestRNGEntity`)
- Funkcje: `test_*` (np. `test_create_rng_with_valid_data`)

### Struktura testu

```python
def test_feature_with_scenario():
    """Test opisu"""
    # Arrange - przygotowanie
    data = prepare_test_data()
    
    # Act - wykonanie
    result = function_under_test(data)
    
    # Assert - weryfikacja
    assert result == expected_value
```

## Dokumentacja

Pełna dokumentacja testów dostępna w `docs/tests.tex`.

## CI/CD

Testy są automatycznie uruchamiane przy każdym push/pull request przez GitHub Actions.
