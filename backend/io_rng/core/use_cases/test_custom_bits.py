"""
Test Custom Bits Use Case
Testuje własne bity bez zapisu do bazy
"""
from typing import Dict, Any, List
import time

from io_rng.core.use_cases.run_rng_test import RunRNGTestUseCase


class TestCustomBitsUseCase:
    """
    Use case do testowania custom bitów bez generatora i zapisu.
    Reużywa logikę testową z RunRNGTestUseCase.
    """

    def __init__(self):
        """Inicjalizacja (nie potrzeba repozytoriów)"""
        pass

    def execute(
        self,
        bits: List[int],
        test_name: str
    ) -> Dict[str, Any]:
        """
        Wykonuje test statystyczny na bitach bez zapisu.

        Args:
            bits: Lista bitów [0,1,0,1,...]
            test_name: Nazwa testu

        Returns:
            Dict z wynikami testu (bez id/rng_id)
        """

        # Walidacja
        if not bits or len(bits) < 100:
            raise ValueError(f"Need at least 100 bits, got {len(bits)}")

        if not all(b in [0, 1] for b in bits):
            raise ValueError("All bits must be 0 or 1")

        # Konwertuj bity → floaty dla testów podstawowych
        numbers = self._bits_to_floats(bits)

        # Wykonaj test używając metody z RunRNGTestUseCase
        # (utworzymy instancję tylko dla dostępu do metod testowych)
        test_executor = RunRNGTestUseCase(
            rng_repository=None,  # Nie potrzebujemy
            result_repository=None,
            runners=[]
        )

        start_time = time.perf_counter()

        try:
            test_result = test_executor._perform_statistical_test(
                numbers=numbers,
                test_name=test_name,
                bits=bits
            )
        except ValueError as e:
            raise ValueError(f"Test failed: {str(e)}")

        execution_time = (time.perf_counter() - start_time) * 1000  # ms

        # Zwróć rezultat (bez zapisu do bazy)
        return {
            'test_name': test_name,
            'passed': test_result['passed'],
            'score': test_result['score'],
            'execution_time_ms': execution_time,
            'samples_count': len(bits),
            'statistics': test_result['statistics']
        }

    def _bits_to_floats(self, bits: List[int]) -> List[float]:
        """
        Konwertuje bity na floaty [0,1] - 32 bity na liczbę.
        Kopiowane z PythonRNGRunner.
        """
        bits_per_num = 32
        numbers = []
        max_val = (2**bits_per_num) - 1

        for i in range(len(bits) // bits_per_num):
            chunk = bits[i * bits_per_num : (i + 1) * bits_per_num]
            value = sum(bit << (bits_per_num - 1 - j) for j, bit in enumerate(chunk))
            numbers.append(value / max_val)

        return numbers
