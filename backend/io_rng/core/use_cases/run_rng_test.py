"""
Run RNG Test Use Case
Logika biznesowa uruchamiania testów generatorów.
"""
from typing import List, Dict, Any
import time
from datetime import datetime
from io_rng.core.entities.rng import RNG
from io_rng.core.entities.test_result import TestResult
from io_rng.core.interfaces.rng_runner import IRNGRunner
from io_rng.core.interfaces.repositories import IRNGRepository, ITestResultRepository


class RunRNGTestUseCase:
    """
    Use Case odpowiedzialny za uruchamianie testów RNG.
    Implementuje logikę biznesową niezależną od frameworka.
    """

    def __init__(
            self,
            rng_repository: IRNGRepository,
            result_repository: ITestResultRepository,
            runners: List[IRNGRunner]
    ):
        self.rng_repository = rng_repository
        self.result_repository = result_repository
        self.runners = runners

    def execute(
            self,
            rng_id: int,
            test_name: str = "frequency_test",
            samples_count: int = 10000,
            seed: int = None
    ) -> TestResult:
        """
        Uruchamia test dla danego RNG.

        Args:
            rng_id: ID generatora do przetestowania
            test_name: Nazwa testu do wykonania
            samples_count: Liczba próbek do wygenerowania
            seed: Opcjonalny seed dla powtarzalności

        Returns:
            TestResult z wynikami testu

        Raises:
            ValueError: Gdy RNG nie istnieje lub jest nieaktywny
            RuntimeError: Gdy nie można uruchomić testu
        """
        # 1. Pobierz RNG
        rng = self.rng_repository.get_by_id(rng_id)
        if not rng:
            raise ValueError(f"RNG with id {rng_id} not found")

        if not rng.validate_for_execution():
            raise ValueError(f"RNG {rng.name} is not ready for execution")

        # 2. Znajdź odpowiedni runner
        runner = self._find_runner(rng)
        if not runner:
            raise RuntimeError(f"No runner available for {rng.language.value}")

        # 3. Waliduj setup
        if not runner.validate_setup(rng):
            raise RuntimeError(f"Runner setup validation failed for {rng.name}")

        # 4. Uruchom generowanie liczb
        start_time = time.time()
        try:
            numbers = runner.generate_numbers(rng, samples_count, seed)
            execution_time = (time.time() - start_time) * 1000  # ms
        except Exception as e:
            # Zapisz wynik z błędem
            error_result = TestResult(
                rng_id=rng_id,
                test_name=test_name,
                passed=False,
                score=0.0,
                execution_time_ms=0.0,
                samples_count=samples_count,
                statistics={},
                error_message=str(e),
                created_at=datetime.now()
            )
            return self.result_repository.save(error_result)

        # 5. Wykonaj test statystyczny
        test_result = self._perform_statistical_test(
            numbers=numbers,
            test_name=test_name
        )

        # 6. Stwórz wynik
        result = TestResult(
            rng_id=rng_id,
            test_name=test_name,
            passed=test_result['passed'],
            score=test_result['score'],
            execution_time_ms=execution_time,
            samples_count=samples_count,
            statistics=test_result['statistics'],
            created_at=datetime.now()
        )

        # 7. Zapisz wynik
        return self.result_repository.save(result)

    def _find_runner(self, rng: RNG) -> IRNGRunner:
        """Znajduje runner obsługujący dany RNG"""
        for runner in self.runners:
            if runner.can_run(rng):
                return runner
        return None

    def _perform_statistical_test(
            self,
            numbers: List[float],
            test_name: str
    ) -> Dict[str, Any]:
        """
        Wykonuje test statystyczny na wygenerowanych liczbach.

        Tutaj implementujemy różne testy (frequency, chi-square, etc.)
        """
        if test_name == "frequency_test":
            return self._frequency_test(numbers)
        elif test_name == "uniformity_test":
            return self._uniformity_test(numbers)
        else:
            raise ValueError(f"Unknown test: {test_name}")

    def _frequency_test(self, numbers: List[float]) -> Dict[str, Any]:
        """
        Test częstotliwości - sprawdza czy liczby są równomiernie rozłożone.
        Prosty test dla przykładu.
        """
        # Podziel zakres [0,1] na 10 binów
        bins = [0] * 10
        for num in numbers:
            bin_index = min(int(num * 10), 9)
            bins[bin_index] += 1

        # Oczekiwana liczba w każdym binie
        expected = len(numbers) / 10

        # Oblicz chi-square statistic
        chi_square = sum((observed - expected) ** 2 / expected for observed in bins)

        # Dla 9 stopni swobody, wartość krytyczna (p=0.05) ≈ 16.919
        passed = chi_square < 16.919

        # Score: im bliżej 0, tym lepiej (normalizujemy do 0-1)
        score = max(0, 1 - (chi_square / 30))

        return {
            'passed': passed,
            'score': score,
            'statistics': {
                'chi_square': chi_square,
                'bins': bins,
                'expected_per_bin': expected
            }
        }

    def _uniformity_test(self, numbers: List[float]) -> Dict[str, Any]:
        """Test uniformity - prosty przykład"""
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)

        # Dla uniform distribution [0,1]: mean ≈ 0.5, variance ≈ 0.083
        mean_diff = abs(mean - 0.5)
        var_diff = abs(variance - 0.083)

        passed = mean_diff < 0.05 and var_diff < 0.02
        score = max(0, 1 - (mean_diff * 10 + var_diff * 5))

        return {
            'passed': passed,
            'score': score,
            'statistics': {
                'mean': mean,
                'variance': variance,
                'expected_mean': 0.5,
                'expected_variance': 0.083
            }
        }
