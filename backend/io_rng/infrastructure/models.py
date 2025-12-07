"""
Django Models - Infrastructure Layer
"""
from django.db import models


class RNGModel(models.Model):
    """Django model dla RNG"""
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=50)
    algorithm = models.CharField(max_length=100)
    description = models.TextField()
    code_path = models.CharField(max_length=500)
    parameters = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rngs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.algorithm})"


class TestResultModel(models.Model):
    """Django model dla wyników testów"""
    rng = models.ForeignKey(
        RNGModel,
        on_delete=models.CASCADE,
        related_name='test_results'
    )
    test_name = models.CharField(max_length=100)
    passed = models.BooleanField()
    score = models.FloatField()
    execution_time_ms = models.FloatField()
    samples_count = models.IntegerField()
    statistics = models.JSONField()
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_results'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rng', '-created_at']),
            models.Index(fields=['test_name', '-created_at']),
        ]

    def __str__(self):
        return f"{self.rng.name} - {self.test_name} ({'PASS' if self.passed else 'FAIL'})"