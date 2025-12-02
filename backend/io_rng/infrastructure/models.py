"""
Django Models - Infrastructure Layer
Mapowanie encji domenowych na tabele bazy danych.
"""
from django.db import models


class RNGModel(models.Model):
    """Model Django dla RNG - mapowanie entity na tabelę DB"""

    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('javascript', 'JavaScript'),
        ('rust', 'Rust'),
        ('go', 'Go'),
    ]

    ALGORITHM_CHOICES = [
        ('linear_congruential', 'Linear Congruential'),
        ('mersenne_twister', 'Mersenne Twister'),
        ('xorshift', 'XORShift'),
        ('pcg', 'PCG'),
        ('builtin', 'Built-in'),
    ]

    name = models.CharField(max_length=200, unique=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    algorithm = models.CharField(max_length=50, choices=ALGORITHM_CHOICES)
    description = models.TextField()
    code_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rngs'
        ordering = ['-created_at']
        verbose_name = 'RNG'
        verbose_name_plural = 'RNGs'

    def __str__(self):
        return f"{self.name} ({self.language})"


class TestResultModel(models.Model):
    """Model Django dla wyników testów"""

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
        verbose_name = 'Test Result'
        verbose_name_plural = 'Test Results'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['rng', '-created_at']),
        ]

    def __str__(self):
        status = "✓" if self.passed else "✗"
        return f"{status} {self.rng.name} - {self.test_name}"
