# Tests
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
    from scipy.special import gammaincc

    HAS_GAMMAINCC = True
except ImportError:
    HAS_GAMMAINCC = False

# NIST RNG Library import
try:
    import nistrng

    HAS_NIST_LIB = True
except ImportError:
    HAS_NIST_LIB = False

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
        runners: List[IRNGRunner],
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
        parameters: Dict[str, Any] = None,
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

            raw_data, data_type = runner.generate_raw(
                rng, samples_count, seed, parameters
            )

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
            passed=test_result["passed"],
            score=test_result["score"],
            execution_time_ms=execution_time,
            samples_count=samples_count,
            statistics=test_result["statistics"],
            test_parameters=parameters,
        )

        # 6. Zapisz wynik
        return self.result_repository.save(result)

    def _perform_statistical_test(
        self, numbers: List[float], test_name: str, bits: List[int] = None
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
        chi_square = sum((observed - expected) ** 2 / expected for observed in bins)

        # Krytyczna wartość dla p=0.05, df=9
        critical_value = 16.919
        passed = chi_square < critical_value

        # Score: 1.0 = idealny, 0.0 = bardzo zły
        score = max(0.0, min(1.0, 1 - (chi_square / critical_value)))

        return {
            "passed": passed,
            "score": round(score, 2),
            "statistics": {
                "chi_square": round(chi_square, 3),
                "critical_value": critical_value,
                "bins": bins,
                "expected_per_bin": expected,
            },
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
            "passed": passed,
            "score": round(score, 2),
            "statistics": {
                "mean": round(mean, 6),
                "expected_mean": expected_mean,
                "variance": round(variance, 6),
                "expected_variance": round(expected_variance, 6),
                "mean_diff": round(mean_diff, 6),
                "var_diff": round(var_diff, 6),
            },
        }

    def _create_error_result(
        self, rng_id: int, test_name: str, error_message: str
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
            error_message=error_message,
        )

        return self.result_repository.save(result)

    # ===== NIST Test Suite =====

    def _run_nistrng_test(
        self, nist_key: str, bits: List[int], **params
    ) -> Dict[str, Any]:
        """
        Pomocnicza metoda do uruchamiania testów z biblioteki nistrng.
        """
        if not HAS_NIST_LIB:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {"error": "nistrng library not installed"},
            }

        try:
            # 1. Przygotuj bity (nistrng wymaga numpy array int8 z zerami i jedynkami)
            # UWAGA: Nie używamy pack_sequence, bo ono służy do rozpakowywania bajtów!
            # My mamy już surowe bity w liście.
            if HAS_NUMPY:
                packed_bits = np.array(bits, dtype=np.int8)
            else:
                import numpy

                packed_bits = numpy.array(bits, dtype=numpy.int8)

            # 2. Pobierz instancję testu
            test = nistrng.SP800_22R1A_BATTERY.get(nist_key)
            if not test:
                return {
                    "passed": False,
                    "score": 0.0,
                    "statistics": {"error": f"Unknown nistrng test key: {nist_key}"},
                }

            # 3. Zastosuj parametry (hackowanie prywatnych atrybutów)
            if "block_size" in params:
                if hasattr(test, "_block_size"):
                    test._block_size = params["block_size"]
            if "block_length" in params:
                if hasattr(test, "_block_length"):
                    test._block_length = params["block_length"]
            # Specjalne przypadki dla parametru 'm'
            if "m" in params:
                if hasattr(test, "_block_length"):
                    test._block_length = params["m"]
                elif hasattr(test, "_block_size"):
                    test._block_size = params["m"]

            # 4. Uruchom test
            result_tuple = test.run(packed_bits)

            # Obsługa różnych typów wyników
            if isinstance(result_tuple, list):
                # Dla Random Excursions, które zwracają listę wyników
                results_list = result_tuple

                if not results_list:
                    return {
                        "passed": False,
                        "score": 0.0,
                        "statistics": {
                            "error": "Test returned no results (insufficient data?)"
                        },
                    }

                # Sprawdź czy pierwszy element to krotka (Result, time)
                first = results_list[0]
                if isinstance(first, tuple):
                    results_objs = [r[0] for r in results_list]
                else:
                    results_objs = results_list

                # Agregacja wyników
                passed = all(r.passed for r in results_objs)
                avg_score = sum(r.score for r in results_objs) / len(results_objs)
                min_score = min(r.score for r in results_objs)

                return {
                    "passed": passed,
                    "score": round(min_score, 4),
                    "statistics": {
                        "avg_p_value": round(avg_score, 6),
                        "min_p_value": round(min_score, 6),
                        "num_subtests": len(results_objs),
                        "threshold": 0.01,
                    },
                }
            else:
                # Pojedynczy wynik
                result_obj = result_tuple[0]
                p_value = result_obj.score
                passed = result_obj.passed

                return {
                    "passed": passed,
                    "score": round(p_value, 4),
                    "statistics": {
                        "p_value": round(p_value, 6),
                        "threshold": 0.01,
                    },
                }

        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {"error": f"NIST library error: {str(e)}"},
            }

    def _nist_monobit_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        NIST Monobit Test (Frequency Test)
        Sprawdza czy liczba jedynek i zer jest w przybliżeniu równa.
        """
        return self._run_nistrng_test("monobit", bits)

    def _nist_block_frequency_test(
        self, bits: List[int], block_size: int = 128
    ) -> Dict[str, Any]:
        """
        NIST Block Frequency Test
        Sprawdza czy proporcja jedynek w blokach jest bliska 0.5
        """
        return self._run_nistrng_test(
            "frequency_within_block", bits, block_size=block_size
        )

    def _nist_runs_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Runs Test"""
        return self._run_nistrng_test("runs", bits)

    def _nist_longest_run_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Longest Run of Ones Test"""
        return self._run_nistrng_test("longest_run_ones_in_a_block", bits)

    def _nist_cumulative_sums_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Cumulative Sums Test"""
        return self._run_nistrng_test("cumulative_sums", bits)

    def _nist_approximate_entropy_test(
        self, bits: List[int], m: int = 10
    ) -> Dict[str, Any]:
        """NIST Approximate Entropy Test"""
        return self._run_nistrng_test("approximate_entropy", bits, m=m)

    def _nist_matrix_rank_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Binary Matrix Rank Test"""
        return self._run_nistrng_test("binary_matrix_rank", bits)

    def _nist_dft_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Discrete Fourier Transform (Spectral) Test"""
        return self._run_nistrng_test("dft", bits)

    def _nist_non_overlapping_template_test(
        self, bits: List[int], template: List[int] = None
    ) -> Dict[str, Any]:
        """NIST Non-overlapping Template Matching Test"""
        return self._run_nistrng_test("non_overlapping_template_matching", bits)

    def _nist_overlapping_template_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Overlapping Template Matching Test"""
        return self._run_nistrng_test("overlapping_template_matching", bits)

    def _nist_universal_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Maurer's Universal Statistical Test"""
        return self._run_nistrng_test("maurers_universal", bits)

    def _nist_linear_complexity_test(
        self, bits: List[int], M: int = 500
    ) -> Dict[str, Any]:
        """NIST Linear Complexity Test (Berlekamp-Massey)"""
        return self._run_nistrng_test("linear_complexity", bits, block_size=M)

    def _nist_serial_test(self, bits: List[int], m: int = 16) -> Dict[str, Any]:
        """NIST Serial Test"""
        return self._run_nistrng_test("serial", bits, m=m)

    def _nist_random_excursions_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Random Excursions Test"""
        return self._run_nistrng_test("random_excursion", bits)

    def _nist_random_excursions_variant_test(self, bits: List[int]) -> Dict[str, Any]:
        """NIST Random Excursions Variant Test"""
        return self._run_nistrng_test("random_excursion_variant", bits)

    # ==================== DIEHARD TEST SUITE ====================

    def _diehard_birthday_spacings_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Birthday Spacings Test

        Testuje liczbę wartości powtarzających się więcej niż raz (duplikatów).
        Zgodnie z oryginalnym testem Diehard, liczba takich wartości j
        powinna mieć rozkład Poissona z lambda = m^3 / (4*n), gdzie:
        - m = liczba "urodzin" (512 w każdym bloku)
        - n = rozmiar przestrzeni (2^24 dla 24-bitowych słów)

        Minimum: 2^18 = 262,144 bitów
        Zalecane: 2^20 = 1,048,576 bitów
        """
        from math import exp

        n = len(bits)

        # Wymagane minimum
        if n < 262144:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 262144 bits, got {n}",
                    "bits_needed": 262144,
                },
            }

        # OPTYMALIZACJA: Konwertuj bity na 24-bitowe słowa używając numpy
        if HAS_NUMPY:
            word_length = 24
            num_words = (len(bits) - 23) // 24
            if num_words > 0:
                bits_arr = np.array(bits[: num_words * word_length], dtype=np.int8)
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

        # Podziel na bloki (każdy blok = 512 słów = m)
        m = 512  # liczba "urodzin" w każdym bloku
        space_size = 2**24  # n - rozmiar przestrzeni dla 24-bitowych słów
        num_blocks = len(words) // m

        if num_blocks < 10:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 10 blocks, got {num_blocks}",
                    "blocks_needed": 10,
                },
            }

        # Dla każdego bloku zlicz liczbę wartości które występują > 1 raz (j)
        j_values = []

        for block_idx in range(num_blocks):
            block_words = words[block_idx * m : (block_idx + 1) * m]

            # Zlicz częstości
            from collections import Counter

            counts = Counter(block_words)

            # j = liczba wartości które występują więcej niż raz
            j = sum(1 for count in counts.values() if count > 1)
            j_values.append(j)

        # Teoretyczny rozkład Poissona: lambda = m^3 / (4*n)
        # Dla m=512, n=2^24: lambda = 512^3 / (4 * 2^24) = 2.0
        lambda_param = (m**3) / (4.0 * space_size)

        # Buduj histogram j_values i porównaj z rozkładem Poissona
        # Zlicz częstości różnych wartości j
        from collections import Counter

        j_counts = Counter(j_values)

        # Oczekiwane częstości dla rozkładu Poissona
        # P(j=k) = (lambda^k * e^(-lambda)) / k!
        def poisson_prob(k, lam):
            from math import factorial

            return (lam**k * exp(-lam)) / factorial(k)

        # Chi-square test
        # Określ zakres j (zazwyczaj 0 do ~10 dla lambda=2)
        max_j = max(j_values) if j_values else 5
        min_j = 0

        expected_counts = {}
        observed_counts = {}

        # Buduj oczekiwane i obserwowane częstości
        for k in range(min_j, max_j + 2):  # +2 dla "tail"
            if k <= max_j:
                expected_counts[k] = poisson_prob(k, lambda_param) * num_blocks
                observed_counts[k] = j_counts.get(k, 0)
            else:
                # Ogon rozkładu (j > max_j)
                tail_prob = sum(poisson_prob(i, lambda_param) for i in range(k, k + 10))
                expected_counts[">=" + str(k)] = tail_prob * num_blocks
                observed_counts[">=" + str(k)] = sum(
                    c for j, c in j_counts.items() if j >= k
                )

        # Chi-square
        chi_square = 0
        for key in expected_counts:
            exp = expected_counts[key]
            obs = observed_counts[key]
            if exp > 0:
                chi_square += (obs - exp) ** 2 / exp

        # Stopnie swobody = liczba kategorii - 1 - liczba estymowanych parametrów
        df = len(expected_counts) - 1  # -1 bo suma jest znana

        # P-value
        if HAS_GAMMAINCC:
            p_value = gammaincc(df / 2.0, chi_square / 2.0)
        else:
            from math import erfc

            # Aproksymacja normalna dla chi-square
            p_value = erfc((chi_square / (2.0 * df)) ** 0.5)

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "chi_square": round(chi_square, 4),
                "lambda": round(lambda_param, 4),
                "mean_j": round(sum(j_values) / len(j_values), 2),
                "expected_mean_j": round(lambda_param, 2),
                "num_blocks": num_blocks,
                "df": df,
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 1048576 bits, got {n}",
                    "bits_needed": 1048576,
                },
            }

        # Konwertuj bity na 8-bitowe bajty
        if HAS_NUMPY:
            # Numpy version - szybsza konwersja bitów na bajty
            num_bytes = (len(bits) - 7) // 8
            bits_arr = np.array(bits[: num_bytes * 8], dtype=np.int8)
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
            window = bytes_list[i : i + window_size]

            # Konwertuj do rangi (permutacji) - poprawiona wersja z tie-breaking
            # Sortuj wartości z zachowaniem oryginalnych indeksów
            indexed_window = sorted(enumerate(window), key=lambda x: (x[1], x[0]))

            # Przypisz rangi na podstawie pozycji w posortowanej liście
            ranks = [0] * window_size
            for rank, (original_idx, _) in enumerate(indexed_window):
                ranks[original_idx] = rank

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

        # P-value using chi-square distribution with df=119
        if HAS_GAMMAINCC:
            p_value = gammaincc(df / 2, chi_square / 2)
        else:
            # Fallback: erfc approximation (mniej dokładne)
            p_value = erfc((chi_square / (2 * df)) ** 0.5)

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "chi_square": round(chi_square, 4),
                "degrees_of_freedom": df,
                "unique_permutations": len(perm_counts),
                "expected_permutations": num_perms,
                "total_windows": total_windows,
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= {bits_per_matrix * 10} bits, got {n}",
                    "bits_needed": bits_per_matrix * 10,
                },
            }

        num_matrices = n // bits_per_matrix
        rank_counts = {32: 0, 31: 0, "other": 0}

        # OPTYMALIZACJA: Użyj numpy dla macierzy
        if HAS_NUMPY:
            bits_arr = np.array(bits[: num_matrices * bits_per_matrix], dtype=np.int8)
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
                    rank_counts["other"] += 1
        else:
            # Fallback: oryginalna implementacja
            for m in range(num_matrices):
                # Wyciągnij bity dla macierzy
                start = m * bits_per_matrix
                matrix_bits = bits[start : start + bits_per_matrix]

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
                    rank_counts["other"] += 1

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
            (rank_counts[32] - expected_32) ** 2 / expected_32
            + (rank_counts[31] - expected_31) ** 2 / expected_31
            + (rank_counts["other"] - expected_other) ** 2 / expected_other
        )

        # df = 3 - 1 = 2
        if HAS_GAMMAINCC:
            p_value = gammaincc(1, chi_square / 2)  # df/2 = 2/2 = 1
        else:
            # Fallback: erfc approximation (mniej dokładne)
            p_value = erfc((chi_square / 4) ** 0.5)

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "chi_square": round(chi_square, 4),
                "rank_32_count": rank_counts[32],
                "rank_31_count": rank_counts[31],
                "rank_other_count": rank_counts["other"],
                "expected_32": round(expected_32, 2),
                "expected_31": round(expected_31, 2),
                "num_matrices": num_matrices,
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 2097152 bits, got {n}",
                    "bits_needed": 2097152,
                },
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
                words[i] = np.sum(bits_arr[i : i + word_length] * powers)

            # Policz unikalne słowa
            unique_words, counts = np.unique(words, return_counts=True)
            word_counts = dict(zip(unique_words.tolist(), counts.tolist()))
        else:
            # Fallback: oryginalna implementacja
            word_counts = {}

            # Overlapping windows
            for i in range(n - word_length + 1):
                word = tuple(bits[i : i + word_length])
                word_counts[word] = word_counts.get(word, 0) + 1

        total_words = n - word_length + 1

        # Znajdź min/max częstości
        if not word_counts:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {"error": "No words found"},
            }

        max_count = int(max(word_counts.values()))
        min_count = int(min(word_counts.values()))

        # Oczekiwana częstość dla każdego słowa (równomierne)
        num_possible_words = 2**word_length
        expected_count = total_words / num_possible_words

        # Test: czy max/min są w rozsądnym zakresie?
        max_deviation = abs(max_count - expected_count) / (expected_count**0.5)
        min_deviation = abs(min_count - expected_count) / (expected_count**0.5)

        # Z-score combined
        z_score = max(max_deviation, min_deviation)
        p_value = erfc(z_score / (2**0.5))

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "max_count": max_count,
                "min_count": min_count,
                "expected_count": round(expected_count, 2),
                "unique_words": len(word_counts),
                "possible_words": num_possible_words,
                "total_words": total_words,
                "z_score": round(z_score, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 2097152 bits, got {n}",
                    "bits_needed": 2097152,
                },
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
                words[i] = np.sum(bits_arr[i : i + word_length] * powers)

            # Policz unikalne słowa i ich częstości
            unique_words, counts = np.unique(words, return_counts=True)

            # Policz singletons (count == 1)
            singleton_count = int(np.sum(counts == 1))
        else:
            # Fallback: oryginalna implementacja
            word_counts = {}

            # Overlapping
            for i in range(n - word_length + 1):
                word = tuple(bits[i : i + word_length])
                word_counts[word] = word_counts.get(word, 0) + 1

            # Policz słowa występujące dokładnie 1 raz
            singleton_count = sum(1 for count in word_counts.values() if count == 1)

        total_words = n - word_length + 1
        num_possible_words = 2**word_length

        # Teoretyczna wartość: dla prawdziwie losowego źródła
        # P(słowo występuje 1x) zależy od rozkładu Poissona
        lambda_param = total_words / num_possible_words
        expected_singletons = num_possible_words * lambda_param * exp(-lambda_param)

        # Chi-square dla różnicy
        if expected_singletons > 0:
            chi_square = (
                singleton_count - expected_singletons
            ) ** 2 / expected_singletons
            # df = 1 (testujemy jedną kategorię)
            if HAS_GAMMAINCC:
                p_value = gammaincc(0.5, chi_square / 2)
            else:
                # Fallback: erfc approximation
                p_value = erfc((chi_square / 2) ** 0.5)
        else:
            p_value = 0.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "singleton_count": singleton_count,
                "expected_singletons": round(expected_singletons, 2),
                "total_words": total_words,
                "unique_words": len(unique_words) if HAS_NUMPY else len(word_counts),
                "lambda": round(lambda_param, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 2097152 bits, got {n}",
                    "bits_needed": 2097152,
                },
            }

        # Konwertuj bity na 32-bitowe słowa
        if HAS_NUMPY:
            # Numpy version - szybsza konwersja
            num_words = n // 32
            bits_arr = np.array(bits[: num_words * 32], dtype=np.int8)
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
                    quad = tuple(letters[i : i + 4])
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
                word_bits = bits[i * 32 : (i + 1) * 32]
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
                    quad = tuple(letters[j : j + 4])
                    quadruples.append(quad)

            quad_counts = {}
            for quad in quadruples:
                quad_counts[quad] = quad_counts.get(quad, 0) + 1

        # Policz czwórki występujące dokładnie raz
        singleton_count = sum(1 for count in quad_counts.values() if count == 1)

        total_quads = len(quadruples)
        num_possible_quads = 32**4  # 32 możliwych liter, 4-literowe słowa

        # Rozkład Poissona
        lambda_param = total_quads / num_possible_quads
        expected_singletons = num_possible_quads * lambda_param * exp(-lambda_param)

        if expected_singletons > 0:
            chi_square = (
                singleton_count - expected_singletons
            ) ** 2 / expected_singletons
            # df = 1 (testujemy jedną kategorię)
            if HAS_GAMMAINCC:
                p_value = gammaincc(0.5, chi_square / 2)
            else:
                # Fallback: erfc approximation
                p_value = erfc((chi_square / 2) ** 0.5)
        else:
            p_value = 0.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "singleton_count": singleton_count,
                "expected_singletons": round(expected_singletons, 2),
                "total_quadruples": total_quads,
                "unique_quadruples": len(quad_counts),
                "lambda": round(lambda_param, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 2097152 bits, got {n}",
                    "bits_needed": 2097152,
                },
            }

        # Konwertuj pary bitów na litery DNA (0-3)
        word_length = 10  # 10 liter DNA
        bits_per_letter = 2  # 2 bity na literę

        if HAS_NUMPY:
            # Numpy version
            num_letters = n // bits_per_letter
            bits_arr = np.array(bits[: num_letters * bits_per_letter], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_letters, bits_per_letter)

            # Konwertuj pary bitów na liczby 0-3
            letters = bits_reshaped[:, 0] * 2 + bits_reshaped[:, 1]

            # Twórz nakładające się 10-literowe słowa
            words = []
            for i in range(len(letters) - word_length + 1):
                word = tuple(letters[i : i + word_length].tolist())
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
                letter = bits[i * 2] * 2 + bits[i * 2 + 1]
                letters.append(letter)

            # Nakładające się słowa
            words = []
            for i in range(len(letters) - word_length + 1):
                word = tuple(letters[i : i + word_length])
                words.append(word)

            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Policz singletons
        singleton_count = sum(1 for count in word_counts.values() if count == 1)

        total_words = len(words)
        num_possible_words = 4**word_length  # 4 litery, 10-literowe słowa

        lambda_param = total_words / num_possible_words
        expected_singletons = num_possible_words * lambda_param * exp(-lambda_param)

        if expected_singletons > 0:
            chi_square = (
                singleton_count - expected_singletons
            ) ** 2 / expected_singletons
            # df = 1 (testujemy jedną kategorię)
            if HAS_GAMMAINCC:
                p_value = gammaincc(0.5, chi_square / 2)
            else:
                # Fallback: erfc approximation
                p_value = erfc((chi_square / 2) ** 0.5)
        else:
            p_value = 0.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "singleton_count": singleton_count,
                "expected_singletons": round(expected_singletons, 2),
                "total_words": total_words,
                "unique_words": len(word_counts),
                "lambda": round(lambda_param, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 256000 bits, got {n}",
                    "bits_needed": 256000,
                },
            }

        # Konwertuj bity na bajty i zlicz jedynki
        if HAS_NUMPY:
            # Numpy version
            num_bytes = n // 8
            bits_arr = np.array(bits[: num_bytes * 8], dtype=np.int8)
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
                byte_bits = bits[i * 8 : (i + 1) * 8]
                ones = sum(byte_bits)
                ones_counts.append(ones)

            observed = [0] * 9
            for count in ones_counts:
                observed[count] += 1

        # Teoretyczny rozkład dwumianowy B(8, 0.5)
        # P(k jedynek) = C(8,k) * 0.5^8
        expected = []
        for k in range(9):
            prob = comb(8, k) * (0.5**8)
            expected.append(prob * num_bytes)

        # Chi-square test
        chi_square = 0
        for i in range(9):
            if expected[i] > 0:
                obs = int(observed[i]) if HAS_NUMPY else observed[i]
                chi_square += (obs - expected[i]) ** 2 / expected[i]

        # Stopnie swobody = 8 (9 kategorii - 1)
        df = 8

        # P-value dla chi-square (użyj gammaincc jeśli dostępne)
        if HAS_GAMMAINCC:
            p_value = gammaincc(df / 2.0, chi_square / 2.0)
        else:
            # Fallback: aproksymacja normalna (mniej dokładna)
            from math import erfc

            p_value = erfc((chi_square / (2 * df)) ** 0.5)

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "chi_square": round(chi_square, 4),
                "num_bytes": num_bytes,
                "observed": observed.tolist() if HAS_NUMPY else observed,
                "expected": [round(e, 2) for e in expected],
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 384000 bits, got {n}",
                    "bits_needed": 384000,
                },
            }

        # Konwertuj bity na floaty [0,1] dla współrzędnych
        bits_per_coord = 16  # 16 bitów na współrzędną
        num_points = n // (bits_per_coord * 2)  # 2 współrzędne (x, y)

        if HAS_NUMPY:
            # Numpy version
            bits_arr = np.array(bits[: num_points * bits_per_coord * 2], dtype=np.int8)

            # Konwertuj grupy bitów na liczby 0-65535, potem normalizuj do [0,1]
            bits_grouped = bits_arr.reshape(num_points * 2, bits_per_coord)
            powers = 2 ** np.arange(bits_per_coord - 1, -1, -1, dtype=np.int32)
            coords = (bits_grouped * powers).sum(axis=1) / (2**bits_per_coord)

            # Rozdziel na x i y
            x = coords[0::2]
            y = coords[1::2]

            # Parkowanie: sprawdź kolizje (odległość < 2*radius)
            radius = 0.01  # Mały promień dla większej liczby samochodów
            parked = []

            for i in range(len(x)):
                can_park = True
                for px, py in parked:
                    dist = sqrt((float(x[i]) - px) ** 2 + (float(y[i]) - py) ** 2)
                    if dist < 2 * radius:
                        can_park = False
                        break
                if can_park:
                    parked.append((float(x[i]), float(y[i])))
        else:
            # Fallback
            coords = []
            for i in range(num_points * 2):
                coord_bits = bits[i * bits_per_coord : (i + 1) * bits_per_coord]
                value = 0
                for bit in coord_bits:
                    value = (value << 1) | bit
                coords.append(value / (2**bits_per_coord))

            x = coords[0::2]
            y = coords[1::2]

            radius = 0.01
            parked = []

            for i in range(len(x)):
                can_park = True
                for px, py in parked:
                    dist = sqrt((x[i] - px) ** 2 + (y[i] - py) ** 2)
                    if dist < 2 * radius:
                        can_park = False
                        break
                if can_park:
                    parked.append((x[i], y[i]))

        num_parked = len(parked)

        # Teoretyczna wartość według oryginalnego testu Diehard:
        # Dla 12,000 prób w kwadracie 100×100 z kołami o promieniu 1:
        # średnia = 3523, sigma = 21.9
        # Skalujemy proporcjonalnie dla innych liczb prób
        standard_attempts = 12000
        standard_mean = 3523.0
        standard_sigma = 21.9

        # Skalowanie liniowe względem liczby prób
        expected = standard_mean * (num_points / standard_attempts)
        sigma = standard_sigma * sqrt(num_points / standard_attempts)

        # Test normalności (k-3523)/21.9 ~ N(0,1) dla standardowych parametrów
        if sigma > 0:
            z_score = abs(num_parked - expected) / sigma
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "num_parked": num_parked,
                "num_attempted": num_points,
                "expected": round(expected, 2),
                "sigma": round(sigma, 2),
                "z_score": round(z_score, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 100000 bits, got {n}",
                    "bits_needed": 100000,
                },
            }

        # Konwertuj bity na 32-bitowe integery
        if HAS_NUMPY:
            # Numpy version
            num_ints = n // 32
            bits_arr = np.array(bits[: num_ints * 32], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_ints, 32)
            powers = 2 ** np.arange(31, -1, -1, dtype=np.int64)
            integers = (bits_reshaped * powers).sum(axis=1)

            # Konwertuj też na floaty [0,1] dla mnożników
            floats = integers / (2**32)

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
                int_bits = bits[i * 32 : (i + 1) * 32]
                value = 0
                for bit in int_bits:
                    value = (value << 1) | bit
                integers.append(value)

            floats = [x / (2**32) for x in integers]

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
            variance = sum((x - mean_count) ** 2 for x in squeeze_counts) / len(
                squeeze_counts
            )
            std_count = sqrt(variance)

        # Teoretyczna średnia według oryginalnego Diehard (z symulacji):
        # Dla k = 2^31, squeeze process ma średnią ~47 iteracji
        # Wartość ta została określona empirycznie przez Marsaglia
        # Dla prawdziwie losowych U~Uniform(0,1):
        # E[iteracje] = -ln(2^31) / E[ln(U)] = ln(2^31) / 1 ≈ 21.5 * ln(2) ≈ 14.9
        # Jednak praktyczna wartość z symulacji to ~47 dla pełnego algorytmu
        expected_mean = 47.0  # Wartość empiryczna z oryginalnego Diehard

        # Test normalności: (mean - 47) / (std/sqrt(n)) ~ N(0,1)
        if std_count > 0 and len(squeeze_counts) > 0:
            # Błąd standardowy średniej
            se = std_count / sqrt(len(squeeze_counts))
            z_score = abs(mean_count - expected_mean) / se if se > 0 else 0
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "mean_squeezes": round(mean_count, 2),
                "std_squeezes": round(std_count, 2),
                "expected_mean": expected_mean,
                "num_samples": len(squeeze_counts),
                "z_score": round(z_score, 4),
                "note": "Expected mean from Diehard empirical simulation",
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 100000 bits, got {n}",
                    "bits_needed": 100000,
                },
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
            run_counts = np.zeros(
                7, dtype=np.int32
            )  # 0: len=1, 1: len=2, ..., 6: len>=7
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
                if bits[i] == bits[i - 1]:
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
        prob_7plus = 2 * (0.5**8)
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
        p_value = erfc((chi_square / (2 * df)) ** 0.5)

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "chi_square": round(chi_square, 4),
                "total_runs": total_runs,
                "observed": run_counts.tolist() if HAS_NUMPY else run_counts,
                "expected": [round(e, 2) for e in expected],
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 200000 bits, got {n}",
                    "bits_needed": 200000,
                },
            }

        # Konwertuj bity na rzuty kostką (1-6)
        # Każdy rzut = 3 bity (0-7), odrzucamy 6,7 i próbujemy ponownie
        def bits_to_dice(bits_arr, start_idx):
            """Konwertuj 3 bity na rzut kostką (1-6)"""
            while start_idx + 2 < len(bits_arr):
                if HAS_NUMPY:
                    value = int(
                        bits_arr[start_idx] * 4
                        + bits_arr[start_idx + 1] * 2
                        + bits_arr[start_idx + 2]
                    )
                else:
                    value = (
                        bits_arr[start_idx] * 4
                        + bits_arr[start_idx + 1] * 2
                        + bits_arr[start_idx + 2]
                    )

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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": "Not enough complete games",
                    "total_games": total_games,
                },
            }

        # Teoretyczna szansa wygranej w craps ≈ 0.493
        expected_wins = total_games * 0.493
        expected_losses = total_games * 0.507

        # Chi-square test
        chi_square = (games_won - expected_wins) ** 2 / expected_wins + (
            games_lost - expected_losses
        ) ** 2 / expected_losses

        df = 1
        p_value = erfc((chi_square / (2 * df)) ** 0.5)

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "chi_square": round(chi_square, 4),
                "games_won": games_won,
                "games_lost": games_lost,
                "total_games": total_games,
                "win_rate": round(games_won / total_games, 4),
                "expected_win_rate": 0.493,
                "threshold": 0.001,
            },
        }

    def _diehard_minimum_distance_test(self, bits: List[int]) -> Dict[str, Any]:
        """
        Diehard Minimum Distance Test

        Zgodnie z oryginalnym testem Diehard:
        Losuje 8000 punktów w kwadracie 10000×10000, następnie znajduje
        minimalną odległość d między parami. KWADRAT tej odległości (d²)
        powinien mieć rozkład wykładniczy ze średnią 0.995.

        Test wykonuje się 100 razy i stosuje KS test na wartości
        1 - exp(-d²/0.995), które powinny być jednorodne w [0,1).

        Minimum: 200000 bitów
        """
        from math import exp, sqrt

        n = len(bits)

        if n < 200000:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 200000 bits, got {n}",
                    "bits_needed": 200000,
                },
            }

        # Parametry zgodne z oryginalnym Diehard
        square_size = 10000  # Rozmiar kwadratu
        points_per_sample = 8000  # Liczba punktów na próbę
        num_samples = 100  # Liczba powtórzeń (dla KS testu)

        # Ile bitów potrzebujemy na współrzędną?
        # Dla 10000 pozycji potrzebujemy ~14 bitów (2^14 = 16384 > 10000)
        bits_per_coord = 14
        bits_per_point = bits_per_coord * 2  # x i y

        total_bits_needed = points_per_sample * bits_per_point * num_samples

        if n < total_bits_needed:
            # Dostosuj num_samples jeśli nie ma wystarczająco bitów
            num_samples = n // (points_per_sample * bits_per_point)
            if num_samples < 10:
                return {
                    "passed": False,
                    "score": 0.0,
                    "statistics": {
                        "error": f"Need at least {points_per_sample * bits_per_point * 10} bits for minimum 10 samples",
                        "bits_needed": points_per_sample * bits_per_point * 10,
                    },
                }

        # Dla każdej próbki znajdź minimalną odległość
        uniform_values = []  # Wartości 1 - exp(-d²/0.995)

        bit_idx = 0
        for sample_idx in range(num_samples):
            # Generuj punkty dla tej próbki
            points = []
            for _ in range(points_per_sample):
                if bit_idx + bits_per_point > len(bits):
                    break

                # Konwertuj bity na współrzędne x, y w zakresie [0, square_size)
                x_bits = bits[bit_idx : bit_idx + bits_per_coord]
                y_bits = bits[bit_idx + bits_per_coord : bit_idx + bits_per_point]

                x_val = 0
                for bit in x_bits:
                    x_val = (x_val << 1) | bit
                y_val = 0
                for bit in y_bits:
                    y_val = (y_val << 1) | bit

                # Skaluj do [0, square_size)
                x = (x_val / (2**bits_per_coord)) * square_size
                y = (y_val / (2**bits_per_coord)) * square_size

                points.append((x, y))
                bit_idx += bits_per_point

            if len(points) < points_per_sample:
                break

            # Znajdź minimalną odległość między parami punktów
            min_dist_squared = float("inf")

            # Optymalizacja: nie sprawdzaj wszystkich par, tylko losową próbkę
            # lub użyj bardziej efektywnego algorytmu
            for i in range(len(points)):
                for j in range(i + 1, len(points)):
                    dx = points[i][0] - points[j][0]
                    dy = points[i][1] - points[j][1]
                    dist_squared = dx * dx + dy * dy
                    if dist_squared < min_dist_squared:
                        min_dist_squared = dist_squared

            # Przekształć d² do wartości jednorodnej [0,1) używając CDF rozkładu wykładniczego
            # Dla Exp(mean=0.995): CDF(x) = 1 - exp(-x/0.995)
            mean_exp = 0.995
            uniform_val = 1.0 - exp(-min_dist_squared / mean_exp)
            uniform_values.append(uniform_val)

        if len(uniform_values) < 10:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Not enough samples generated, got {len(uniform_values)}",
                    "samples_needed": 10,
                },
            }

        # Kolmogorov-Smirnov test na jednorodność
        # Sortuj wartości
        sorted_vals = sorted(uniform_values)
        n_vals = len(sorted_vals)

        # Oblicz statystykę KS: max|F_empirical(x) - F_theoretical(x)|
        ks_stat = 0.0
        for i, val in enumerate(sorted_vals):
            # F_empirical(val) = (i+1)/n
            # F_theoretical(val) = val (dla uniform [0,1))
            f_emp = (i + 1) / n_vals
            f_theo = val
            ks_stat = max(ks_stat, abs(f_emp - f_theo))

        # P-value dla KS testu (aproksymacja)
        # Dla dużych n: P(D > d) ≈ 2 * sum_{k=1}^∞ (-1)^(k-1) exp(-2k²n d²)
        # Uproszczona wersja: używamy asymptotycznej formuły
        from math import sqrt

        ks_stat_adjusted = ks_stat * sqrt(n_vals)

        # Kolmogorov distribution approximation
        p_value = min(1.0, 2.0 * exp(-2.0 * ks_stat_adjusted**2))

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "ks_statistic": round(ks_stat, 6),
                "num_samples": len(uniform_values),
                "mean_uniform": round(sum(uniform_values) / len(uniform_values), 4),
                "expected_mean_uniform": 0.5,
                "note": "Tests d² ~ Exponential(mean=0.995)",
                "threshold": 0.001,
            },
        }

        # Konwertuj bity na punkty 2D w [0,1]x[0,1]
        bits_per_coord = 10  # 10 bitów na współrzędną
        num_points = n // (bits_per_coord * 2)

        if num_points < 100:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {"error": f"Need at least 100 points, got {num_points}"},
            }

        if HAS_NUMPY:
            # Numpy version
            bits_arr = np.array(bits[: num_points * bits_per_coord * 2], dtype=np.int8)
            bits_grouped = bits_arr.reshape(num_points * 2, bits_per_coord)
            powers = 2 ** np.arange(bits_per_coord - 1, -1, -1, dtype=np.int32)
            coords = (bits_grouped * powers).sum(axis=1) / (2**bits_per_coord)

            points = coords.reshape(num_points, 2)

            # Oblicz minimalną odległość dla każdego punktu do najbliższego sąsiada
            min_distances = []
            for i in range(min(num_points, 500)):  # Limit dla wydajności
                dists = np.sqrt(np.sum((points - points[i]) ** 2, axis=1))
                dists[i] = float("inf")  # Ignoruj siebie
                min_dist = float(np.min(dists))
                min_distances.append(min_dist)
        else:
            # Fallback
            coords = []
            for i in range(num_points * 2):
                coord_bits = bits[i * bits_per_coord : (i + 1) * bits_per_coord]
                value = 0
                for bit in coord_bits:
                    value = (value << 1) | bit
                coords.append(value / (2**bits_per_coord))

            points = [(coords[i * 2], coords[i * 2 + 1]) for i in range(num_points)]

            min_distances = []
            for i in range(min(num_points, 500)):
                min_dist = float("inf")
                for j in range(num_points):
                    if i != j:
                        dist = sqrt(
                            (points[i][0] - points[j][0]) ** 2
                            + (points[i][1] - points[j][1]) ** 2
                        )
                        min_dist = min(min_dist, dist)
                min_distances.append(min_dist)

        # Analiza rozkładu minimalnych odległości
        if HAS_NUMPY:
            mean_dist = float(np.mean(min_distances))
            std_dist = float(np.std(min_distances))
        else:
            mean_dist = sum(min_distances) / len(min_distances)
            variance = sum((x - mean_dist) ** 2 for x in min_distances) / len(
                min_distances
            )
            std_dist = sqrt(variance)

        # Teoretyczna średnia odległość zależy od gęstości punktów
        expected_mean = sqrt(1.0 / num_points)  # Przybliżone

        if std_dist > 0:
            z_score = abs(mean_dist - expected_mean) / std_dist
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "mean_distance": round(mean_dist, 6),
                "std_distance": round(std_dist, 6),
                "expected_mean": round(expected_mean, 6),
                "num_points": num_points,
                "num_samples": len(min_distances),
                "z_score": round(z_score, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 150000 bits, got {n}",
                    "bits_needed": 150000,
                },
            }

        # Konwertuj bity na punkty 3D w [0,1]^3
        bits_per_coord = 10  # 10 bitów na współrzędną
        num_points = n // (bits_per_coord * 3)  # 3 współrzędne (x, y, z)

        if num_points < 100:
            return {
                "passed": False,
                "score": 0.0,
                "statistics": {"error": f"Need at least 100 points, got {num_points}"},
            }

        if HAS_NUMPY:
            # Numpy version
            bits_arr = np.array(bits[: num_points * bits_per_coord * 3], dtype=np.int8)
            bits_grouped = bits_arr.reshape(num_points * 3, bits_per_coord)
            powers = 2 ** np.arange(bits_per_coord - 1, -1, -1, dtype=np.int32)
            coords = (bits_grouped * powers).sum(axis=1) / (2**bits_per_coord)

            # Rozdziel na x, y, z
            x = coords[0::3]
            y = coords[1::3]
            z = coords[2::3]

            # Sfera z centrum w (0.5, 0.5, 0.5), promień 0.5
            center = 0.5
            radius = 0.5

            # Oblicz odległości od centrum
            distances = np.sqrt(
                (x - center) ** 2 + (y - center) ** 2 + (z - center) ** 2
            )

            # Zlicz punkty wewnątrz sfery
            inside_count = int(np.sum(distances <= radius))
        else:
            # Fallback
            coords = []
            for i in range(num_points * 3):
                coord_bits = bits[i * bits_per_coord : (i + 1) * bits_per_coord]
                value = 0
                for bit in coord_bits:
                    value = (value << 1) | bit
                coords.append(value / (2**bits_per_coord))

            x = coords[0::3]
            y = coords[1::3]
            z = coords[2::3]

            center = 0.5
            radius = 0.5

            inside_count = 0
            for i in range(num_points):
                dist = sqrt(
                    (x[i] - center) ** 2 + (y[i] - center) ** 2 + (z[i] - center) ** 2
                )
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
            z_score = abs(inside_count - expected_inside) / sqrt(
                expected_inside * (1 - expected_ratio)
            )
            p_value = erfc(z_score / sqrt(2))
        else:
            z_score = 0.0
            p_value = 1.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "inside_count": inside_count,
                "outside_count": num_points - inside_count,
                "total_points": num_points,
                "inside_ratio": round(inside_count / num_points, 4),
                "expected_ratio": expected_ratio,
                "z_score": round(z_score, 4),
                "threshold": 0.001,
            },
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
                "passed": False,
                "score": 0.0,
                "statistics": {
                    "error": f"Need >= 100000 bits, got {n}",
                    "bits_needed": 100000,
                },
            }

        # Konwertuj grupy bitów na liczby [0,1]
        bits_per_num = 8  # 8 bitów na liczbę
        window_size = 10  # Rozmiar okna sumowania

        if HAS_NUMPY:
            # Numpy version
            num_values = n // bits_per_num
            bits_arr = np.array(bits[: num_values * bits_per_num], dtype=np.int8)
            bits_reshaped = bits_arr.reshape(num_values, bits_per_num)
            powers = 2 ** np.arange(bits_per_num - 1, -1, -1, dtype=np.int32)
            values = (bits_reshaped * powers).sum(axis=1) / (2**bits_per_num)

            # Oblicz sumy nakładających się okien
            sums = []
            for i in range(len(values) - window_size + 1):
                window_sum = float(np.sum(values[i : i + window_size]))
                sums.append(window_sum)

            mean_sum = float(np.mean(sums))
            std_sum = float(np.std(sums))
        else:
            # Fallback
            num_values = n // bits_per_num
            values = []

            for i in range(num_values):
                value_bits = bits[i * bits_per_num : (i + 1) * bits_per_num]
                value = 0
                for bit in value_bits:
                    value = (value << 1) | bit
                values.append(value / (2**bits_per_num))

            # Sumy nakładających się okien
            sums = []
            for i in range(len(values) - window_size + 1):
                window_sum = sum(values[i : i + window_size])
                sums.append(window_sum)

            mean_sum = sum(sums) / len(sums)
            variance = sum((x - mean_sum) ** 2 for x in sums) / len(sums)
            std_sum = sqrt(variance)

        # Teoretyczna średnia i odchylenie standardowe
        # Dla uniform [0,1], suma n wartości ma średnią n/2 i wariancję n/12
        expected_mean = window_size / 2.0
        expected_std = sqrt(window_size / 12.0)

        # Test normalności (z-score)
        if std_sum > 0:
            z_score_mean = abs(mean_sum - expected_mean) / (
                expected_std / sqrt(len(sums))
            )
            z_score_std = abs(std_sum - expected_std) / (
                expected_std / sqrt(2 * len(sums))
            )

            # Łączny test
            chi_square = z_score_mean**2 + z_score_std**2
            p_value = erfc(sqrt(chi_square / 2))
        else:
            chi_square = 0.0
            p_value = 1.0

        passed = 0.001 <= p_value <= 0.999
        score = min(1.0, p_value)

        return {
            "passed": passed,
            "score": round(score, 4),
            "statistics": {
                "p_value": round(p_value, 6),
                "mean_sum": round(mean_sum, 4),
                "std_sum": round(std_sum, 4),
                "expected_mean": round(expected_mean, 4),
                "expected_std": round(expected_std, 4),
                "num_sums": len(sums),
                "chi_square": round(chi_square, 4),
                "threshold": 0.001,
            },
        }
