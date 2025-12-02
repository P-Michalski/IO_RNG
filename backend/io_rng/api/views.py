"""
Django REST Framework Views - API Endpoints
Warstwa prezentacji - obsługa HTTP requests/responses.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg

from io_rng.core.entities.rng import RNG, Language, Algorithm
from io_rng.core.use_cases.run_rng_test import RunRNGTestUseCase
from io_rng.infrastructure.models import RNGModel, TestResultModel
from io_rng.infrastructure.repositories.django_repositories import (
    DjangoRNGRepository,
    DjangoTestResultRepository
)
from io_rng.infrastructure.runners.python_runner import PythonRNGRunner
from io_rng.api.serializers import (
    RNGSerializer,
    TestResultSerializer,
    RunTestRequestSerializer,
    RNGDetailSerializer
)


class RNGViewSet(viewsets.ViewSet):
    """
    ViewSet dla RNG - Clean Architecture approach.
    Views są cienkie - przekazują pracę do use cases.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection - inicjalizacja repozytoriów i use cases
        self.rng_repository = DjangoRNGRepository()
        self.result_repository = DjangoTestResultRepository()
        self.runners = [PythonRNGRunner()]  # Możesz dodać więcej runnerów

    def list(self, request):
        """
        GET /api/rngs/
        Lista wszystkich RNG.
        """
        rngs = self.rng_repository.get_all()
        serializer = RNGSerializer(rngs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET /api/rngs/{id}/
        Szczegóły konkretnego RNG.
        """
        rng = self.rng_repository.get_by_id(int(pk))
        if not rng:
            return Response(
                {"error": "RNG not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RNGSerializer(rng)
        return Response(serializer.data)

    def create(self, request):
        """
        POST /api/rngs/
        Tworzenie nowego RNG.
        """
        serializer = RNGSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Konwersja z dict na entity
        data = serializer.validated_data
        rng = RNG(
            name=data['name'],
            language=Language(data['language']),
            algorithm=Algorithm(data['algorithm']),
            description=data['description'],
            code_path=data['code_path'],
            is_active=data.get('is_active', True)
        )

        # Zapisz przez repozytorium
        saved_rng = self.rng_repository.save(rng)

        return Response(
            RNGSerializer(saved_rng).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        """
        PUT /api/rngs/{id}/
        Aktualizacja RNG.
        """
        rng = self.rng_repository.get_by_id(int(pk))
        if not rng:
            return Response(
                {"error": "RNG not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RNGSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Aktualizuj entity
        data = serializer.validated_data
        rng.name = data['name']
        rng.language = Language(data['language'])
        rng.algorithm = Algorithm(data['algorithm'])
        rng.description = data['description']
        rng.code_path = data['code_path']
        rng.is_active = data.get('is_active', True)

        updated_rng = self.rng_repository.update(rng)

        return Response(RNGSerializer(updated_rng).data)

    def destroy(self, request, pk=None):
        """
        DELETE /api/rngs/{id}/
        Usunięcie RNG.
        """
        success = self.rng_repository.delete(int(pk))
        if not success:
            return Response(
                {"error": "RNG not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def run_test(self, request, pk=None):
        """
        POST /api/rngs/{id}/run_test/
        Uruchamia test dla RNG - to jest główna akcja!
        """
        # Walidacja parametrów
        serializer = RunTestRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        # Wywołaj Use Case
        use_case = RunRNGTestUseCase(
            rng_repository=self.rng_repository,
            result_repository=self.result_repository,
            runners=self.runners
        )

        try:
            result = use_case.execute(
                rng_id=int(pk),
                test_name=data['test_name'],
                samples_count=data['samples_count'],
                seed=data.get('seed')
            )

            return Response(
                TestResultSerializer(result).data,
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except RuntimeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def test_results(self, request, pk=None):
        """
        GET /api/rngs/{id}/test_results/
        Pobiera wyniki testów dla RNG.
        """
        results = self.result_repository.get_by_rng(int(pk))
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)


class TestResultViewSet(viewsets.ViewSet):
    """ViewSet dla wyników testów"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = DjangoTestResultRepository()

    def list(self, request):
        """
        GET /api/test-results/
        Lista wyników testów (najnowsze).
        """
        limit = int(request.query_params.get('limit', 20))
        results = self.repository.get_latest(limit)
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET /api/test-results/{id}/
        Szczegóły wyniku testu.
        """
        result = self.repository.get_by_id(int(pk))
        if not result:
            return Response(
                {"error": "Test result not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TestResultSerializer(result)
        return Response(serializer.data)