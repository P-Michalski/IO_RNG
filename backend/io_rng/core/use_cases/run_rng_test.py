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
            numbers = runner.generate_numbers(rng, samples_count, seed, parameters)
        except Exception as e:
            return self._create_error_result(rng_id, test_name, str(e))

        execution_time = (time.perf_counter() - start_time) * 1000  # ms

        # 4. Wykonaj test statystyczny
        test_result = self._perform_statistical_test(numbers, test_name)

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
        test_name: str
    ) -> Dict[str, Any]:
        """
        Wykonuje test statystyczny na liczbach losowych.

        Args:
            numbers: Lista liczb float w zakresie [0, 1]
            test_name: Nazwa testu do wykonania

        Returns:
            Słownik z wynikami: {'passed': bool, 'score': float, 'statistics': dict}

        Raises:
            ValueError: Jeśli test_name jest nieznany
        """

        if test_name == "frequency_test":
            return self._frequency_test(numbers)
        elif test_name == "uniformity_test":
            return self._uniformity_test(numbers)
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