"""
RNG Runner Interface - Port
Abstrakcja do uruchamiania generatorów liczb losowych.
Pozwala na różne implementacje dla różnych języków.
"""
from abc import ABC, abstractmethod
from typing import List
from io_rng.core.entities.rng import RNG


class IRNGRunner(ABC):
    """
    Interface definiujący kontrakt dla runnerów RNG.
    Każdy język będzie miał swoją implementację.
    """

    @abstractmethod
    def can_run(self, rng: RNG) -> bool:
        """
        Sprawdza czy runner obsługuje dany RNG.

        Args:
            rng: Entity RNG do sprawdzenia

        Returns:
            True jeśli runner może uruchomić ten RNG
        """
        pass

    @abstractmethod
    def generate_numbers(self, rng: RNG, count: int, seed: int = None) -> List[float]:
        """
        Generuje liczby losowe używając danego RNG.

        Args:
            rng: Entity RNG do uruchomienia
            count: Liczba liczb do wygenerowania
            seed: Opcjonalny seed dla powtarzalności

        Returns:
            Lista wygenerowanych liczb (0.0 - 1.0)

        Raises:
            RuntimeError: Gdy nie można uruchomić RNG
        """
        pass

    @abstractmethod
    def validate_setup(self, rng: RNG) -> bool:
        """
        Sprawdza czy środowisko jest gotowe do uruchomienia RNG.

        Args:
            rng: Entity RNG do walidacji

        Returns:
            True jeśli setup jest poprawny
        """
        pass