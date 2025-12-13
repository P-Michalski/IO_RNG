"""
Run RNG Test Use Case
"""
from typing import Dict, Any, List
import time

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
            statistics=test_result['statistics'],
            generated_bits=bits  # Zapisz wygenerowane bity
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

        # Chi-square statistic
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

        # Dla każdego bloku znajdź najdłuższy run jedynek
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

        # Forward cumulative sum
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

        # Przetwórz każdą macierz
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
        import cmath

        n = len(bits)

        if n < 100:
            return {
                'passed': False,
                'score': 0.0,
                'statistics': {'error': 'Minimum 100 bits required'}
            }

        # Konwertuj bity do +1/-1
        X = [2 * bit - 1 for bit in bits]

        # Prosta implementacja DFT (dla małych n)
        # Dla dużych n lepiej użyć numpy.fft
        def dft(x):
            N = len(x)
            result = []
            for k in range(N // 2):  # Tylko połowa (symetria)
                sum_val = 0
                for n in range(N):
                    angle = -2j * cmath.pi * k * n / N
                    sum_val += x[n] * cmath.exp(angle)
                result.append(abs(sum_val))
            return result

        # Oblicz DFT
        S = dft(X)

        # Próg wykrywania pików
        T = math.sqrt(math.log(1 / 0.05) * n)

        # Zlicz wartości przekraczające próg
        N0 = 0.95 * n / 2
        N1 = sum(1 for s in S if s < T)

        # Różnica
        d = (N1 - N0) / math.sqrt(n * 0.95 * 0.05 / 4)

        # P-value
        p_value = erfc(abs(d) / math.sqrt(2))

        passed = p_value >= 0.01
        score = min(1.0, p_value)

        return {
            'passed': passed,
            'score': round(score, 4),
            'statistics': {
                'p_value': round(p_value, 6),
                'peaks_below_threshold': N1,
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

        # Zlicz wystąpienia w każdym bloku (overlapping)
        counts = []
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

        # Inicjalizacja tablicy
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

        def berlekamp_massey(bits):
            """Algorytm Berlekamp-Massey - oblicza złożoność liniową"""
            n = len(bits)
            c = [0] * n
            b = [0] * n
            c[0] = b[0] = 1
            L = 0
            m = -1
            N = 0

            while N < n:
                d = bits[N]
                for i in range(1, L + 1):
                    d ^= c[i] & bits[N - i]

                if d == 1:
                    t = c[:]
                    for i in range(n - N + m):
                        c[N - m + i] ^= b[i]
                    if L <= N // 2:
                        L = N + 1 - L
                        m = N
                        b = t
                N += 1

            return L

        # Oblicz złożoność dla każdego bloku
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

        # Konwertuj do +1/-1
        X = [2 * bit - 1 for bit in bits]

        # Oblicz partial sums
        S = [0]
        for x in X:
            S.append(S[-1] + x)

        # Zlicz cykle (powroty do 0)
        cycles = 0
        for i in range(1, len(S)):
            if S[i] == 0:
                cycles += 1

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

        # Konwertuj do +1/-1
        X = [2 * bit - 1 for bit in bits]

        # Oblicz partial sums
        S = [0]
        for x in X:
            S.append(S[-1] + x)

        # Zlicz cykle
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