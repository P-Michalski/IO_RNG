"""
Universal Adapter - automatycznie wykrywa i adaptuje generatory
"""
from typing import List, Tuple, Any, Dict, Optional
import inspect
import time
from io_rng.core.entities.test_result import DataType


class UniversalRNGAdapter:
    """
    Automatycznie wykrywa generator i zwraca surowe dane.
    Obsługuje parametry dla generatorów takich jak LCG, AWCG.
    """

    def __init__(self, module, parameters: Optional[Dict[str, Any]] = None):
        self.module = module
        self.parameters = parameters or {}
        self.generator_func = self._detect_generator_function()
        self.generator_type = self._detect_generator_type()

    def _detect_generator_function(self):
        """Znajduje główną funkcję generatora"""
        # Priority 1: generate()
        if hasattr(self.module, 'generate'):
            return self.module.generate

        # Priority 2: *_bit_stream()
        for name in dir(self.module):
            if name.endswith('_bit_stream') and not name.startswith('_'):
                func = getattr(self.module, name)
                if callable(func):
                    return func

        raise RuntimeError("No generator function found")

    def _detect_generator_type(self) -> DataType:
        """Wykrywa jaki typ danych zwraca generator"""
        func_name = self.generator_func.__name__

        if func_name.endswith('_bit_stream'):
            return DataType.BITS
        elif func_name == 'generate':
            # Spróbuj wygenerować 1 próbkę i sprawdź
            try:
                test = self.generator_func(1, seed=42)
                if isinstance(test[0], int) and test[0] in [0, 1]:
                    return DataType.BITS
                elif isinstance(test[0], int):
                    return DataType.INTEGERS
                else:
                    return DataType.FLOATS
            except:
                return DataType.FLOATS  # Domyślnie

        return DataType.FLOATS

    def generate_raw(self, count: int, seed: int = None) -> Tuple[List[Any], DataType]:
        """
        Generuje surowe dane BEZ konwersji.

        Returns:
            (data, data_type) - surowe dane i ich typ
        """
        if seed is None:
            import random
            seed = random.randint(1, 2**31 - 1)

        if self.generator_type == DataType.BITS:
            data = self._generate_bits(count, seed)
            return data, DataType.BITS
        else:
            # Wywołaj standardową funkcję
            data = self._call_standard(count, seed)

            # Wykryj typ na podstawie pierwszego elementu
            if data and isinstance(data[0], int):
                if data[0] in [0, 1]:
                    return data, DataType.BITS
                else:
                    return data, DataType.INTEGERS
            else:
                return data, DataType.FLOATS

    def _generate_bits(self, count: int, seed: int) -> List[int]:
        """Generuje bity z *_bit_stream funkcji"""
        func_name = self.generator_func.__name__

        # Specjalna obsługa dla LCG z parametrami
        if func_name == 'lcg_bit_stream' and self.parameters:
            a = self.parameters.get('a', 1103515245)
            c = self.parameters.get('c', 12345)
            m = self.parameters.get('m', 2**31)
            bits_per_value = self.parameters.get('bits_per_value', 31)

            try:
                result = self.generator_func(seed, a, c, m, count,
                                           bits_per_value=bits_per_value,
                                           return_time=False)
            except TypeError:
                result = self.generator_func(seed, a, c, m, count)

            if isinstance(result, tuple):
                return result[0]
            return result

        # Specjalna obsługa dla AWCG z parametrami
        if func_name == 'awcg_bit_stream' and self.parameters:
            r = self.parameters.get('r', 24)
            s = self.parameters.get('s', 10)
            base = self.parameters.get('base', 2**32)
            bits_per_value = self.parameters.get('bits_per_value', 32)

            try:
                result = self.generator_func(seed, count,
                                           r=r, s=s, base=base,
                                           bits_per_value=bits_per_value,
                                           return_time=False)
            except TypeError:
                result = self.generator_func(seed, count)

            if isinstance(result, tuple):
                return result[0]
            return result

        # Standardowa obsługa dla pozostałych generatorów
        try:
            result = self.generator_func(seed, count)
        except TypeError:
            try:
                result = self.generator_func(seed, count, return_time=False)
            except TypeError:
                try:
                    result = self.generator_func(seed, count, bits_per_value=32)
                except TypeError:
                    raise RuntimeError(f"Cannot call {func_name} with standard signature")

        # Handle (bits, time) tuple
        if isinstance(result, tuple):
            return result[0]
        return result

    def _call_standard(self, count: int, seed: int) -> List[Any]:
        """Wywołaj standardową funkcję generate()"""
        return self.generator_func(count, seed)