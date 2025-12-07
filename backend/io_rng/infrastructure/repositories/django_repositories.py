"""
Django ORM Repositories - Infrastructure Layer
"""
from typing import List, Optional
from io_rng.core.entities.rng import RNG, Language, Algorithm
from io_rng.core.entities.test_result import TestResult
from io_rng.core.interfaces.repositories import IRNGRepository, ITestResultRepository
from io_rng.infrastructure.models import RNGModel, TestResultModel


class DjangoRNGRepository(IRNGRepository):
    """Repository dla RNG używający Django ORM"""

    def get_by_id(self, rng_id: int) -> Optional[RNG]:
        """Pobiera RNG po ID"""
        try:
            model = RNGModel.objects.get(id=rng_id)
            return self._to_entity(model)
        except RNGModel.DoesNotExist:
            return None

    def get_all(self) -> List[RNG]:
        """Pobiera wszystkie RNG"""
        models = RNGModel.objects.all()
        return [self._to_entity(m) for m in models]

    def get_by_language(self, language: str) -> List[RNG]:  # ← str!
        """Pobiera RNG według języka"""
        models = RNGModel.objects.filter(language=language)
        return [self._to_entity(m) for m in models]

    def save(self, rng: RNG) -> RNG:
        """Zapisuje RNG (create lub update)"""
        if rng.id:
            # Update
            model = RNGModel.objects.get(id=rng.id)
            model.name = rng.name
            model.language = rng.language.value
            model.algorithm = rng.algorithm.value
            model.description = rng.description
            model.code_path = rng.code_path
            model.parameters = rng.parameters
            model.is_active = rng.is_active
        else:
            # Create
            model = RNGModel(
                name=rng.name,
                language=rng.language.value,
                algorithm=rng.algorithm.value,
                description=rng.description,
                code_path=rng.code_path,
                parameters=rng.parameters,
                is_active=rng.is_active
            )

        model.save()
        return self._to_entity(model)

    def update(self, rng: RNG) -> RNG:
        """Aktualizuje istniejący RNG"""
        if not rng.id:
            raise ValueError("Cannot update RNG without ID")

        try:
            model = RNGModel.objects.get(id=rng.id)
            model.name = rng.name
            model.language = rng.language.value
            model.algorithm = rng.algorithm.value
            model.description = rng.description
            model.code_path = rng.code_path
            model.parameters = rng.parameters
            model.is_active = rng.is_active
            model.save()

            return self._to_entity(model)
        except RNGModel.DoesNotExist:
            raise ValueError(f"RNG with id {rng.id} not found")

    def delete(self, rng_id: int) -> bool:
        """Usuwa RNG"""
        try:
            RNGModel.objects.get(id=rng_id).delete()
            return True
        except RNGModel.DoesNotExist:
            return False

    def _to_entity(self, model: RNGModel) -> RNG:
        """Konwertuje Django model na entity"""
        return RNG(
            id=model.id,
            name=model.name,
            language=Language(model.language),
            algorithm=Algorithm(model.algorithm),
            description=model.description,
            code_path=model.code_path,
            parameters=model.parameters or {},
            is_active=model.is_active
        )


class DjangoTestResultRepository(ITestResultRepository):
    """Repository dla TestResult używający Django ORM"""

    def save(self, result: TestResult) -> TestResult:
        """Zapisuje wynik testu"""
        model = TestResultModel(
            rng_id=result.rng_id,
            test_name=result.test_name,
            passed=result.passed,
            score=result.score,
            execution_time_ms=result.execution_time_ms,
            samples_count=result.samples_count,
            statistics=result.statistics,
            error_message=result.error_message
        )
        model.save()

        return self._to_entity(model)

    def get_by_id(self, result_id: int) -> Optional[TestResult]:
        """Pobiera wynik po ID"""
        try:
            model = TestResultModel.objects.get(id=result_id)
            return self._to_entity(model)
        except TestResultModel.DoesNotExist:
            return None

    def get_by_rng(self, rng_id: int) -> List[TestResult]:  # ← usuń limit z sygnatury!
        """Pobiera wyniki dla danego RNG"""
        models = TestResultModel.objects.filter(
            rng_id=rng_id
        ).order_by('-created_at')

        return [self._to_entity(m) for m in models]

    def get_latest(self, limit: int = 10) -> List[TestResult]:  # ← to pasuje do interface!
        """Pobiera najnowsze wyniki"""
        models = TestResultModel.objects.all().order_by('-created_at')[:limit]
        return [self._to_entity(m) for m in models]

    def delete(self, result_id: int) -> bool:  # ← DODAJ tę metodę!
        """Usuwa wynik testu"""
        try:
            TestResultModel.objects.get(id=result_id).delete()
            return True
        except TestResultModel.DoesNotExist:
            return False

    def _to_entity(self, model: TestResultModel) -> TestResult:
        """Konwertuje Django model na entity"""
        return TestResult(
            id=model.id,
            rng_id=model.rng_id,
            test_name=model.test_name,
            passed=model.passed,
            score=model.score,
            execution_time_ms=model.execution_time_ms,
            samples_count=model.samples_count,
            statistics=model.statistics,
            error_message=model.error_message,
            created_at=model.created_at
        )