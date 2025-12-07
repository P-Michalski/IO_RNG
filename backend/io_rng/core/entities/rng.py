"""
RNG Entity - Domain Model
Reprezentuje generator liczb losowych niezależnie od frameworka.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class Language(Enum):
    """Wspierane języki programowania"""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    GO = "go"


class Algorithm(Enum):
    """Algorytmy RNG"""
    LINEAR_CONGRUENTIAL = "linear_congruential"
    MERSENNE_TWISTER = "mersenne_twister"
    XORSHIFT = "xorshift"
    PCG = "pcg"
    BUILTIN = "builtin"
    SPLITMIX = "splitmix"
    SYSTEM = "system"
    CUSTOM = "custom"
    AWC = "awc"


@dataclass
class RNG:
    """
    Entity reprezentująca generator liczb losowych.
    Pure domain object - bez zależności od Django/bazy danych.
    """
    name: str
    language: Language
    algorithm: Algorithm
    description: str
    code_path: str
    parameters: Optional[Dict[str, Any]] = None
    id: Optional[int] = None
    is_active: bool = True

    def __post_init__(self):
        """Walidacja po inicjalizacji"""
        if not self.name:
            raise ValueError("RNG name cannot be empty")
        if not self.code_path:
            raise ValueError("Code path cannot be empty")

        # Domyślne parametry jeśli None
        if self.parameters is None:
            self.parameters = {}

    def validate_for_execution(self) -> bool:
        """Sprawdza czy RNG jest gotowy do uruchomienia"""
        return self.is_active and bool(self.code_path)

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Pobiera parametr generatora"""
        return self.parameters.get(key, default) if self.parameters else default