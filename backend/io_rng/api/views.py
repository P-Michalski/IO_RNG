"""
Django REST Framework Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from io_rng.api.serializers import (
    RNGSerializer,
    TestResultSerializer,
    RunTestRequestSerializer
)
from io_rng.core.entities.rng import RNG, Language, Algorithm
from io_rng.core.use_cases.run_rng_test import RunRNGTestUseCase
from io_rng.infrastructure.repositories.django_repositories import (
    DjangoRNGRepository,
    DjangoTestResultRepository
)
from io_rng.infrastructure.runners.python_runner import PythonRNGRunner


class RNGViewSet(viewsets.ViewSet):
    """
    ViewSet dla RNG.
    Udostępnia CRUD + akcję run_test.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rng_repository = DjangoRNGRepository()
        self.result_repository = DjangoTestResultRepository()
        self.runners = [PythonRNGRunner()]

    def list(self, request):
        """GET /api/rngs/ - Lista wszystkich RNG"""
        rngs = self.rng_repository.get_all()
        serializer = RNGSerializer(rngs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/rngs/{id}/ - Szczegóły RNG"""
        rng = self.rng_repository.get_by_id(int(pk))
        if not rng:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RNGSerializer(rng)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/rngs/ - Tworzy nowy RNG"""
        serializer = RNGSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        rng = RNG(
            name=data['name'],
            language=Language(data['language']),
            algorithm=Algorithm(data['algorithm']),
            description=data['description'],
            code_path=data['code_path'],
            parameters=data.get('parameters'),
            is_active=data.get('is_active', True)
        )

        saved_rng = self.rng_repository.save(rng)
        result_serializer = RNGSerializer(saved_rng)

        return Response(
            result_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        """PUT /api/rngs/{id}/ - Aktualizuje RNG"""
        rng = self.rng_repository.get_by_id(int(pk))
        if not rng:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RNGSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        rng.name = data['name']
        rng.language = Language(data['language'])
        rng.algorithm = Algorithm(data['algorithm'])
        rng.description = data['description']
        rng.code_path = data['code_path']
        rng.parameters = data.get('parameters')
        rng.is_active = data.get('is_active', True)

        updated_rng = self.rng_repository.update(rng)
        result_serializer = RNGSerializer(updated_rng)

        return Response(result_serializer.data)

    def destroy(self, request, pk=None):
        """DELETE /api/rngs/{id}/ - Usuwa RNG"""
        success = self.rng_repository.delete(int(pk))
        if not success:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def run_test(self, request, pk=None):
        """
        POST /api/rngs/{id}/run_test/
        Uruchamia test dla RNG - to jest główna akcja!
        """
        serializer = RunTestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

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
                seed=data.get('seed'),
                parameters=data.get('parameters')
            )

            result_serializer = TestResultSerializer(result)
            return Response(result_serializer.data)

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Test failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def test_results(self, request, pk=None):
        """GET /api/rngs/{id}/test_results/ - Wyniki testów dla RNG"""
        results = self.result_repository.get_by_rng(int(pk))
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)


class TestResultViewSet(viewsets.ViewSet):
    """ViewSet dla wyników testów"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = DjangoTestResultRepository()

    def list(self, request):
        """GET /api/test-results/ - Najnowsze wyniki"""
        limit = int(request.query_params.get('limit', 20))
        results = self.repository.get_latest(limit)
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/test-results/{id}/ - Szczegóły wyniku"""
        result = self.repository.get_by_id(int(pk))
        if not result:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TestResultSerializer(result)
        return Response(serializer.data)