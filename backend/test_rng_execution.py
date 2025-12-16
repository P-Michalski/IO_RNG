"""
Test wykonania algorytmu przez backend
"""
import sys
from pathlib import Path

# Dodaj backend do PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import z backendu
from io_rng.core.entities.rng import RNG, Language
from io_rng.infrastructure.runners.python_runner import PythonRNGRunner

# Test algorytmu LCG
print("=== Test wykonania algorytmu LCG ===\n")

# Parametry GLIBC-like dla LCG
lcg_params = {
    'a': 1103515245,
    'c': 12345,
    'm': 2**31,
    'bits_per_value': 31
}

rng = RNG(
    id=3,
    name="LCG",
    language=Language.PYTHON,
    algorithm="LCG",
    description="Linear Congruential Generator",
    code_path="algorytmy/LCG.py",
    is_active=True,
    parameters=lcg_params
)

runner = PythonRNGRunner()

try:
    print(f"RNG: {rng.name}")
    print(f"Path: {rng.code_path}")
    print(f"Can run: {runner.can_run(rng)}")

    # Generuj 10 bitów
    data, data_type = runner.generate_raw(rng, count=100, seed=42)

    print(f"\nWygenerowano {len(data)} wartości")
    print(f"Typ danych: {data_type}")
    print(f"Pierwsze 20 wartości: {data[:20]}")

    print("\n✓ Backend działa poprawnie z nowymi ścieżkami!")

except Exception as e:
    print(f"\n✗ Błąd: {e}")
    import traceback
    traceback.print_exc()
