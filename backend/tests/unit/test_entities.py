"""
Testy jednostkowe dla encji domenowych
"""

import pytest
from io_rng.core.entities.rng import RNG, Language, Algorithm
from io_rng.core.entities.test_result import TestResult, DataType


class TestRNGEntity:
    """Testy dla encji RNG"""

    def test_create_rng_with_valid_data(self):
        """Test tworzenia RNG z poprawnymi danymi"""
        rng = RNG(
            name="Test RNG",
            language=Language.PYTHON,
            algorithm=Algorithm.LINEAR_CONGRUENTIAL,
            description="Test description",
            code_path="test/path.py",
            parameters={"seed": 42},
        )

        assert rng.name == "Test RNG"
        assert rng.language == Language.PYTHON
        assert rng.algorithm == Algorithm.LINEAR_CONGRUENTIAL
        assert rng.parameters["seed"] == 42
        assert rng.is_active is True

    def test_rng_empty_name_raises_error(self):
        """Test walidacji pustej nazwy"""
        with pytest.raises(ValueError, match="RNG name cannot be empty"):
            RNG(
                name="",
                language=Language.PYTHON,
                algorithm=Algorithm.PCG,
                description="Test",
                code_path="test/path.py",
            )

    def test_rng_empty_code_path_raises_error(self):
        """Test walidacji pustej ścieżki kodu"""
        with pytest.raises(ValueError, match="Code path cannot be empty"):
            RNG(
                name="Test",
                language=Language.PYTHON,
                algorithm=Algorithm.PCG,
                description="Test",
                code_path="",
            )

    def test_rng_validate_for_execution_active(self):
        """Test walidacji RNG dla wykonania - aktywny"""
        rng = RNG(
            name="Test",
            language=Language.PYTHON,
            algorithm=Algorithm.PCG,
            description="Test",
            code_path="test/path.py",
            is_active=True,
        )

        assert rng.validate_for_execution() is True

    def test_rng_validate_for_execution_inactive(self):
        """Test walidacji RNG dla wykonania - nieaktywny"""
        rng = RNG(
            name="Test",
            language=Language.PYTHON,
            algorithm=Algorithm.PCG,
            description="Test",
            code_path="test/path.py",
            is_active=False,
        )

        assert rng.validate_for_execution() is False

    def test_rng_get_parameter_existing(self):
        """Test pobierania istniejącego parametru"""
        rng = RNG(
            name="Test",
            language=Language.PYTHON,
            algorithm=Algorithm.LINEAR_CONGRUENTIAL,
            description="Test",
            code_path="test/path.py",
            parameters={"seed": 42, "a": 1664525},
        )

        assert rng.get_parameter("seed") == 42
        assert rng.get_parameter("a") == 1664525

    def test_rng_get_parameter_non_existing_with_default(self):
        """Test pobierania nieistniejącego parametru z defaultem"""
        rng = RNG(
            name="Test",
            language=Language.PYTHON,
            algorithm=Algorithm.PCG,
            description="Test",
            code_path="test/path.py",
            parameters={},
        )

        assert rng.get_parameter("nonexistent", 999) == 999

    def test_rng_none_parameters_initialized_to_empty_dict(self):
        """Test inicjalizacji None parameters na pusty słownik"""
        rng = RNG(
            name="Test",
            language=Language.PYTHON,
            algorithm=Algorithm.PCG,
            description="Test",
            code_path="test/path.py",
            parameters=None,
        )

        assert rng.parameters == {}


class TestTestResultEntity:
    """Testy dla encji TestResult"""

    def test_create_test_result_with_valid_data(self):
        """Test tworzenia TestResult z poprawnymi danymi"""
        result = TestResult(
            rng_id=1,
            test_name="monobit",
            passed=True,
            score=0.85,
            execution_time_ms=123.45,
            samples_count=10000,
            statistics={"p_value": 0.5},
        )

        assert result.rng_id == 1
        assert result.test_name == "monobit"
        assert result.passed is True
        assert result.score == 0.85
        assert result.execution_time_ms == 123.45
        assert result.samples_count == 10000
        assert result.statistics["p_value"] == 0.5

    def test_test_result_score_above_one_raises_error(self):
        """Test walidacji score > 1"""
        with pytest.raises(ValueError, match="Score must be between 0 and 1"):
            TestResult(
                rng_id=1,
                test_name="test",
                passed=False,
                score=1.5,
                execution_time_ms=100,
                samples_count=1000,
                statistics={},
            )

    def test_test_result_score_below_zero_raises_error(self):
        """Test walidacji score < 0"""
        with pytest.raises(ValueError, match="Score must be between 0 and 1"):
            TestResult(
                rng_id=1,
                test_name="test",
                passed=False,
                score=-0.1,
                execution_time_ms=100,
                samples_count=1000,
                statistics={},
            )

    def test_test_result_negative_samples_count_raises_error(self):
        """Test walidacji ujemnej liczby próbek"""
        with pytest.raises(ValueError, match="Samples count cannot be negative"):
            TestResult(
                rng_id=1,
                test_name="test",
                passed=True,
                score=0.5,
                execution_time_ms=100,
                samples_count=-100,
                statistics={},
            )


class TestDataTypeEnum:
    """Testy dla enum DataType"""

    def test_data_type_bits(self):
        """Test typu BITS"""
        assert DataType.BITS.value == "bits"

    def test_data_type_integers(self):
        """Test typu INTEGERS"""
        assert DataType.INTEGERS.value == "integers"

    def test_data_type_floats(self):
        """Test typu FLOATS"""
        assert DataType.FLOATS.value == "floats"
