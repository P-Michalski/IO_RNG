"""
Test Result Entity - Domain Model
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class DataType(Enum):
    """Typ surowych danych z generatora"""
    BITS = "bits"
    INTEGERS = "integers"
    FLOATS = "floats"


@dataclass
class TestResult:
    """
    Entity reprezentująca wynik testu RNG.
    """
    rng_id: int
    test_name: str
    passed: bool
    score: float
    execution_time_ms: float
    samples_count: int
    statistics: Dict[str, Any]
    id: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Walidacja"""
        if self.score < 0 or self.score > 1:
            raise ValueError("Score must be between 0 and 1")
        if self.samples_count < 0:
            raise ValueError("Samples count cannot be negative")