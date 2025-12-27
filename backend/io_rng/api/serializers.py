"""
Django REST Framework Serializers
Konwersja między JSON a domenowymi entities.
"""
from rest_framework import serializers
from io_rng.core.entities.rng import Language, Algorithm


# Lista dostępnych testów statystycznych (DRY - użyta w wielu serializerach)
TEST_CHOICES = [
    # Testy podstawowe
    'frequency_test',
    'uniformity_test',
    # Pełny zestaw NIST (15 testów)
    'nist_monobit',
    'nist_block_frequency',
    'nist_runs',
    'nist_longest_run',
    'nist_cumulative_sums',
    'nist_approximate_entropy',
    'nist_matrix_rank',
    'nist_dft',
    'nist_non_overlapping_template',
    'nist_overlapping_template',
    'nist_universal',
    'nist_linear_complexity',
    'nist_serial',
    'nist_random_excursions',
    'nist_random_excursions_variant',
    # Diehard Suite (5 podstawowych testów)
    'diehard_birthday_spacings',
    'diehard_overlapping_permutations',
    'diehard_binary_rank',
    'diehard_bitstream',
    'diehard_opso'
]


class RNGSerializer(serializers.Serializer):
    """Serializer dla RNG entity"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    language = serializers.ChoiceField(choices=[l.value for l in Language])
    algorithm = serializers.ChoiceField(choices=[a.value for a in Algorithm])
    description = serializers.CharField()
    code_path = serializers.CharField(max_length=500)
    parameters = serializers.JSONField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)

    def validate_name(self, value):
        """Walidacja nazwy"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()

    def validate_code_path(self, value):
        """Walidacja ścieżki"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Code path cannot be empty")
        return value.strip()


class TestResultSerializer(serializers.Serializer):
    """Serializer dla TestResult entity"""

    id = serializers.IntegerField(read_only=True)
    rng_id = serializers.IntegerField()
    test_name = serializers.CharField()
    passed = serializers.BooleanField()
    score = serializers.FloatField()
    execution_time_ms = serializers.FloatField()
    samples_count = serializers.IntegerField()
    statistics = serializers.JSONField()
    error_message = serializers.CharField(required=False, allow_null=True)
    generated_bits = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
        help_text="Raw bit array (legacy format, use bits_compressed when available)"
    )
    # Pola kompresji base64 (opcjonalne, użyj z ?compressed=true)
    bits_compressed = serializers.CharField(
        required=False,
        allow_null=True,
        read_only=True,
        help_text="Base64-encoded compressed bits"
    )
    bits_format = serializers.CharField(
        required=False,
        allow_null=True,
        read_only=True,
        help_text="Format: 'base64-bitpack' or 'array'"
    )
    bits_count = serializers.IntegerField(
        required=False,
        allow_null=True,
        read_only=True,
        help_text="Number of bits (for validation)"
    )
    created_at = serializers.DateTimeField(read_only=True)


class RunTestRequestSerializer(serializers.Serializer):
    """Serializer dla żądania uruchomienia testu"""

    test_name = serializers.ChoiceField(
        choices=TEST_CHOICES,
        default='frequency_test'
    )
    samples_count = serializers.IntegerField(
        min_value=100,
        max_value=10000000,
        default=10000
    )
    seed = serializers.IntegerField(required=False, allow_null=True)
    parameters = serializers.JSONField(required=False, allow_null=True)


class GenerateRequestSerializer(serializers.Serializer):
    """Serializer dla żądania generowania bitów"""

    count = serializers.IntegerField(
        min_value=100,
        max_value=10000000,
        default=1000,
        help_text="Liczba bitów do wygenerowania"
    )
    seed = serializers.IntegerField(required=False, allow_null=True)
    parameters = serializers.JSONField(required=False, allow_null=True)


class GenerateResponseSerializer(serializers.Serializer):
    """Serializer dla odpowiedzi z wygenerowanymi bitami"""

    bits = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=1),
        required=False,
        allow_null=True,
        help_text="Raw bit array (when compressed=false)"
    )
    # Pola kompresji base64 (opcjonalne, użyj z ?compressed=true)
    bits_compressed = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Base64-encoded compressed bits (when compressed=true)"
    )
    bits_format = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Format: 'base64-bitpack' or 'array'"
    )
    count = serializers.IntegerField(help_text="Liczba wygenerowanych bitów")
    execution_time_ms = serializers.FloatField(help_text="Czas wykonania w milisekundach")
    rng_id = serializers.IntegerField(help_text="ID generatora")
    rng_name = serializers.CharField(help_text="Nazwa generatora")
    seed = serializers.IntegerField(required=False, allow_null=True)


class RNGDetailSerializer(RNGSerializer):
    """Rozszerzony serializer RNG z wynikami testów"""

    recent_tests = TestResultSerializer(many=True, read_only=True, source='test_results')
    test_count = serializers.IntegerField(read_only=True)
    average_score = serializers.FloatField(read_only=True)


class CustomTestRequestSerializer(serializers.Serializer):
    """Serializer dla żądania custom testu na własnych bitach"""

    bits_compressed = serializers.CharField(
        required=True,
        help_text="Base64-encoded compressed bits (from generate endpoint)"
    )
    bits_count = serializers.IntegerField(
        required=True,
        min_value=100,
        max_value=10000000,
        help_text="Number of bits in compressed data"
    )
    test_name = serializers.ChoiceField(
        choices=TEST_CHOICES,
        required=True,
        help_text="Test to run on the bits"
    )


class CustomTestResponseSerializer(serializers.Serializer):
    """Serializer dla wyniku custom testu (bez zapisu do bazy)"""

    test_name = serializers.CharField()
    passed = serializers.BooleanField()
    score = serializers.FloatField()
    execution_time_ms = serializers.FloatField()
    samples_count = serializers.IntegerField()
    statistics = serializers.JSONField()
    # Brak: rng_id, id, created_at (nie zapisujemy do bazy)