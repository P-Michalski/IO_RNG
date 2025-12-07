"""
RNG Runner Interface - Port
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from io_rng.core.entities.rng import RNG


class IRNGRunner(ABC):
    """Interface dla runnerów RNG"""

    @abstractmethod
    def can_run(self, rng: RNG) -> bool:
        """
        Sprawdza czy runner może uruchomić dany RNG.

        Args:
            rng: RNG entity

        Returns:
            True jeśli runner obsługuje ten język
        """
        pass

    @abstractmethod
    def generate_numbers(
        self,
        rng: RNG,
        count: int,
        seed: int = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Generuje liczby losowe z opcjonalnymi parametrami.

        Args:
            rng: RNG entity
            count: Liczba liczb do wygenerowania
            seed: Opcjonalny seed dla powtarzalności
            parameters: Opcjonalne parametry (override rng.parameters)

        Returns:
            Lista liczb float w zakresie [0.0, 1.0]
        """
        pass

    @abstractmethod
    def validate_setup(self, rng: RNG) -> bool:
        """
        Waliduje czy generator jest poprawnie skonfigurowany.

        Args:
            rng: RNG entity

        Returns:
            True jeśli generator może być uruchomiony
        """
        pass