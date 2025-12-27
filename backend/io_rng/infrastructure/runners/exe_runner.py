"""
Executable RNG Runner - uruchamia prekompilowane .exe/.out generatory
"""
import subprocess
import json
from typing import List, Tuple, Any, Dict, Optional
from pathlib import Path

from io_rng.core.entities.rng import RNG, Language
from io_rng.core.entities.test_result import DataType
from io_rng.core.interfaces.rng_runner import IRNGRunner


class ExeRNGRunner(IRNGRunner):
    """
    Runner dla prekompilowanych generatorów (.exe, .out)

    Protokół komunikacji:
    - CLI: ./generator.exe [n_bits] [bits_per_value] [msb_first] [seed?]
    - Output: JSON {"bits": [0,1,0,...], "time": 0.001}
    """

    def can_run(self, rng: RNG) -> bool:
        """Sprawdza czy to executable RNG"""
        return rng.language == Language.EXECUTABLE

    def generate_raw(
        self,
        rng: RNG,
        count: int,
        seed: int = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Any], DataType]:
        """
        Generuje surowe bity wywołując .exe

        Args:
            rng: RNG entity
            count: Liczba bitów
            seed: Opcjonalny seed
            parameters: Nie używane (parametry mogą być wbudowane w .exe)

        Returns:
            (bits, DataType.BITS)
        """
        if not self.can_run(rng):
            raise RuntimeError(f"Cannot run {rng.language.value}")

        # Rozwiąż ścieżkę
        exe_path = self._resolve_path(rng.code_path)

        if not exe_path.exists():
            raise FileNotFoundError(f"Executable not found: {exe_path}")

        # Przygotuj argumenty CLI
        # Format: ./exe [n_bits] [bits_per_value=1] [msb_first=1] [seed?]
        args = [str(exe_path), str(count), "1", "1"]

        if seed is not None:
            args.append(str(seed))

        # Wykonaj
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30,  # 30s timeout
                check=True
            )

            # Parsuj JSON output
            output = json.loads(result.stdout)

            if 'bits' not in output:
                raise ValueError(f"Invalid output format: missing 'bits' field")

            bits = output['bits']

            # Walidacja
            if not isinstance(bits, list):
                raise ValueError(f"'bits' must be a list, got {type(bits)}")

            if len(bits) < count:
                raise ValueError(f"Generated {len(bits)} bits, expected {count}")

            # Obetnij do żądanej liczby
            bits = bits[:count]

            # Walidacja wartości
            if not all(b in [0, 1] for b in bits):
                raise ValueError(f"Invalid bit values (must be 0 or 1)")

            return (bits, DataType.BITS)

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Executable timeout after 30s: {exe_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Executable failed with code {e.returncode}: {e.stderr}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON output from {exe_path}: {e}")

    def generate_numbers(
        self,
        rng: RNG,
        count: int,
        seed: int = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Generuje liczby float [0,1] z bitów.
        """
        bits, data_type = self.generate_raw(rng, count, seed, parameters)

        # Konwertuj bity → floaty (32 bity na liczbę)
        return self._bits_to_floats(bits)

    def _bits_to_floats(self, bits: List[int]) -> List[float]:
        """
        Konwertuje bity na floaty [0,1] - 32 bity na liczbę.
        Kopiowane z PythonRNGRunner dla spójności.
        """
        bits_per_num = 32
        numbers = []
        max_val = (2**bits_per_num) - 1

        for i in range(len(bits) // bits_per_num):
            chunk = bits[i * bits_per_num : (i + 1) * bits_per_num]
            value = sum(bit << (bits_per_num - 1 - j) for j, bit in enumerate(chunk))
            numbers.append(value / max_val)

        return numbers

    def _resolve_path(self, path: str) -> Path:
        """
        Rozwiązuje ścieżkę względną do project root.

        Args:
            path: Ścieżka z bazy (np. "algorytmy/Xorshift256/bin/Xoshiro256.exe")

        Returns:
            Absolutna ścieżka Path
        """
        path_obj = Path(path)

        if path_obj.is_absolute():
            return path_obj

        # Względem project_root (parent of backend/)
        backend_dir = Path(__file__).parent.parent.parent.parent
        project_root = backend_dir.parent

        return project_root / path

    def validate_setup(self, rng: RNG) -> bool:
        """Waliduje czy .exe działa"""
        try:
            bits, _ = self.generate_raw(rng, 100, seed=42)
            return len(bits) >= 100
        except Exception:
            return False
