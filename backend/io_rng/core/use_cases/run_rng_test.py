#Tests
"""
Run RNG Test Use Case
"""
from typing import Dict, Any, List
import time

# Numpy/Scipy imports dla optymalizacji wydajności
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from scipy.fft import fft
    HAS_SCIPY_FFT = True
except ImportError:
    HAS_SCIPY_FFT = False

from io_rng.core.entities.rng import RNG
from io_rng.core.entities.test_result import TestResult
from io_rng.core.interfaces.rng_runner import IRNGRunner
from io_rng.core.interfaces.repositories import IRNGRepository, ITestResultRepository


class RunRNGTestUseCase:
    """Use case do uruchamiania testów RNG"""

    def __init__(
        self,
        rng_repository: IRNGRepository,
        result_repository: ITestResultRepository,
        runners: List[IRNGRunner]
    ):
        self.rng_repository = rng_repository
        self.result_repository = result_repository
        self.runners = runners

    def _find_runner(self, rng: RNG) -> IRNGRunner:
        """
        Znajduje odpowiedni runner dla danego RNG.

        Args:
            rng: RNG entity

        Returns:
            Runner który może uruchomić ten RNG

        Raises:
            RuntimeError: Jeśli nie znaleziono runnera
        """
        for runner in self.runners:
            if runner.can_run(rng):
                return runner

        raise RuntimeError(f"No runner available for {rng.language.value}")

    def execute(
        self,
        rng_id: int,
        test_name: str,
        samples_count: int,
        seed: int = None,
        parameters: Dict[str, Any] = None
    ) -> TestResult:
        """
        Wykonuje test RNG z opcjonalnymi parametrami.

        Args:
            rng_id: ID generatora do przetestowania
            test_name: Nazwa testu statystycznego
            samples_count: Liczba próbek do wygenerowania
            seed: Opcjonalny seed dla powtarzalności
            parameters: Opcjonalne parametry dla generatora (override RNG.parameters)

        Returns:
            TestResult z wynikami testu

        Raises:
            ValueError: Jeśli RNG nie istnieje
            RuntimeError: Jeśli nie ma odpowiedniego runnera
        """

        # 1. Pobierz RNG z repozytorium
        rng = self.rng_repository.get_by_id(rng_id)
        if not rng:
            raise ValueError(f"RNG {rng_id} not found")

        # 2. Znajdź odpowiedni runner
        runner = self._find_runner(rng)
        if not runner:
            raise RuntimeError(f"No runner for {rng.language.value}")

        # 3. Generuj liczby losowe (z parametrami z requesta)
        start_time = time.perf_counter()

        try:
            # Generuj surowe dane aby zachować bity
            from io_rng.core.entities.test_result import DataType
            raw_data, data_type = runner.generate_raw(rng, samples_count, seed, parameters)

            # Konwertuj do bitów jeśli nie są bitami
            if data_type == DataType.BITS:
                bits = raw_data
            elif data_type == DataType.INTEGERS:
                # Konwertuj integery do bitów (najmłodszy bit)
                bits = [num & 1 for num in raw_data]
            else:
                # Konwertuj floaty [0,1] do bitów
                bits = [1 if x > 0.5 else 0 for x in raw_data]

            # Konwertuj do floatów dla testów statystycznych
            numbers = runner.generate_numbers(rng, samples_count, seed, parameters)
        except Exception as e:
            return self._create_error_result(rng_id, test_name, str(e))

        execution_time = (time.perf_counter() - start_time) * 1000  # ms

        # 4. Wykonaj test statystyczny
        test_result = self._perform_statistical_test(numbers, test_name, bits)

        # 5. Utwórz TestResult entity
        result = TestResult(
            rng_id=rng_id,
            test_name=test_name,
            passed=test_result['passed'],
            score=test_result['score'],
            execution_time_ms=execution_time,
            samples_count=samples_count,
            statistics=test_result['statistics']
        )

        # 6. Zapisz wynik
        return self.result_repository.save(result)

    def _perform_statistical_test(
        self,
        numbers: List[float],
        test_name: str,
        bits: List[int] = None
    ) -> Dict[str, Any]:
        """
        Wykonuje test statystyczny na liczbach losowych.

        Args:
            numbers: Lista liczb float w zakresie [0, 1]
            test_name: Nazwa testu do wykonania
            bits: Opcjonalnie lista bitów [0, 1]

        Returns:
            Słownik z wynikami: {'passed': bool, 'score': float, 'statistics': dict}

        Raises:
            ValueError: Jeśli test_name jest nieznany
        """

        # Testy oparte na floatach
        if test_name == "frequency_test":
            return self._frequency_test(numbers)
        elif test_name == "uniformity_test":
            return self._uniformity_test(numbers)

        # Testy NIST - wymagają bitów
        elif test_name == "nist_monobit":
            return self._nist_monobit_test(bits)
        elif test_name == "nist_block_frequency":
            return self._nist_block_frequency_test(bits)
        elif test_name == "nist_runs":
            return self._nist_runs_test(bits)
        elif test_name == "nist_longest_run":
            return self._nist_longest_run_test(bits)
        elif test_name == "nist_cumulative_sums":
            return self._nist_cumulative_sums_test(bits)
        elif test_name == "nist_approximate_entropy":
            return self._nist_approximate_entropy_test(bits)
        elif test_name == "nist_matrix_rank":
            return self._nist_matrix_rank_test(bits)
        elif test_name == "nist_dft":
            return self._nist_dft_test(bits)
        elif test_name == "nist_non_overlapping_template":
            return self._nist_non_overlapping_template_test(bits)
        elif test_name == "nist_overlapping_template":
            return self._nist_overlapping_template_test(bits)
        elif test_name == "nist_universal":
            return self._nist_universal_test(bits)
        elif test_name == "nist_linear_complexity":
            return self._nist_linear_complexity_test(bits)
        elif test_name == "nist_serial":
            return self._nist_serial_test(bits)
        elif test_name == "nist_random_excursions":
            return self._nist_random_excursions_test(bits)
        elif test_name == "nist_random_excursions_variant":
            return self._nist_random_excursions_variant_test(bits)

        # Testy Diehard - wymagają bitów
        elif test_name == "diehard_birthday_spacings":
            return self._diehard_birthday_spacings_test(bits)
        elif test_name == "diehard_overlapping_permutations":
            return self._diehard_overlapping_permutations_test(bits)
        elif test_name == "diehard_binary_rank":
            return self._diehard_binary_rank_test(bits)
        elif test_name == "diehard_bitstream":
            return self._diehard_bitstream_test(bits)
        elif test_name == "diehard_opso":
            return self._diehard_opso_test(bits)
        elif test_name == "diehard_oqso":
            return self._diehard_oqso_test(bits)
        elif test_name == "diehard_dna":
            return self._diehard_dna_test(bits)
        elif test_name == "diehard_count_1s":
            return self._diehard_count_1s_test(bits)
        elif test_name == "diehard_parking_lot":
            return self._diehard_parking_lot_test(bits)
        elif test_name == "diehard_squeeze":
            return self._diehard_squeeze_test(bits)
        elif test_name == "diehard_runs":
            return self._diehard_runs_test(bits)
        elif test_name == "diehard_craps":
            return self._diehard_craps_test(bits)
        elif test_name == "diehard_minimum_distance":
            return self._diehard_minimum_distance_test(bits)
        elif test_name == "diehard_3dspheres":
            return self._diehard_3dspheres_test(bits)
        elif test_name == "diehard_overlapping_sums":
            return self._diehard_overlapping_sums_test(bits)
        else:
            raise ValueError(f"Unknown test: {test_name}")

    def _frequency_test(self, numbers: List[float]) -> Dict[str, Any]:
        """
        Test częstości (Chi-square test).
        Sprawdza czy liczby są równomiernie rozłożone w binach.

        Args:
            numbers: Lista liczb [0, 1]

        Returns:
            Wynik testu z chi-square statystyką
        """
        num_bins = 10
        bins = [0] * num_bins

        # Zlicz liczby w każdym binie
        for num in numbers:
            bin_idx = min(int(num * num_bins), num_bins - 1)
            bins[bin_idx] += 1

        # Chi-square test
        expected = len(numbers) / num_bins
        chi_square = sum(
            (observed - expected) ** 2 / expected
            for observed in bins
        )

        # Krytyczna wartość dla p=0.05, df=9
        critical_value = 16.919
        passed = chi_square < critical_value

        # Score: 1.0 = idealny, 0.0 = bardzo zły
        score = max(0.0, min(1.0, 1 - (chi_square / critical_value)))

        return {
            'passed': passed,
            'score': round(score, 2),
            'statistics': {
                'chi_square': round(chi_square, 3),
                'critical_value': critical_value,
                'bins': bins,
                'expected_per_bin': expected
            }
        }

    def _uniformity_test(self, numbers: List[float]) -> Dict[str, Any]:
        """
        Test równomierności (mean & variance test).
        Sprawdza czy średnia ≈ 0.5 i wariancja ≈ 1/12.

        Args:
            numbers: Lista liczb [0, 1]

        Returns:
            Wynik testu z mean i variance
        """
        n = len(numbers)

        # Oblicz średnią
        mean = sum(numbers) / n

        # Oblicz wariancję
        variance = sum((x - mean) ** 2 for x in numbers) / n

        # Wartości oczekiwane dla rozkładu uniform [0,1]
        expected_mean = 0.5
        expected_variance = 1.0 / 12.0  # ≈ 0.083

        # Różnice
        mean_diff = abs(mean - expected_mean)
        var_diff = abs(variance - expected_variance)

        # Test przechodzi jeśli różnice są małe
        passed = mean_diff < 0.05 and var_diff < 0.02

        # Score bazujący na różnicach
        score = max(0.0, min(1.0, 1 - (mean_diff * 10 + var_diff * 5)))

        return {
            'passed': passed,
            'score': round(score, 2),
            'statistics': {
                'mean': round(mean, 6),
                'expected_mean': expected_mean,
                'variance': round(variance, 6),
                'expected_variance': round(expected_variance, 6),
                'mean_diff': round(mean_diff, 6),
                'var_diff': round(var_diff, 6)
            }
        }

    def _create_error_result(
        self,
        rng_id: int,
        test_name: str,
        error_message: str
    ) -> TestResult:
        """
        Tworzy TestResult z błędem.

        Args:
            rng_id: ID generatora
            test_name: Nazwa testu
            error_message: Komunikat błędu

        Returns:
            TestResult z error_message
        """
        result = TestResult(
            rng_id=rng_id,
            test_name=test_name,
            passed=False,
            score=0.0,
            execution_time_ms=0.0,
            samples_count=0,
            statistics={},
            error_message=error_message
        )

        return self.result_repository.save(result)

    # ===== NIST Test Suite =====

    def _nist_monobit_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Monobit Test (Frequency Test)
        Sprawdza czy liczba jedynek i zer jest w przybliżeniu równa.
        """
        import math

        n = len(bits)
        # S = suma bitów (jako +1/-1)
        s = sum(1 if bit == 1 else -1 for bit in bits)

        # Test statistic
        s_obs = abs(s) / math.sqrt(n)

        # P-value
        from math import erfc
        p_value = erfc(s_obs / math.sqrt(2))

        # Test passes if p-value >= 0.01
        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'test_statistic': round(s_obs, 6),
                'ones': sum(bits),
                'zeros': n - sum(bits),
                'threshold': 0.01
            }
        }

    def _nist_block_frequency_test(self, bits: List[int], block_size: int = 128) -> Dict[str, Any]:
        """
        NIST Block Frequency Test
        Sprawdza czy proporcja jedynek w blokach jest bliska 0.5
        """
        import math
        from math import erfc

        n = len(bits)
        num_blocks = n // block_size

        if num_blocks == 0:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Not enough bits for block test'}
            }

        # OPTYMALIZACJA: Użyj numpy dla szybszych operacji na blokach
        if HAS_NUMPY:
            bits_arr = np.array(bits[:num_blocks * block_size], dtype=np.int8)
            # Reshape do macierzy bloków
            blocks = bits_arr.reshape(num_blocks, block_size)
            # Oblicz proporcje dla wszystkich bloków naraz
            proportions = np.sum(blocks, axis=1) / block_size
            # Chi-square
            chi_square = np.sum((proportions - 0.5) ** 2) * 4 * block_size
            proportions = proportions.tolist()
        else:
            # Fallback: oryginalna implementacja
            chi_square = 0.0
            proportions = []
            for i in range(num_blocks):
                block = bits[i * block_size:(i + 1) * block_size]
                proportion = sum(block) / block_size
                proportions.append(proportion)
                chi_square += (proportion - 0.5) ** 2
            chi_square *= 4 * block_size

        # P-value using incomplete gamma function approximation
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 6),
                'num_blocks': num_blocks,
                'block_size': block_size,
                'threshold': 0.01
            }
        }

    def _nist_runs_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Runs Test
        Sprawdza czy liczba przejść (runs) między 0 a 1 jest prawidłowa
        """
        import math
        from math import erfc

        n = len(bits)

        # OPTYMALIZACJA: Użyj numpy dla zliczania
        if HAS_NUMPY:
            bits_arr = np.array(bits, dtype=np.int8)
            ones = np.sum(bits_arr)
            pi = ones / n

            # Pre-test
            if abs(pi - 0.5) >= 2 / math.sqrt(n):
                return {
                    'passed': False,
                    'score': 0.0,
                    'statistics': {
                        'error': 'Pre-test failed: proportion of ones not close to 0.5',
                        'proportion': round(pi, 6)
                    }
                }

            # Zlicz runs używając diff (przejścia = zmiana wartości)
            # runs = 1 + liczba zmian
            runs = int(1 + np.sum(np.diff(bits_arr) != 0))  # Konwertuj do int dla JSON
        else:
            # Fallback: oryginalna implementacja
            ones = sum(bits)
            pi = ones / n

            # Pre-test: proporcja jedynek musi być bliska 0.5
            if abs(pi - 0.5) >= 2 / math.sqrt(n):
                return {
                    'passed': False,
                    'score': 0.0,
                    'statistics': {
                        'error': 'Pre-test failed: proportion of ones not close to 0.5',
                        'proportion': round(pi, 6)
                    }
                }

            # Zlicz runs
            runs = 1
            for i in range(1, n):
                if bits[i] != bits[i - 1]:
                    runs += 1

        # Expected value
        expected_runs = 2 * n * pi * (1 - pi)

        # Test statistic
        numerator = abs(runs - expected_runs)
        denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
        test_stat = numerator / denominator if denominator != 0 else 0

        # P-value
        p_value = erfc(test_stat / math.sqrt(2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'runs': runs,
                'expected_runs': round(expected_runs, 2),
                'threshold': 0.01
            }
        }

    def _nist_longest_run_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Longest Run of Ones Test
        Sprawdza czy najdłuższy ciąg jedynek jest prawidłowy
        """
        import math

        n = len(bits)

        # Parametry dla różnych długości bitów (uproszczone)
        if n < 128:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Minimum 128 bits required'}
            }
        elif n < 6272:
            K, M = 3, 8
            v_values = [1, 2, 3, 4]
            pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
        elif n < 750000:
            K, M = 5, 128
            v_values = [4, 5, 6, 7, 8, 9]
            pi_values = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
        else:
            K, M = 6, 10000
            v_values = [10, 11, 12, 13, 14, 15, 16]
            pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

        num_blocks = n // M
        frequencies = [0] * (K + 1)

        # OPTYMALIZACJA: Użyj numpy dla bloków (częściowa optymalizacja)
        if HAS_NUMPY and num_blocks > 0:
            bits_arr = np.array(bits[:num_blocks * M], dtype=np.int8)
            blocks_arr = bits_arr.reshape(num_blocks, M)

            # Dla każdego bloku znajdź najdłuższy run jedynek
            for block in blocks_arr:
                max_run = 0
                current_run = 0
                for bit in block:
                    if bit == 1:
                        current_run += 1
                        max_run = max(max_run, current_run)
                    else:
                        current_run = 0

                # Przypisz do kategorii
                if max_run <= v_values[0]:
                    frequencies[0] += 1
                elif max_run >= v_values[-1]:
                    frequencies[K] += 1
                else:
                    for j in range(len(v_values) - 1):
                        if v_values[j] < max_run <= v_values[j + 1]:
                            frequencies[j + 1] += 1
                            break
        else:
            # Fallback: oryginalna implementacja
            for i in range(num_blocks):
                block = bits[i * M:(i + 1) * M]
                max_run = 0
                current_run = 0

                for bit in block:
                    if bit == 1:
                        current_run += 1
                        max_run = max(max_run, current_run)
                    else:
                        current_run = 0

            # Przypisz do kategorii
            if max_run <= v_values[0]:
                frequencies[0] += 1
            elif max_run >= v_values[-1]:
                frequencies[K] += 1
            else:
                for j in range(len(v_values) - 1):
                    if v_values[j] < max_run <= v_values[j + 1]:
                        frequencies[j + 1] += 1
                        break

        # Chi-square
        chi_square = sum((frequencies[i] - num_blocks * pi_values[i]) ** 2 / (num_blocks * pi_values[i])
                         for i in range(K + 1))

        # P-value (simplified)
        from math import erfc
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 6),
                'frequencies': frequencies,
                'num_blocks': num_blocks,
                'threshold': 0.01
            }
        }

    def _nist_cumulative_sums_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Cumulative Sums Test
        Sprawdza maksymalne odchylenie kumulatywnej sumy
        """
        import math
        from math import erfc

        n = len(bits)

        # OPTYMALIZACJA: Użyj numpy dla kumulatywnej sumy
        if HAS_NUMPY:
            # Konwertuj bity do +1/-1 i oblicz kumulatywną sumę
            bits_arr = np.array(bits, dtype=np.int8) * 2 - 1
            s = np.concatenate(([0], np.cumsum(bits_arr)))
            z_forward = int(np.max(np.abs(s)))  # Konwertuj do int dla JSON
        else:
            # Fallback: oryginalna implementacja
            s = [0]
            for bit in bits:
                s.append(s[-1] + (1 if bit == 1 else -1))
            z_forward = max(abs(val) for val in s)

        # Test statistic
        sum_val = 0.0
        for k in range(int((-n / z_forward + 1) / 4), int((n / z_forward - 1) / 4) + 1):
            term1 = erfc((4 * k + 1) * z_forward / math.sqrt(n) / math.sqrt(2))
            term2 = erfc((4 * k - 1) * z_forward / math.sqrt(n) / math.sqrt(2))
            sum_val += term1 - term2

        p_value = 1 - sum_val

        passed = p_value >= 0.01
        score = min(1.0, max(0.0, p_value))

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'max_excursion': z_forward,
                'threshold': 0.01
            }
        }

    def _nist_approximate_entropy_test(self, bits: List[int], m: int = 10) -> Dict[str, Any]:
        """
        NIST Approximate Entropy Test
        Mierzy częstotliwość wszystkich możliwych nakładających się wzorców
        """
        import math

        n = len(bits)

        if n < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Minimum 100 bits required'}
            }

        # Adjust m if n is too small
        m = min(m, int(math.log2(n)) - 5)
        if m < 2:
            m = 2

        # OPTYMALIZACJA: Użyj numpy dla pattern counting
        if HAS_NUMPY:
            def compute_phi_numpy(m_local):
                bits_arr = np.array(bits, dtype=np.int8)
                # Generuj overlapping patterns jako integery
                patterns = np.zeros(n, dtype=np.int32)
                powers = 2 ** np.arange(m_local - 1, -1, -1, dtype=np.int32)

                for i in range(n):
                    pattern_bits = np.array([bits_arr[(i + j) % n] for j in range(m_local)])
                    patterns[i] = np.sum(pattern_bits * powers)

                # Policz unikalne wzorce
                unique, counts = np.unique(patterns, return_counts=True)
                phi = np.sum((counts / n) * np.log(counts / n))
                return phi

            phi_m = compute_phi_numpy(m)
            phi_m_plus_1 = compute_phi_numpy(m + 1)
        else:
            # Fallback: oryginalna implementacja
            def compute_phi(m_local):
                patterns = {}
                for i in range(n):
                    pattern = tuple(bits[(i + j) % n] for j in range(m_local))
                    patterns[pattern] = patterns.get(pattern, 0) + 1

                phi = sum((count / n) * math.log((count / n)) for count in patterns.values())
                return phi

            phi_m = compute_phi(m)
            phi_m_plus_1 = compute_phi(m + 1)

        apen = phi_m - phi_m_plus_1

        # Chi-square approximation
        chi_square = 2 * n * (math.log(2) - apen)

        # P-value (simplified)
        from math import erfc
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'approximate_entropy': round(apen, 6),
                'chi_square': round(chi_square, 6),
                'm': m,
                'threshold': 0.01
            }
        }

    def _nist_matrix_rank_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Binary Matrix Rank Test
        Sprawdza rangę macierzy binarnych utworzonych z sekwencji
        """
        import math
        from math import erfc

        n = len(bits)
        M = Q = 32  # Rozmiar macierzy 32x32

        if n < M * Q:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': f'Minimum {M*Q} bits required'}
            }

        num_matrices = n // (M * Q)

        # Zlicz macierze według rangi
        rank_counts = {M: 0, M-1: 0, 'other': 0}

        def compute_rank(matrix):
            """Oblicza rangę macierzy binarnej metodą eliminacji Gaussa"""
            rows = len(matrix)
            cols = len(matrix[0])
            rank = 0

            # Kopia macierzy do modyfikacji
            m = [row[:] for row in matrix]

            for col in range(min(rows, cols)):
                # Znajdź pivot
                pivot_row = None
                for row in range(rank, rows):
                    if m[row][col] == 1:
                        pivot_row = row
                        break

                if pivot_row is None:
                    continue

                # Zamień wiersze
                if pivot_row != rank:
                    m[rank], m[pivot_row] = m[pivot_row], m[rank]

                # Eliminuj
                for row in range(rows):
                    if row != rank and m[row][col] == 1:
                        for c in range(cols):
                            m[row][c] ^= m[rank][c]

                rank += 1

            return rank

        # OPTYMALIZACJA: Użyj numpy dla macierzy
        if HAS_NUMPY:
            bits_arr = np.array(bits[:num_matrices * M * Q], dtype=np.int8)
            # Reshape do tensora macierzy [num_matrices, M, Q]
            matrices = bits_arr.reshape(num_matrices, M, Q)

            # Oblicz rangę dla każdej macierzy
            for matrix in matrices:
                # Użyj numpy dla eliminacji Gaussa (szybsze operacje)
                rank = self._binary_matrix_rank_numpy(matrix)

                if rank == M:
                    rank_counts[M] += 1
                elif rank == M - 1:
                    rank_counts[M-1] += 1
                else:
                    rank_counts['other'] += 1
        else:
            # Fallback: oryginalna implementacja
            for i in range(num_matrices):
                # Pobierz M*Q bitów
                block = bits[i * M * Q:(i + 1) * M * Q]

                # Utwórz macierz M x Q
                matrix = []
                for row in range(M):
                    matrix.append(block[row * Q:(row + 1) * Q])

                # Oblicz rangę
                rank = compute_rank(matrix)

                if rank == M:
                    rank_counts[M] += 1
                elif rank == M - 1:
                    rank_counts[M-1] += 1
                else:
                    rank_counts['other'] += 1

        # Prawdopodobieństwa teoretyczne dla M=Q=32
        pi = {
            M: 0.2888,
            M-1: 0.5776,
            'other': 0.1336
        }

        # Chi-square
        chi_square = sum(
            (rank_counts[r] - num_matrices * pi[r]) ** 2 / (num_matrices * pi[r])
            for r in [M, M-1, 'other']
        )

        # P-value (df=2)
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 6),
                'rank_counts': rank_counts,
                'num_matrices': num_matrices,
                'matrix_size': f'{M}x{Q}',
                'threshold': 0.01
            }
        }

    def _nist_dft_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Discrete Fourier Transform (Spectral) Test
        Wykrywa okresowe wzorce za pomocą FFT
        """
        import math
        from math import erfc

        # Wersja wektorowa oparta na numpy.fft – O(n log n) zamiast O(n^2)
        try:
            import numpy as np
        except ImportError:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'numpy is required for nist_dft_test'}
            }

        n = len(bits)

        if n < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Minimum 100 bits required'}
            }

        # Konwertuj bity do +1/-1 w tablicy wektorowej
        X = np.asarray(bits, dtype=np.int8) * 2 - 1

        # RFFT zwraca tylko nieujemne częstotliwości
        spectrum = np.fft.rfft(X)
        magnitudes = np.abs(spectrum)

        # Próg wykrywania pików
        T = math.sqrt(math.log(1 / 0.05) * n)

        # Zlicz wartości poniżej progu (zgodnie z definicją testu)
        N0 = 0.95 * n / 2
        N1 = int(np.count_nonzero(magnitudes < T))

        # Statystyka i p-value
        d = (N1 - N0) / math.sqrt(n * 0.95 * 0.05 / 4)
        p_value = erfc(abs(d) / math.sqrt(2))

        passed = p_value >= 0.01
        score = min(1.0, float(p_value))

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(float(p_value), 6),
                'peaks_below_threshold': int(N1),
                'expected_peaks': round(N0, 2),
                'threshold': 0.01
            }
        }


    def _nist_non_overlapping_template_test(self, bits: List[int],
                                            template: List[int] = None) -> Dict[str, Any]:
        """
        NIST Non-overlapping Template Matching Test
        Szuka nienachodżących na siebie wystąpień wzorca
        """
        import math
        from math import erfc

        n = len(bits)

        # Domyślny template: 9-bitowy wzorzec "000000001"
        if template is None:
            template = [0, 0, 0, 0, 0, 0, 0, 0, 1]

        m = len(template)
        M = 1000  # Rozmiar bloku

        if n < M:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': f'Minimum {M} bits required'}
            }

        N = n // M

        # OPTYMALIZACJA: Użyj numpy dla bloków
        if HAS_NUMPY:
            bits_arr = np.array(bits[:N * M], dtype=np.int8)
            blocks_arr = bits_arr.reshape(N, M)
            template_arr = np.array(template, dtype=np.int8)

            counts = []
            for block in blocks_arr:
                count = 0
                i = 0
                while i <= len(block) - m:
                    # Szybsze porównanie używając numpy
                    if np.array_equal(block[i:i + m], template_arr):
                        count += 1
                        i += m  # Przeskocz template (non-overlapping)
                    else:
                        i += 1
                counts.append(count)
        else:
            # Fallback: oryginalna implementacja
            blocks = [bits[i * M:(i + 1) * M] for i in range(N)]

            # Zlicz wystąpienia w każdym bloku
            counts = []
            for block in blocks:
                count = 0
                i = 0
                while i <= len(block) - m:
                    if block[i:i + m] == template:
                        count += 1
                        i += m  # Przeskocz template (non-overlapping)
                    else:
                        i += 1
                counts.append(count)

        # Oczekiwana liczba wystąpień
        mu = (M - m + 1) / (2 ** m)
        sigma_sq = M * ((1 / (2 ** m)) - ((2 * m - 1) / (2 ** (2 * m))))

        # Chi-square
        chi_square = sum((c - mu) ** 2 for c in counts) / sigma_sq

        # P-value
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 6),
                'template': template,
                'num_blocks': N,
                'threshold': 0.01
            }
        }

    def _nist_overlapping_template_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Overlapping Template Matching Test
        Szuka nachodżących na siebie wystąpień 9-bitowego wzorca
        """
        import math
        from math import erfc

        n = len(bits)
        m = 9  # Długość wzorca
        template = [1] * m  # Wzorzec: 111111111
        M = 1032  # Rozmiar bloku

        if n < M:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': f'Minimum {M} bits required'}
            }

        N = n // M

        # OPTYMALIZACJA: Użyj numpy dla sliding window
        counts = []
        if HAS_NUMPY:
            bits_arr = np.array(bits[:N * M], dtype=np.int8)
            blocks_arr = bits_arr.reshape(N, M)

            # Dla każdego bloku, użyj rolling sum aby znaleźć wzorzec 111111111
            for block in blocks_arr:
                # Sprawdź gdzie suma 9 kolejnych bitów == 9 (wszystkie jedynki)
                count = 0
                for j in range(M - m + 1):
                    if np.sum(block[j:j + m]) == m:
                        count += 1
                counts.append(min(count, 5))  # Cap at 5
        else:
            # Fallback: oryginalna implementacja
            for i in range(N):
                block = bits[i * M:(i + 1) * M]
                count = 0
                for j in range(len(block) - m + 1):
                    if block[j:j + m] == template:
                        count += 1
                counts.append(min(count, 5))  # Cap at 5

        # Prawdopodobieństwa teoretyczne
        lambda_param = (M - m + 1) / (2 ** m)
        eta = lambda_param / 2.0

        pi = [0.364091, 0.185659, 0.139381, 0.100571, 0.0704323, 0.139865]

        # Zlicz wystąpienia każdej kategorii
        v = [0] * 6
        for c in counts:
            v[c] += 1

        # Chi-square
        chi_square = sum((v[i] - N * pi[i]) ** 2 / (N * pi[i]) for i in range(6))

        # P-value (df=5)
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 6),
                'frequencies': v,
                'num_blocks': N,
                'threshold': 0.01
            }
        }

    def _nist_universal_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Maurer's Universal Statistical Test
        Mierzy kompresowność sekwencji
        """
        import math
        from math import erfc

        n = len(bits)

        # Parametry dla różnych długości
        if n < 387840:
            L = 6
            Q = 640
        elif n < 904960:
            L = 7
            Q = 1280
        else:
            L = 8
            Q = 2560

        K = n // L - Q

        if K <= 0:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': f'Minimum {(Q + 100) * L} bits required'}
            }

        # OPTYMALIZACJA: Konwertuj bloki bitów na integery używając numpy
        if HAS_NUMPY:
            # Przygotuj tablicę bitów
            total_blocks = Q + K
            bits_arr = np.array(bits[:total_blocks * L], dtype=np.int8)
            blocks_arr = bits_arr.reshape(total_blocks, L)

            # Konwertuj każdy blok na integer (szybsza wersja tuple)
            powers = 2 ** np.arange(L - 1, -1, -1, dtype=np.int32)
            block_ints = np.sum(blocks_arr * powers, axis=1)

            # Inicjalizacja tablicy (pierwsze Q bloków)
            T = {}
            for i in range(Q):
                block_val = int(block_ints[i])
                T[block_val] = i + 1

            # Faza testowa
            sum_log = 0.0
            for i in range(Q, total_blocks):
                block_val = int(block_ints[i])
                idx = i + 1
                if block_val in T:
                    distance = idx - T[block_val]
                    sum_log += math.log2(distance)
                T[block_val] = idx
        else:
            # Fallback: oryginalna implementacja
            T = {}

            # Faza inicjalizacji (pierwsze Q bloków)
            for i in range(1, Q + 1):
                block = tuple(bits[(i - 1) * L:i * L])
                T[block] = i

            # Faza testowa
            sum_log = 0.0
            for i in range(Q + 1, Q + K + 1):
                block = tuple(bits[(i - 1) * L:i * L])
                if block in T:
                    distance = i - T[block]
                    sum_log += math.log2(distance)
                T[block] = i

        fn = sum_log / K

        # Wartości teoretyczne (tabela z NIST)
        expected_values = {
            6: (5.2177052, 2.576),
            7: (6.1962507, 3.125),
            8: (7.1836656, 3.238)
        }

        expected, c = expected_values.get(L, (7.0, 3.0))

        # Statystyka
        test_stat = abs(fn - expected) / (c / math.sqrt(K))

        # P-value
        p_value = erfc(test_stat / math.sqrt(2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'fn': round(fn, 6),
                'expected': round(expected, 6),
                'L': L,
                'Q': Q,
                'K': K,
                'threshold': 0.01
            }
        }

    def _nist_linear_complexity_test(self, bits: List[int], M: int = 500) -> Dict[str, Any]:
        """
        NIST Linear Complexity Test
        Mierzy długość najkrótszego LFSR generującego sekwencję
        """
        import math
        from math import erfc

        n = len(bits)
        N = n // M

        if N < 200:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Need at least 200 blocks (minimum 100000 bits for M=500)'}
            }

        def berlekamp_massey(bits_block):
            """Algorytm Berlekamp-Massey - oblicza złożoność liniową"""
            if HAS_NUMPY and isinstance(bits_block, np.ndarray):
                # Numpy version - konwertuj do listy dla BM
                bits_list = bits_block.tolist()
            else:
                bits_list = bits_block

            n_bm = len(bits_list)
            c = [0] * n_bm
            b = [0] * n_bm
            c[0] = b[0] = 1
            L = 0
            m = -1
            N_bm = 0

            while N_bm < n_bm:
                d = bits_list[N_bm]
                for i in range(1, L + 1):
                    d ^= c[i] & bits_list[N_bm - i]

                if d == 1:
                    t = c[:]
                    for i in range(n_bm - N_bm + m):
                        c[N_bm - m + i] ^= b[i]
                    if L <= N_bm // 2:
                        L = N_bm + 1 - L
                        m = N_bm
                        b = t
                N_bm += 1

            return L

        # Oblicz złożoność dla każdego bloku
        if HAS_NUMPY:
            # Numpy version - reshape na bloki i przetwórz
            bits_arr = np.array(bits[:N * M], dtype=np.int8)
            blocks = bits_arr.reshape(N, M)
            complexities = [berlekamp_massey(blocks[i]) for i in range(N)]
        else:
            # Fallback
            complexities = []
            for i in range(N):
                block = bits[i * M:(i + 1) * M]
                L = berlekamp_massey(block)
                complexities.append(L)

        # Oczekiwana wartość
        mu = M / 2.0 + (9.0 + (-1) ** (M + 1)) / 36.0 - (M / 3.0 + 2.0 / 9.0) / (2 ** M)

        # Zlicz odstępstwa
        T = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]
        v = [0] * 7

        for L in complexities:
            Ti = (L - mu + 2.0 / 9.0) / ((M / 2.0) ** 0.5)

            if Ti <= T[0]:
                v[0] += 1
            elif Ti > T[5]:
                v[6] += 1
            else:
                for j in range(5):
                    if T[j] < Ti <= T[j + 1]:
                        v[j + 1] += 1
                        break

        # Prawdopodobieństwa
        pi = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]

        # Chi-square
        chi_square = sum((v[i] - N * pi[i]) ** 2 / (N * pi[i]) for i in range(7))

        # P-value
        p_value = erfc(math.sqrt(chi_square / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 6),
                'frequencies': v,
                'M': M,
                'N': N,
                'threshold': 0.01
            }
        }

    def _nist_serial_test(self, bits: List[int], m: int = 16) -> Dict[str, Any]:
        """
        NIST Serial Test
        Sprawdza częstość wszystkich możliwych nakładających się m-bitowych wzorców
        """
        import math
        from math import erfc

        n = len(bits)

        if n < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Minimum 100 bits required'}
            }

        # Dostosuj m
        m = min(m, int(math.log2(n)) - 2)
        if m < 2:
            m = 2

        # OPTYMALIZACJA: Użyj numpy dla pattern counting
        if HAS_NUMPY:
            def psi_sq_numpy(m_local, bits_seq):
                """Oblicza psi^2_m używając numpy"""
                n_local = len(bits_seq)
                bits_arr = np.array(bits_seq, dtype=np.int8)

                # Generuj overlapping patterns jako integery
                patterns = np.zeros(n_local, dtype=np.int32)
                powers = 2 ** np.arange(m_local - 1, -1, -1, dtype=np.int32)

                for i in range(n_local):
                    pattern_bits = np.array([bits_arr[(i + j) % n_local] for j in range(m_local)])
                    patterns[i] = np.sum(pattern_bits * powers)

                # Policz unikalne wzorce i ich częstości
                unique, counts = np.unique(patterns, return_counts=True)
                sum_val = np.sum(counts ** 2)
                return (2 ** m_local / n_local) * sum_val - n_local

            psi2_m = psi_sq_numpy(m, bits)
            psi2_m1 = psi_sq_numpy(m - 1, bits)
            psi2_m2 = psi_sq_numpy(m - 2, bits)
        else:
            # Fallback: oryginalna implementacja
            def psi_sq(m_local, bits_seq):
                """Oblicza psi^2_m"""
                n_local = len(bits_seq)
                patterns = {}

                for i in range(n_local):
                    pattern = tuple(bits_seq[(i + j) % n_local] for j in range(m_local))
                    patterns[pattern] = patterns.get(pattern, 0) + 1

                sum_val = sum(count ** 2 for count in patterns.values())
                return (2 ** m_local / n_local) * sum_val - n_local

            psi2_m = psi_sq(m, bits)
            psi2_m1 = psi_sq(m - 1, bits)
            psi2_m2 = psi_sq(m - 2, bits)

        delta1 = psi2_m - psi2_m1
        delta2 = psi2_m - 2 * psi2_m1 + psi2_m2

        # P-values
        p_value1 = erfc(math.sqrt(abs(delta1) / 2))
        p_value2 = erfc(math.sqrt(abs(delta2) / 2))

        # Test przechodzi gdy obie p-values >= 0.01
        passed = p_value1 >= 0.01 and p_value2 >= 0.01
        score = min(1.0, min(p_value1, p_value2))

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value1': round(p_value1, 6),
                'p_value2': round(p_value2, 6),
                'delta1': round(delta1, 6),
                'delta2': round(delta2, 6),
                'm': m,
                'threshold': 0.01
            }
        }

    def _nist_random_excursions_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Random Excursions Test
        Analizuje liczbę cykli w random walk
        """
        import math
        from math import erfc

        n = len(bits)

        # OPTYMALIZACJA: Użyj numpy dla partial sums
        if HAS_NUMPY:
            # Konwertuj bity do +1/-1 i oblicz kumulatywną sumę
            X = np.array(bits, dtype=np.int8) * 2 - 1
            S = np.concatenate(([0], np.cumsum(X)))

            # Zlicz cykle (powroty do 0)
            cycles = int(np.sum(S == 0))  # Konwertuj do int dla JSON
        else:
            # Fallback: oryginalna implementacja
            X = [2 * bit - 1 for bit in bits]
            S = [0]
            for x in X:
                S.append(S[-1] + x)
            cycles = sum(1 for i in range(1, len(S)) if S[i] == 0)

        if cycles < 500:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': 'Too few cycles (need >= 500)',
                    'cycles': cycles
                }
            }

        # Stany do testowania
        states = [-4, -3, -2, -1, 1, 2, 3, 4]

        # Zlicz wizyty w każdym stanie
        results = []
        for x in states:
            if HAS_NUMPY:
                visits = int(np.sum(S == x))  # Konwertuj do int dla JSON
            else:
                visits = sum(1 for s in S if s == x)

            # Oczekiwana liczba wizyt
            expected = cycles * self._excursion_probability(x)

            # Chi-square dla tego stanu
            if expected > 0:
                chi = (visits - expected) ** 2 / expected
            else:
                chi = 0

            results.append({
                'state': x,
                'visits': visits,
                'expected': round(expected, 2),
                'chi_square': round(chi, 4)
            })

        # Średnia chi-square
        avg_chi = sum(r['chi_square'] for r in results) / len(results)

        # P-value (uproszczone)
        p_value = erfc(math.sqrt(avg_chi / 2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'cycles': cycles,
                'avg_chi_square': round(avg_chi, 4),
                'states': results,
                'threshold': 0.01
            }
        }

    def _excursion_probability(self, x: int) -> float:
        """Pomocnicza funkcja dla Random Excursions"""
        # Uproszczone prawdopodobieństwa
        probs = {
            -4: 0.0046, -3: 0.0163, -2: 0.0537, -1: 0.1458,
            1: 0.1458, 2: 0.0537, 3: 0.0163, 4: 0.0046
        }
        return probs.get(x, 0.0)

    def _nist_random_excursions_variant_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Random Excursions Variant Test
        Wariant testu Random Excursions z innymi stanami
        """
        import math
        from math import erfc

        n = len(bits)

        # OPTYMALIZACJA: Użyj numpy dla partial sums
        if HAS_NUMPY:
            # Konwertuj bity do +1/-1 i oblicz kumulatywną sumę
            X = np.array(bits, dtype=np.int8) * 2 - 1
            S = np.concatenate(([0], np.cumsum(X)))

            # Zlicz cykle
            cycles = int(np.sum(S == 0))  # Konwertuj do int dla JSON
        else:
            # Fallback: oryginalna implementacja
            X = [2 * bit - 1 for bit in bits]
            S = [0]
            for x in X:
                S.append(S[-1] + x)
            cycles = sum(1 for i in range(1, len(S)) if S[i] == 0)

        if cycles < 500:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': 'Too few cycles (need >= 500)',
                    'cycles': cycles
                }
            }

        # Stany do testowania
        states = [-9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        results = []
        p_values = []

        for x in states:
            # Zlicz wizyty
            if HAS_NUMPY:
                visits = int(np.sum(S == x))  # Konwertuj do int dla JSON
            else:
                visits = sum(1 for s in S if s == x)

            # Test statistic
            if cycles > 0:
                stat = abs(visits - cycles) / math.sqrt(2 * cycles * (4 * abs(x) - 2))
                p_value = erfc(stat / math.sqrt(2))
            else:
                p_value = 0.0

            p_values.append(p_value)
            results.append({
                'state': x,
                'visits': visits,
                'p_value': round(p_value, 6)
            })

        # Test przechodzi gdy wszystkie p-values >= 0.01
        min_p_value = min(p_values) if p_values else 0.0
        passed = all(p >= 0.01 for p in p_values)
        score = min(1.0, min_p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'min_p_value': round(min_p_value, 6),
                'cycles': cycles,
                'states': results[:6],  # Pokaż tylko pierwsze 6 dla zwięzłości
                'threshold': 0.01
            }
        }

    # ==================== DIEHARD TEST SUITE ====================

    def _diehard_birthday_spacings_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Birthday Spacings Test

        Testuje odległości między "urodzinami" (powtórzeniami wartości).
        Dla prawdziwie losowego źródła, rozkład odległości powinien być Poissona.

        Minimum: 2^18 = 262,144 bitów
        Zalecane: 2^20 = 1,048,576 bitów
        """
        from math import erfc

        n = len(bits)

        # Wymagane minimum
        if n < 262144:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 262144 bits, got {n}',
                    'bits_needed': 262144
                }
            }

        # OPTYMALIZACJA: Konwertuj bity na 24-bitowe słowa używając numpy
        if HAS_NUMPY:
            word_length = 24
            num_words = (len(bits) - 23) // 24
            if num_words > 0:
                bits_arr = np.array(bits[:num_words * word_length], dtype=np.int8)
                bits_reshaped = bits_arr.reshape(num_words, word_length)
                powers = 2 ** np.arange(word_length - 1, -1, -1, dtype=np.int32)
                words = (bits_reshaped * powers).sum(axis=1).tolist()
            else:
                words = []
        else:
            # Fallback: oryginalna implementacja
            words = []
            for i in range(0, len(bits) - 23, 24):
                word = 0
                for j in range(24):
                    word = (word << 1) | bits[i + j]
                words.append(word)

        # Podziel na bloki (każdy blok = 512 słów)
        block_size = 512
        num_blocks = len(words) // block_size

        if num_blocks < 10:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 10 blocks, got {num_blocks}',
                    'blocks_needed': 10
                }
            }

        spacings = []

        for block_idx in range(num_blocks):
            block_words = words[block_idx * block_size : (block_idx + 1) * block_size]

            # Sortuj dla znalezienia duplikatów
            sorted_words = sorted(enumerate(block_words), key=lambda x: x[1])

            # Znajdź spacing (odległość między duplikatami)
            last_val = None
            last_pos = -1

            for pos, val in sorted_words:
                if val == last_val:
                    spacing = pos - last_pos
                    spacings.append(spacing)
                last_val = val
                last_pos = pos

        if len(spacings) < 10:
            # Brak wystarczających duplikatów - bardzo dobre losowe źródło
            return {
                'passed': True,
                'score': 0.95,
                'statistics': {
                    'spacings_found': len(spacings),
                    'note': 'Very few duplicates - excellent randomness',
                    'threshold': 0.01
                }
            }

        # Testuj zgodność z rozkładem Poissona
        mean_spacing = sum(spacings) / len(spacings)

        # Teoretyczna średnia dla rozkładu Poissona w przestrzeni 2^24 z 512 próbkami
        expected_mean = (2**24) / block_size

        # Chi-square test dla zgodności
        variance = sum((s - mean_spacing)**2 for s in spacings) / len(spacings)

        # Normalizuj do p-value
        chi_square = abs(mean_spacing - expected_mean) / (variance / len(spacings))**0.5
        p_value = erfc(chi_square / (2**0.5))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'mean_spacing': round(mean_spacing, 2),
                'expected_mean': round(expected_mean, 2),
                'num_spacings': len(spacings),
                'num_blocks': num_blocks,
                'threshold': 0.01
            }
        }

    def _diehard_overlapping_permutations_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Overlapping Permutations Test

        Analizuje częstości permutacji 5 kolejnych wartości w nakładających się oknach.
        Dla 5 wartości jest 5! = 120 możliwych permutacji.

        Minimum: 2^20 = 1,048,576 bitów
        """
        from math import erfc

        n = len(bits)

        if n < 1048576:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 1048576 bits, got {n}',
                    'bits_needed': 1048576
                }
            }

        # Konwertuj bity na 8-bitowe bajty
        if HAS_NUMPY:
            # Numpy version - szybsza konwersja bitów na bajty
            num_bytes = (len(bits) - 7) // 8
            bits_arr = np.array(bits[:num_bytes * 8], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_bytes, 8)
            powers = 2 ** np.arange(7, -1, -1, dtype=np.int32)
            bytes_list = (bits_reshaped * powers).sum(axis=1).tolist()
        else:
            # Fallback
            bytes_list = []
            for i in range(0, len(bits) - 7, 8):
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | bits[i + j]
                bytes_list.append(byte_val)

        # Analizuj okna po 5 bajtów (overlapping)
        window_size = 5
        perm_counts = {}

        for i in range(len(bytes_list) - window_size + 1):
            window = bytes_list[i:i + window_size]

            # Konwertuj do rangi (permutacji)
            ranks = [0] * window_size
            for j in range(window_size):
                rank = sum(1 for k in range(window_size) if window[k] < window[j])
                ranks[j] = rank

            perm_key = tuple(ranks)
            perm_counts[perm_key] = perm_counts.get(perm_key, 0) + 1

        total_windows = len(bytes_list) - window_size + 1

        # Teoretyczna liczba permutacji
        num_perms = 120  # 5!
        expected_count = total_windows / num_perms

        # Chi-square test
        chi_square = 0
        for count in perm_counts.values():
            chi_square += (count - expected_count) ** 2 / expected_count

        # Stopnie swobody = 119 (120 - 1)
        df = num_perms - 1

        # P-value (uproszczone dla dużych df)
        p_value = erfc((chi_square / (2 * df))**0.5)

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 4),
                'degrees_of_freedom': df,
                'unique_permutations': len(perm_counts),
                'expected_permutations': num_perms,
                'total_windows': total_windows,
                'threshold': 0.01
            }
        }

    def _diehard_binary_rank_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Binary Rank Test

        Testuje rangę (rank) macierzy binarnych 32x32 utworzonych z bitów.
        Dla prawdziwie losowych bitów, rozkład rang powinien być charakterystyczny.

        Minimum: 10,240 bitów dla 10 macierzy
        Zalecane: 100,000+ bitów
        """
        from math import erfc

        n = len(bits)
        matrix_size = 32
        bits_per_matrix = matrix_size * matrix_size  # 1024

        if n < bits_per_matrix * 10:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= {bits_per_matrix * 10} bits, got {n}',
                    'bits_needed': bits_per_matrix * 10
                }
            }

        num_matrices = n // bits_per_matrix
        rank_counts = {32: 0, 31: 0, 'other': 0}

        # OPTYMALIZACJA: Użyj numpy dla macierzy
        if HAS_NUMPY:
            bits_arr = np.array(bits[:num_matrices * bits_per_matrix], dtype=np.int8)
            # Reshape do tensora macierzy [num_matrices, matrix_size, matrix_size]
            matrices = bits_arr.reshape(num_matrices, matrix_size, matrix_size)

            # Oblicz rangę dla każdej macierzy
            for matrix in matrices:
                rank = self._binary_matrix_rank_numpy(matrix)

                if rank == 32:
                    rank_counts[32] += 1
                elif rank == 31:
                    rank_counts[31] += 1
                else:
                    rank_counts['other'] += 1
        else:
            # Fallback: oryginalna implementacja
            for m in range(num_matrices):
                # Wyciągnij bity dla macierzy
                start = m * bits_per_matrix
                matrix_bits = bits[start:start + bits_per_matrix]

                # Utwórz macierz 32x32
                matrix = []
                for i in range(matrix_size):
                    row = matrix_bits[i * matrix_size : (i + 1) * matrix_size]
                    matrix.append(row)

                # Oblicz rangę (binary matrix rank)
                rank = self._binary_matrix_rank(matrix)

                if rank == 32:
                    rank_counts[32] += 1
                elif rank == 31:
                    rank_counts[31] += 1
                else:
                    rank_counts['other'] += 1

        # Teoretyczne prawdopodobieństwa dla 32x32
        # Dla prawdziwie losowej macierzy:
        # P(rank=32) ≈ 0.2888
        # P(rank=31) ≈ 0.5776
        # P(rank<=30) ≈ 0.1336

        expected_32 = num_matrices * 0.2888
        expected_31 = num_matrices * 0.5776
        expected_other = num_matrices * 0.1336

        # Chi-square test
        chi_square = (
            (rank_counts[32] - expected_32) ** 2 / expected_32 +
            (rank_counts[31] - expected_31) ** 2 / expected_31 +
            (rank_counts['other'] - expected_other) ** 2 / expected_other
        )

        # df = 3 - 1 = 2
        p_value = erfc((chi_square / 4)**0.5)

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 4),
                'rank_32_count': rank_counts[32],
                'rank_31_count': rank_counts[31],
                'rank_other_count': rank_counts['other'],
                'expected_32': round(expected_32, 2),
                'expected_31': round(expected_31, 2),
                'num_matrices': num_matrices,
                'threshold': 0.01
            }
        }

    def _binary_matrix_rank_numpy(self, matrix: np.ndarray) -> int:
        """
        Oblicza rangę macierzy binarnej używając eliminacji Gaussa w GF(2) z numpy.
        ZNACZNIE szybsze niż wersja z listami.

        Args:
            matrix: Macierz numpy jako array [0,1]

        Returns:
            Ranga macierzy (0 do n)
        """
        # Kopiuj macierz (numpy copy jest szybkie)
        m = matrix.copy()
        rows, cols = m.shape
        rank = 0

        for col in range(cols):
            # Znajdź pivot
            pivot_rows = np.where(m[rank:rows, col] == 1)[0]
            if len(pivot_rows) == 0:
                continue

            pivot_row = pivot_rows[0] + rank

            # Zamień wiersze (numpy swap jest szybki)
            if pivot_row != rank:
                m[[rank, pivot_row]] = m[[pivot_row, rank]]

            # Eliminuj (XOR w GF(2)) - użyj numpy broadcasting
            # Znajdź wiersze z 1 w tej kolumnie (poza pivot)
            rows_to_eliminate = np.where(m[:, col] == 1)[0]
            rows_to_eliminate = rows_to_eliminate[rows_to_eliminate != rank]

            # XOR tych wierszy z pivot row
            for row in rows_to_eliminate:
                m[row] ^= m[rank]

            rank += 1

        return rank

    def _binary_matrix_rank(self, matrix: List[List[int]]) -> int:
        """
        Oblicza rangę macierzy binarnej używając eliminacji Gaussa w GF(2).

        Args:
            matrix: Macierz jako lista list [0,1]

        Returns:
            Ranga macierzy (0 do n)
        """
        # Kopiuj macierz
        m = [row[:] for row in matrix]
        rows = len(m)
        cols = len(m[0]) if rows > 0 else 0

        rank = 0

        for col in range(cols):
            # Znajdź pivot
            pivot_row = None
            for row in range(rank, rows):
                if m[row][col] == 1:
                    pivot_row = row
                    break

            if pivot_row is None:
                continue

            # Zamień wiersze
            if pivot_row != rank:
                m[rank], m[pivot_row] = m[pivot_row], m[rank]

            # Eliminuj (XOR w GF(2))
            for row in range(rows):
                if row != rank and m[row][col] == 1:
                    for c in range(cols):
                        m[row][c] ^= m[rank][c]

            rank += 1

        return rank

    def _diehard_bitstream_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Bitstream Test

        Testuje bity poprzez liczenie wystąpień 20-bitowych słów w nakładających się oknach.
        Sprawdza, czy liczba wystąpień najbardziej i najmniej częstego słowa jest w normie.

        Minimum: 2^21 = 2,097,152 bitów
        """
        from math import erfc

        n = len(bits)

        if n < 2097152:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 2097152 bits, got {n}',
                    'bits_needed': 2097152
                }
            }

        # Użyj 20-bitowych słów
        word_length = 20

        # OPTYMALIZACJA: Użyj numpy dla sliding window
        if HAS_NUMPY:
            bits_arr = np.array(bits, dtype=np.int8)
            total_words = n - word_length + 1

            # Konwertuj sliding windows na integery
            words = np.zeros(total_words, dtype=np.int32)
            powers = 2 ** np.arange(word_length - 1, -1, -1, dtype=np.int32)

            for i in range(total_words):
                words[i] = np.sum(bits_arr[i:i + word_length] * powers)

            # Policz unikalne słowa
            unique_words, counts = np.unique(words, return_counts=True)
            word_counts = dict(zip(unique_words, counts))
        else:
            # Fallback: oryginalna implementacja
            word_counts = {}

            # Overlapping windows
            for i in range(n - word_length + 1):
                word = tuple(bits[i:i + word_length])
                word_counts[word] = word_counts.get(word, 0) + 1

        total_words = n - word_length + 1

        # Znajdź min/max częstości
        if not word_counts:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'No words found'}
            }

        max_count = max(word_counts.values())
        min_count = min(word_counts.values())

        # Oczekiwana częstość dla każdego słowa (równomierne)
        num_possible_words = 2 ** word_length
        expected_count = total_words / num_possible_words

        # Test: czy max/min są w rozsądnym zakresie?
        max_deviation = abs(max_count - expected_count) / (expected_count**0.5)
        min_deviation = abs(min_count - expected_count) / (expected_count**0.5)

        # Z-score combined
        z_score = max(max_deviation, min_deviation)
        p_value = erfc(z_score / (2**0.5))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'max_count': max_count,
                'min_count': min_count,
                'expected_count': round(expected_count, 2),
                'unique_words': len(word_counts),
                'possible_words': num_possible_words,
                'total_words': total_words,
                'z_score': round(z_score, 4),
                'threshold': 0.01
            }
        }

    def _diehard_opso_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard OPSO (Overlapping-Pairs-Sparse-Occupancy) Test

        Sprawdza jak często 10-literowe "słowa" (z alfabetu {0,1}) pojawiają się
        dokładnie 1 raz w strumieniu. Liczy "sparse occupancy".

        Minimum: 2^21 = 2,097,152 bitów
        """
        from math import erfc, exp

        n = len(bits)

        if n < 2097152:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 2097152 bits, got {n}',
                    'bits_needed': 2097152
                }
            }

        # Użyj 10-bitowych par
        word_length = 10

        # OPTYMALIZACJA: Użyj numpy dla sliding window
        if HAS_NUMPY:
            bits_arr = np.array(bits, dtype=np.int8)
            total_words = n - word_length + 1

            # Konwertuj sliding windows na integery
            words = np.zeros(total_words, dtype=np.int32)
            powers = 2 ** np.arange(word_length - 1, -1, -1, dtype=np.int32)

            for i in range(total_words):
                words[i] = np.sum(bits_arr[i:i + word_length] * powers)

            # Policz unikalne słowa i ich częstości
            unique_words, counts = np.unique(words, return_counts=True)

            # Policz singletons (count == 1)
            singleton_count = int(np.sum(counts == 1))
        else:
            # Fallback: oryginalna implementacja
            word_counts = {}

            # Overlapping
            for i in range(n - word_length + 1):
                word = tuple(bits[i:i + word_length])
                word_counts[word] = word_counts.get(word, 0) + 1

            # Policz słowa występujące dokładnie 1 raz
            singleton_count = sum(1 for count in word_counts.values() if count == 1)

        total_words = n - word_length + 1
        num_possible_words = 2 ** word_length

        # Teoretyczna wartość: dla prawdziwie losowego źródła
        # P(słowo występuje 1x) zależy od rozkładu Poissona
        lambda_param = total_words / num_possible_words
        expected_singletons = num_possible_words * lambda_param * exp(-lambda_param)

        # Chi-square dla różnicy
        if expected_singletons > 0:
            chi_square = (singleton_count - expected_singletons) ** 2 / expected_singletons
            p_value = erfc((chi_square / 2)**0.5)
        else:
            p_value = 0.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'singleton_count': singleton_count,
                'expected_singletons': round(expected_singletons, 2),
                'total_words': total_words,
                'unique_words': len(unique_words) if HAS_NUMPY else len(word_counts),
                'lambda': round(lambda_param, 4),
                'threshold': 0.01
            }
        }

    def _diehard_oqso_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard OQSO (Overlapping-Quadruples-Sparse-Occupancy) Test

        Podobny do OPSO, ale analizuje 4-literowe słowa zamiast par.
        Dzieli bity na 32-bitowe słowa, następnie na 4-literowe "słowa"
        (każda litera = 5 bitów), tworząc nakładające się czwórki.

        Minimum: ~2^21 bitów (~2M)
        """
        from math import erfc, exp

        n = len(bits)

        if n < 2097152:  # 2^21
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 2097152 bits, got {n}',
                    'bits_needed': 2097152
                }
            }

        # Konwertuj bity na 32-bitowe słowa
        if HAS_NUMPY:
            # Numpy version - szybsza konwersja
            num_words = n // 32
            bits_arr = np.array(bits[:num_words * 32], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_words, 32)
            powers = 2 ** np.arange(31, -1, -1, dtype=np.int64)
            words = (bits_reshaped * powers).sum(axis=1)

            # Każde 32-bitowe słowo dzielimy na 6 5-bitowych "liter" (30 bitów używanych)
            # Tworzymy nakładające się czwórki liter
            quadruples = []
            for word in words:
                # Wyciągnij 6 5-bitowych liter z 32-bitowego słowa
                letters = []
                for i in range(6):
                    letter = int((word >> (27 - i * 5)) & 0x1F)  # 5 bitów
                    letters.append(letter)

                # Twórz nakładające się czwórki (0-1-2-3, 1-2-3-4, 2-3-4-5)
                for i in range(3):
                    quad = tuple(letters[i:i+4])
                    quadruples.append(quad)

            # Policz wystąpienia
            quad_counts = {}
            for quad in quadruples:
                quad_counts[quad] = quad_counts.get(quad, 0) + 1
        else:
            # Fallback
            num_words = n // 32
            quadruples = []

            for i in range(num_words):
                word_bits = bits[i*32:(i+1)*32]
                word = 0
                for bit in word_bits:
                    word = (word << 1) | bit

                # Wyciągnij 6 5-bitowych liter
                letters = []
                for j in range(6):
                    letter = (word >> (27 - j * 5)) & 0x1F
                    letters.append(letter)

                # Nakładające się czwórki
                for j in range(3):
                    quad = tuple(letters[j:j+4])
                    quadruples.append(quad)

            quad_counts = {}
            for quad in quadruples:
                quad_counts[quad] = quad_counts.get(quad, 0) + 1

        # Policz czwórki występujące dokładnie raz
        singleton_count = sum(1 for count in quad_counts.values() if count == 1)

        total_quads = len(quadruples)
        num_possible_quads = 32 ** 4  # 32 możliwych liter, 4-literowe słowa

        # Rozkład Poissona
        lambda_param = total_quads / num_possible_quads
        expected_singletons = num_possible_quads * lambda_param * exp(-lambda_param)

        if expected_singletons > 0:
            chi_square = (singleton_count - expected_singletons) ** 2 / expected_singletons
            p_value = erfc((chi_square / 2)**0.5)
        else:
            p_value = 0.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'singleton_count': singleton_count,
                'expected_singletons': round(expected_singletons, 2),
                'total_quadruples': total_quads,
                'unique_quadruples': len(quad_counts),
                'lambda': round(lambda_param, 4),
                'threshold': 0.01
            }
        }

    def _diehard_dna_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard DNA Test

        Traktuje bity jako sekwencję DNA (10-literowy alfabet A,C,G,T).
        Każda litera = 2 bity (00=A, 01=C, 10=G, 11=T).
        Analizuje nakładające się 10-literowe "słowa" DNA.

        Minimum: ~2^21 bitów (~2M)
        """
        from math import erfc, exp

        n = len(bits)

        if n < 2097152:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 2097152 bits, got {n}',
                    'bits_needed': 2097152
                }
            }

        # Konwertuj pary bitów na litery DNA (0-3)
        word_length = 10  # 10 liter DNA
        bits_per_letter = 2  # 2 bity na literę

        if HAS_NUMPY:
            # Numpy version
            num_letters = n // bits_per_letter
            bits_arr = np.array(bits[:num_letters * bits_per_letter], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_letters, bits_per_letter)

            # Konwertuj pary bitów na liczby 0-3
            letters = bits_reshaped[:, 0] * 2 + bits_reshaped[:, 1]

            # Twórz nakładające się 10-literowe słowa
            words = []
            for i in range(len(letters) - word_length + 1):
                word = tuple(letters[i:i+word_length].tolist())
                words.append(word)

            # Policz wystąpienia
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
        else:
            # Fallback
            num_letters = n // bits_per_letter
            letters = []

            for i in range(num_letters):
                letter = bits[i*2] * 2 + bits[i*2 + 1]
                letters.append(letter)

            # Nakładające się słowa
            words = []
            for i in range(len(letters) - word_length + 1):
                word = tuple(letters[i:i+word_length])
                words.append(word)

            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Policz singletons
        singleton_count = sum(1 for count in word_counts.values() if count == 1)

        total_words = len(words)
        num_possible_words = 4 ** word_length  # 4 litery, 10-literowe słowa

        lambda_param = total_words / num_possible_words
        expected_singletons = num_possible_words * lambda_param * exp(-lambda_param)

        if expected_singletons > 0:
            chi_square = (singleton_count - expected_singletons) ** 2 / expected_singletons
            p_value = erfc((chi_square / 2)**0.5)
        else:
            p_value = 0.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'singleton_count': singleton_count,
                'expected_singletons': round(expected_singletons, 2),
                'total_words': total_words,
                'unique_words': len(word_counts),
                'lambda': round(lambda_param, 4),
                'threshold': 0.01
            }
        }

    def _diehard_count_1s_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Count-the-1s Test

        Zlicza liczbę jedynek w sekwencji bajtów i sprawdza rozkład.
        Każdy bajt może mieć 0-8 jedynek. Test sprawdza czy rozkład
        liczby jedynek zgadza się z rozkładem dwumianowym.

        Minimum: 256000 bitów (32000 bajtów)
        """
        from math import erfc, comb

        n = len(bits)

        if n < 256000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 256000 bits, got {n}',
                    'bits_needed': 256000
                }
            }

        # Konwertuj bity na bajty i zlicz jedynki
        if HAS_NUMPY:
            # Numpy version
            num_bytes = n // 8
            bits_arr = np.array(bits[:num_bytes * 8], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_bytes, 8)

            # Zlicz jedynki w każdym bajcie
            ones_per_byte = np.sum(bits_reshaped, axis=1)

            # Policz rozkład (0-8 jedynek)
            observed = np.zeros(9, dtype=np.int32)
            for count in ones_per_byte:
                observed[int(count)] += 1
        else:
            # Fallback
            num_bytes = n // 8
            ones_counts = []

            for i in range(num_bytes):
                byte_bits = bits[i*8:(i+1)*8]
                ones = sum(byte_bits)
                ones_counts.append(ones)

            observed = [0] * 9
            for count in ones_counts:
                observed[count] += 1

        # Teoretyczny rozkład dwumianowy B(8, 0.5)
        # P(k jedynek) = C(8,k) * 0.5^8
        expected = []
        for k in range(9):
            prob = comb(8, k) * (0.5 ** 8)
            expected.append(prob * num_bytes)

        # Chi-square test
        chi_square = 0
        for i in range(9):
            if expected[i] > 0:
                obs = int(observed[i]) if HAS_NUMPY else observed[i]
                chi_square += (obs - expected[i]) ** 2 / expected[i]

        # Stopnie swobody = 8 (9 kategorii - 1)
        df = 8
        p_value = erfc((chi_square / (2 * df))**0.5)

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 4),
                'num_bytes': num_bytes,
                'observed': observed.tolist() if HAS_NUMPY else observed,
                'expected': [round(e, 2) for e in expected],
                'threshold': 0.01
            }
        }

    def _diehard_parking_lot_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Parking Lot Test

        Losuje punkty (x,y) na jednostkowym kwadracie [0,1]x[0,1].
        Każdy punkt ma promień r. Test zlicza ile "samochodów" (kół)
        można "zaparkować" bez kolizji.

        Minimum: 384000 bitów (dla 12000 prób po 32 bity)
        """
        from math import erfc, sqrt

        n = len(bits)

        if n < 384000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 384000 bits, got {n}',
                    'bits_needed': 384000
                }
            }

        # Konwertuj bity na floaty [0,1] dla współrzędnych
        bits_per_coord = 16  # 16 bitów na współrzędną
        num_points = n // (bits_per_coord * 2)  # 2 współrzędne (x, y)

        if HAS_NUMPY:
            # Numpy version
            bits_arr = np.array(bits[:num_points * bits_per_coord * 2], dtype=np.int8)

            # Konwertuj grupy bitów na liczby 0-65535, potem normalizuj do [0,1]
            bits_grouped = bits_arr.reshape(num_points * 2, bits_per_coord)
            powers = 2 ** np.arange(bits_per_coord - 1, -1, -1, dtype=np.int32)
            coords = (bits_grouped * powers).sum(axis=1) / (2 ** bits_per_coord)

            # Rozdziel na x i y
            x = coords[0::2]
            y = coords[1::2]

            # Parkowanie: sprawdź kolizje (odległość < 2*radius)
            radius = 0.01  # Mały promień dla większej liczby samochodów
            parked = []

            for i in range(len(x)):
                can_park = True
                for px, py in parked:
                    dist = sqrt((float(x[i]) - px)**2 + (float(y[i]) - py)**2)
                    if dist < 2 * radius:
                        can_park = False
                        break
                if can_park:
                    parked.append((float(x[i]), float(y[i])))
        else:
            # Fallback
            coords = []
            for i in range(num_points * 2):
                coord_bits = bits[i*bits_per_coord:(i+1)*bits_per_coord]
                value = 0
                for bit in coord_bits:
                    value = (value << 1) | bit
                coords.append(value / (2 ** bits_per_coord))

            x = coords[0::2]
            y = coords[1::2]

            radius = 0.01
            parked = []

            for i in range(len(x)):
                can_park = True
                for px, py in parked:
                    dist = sqrt((x[i] - px)**2 + (y[i] - py)**2)
                    if dist < 2 * radius:
                        can_park = False
                        break
                if can_park:
                    parked.append((x[i], y[i]))

        num_parked = len(parked)

        # Teoretyczna wartość zależy od rozmiaru kwadratu i promienia
        # Dla losowych punktów oczekiwana liczba zaparkowanych ~ num_points * exp(-lambda)
        # gdzie lambda zależy od gęstości
        expected = num_points * 0.3  # Przybliżone

        # Test czy liczba zaparkowanych jest w rozsądnym zakresie
        z_score = abs(num_parked - expected) / sqrt(expected) if expected > 0 else 0
        p_value = erfc(z_score / sqrt(2)) if z_score > 0 else 1.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'num_parked': num_parked,
                'num_attempted': num_points,
                'expected': round(expected, 2),
                'z_score': round(z_score, 4),
                'threshold': 0.01
            }
        }

    def _diehard_squeeze_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Squeeze Test

        Kompresuje losowe 32-bitowe integery poprzez iteracyjne mnożenie
        przez losowe floaty [0,1] aż wynik będzie < 1.
        Zlicza liczbę iteracji potrzebnych do kompresji.

        Minimum: 100000 bitów
        """
        from math import erfc, sqrt

        n = len(bits)

        if n < 100000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 100000 bits, got {n}',
                    'bits_needed': 100000
                }
            }

        # Konwertuj bity na 32-bitowe integery
        if HAS_NUMPY:
            # Numpy version
            num_ints = n // 32
            bits_arr = np.array(bits[:num_ints * 32], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_ints, 32)
            powers = 2 ** np.arange(31, -1, -1, dtype=np.int64)
            integers = (bits_reshaped * powers).sum(axis=1)

            # Konwertuj też na floaty [0,1] dla mnożników
            floats = integers / (2 ** 32)

            # Squeeze: mnóż przez kolejne floaty aż < 1
            squeeze_counts = []
            for i in range(0, len(integers) - 1, 2):
                value = float(integers[i])
                count = 0
                j = i + 1

                while value >= 1.0 and j < len(floats):
                    value *= float(floats[j])
                    count += 1
                    j += 1

                    if count > 100:  # Zabezpieczenie
                        break

                squeeze_counts.append(count)

            mean_count = float(np.mean(squeeze_counts))
            std_count = float(np.std(squeeze_counts))
        else:
            # Fallback
            num_ints = n // 32
            integers = []

            for i in range(num_ints):
                int_bits = bits[i*32:(i+1)*32]
                value = 0
                for bit in int_bits:
                    value = (value << 1) | bit
                integers.append(value)

            floats = [x / (2 ** 32) for x in integers]

            squeeze_counts = []
            for i in range(0, len(integers) - 1, 2):
                value = float(integers[i])
                count = 0
                j = i + 1

                while value >= 1.0 and j < len(floats):
                    value *= floats[j]
                    count += 1
                    j += 1

                    if count > 100:
                        break

                squeeze_counts.append(count)

            mean_count = sum(squeeze_counts) / len(squeeze_counts)
            variance = sum((x - mean_count)**2 for x in squeeze_counts) / len(squeeze_counts)
            std_count = sqrt(variance)

        # Teoretyczna średnia dla losowych wartości
        expected_mean = 47.0  # Przybliżona wartość teoretyczna

        if std_count > 0:
            z_score = abs(mean_count - expected_mean) / std_count
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'mean_squeezes': round(mean_count, 2),
                'std_squeezes': round(std_count, 2),
                'expected_mean': expected_mean,
                'num_samples': len(squeeze_counts),
                'z_score': round(z_score, 4),
                'threshold': 0.01
            }
        }

    def _diehard_runs_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Runs Test

        Analizuje długości ciągów (runs) zer i jedynek.
        Dla prawdziwie losowego generatora, rozkład długości
        runs powinien być zgodny z rozkładem teoretycznym.

        Minimum: 100000 bitów
        """
        from math import erfc

        n = len(bits)

        if n < 100000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 100000 bits, got {n}',
                    'bits_needed': 100000
                }
            }

        # Zlicz runs (ciągi kolejnych zer lub jedynek)
        if HAS_NUMPY:
            # Numpy version - wykorzystaj diff do wykrycia zmian
            bits_arr = np.array(bits, dtype=np.int8)

            # Znajdź miejsca zmiany wartości
            changes = np.diff(bits_arr)
            change_indices = np.where(changes != 0)[0] + 1

            # Dodaj początek i koniec
            run_starts = np.concatenate(([0], change_indices))
            run_ends = np.concatenate((change_indices, [n]))

            # Oblicz długości runs
            run_lengths = run_ends - run_starts

            # Policz runs według długości (grupujemy 1-6, 7+)
            run_counts = np.zeros(7, dtype=np.int32)  # 0: len=1, 1: len=2, ..., 6: len>=7
            for length in run_lengths:
                if length <= 6:
                    run_counts[int(length) - 1] += 1
                else:
                    run_counts[6] += 1
        else:
            # Fallback
            runs = []
            current_run = 1

            for i in range(1, n):
                if bits[i] == bits[i-1]:
                    current_run += 1
                else:
                    runs.append(current_run)
                    current_run = 1
            runs.append(current_run)

            # Policz według długości
            run_counts = [0] * 7
            for length in runs:
                if length <= 6:
                    run_counts[length - 1] += 1
                else:
                    run_counts[6] += 1

        # Teoretyczny rozkład dla losowych bitów
        # P(run długości k) = 2 * (1/2)^(k+1) dla k < max
        total_runs = sum(run_counts) if not HAS_NUMPY else int(np.sum(run_counts))
        expected = []
        for k in range(1, 7):
            prob = 2 * (0.5 ** (k + 1))
            expected.append(prob * total_runs)
        # Dla runs >= 7
        prob_7plus = 2 * (0.5 ** 8)
        expected.append(prob_7plus * total_runs)

        # Chi-square test
        chi_square = 0
        for i in range(7):
            obs = int(run_counts[i]) if HAS_NUMPY else run_counts[i]
            exp = expected[i]
            if exp > 0:
                chi_square += (obs - exp) ** 2 / exp

        # Stopnie swobody = 6 (7 kategorii - 1)
        df = 6
        p_value = erfc((chi_square / (2 * df))**0.5)

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 4),
                'total_runs': total_runs,
                'observed': run_counts.tolist() if HAS_NUMPY else run_counts,
                'expected': [round(e, 2) for e in expected],
                'threshold': 0.01
            }
        }

    def _diehard_craps_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Craps Test

        Symuluje grę w kości (craps) używając bitów jako źródła losowości.
        Zlicza liczbę rzutów potrzebnych do wygrania/przegrania gry.

        Zasady craps:
        - Suma 7 lub 11 na pierwszym rzucie = wygrana
        - Suma 2, 3, lub 12 na pierwszym rzucie = przegrana
        - Inne sumy = "point", rzucaj aż wypadnie point (wygrana) lub 7 (przegrana)

        Minimum: 200000 bitów
        """
        from math import erfc

        n = len(bits)

        if n < 200000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 200000 bits, got {n}',
                    'bits_needed': 200000
                }
            }

        # Konwertuj bity na rzuty kostką (1-6)
        # Każdy rzut = 3 bity (0-7), odrzucamy 6,7 i próbujemy ponownie
        def bits_to_dice(bits_arr, start_idx):
            """Konwertuj 3 bity na rzut kostką (1-6)"""
            while start_idx + 2 < len(bits_arr):
                if HAS_NUMPY:
                    value = int(bits_arr[start_idx] * 4 + bits_arr[start_idx+1] * 2 + bits_arr[start_idx+2])
                else:
                    value = bits_arr[start_idx] * 4 + bits_arr[start_idx+1] * 2 + bits_arr[start_idx+2]

                if value < 6:
                    return value + 1, start_idx + 3
                start_idx += 3
            return None, start_idx

        if HAS_NUMPY:
            bits_arr = np.array(bits, dtype=np.int8)
        else:
            bits_arr = bits

        # Symuluj gry w craps
        games_won = 0
        games_lost = 0
        idx = 0
        max_games = 1000  # Limit gier

        while idx < n - 50 and (games_won + games_lost) < max_games:
            # Pierwszy rzut (2 kostki)
            dice1, idx = bits_to_dice(bits_arr, idx)
            if dice1 is None:
                break
            dice2, idx = bits_to_dice(bits_arr, idx)
            if dice2 is None:
                break

            first_roll = dice1 + dice2

            if first_roll in [7, 11]:
                games_won += 1
            elif first_roll in [2, 3, 12]:
                games_lost += 1
            else:
                # Point - rzucaj aż wypadnie point lub 7
                point = first_roll
                while idx < n - 50:
                    dice1, idx = bits_to_dice(bits_arr, idx)
                    if dice1 is None:
                        break
                    dice2, idx = bits_to_dice(bits_arr, idx)
                    if dice2 is None:
                        break

                    roll = dice1 + dice2
                    if roll == point:
                        games_won += 1
                        break
                    elif roll == 7:
                        games_lost += 1
                        break

        total_games = games_won + games_lost

        if total_games < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': 'Not enough complete games',
                    'total_games': total_games
                }
            }

        # Teoretyczna szansa wygranej w craps ≈ 0.493
        expected_wins = total_games * 0.493
        expected_losses = total_games * 0.507

        # Chi-square test
        chi_square = ((games_won - expected_wins) ** 2 / expected_wins +
                     (games_lost - expected_losses) ** 2 / expected_losses)

        df = 1
        p_value = erfc((chi_square / (2 * df))**0.5)

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'chi_square': round(chi_square, 4),
                'games_won': games_won,
                'games_lost': games_lost,
                'total_games': total_games,
                'win_rate': round(games_won / total_games, 4),
                'expected_win_rate': 0.493,
                'threshold': 0.01
            }
        }

    def _diehard_minimum_distance_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Minimum Distance Test

        Losuje punkty w przestrzeni 2D i oblicza minimalną odległość
        między parami punktów. Rozkład minimalnych odległości powinien
        być zgodny z rozkładem teoretycznym.

        Minimum: 200000 bitów
        """
        from math import erfc, sqrt

        n = len(bits)

        if n < 200000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 200000 bits, got {n}',
                    'bits_needed': 200000
                }
            }

        # Konwertuj bity na punkty 2D w [0,1]x[0,1]
        bits_per_coord = 10  # 10 bitów na współrzędną
        num_points = n // (bits_per_coord * 2)

        if num_points < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need at least 100 points, got {num_points}'
                }
            }

        if HAS_NUMPY:
            # Numpy version
            bits_arr = np.array(bits[:num_points * bits_per_coord * 2], dtype=np.int8)
            bits_grouped = bits_arr.reshape(num_points * 2, bits_per_coord)
            powers = 2 ** np.arange(bits_per_coord - 1, -1, -1, dtype=np.int32)
            coords = (bits_grouped * powers).sum(axis=1) / (2 ** bits_per_coord)

            points = coords.reshape(num_points, 2)

            # Oblicz minimalną odległość dla każdego punktu do najbliższego sąsiada
            min_distances = []
            for i in range(min(num_points, 500)):  # Limit dla wydajności
                dists = np.sqrt(np.sum((points - points[i]) ** 2, axis=1))
                dists[i] = float('inf')  # Ignoruj siebie
                min_dist = float(np.min(dists))
                min_distances.append(min_dist)
        else:
            # Fallback
            coords = []
            for i in range(num_points * 2):
                coord_bits = bits[i*bits_per_coord:(i+1)*bits_per_coord]
                value = 0
                for bit in coord_bits:
                    value = (value << 1) | bit
                coords.append(value / (2 ** bits_per_coord))

            points = [(coords[i*2], coords[i*2+1]) for i in range(num_points)]

            min_distances = []
            for i in range(min(num_points, 500)):
                min_dist = float('inf')
                for j in range(num_points):
                    if i != j:
                        dist = sqrt((points[i][0] - points[j][0])**2 +
                                   (points[i][1] - points[j][1])**2)
                        min_dist = min(min_dist, dist)
                min_distances.append(min_dist)

        # Analiza rozkładu minimalnych odległości
        if HAS_NUMPY:
            mean_dist = float(np.mean(min_distances))
            std_dist = float(np.std(min_distances))
        else:
            mean_dist = sum(min_distances) / len(min_distances)
            variance = sum((x - mean_dist)**2 for x in min_distances) / len(min_distances)
            std_dist = sqrt(variance)

        # Teoretyczna średnia odległość zależy od gęstości punktów
        expected_mean = sqrt(1.0 / num_points)  # Przybliżone

        if std_dist > 0:
            z_score = abs(mean_dist - expected_mean) / std_dist
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'mean_distance': round(mean_dist, 6),
                'std_distance': round(std_dist, 6),
                'expected_mean': round(expected_mean, 6),
                'num_points': num_points,
                'num_samples': len(min_distances),
                'z_score': round(z_score, 4),
                'threshold': 0.01
            }
        }

    def _diehard_3dspheres_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard 3D Spheres Test

        Losuje punkty w przestrzeni 3D w sześcianie [0,1]^3.
        Zlicza punkty wewnątrz sfery o promieniu r z centrum w (0.5, 0.5, 0.5).
        Liczba punktów wewnątrz powinna być zgodna z rozkładem teoretycznym.

        Minimum: 150000 bitów
        """
        from math import erfc, sqrt

        n = len(bits)

        if n < 150000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 150000 bits, got {n}',
                    'bits_needed': 150000
                }
            }

        # Konwertuj bity na punkty 3D w [0,1]^3
        bits_per_coord = 10  # 10 bitów na współrzędną
        num_points = n // (bits_per_coord * 3)  # 3 współrzędne (x, y, z)

        if num_points < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need at least 100 points, got {num_points}'
                }
            }

        if HAS_NUMPY:
            # Numpy version
            bits_arr = np.array(bits[:num_points * bits_per_coord * 3], dtype=np.int8)
            bits_grouped = bits_arr.reshape(num_points * 3, bits_per_coord)
            powers = 2 ** np.arange(bits_per_coord - 1, -1, -1, dtype=np.int32)
            coords = (bits_grouped * powers).sum(axis=1) / (2 ** bits_per_coord)

            # Rozdziel na x, y, z
            x = coords[0::3]
            y = coords[1::3]
            z = coords[2::3]

            # Sfera z centrum w (0.5, 0.5, 0.5), promień 0.5
            center = 0.5
            radius = 0.5

            # Oblicz odległości od centrum
            distances = np.sqrt((x - center)**2 + (y - center)**2 + (z - center)**2)

            # Zlicz punkty wewnątrz sfery
            inside_count = int(np.sum(distances <= radius))
        else:
            # Fallback
            coords = []
            for i in range(num_points * 3):
                coord_bits = bits[i*bits_per_coord:(i+1)*bits_per_coord]
                value = 0
                for bit in coord_bits:
                    value = (value << 1) | bit
                coords.append(value / (2 ** bits_per_coord))

            x = coords[0::3]
            y = coords[1::3]
            z = coords[2::3]

            center = 0.5
            radius = 0.5

            inside_count = 0
            for i in range(num_points):
                dist = sqrt((x[i] - center)**2 + (y[i] - center)**2 + (z[i] - center)**2)
                if dist <= radius:
                    inside_count += 1

        # Teoretyczna objętość sfery / objętość sześcianu
        # V_sphere = (4/3) * π * r^3
        # V_cube = 1
        # Dla r = 0.5: V_sphere/V_cube ≈ 0.5236
        expected_ratio = 0.5236
        expected_inside = num_points * expected_ratio

        # Test statystyczny
        if expected_inside > 0:
            z_score = abs(inside_count - expected_inside) / sqrt(expected_inside * (1 - expected_ratio))
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'inside_count': inside_count,
                'outside_count': num_points - inside_count,
                'total_points': num_points,
                'inside_ratio': round(inside_count / num_points, 4),
                'expected_ratio': expected_ratio,
                'z_score': round(z_score, 4),
                'threshold': 0.01
            }
        }

    def _diehard_overlapping_sums_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Overlapping Sums Test

        Konwertuje bity na liczby zmiennoprzecinkowe i oblicza sumy
        nakładających się okien. Rozkład sum powinien być normalny.

        Minimum: 100000 bitów
        """
        from math import erfc, sqrt

        n = len(bits)

        if n < 100000:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {
                    'error': f'Need >= 100000 bits, got {n}',
                    'bits_needed': 100000
                }
            }

        # Konwertuj grupy bitów na liczby [0,1]
        bits_per_num = 8  # 8 bitów na liczbę
        window_size = 10  # Rozmiar okna sumowania

        if HAS_NUMPY:
            # Numpy version
            num_values = n // bits_per_num
            bits_arr = np.array(bits[:num_values * bits_per_num], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_values, bits_per_num)
            powers = 2 ** np.arange(bits_per_num - 1, -1, -1, dtype=np.int32)
            values = (bits_reshaped * powers).sum(axis=1) / (2 ** bits_per_num)

            # Oblicz sumy nakładających się okien
            sums = []
            for i in range(len(values) - window_size + 1):
                window_sum = float(np.sum(values[i:i+window_size]))
                sums.append(window_sum)

            mean_sum = float(np.mean(sums))
            std_sum = float(np.std(sums))
        else:
            # Fallback
            num_values = n // bits_per_num
            values = []

            for i in range(num_values):
                value_bits = bits[i*bits_per_num:(i+1)*bits_per_num]
                value = 0
                for bit in value_bits:
                    value = (value << 1) | bit
                values.append(value / (2 ** bits_per_num))

            # Sumy nakładających się okien
            sums = []
            for i in range(len(values) - window_size + 1):
                window_sum = sum(values[i:i+window_size])
                sums.append(window_sum)

            mean_sum = sum(sums) / len(sums)
            variance = sum((x - mean_sum)**2 for x in sums) / len(sums)
            std_sum = sqrt(variance)

        # Teoretyczna średnia i odchylenie standardowe
        # Dla uniform [0,1], suma n wartości ma średnią n/2 i wariancję n/12
        expected_mean = window_size / 2.0
        expected_std = sqrt(window_size / 12.0)

        # Test normalności (z-score)
        if std_sum > 0:
            z_score_mean = abs(mean_sum - expected_mean) / (expected_std / sqrt(len(sums)))
            z_score_std = abs(std_sum - expected_std) / (expected_std / sqrt(2 * len(sums)))

            # Łączny test
            chi_square = z_score_mean**2 + z_score_std**2
            p_value = erfc(sqrt(chi_square / 2))
        else:
            chi_square = 0.0
            p_value = 1.0

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'mean_sum': round(mean_sum, 4),
                'std_sum': round(std_sum, 4),
                'expected_mean': round(expected_mean, 4),
                'expected_std': round(expected_std, 4),
                'num_sums': len(sums),
                'chi_square': round(chi_square, 4),
                'threshold': 0.01
            }
        }