"""
Python RNG Runner - Infrastructure
Implementuje uruchamianie RNG napisanych w Pythonie.
"""
import os
import sys
import importlib.util
from typing import List
from io_rng.core.entities.rng import RNG, Language
from io_rng.core.interfaces.rng_runner import IRNGRunner


class PythonRNGRunner(IRNGRunner):
    """
    Runner dla generatorów napisanych w Pythonie.
    Dynamicznie ładuje moduły i uruchamia funkcje generujące.
    """

    def can_run(self, rng: RNG) -> bool:
        """Sprawdza czy to RNG pythonowy"""
        return rng.language == Language.PYTHON

    def generate_numbers(self, rng: RNG, count: int, seed: int = None) -> List[float]:
        """
        Generuje liczby używając pythonowego RNG.

        Oczekiwana struktura modułu RNG:
        - Funkcja generate(count: int, seed: int = None) -> List[float]
        """
        if not self.can_run(rng):
            raise RuntimeError(f"Cannot run {rng.language.value} RNG with Python runner")

        # Załaduj moduł dynamicznie
        module = self._load_module(rng.code_path)

        # Sprawdź czy moduł ma funkcję generate
        if not hasattr(module, 'generate'):
            raise RuntimeError(f"Module {rng.code_path} doesn't have 'generate' function")

        # Wywołaj funkcję
        try:
            numbers = module.generate(count, seed)

            # Walidacja wyników
            if not isinstance(numbers, list):
                raise RuntimeError("generate() must return a list")

            if len(numbers) != count:
                raise RuntimeError(f"Expected {count} numbers, got {len(numbers)}")

            # Sprawdź czy liczby są w zakresie [0, 1]
            for num in numbers:
                if not isinstance(num, (int, float)) or num < 0 or num > 1:
                    raise RuntimeError(f"Invalid number: {num}. Must be in [0, 1]")

            return [float(n) for n in numbers]

        except Exception as e:
            raise RuntimeError(f"Error running RNG: {str(e)}")

    def validate_setup(self, rng: RNG) -> bool:
        """Sprawdza czy moduł może być załadowany"""
        try:
            # Sprawdź czy plik istnieje
            if not os.path.exists(rng.code_path):
                return False

            # Spróbuj załadować moduł
            module = self._load_module(rng.code_path)

            # Sprawdź czy ma wymaganą funkcję
            return hasattr(module, 'generate')

        except Exception:
            return False

    @staticmethod
    def _load_module(path: str):
        """
        Dynamicznie ładuje moduł Pythona z pliku.

        Args:
            path: Ścieżka do pliku .py

        Returns:
            Załadowany moduł
        """
        # Stwórz unikalna nazwę dla modułu
        module_name = os.path.splitext(os.path.basename(path))[0]

        # Załaduj specyfikację modułu
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise RuntimeError(f"Cannot load module from {path}")

        # Stwórz moduł
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        # Wykonaj moduł
        spec.loader.exec_module(module)

        return module
