"""
Django REST Framework Serializers
Konwersja między JSON a domenowymi entities.
"""
from rest_framework import serializers
from io_rng.core.entities.rng import Language, Algorithm


class RNGSerializer(serializers.Serializer):
    """Serializer dla RNG entity"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    language = serializers.ChoiceField(choices=[l.value for l in Language])
    algorithm = serializers.ChoiceField(choices=[a.value for a in Algorithm])
    description = serializers.CharField()
    code_path = serializers.CharField(max_length=500)
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
    created_at = serializers.DateTimeField(read_only=True)
    quality_rating = serializers.SerializerMethodField()

    def get_quality_rating(self, obj):
        """Dodaje rating jakości"""
        return obj.get_quality_rating()


class RunTestRequestSerializer(serializers.Serializer):
    """Serializer dla żądania uruchomienia testu"""

    test_name = serializers.ChoiceField(
        choices=['frequency_test', 'uniformity_test'],
        default='frequency_test'
    )
    samples_count = serializers.IntegerField(
        min_value=100,
        max_value=1000000,
        default=10000
    )
    seed = serializers.IntegerField(required=False, allow_null=True)


class RNGDetailSerializer(RNGSerializer):
    """Rozszerzony serializer RNG z wynikami testów"""

    recent_tests = TestResultSerializer(many=True, read_only=True, source='test_results')
    test_count = serializers.IntegerField(read_only=True)
    average_score = serializers.FloatField(read_only=True)