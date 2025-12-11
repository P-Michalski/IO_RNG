"""
Python RNG Runner - ładuje i uruchamia generatory Python
"""
import importlib.util
import sys
from typing import List, Tuple, Any, Dict, Optional
from pathlib import Path

from io_rng.core.entities.rng import RNG, Language
from io_rng.core.entities.test_result import DataType
from io_rng.core.interfaces.rng_runner import IRNGRunner
from io_rng.infrastructure.runners.universal_adapter import UniversalRNGAdapter


class PythonRNGRunner(IRNGRunner):
    """Runner dla Python RNG - dynamicznie ładuje moduły"""

    def can_run(self, rng: RNG) -> bool:
        """Sprawdza czy to Python RNG"""
        return rng.language == Language.PYTHON

    def generate_raw(
        self,
        rng: RNG,
        count: int,
        seed: int = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Any], DataType]:
        """
        Generuje surowe dane (bity, inty, lub floaty).

        Args:
            rng: RNG entity
            count: Liczba wartości do wygenerowania
            seed: Opcjonalny seed
            parameters: Opcjonalne parametry (override rng.parameters)

        Returns:
            (data, data_type) - surowe dane i ich typ
        """
        if not self.can_run(rng):
            raise RuntimeError(f"Cannot run {rng.language.value}")

        module = self._load_module(rng.code_path)

        # Merge parametrów: rng.parameters < parameters z requesta
        final_parameters = {**(rng.parameters or {}), **(parameters or {})}
        adapter = UniversalRNGAdapter(module, final_parameters)

        return adapter.generate_raw(count, seed)

    def generate_numbers(
        self,
        rng: RNG,
        count: int,
        seed: int = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Generuje liczby float [0,1] z opcjonalnymi parametrami.

        Args:
            rng: RNG entity
            count: Liczba liczb do wygenerowania
            seed: Opcjonalny seed
            parameters: Opcjonalne parametry (override rng.parameters)

        Returns:
            Lista liczb float [0, 1]
        """
        data, data_type = self.generate_raw(rng, count, seed, parameters)

        # Konwertuj do float [0,1] jeśli potrzeba
        if data_type == DataType.FLOATS:
            return data
        elif data_type == DataType.BITS:
            return self._bits_to_floats(data)
        elif data_type == DataType.INTEGERS:
            return self._ints_to_floats(data)

    def _bits_to_floats(self, bits: List[int]) -> List[float]:
        """Konwertuje bity na floaty [0,1] - 32 bity na liczbę"""
        bits_per_num = 32
        numbers = []
        max_val = (2**bits_per_num) - 1

        for i in range(len(bits) // bits_per_num):
            chunk = bits[i * bits_per_num : (i + 1) * bits_per_num]
            value = sum(bit << (bits_per_num - 1 - j) for j, bit in enumerate(chunk))
            numbers.append(value / max_val)

        return numbers

    def _ints_to_floats(self, integers: List[int]) -> List[float]:
        """Konwertuje inty na floaty [0,1]"""
        if not integers:
            return []

        min_val = min(integers)
        max_val = max(integers)

        if min_val == max_val:
            return [0.5] * len(integers)

        return [(x - min_val) / (max_val - min_val) for x in integers]

    def _load_module(self, path: str):
        """Ładuje moduł Python dynamicznie"""
        # If path is just a filename, resolve it relative to project root
        path_obj = Path(path)
        
        if not path_obj.is_absolute():
            # Get project root (parent of backend directory)
            backend_dir = Path(__file__).parent.parent.parent.parent
            project_root = backend_dir.parent
            path_obj = project_root / path
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Module not found: {path_obj}")

        if not path_obj.suffix == '.py':
            raise ValueError(f"Not a Python file: {path_obj}")

        module_name = path_obj.stem
        spec = importlib.util.spec_from_file_location(module_name, str(path_obj))

        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load: {path_obj}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    def validate_setup(self, rng: RNG) -> bool:
        """Waliduje czy generator działa"""
        try:
            data, data_type = self.generate_raw(rng, 10, seed=42)
            return len(data) >= 10 or len(data) >= 320  # 10 liczb lub 320+ bitów
        except:
            return False