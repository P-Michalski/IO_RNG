"""
TestResult Entity - Domain Model
Reprezentuje wynik pojedynczego testu RNG.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class TestResult:
    """
    Entity reprezentująca wynik testu RNG.
    Niezależna od implementacji bazy danych.
    """
    rng_id: int
    test_name: str
    passed: bool
    score: float
    execution_time_ms: float
    samples_count: int
    statistics: Dict[str, Any]
    error_message: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Walidacja danych"""
        if self.score < 0 or self.score > 1:
            raise ValueError("Score must be between 0 and 1")
        if self.samples_count <= 0:
            raise ValueError("Samples count must be positive")
        if self.execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative")

    def is_successful(self) -> bool:
        """Sprawdza czy test zakończył się sukcesem"""
        return self.passed and self.error_message is None

    def get_quality_rating(self) -> str:
        """Zwraca rating jakości na podstawie wyniku"""
        if not self.passed:
            return "FAILED"
        if self.score >= 0.95:
            return "EXCELLENT"
        elif self.score >= 0.80:
            return "GOOD"
        elif self.score >= 0.60:
            return "ACCEPTABLE"
        else:
            return "POOR"