"""
Test sprawdzający czy system poprawnie resolve'uje ścieżki do algorytmów
"""
from pathlib import Path

# Symulacja logiki z PythonRNGRunner._load_module
test_path = "algorytmy/LCG.py"
path_obj = Path(test_path)

print(f"Test path: {test_path}")
print(f"Is absolute: {path_obj.is_absolute()}")

if not path_obj.is_absolute():
    # Symulacja: __file__ byłby w backend/io_rng/infrastructure/runners/python_runner.py
    # Więc symulujemy tę ścieżkę
    current_file = Path(__file__)  # test_path_resolution.py w backend/
    backend_dir = current_file.parent  # backend/
    project_root = backend_dir.parent  # IO_RNG/

    print(f"\nBackend dir: {backend_dir}")
    print(f"Project root: {project_root}")

    resolved_path = project_root / test_path
    print(f"Resolved path: {resolved_path}")
    print(f"Exists: {resolved_path.exists()}")

    if resolved_path.exists():
        print("\n✓ Ścieżka została poprawnie resolve'owana!")
    else:
        print("\n✗ Błąd: Plik nie istnieje pod resolved path")
