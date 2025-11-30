"""
Repository Interfaces - Ports
Abstrakcje dla operacji na danych (persistence layer).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from io_rng.core.entities.rng import RNG
from io_rng.core.entities.test_result import TestResult


class IRNGRepository(ABC):
    """Interface dla repozytorium RNG"""

    @abstractmethod
    def save(self, rng: RNG) -> RNG:
        """Zapisuje RNG i zwraca z przypisanym ID"""
        pass

    @abstractmethod
    def get_by_id(self, rng_id: int) -> Optional[RNG]:
        """Pobiera RNG po ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[RNG]:
        """Pobiera wszystkie RNG"""
        pass

    @abstractmethod
    def get_by_language(self, language: str) -> List[RNG]:
        """Pobiera RNG dla danego języka"""
        pass

    @abstractmethod
    def delete(self, rng_id: int) -> bool:
        """Usuwa RNG"""
        pass

    @abstractmethod
    def update(self, rng: RNG) -> RNG:
        """Aktualizuje RNG"""
        pass


class ITestResultRepository(ABC):
    """Interface dla repozytorium wyników testów"""

    @abstractmethod
    def save(self, result: TestResult) -> TestResult:
        """Zapisuje wynik testu"""
        pass

    @abstractmethod
    def get_by_id(self, result_id: int) -> Optional[TestResult]:
        """Pobiera wynik po ID"""
        pass

    @abstractmethod
    def get_by_rng(self, rng_id: int) -> List[TestResult]:
        """Pobiera wszystkie wyniki dla danego RNG"""
        pass

    @abstractmethod
    def get_latest(self, limit: int = 10) -> List[TestResult]:
        """Pobiera najnowsze wyniki"""
        pass

    @abstractmethod
    def delete(self, result_id: int) -> bool:
        """Usuwa wynik"""
        pass
