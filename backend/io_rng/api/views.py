"""
Django REST Framework Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from io_rng.api.serializers import (
    RNGSerializer,
    TestResultSerializer,
    RunTestRequestSerializer,
    GenerateRequestSerializer,
    GenerateResponseSerializer
)
from io_rng.core.entities.rng import RNG, Language, Algorithm
from io_rng.core.use_cases.run_rng_test import RunRNGTestUseCase
from io_rng.infrastructure.repositories.django_repositories import (
    DjangoRNGRepository,
    DjangoTestResultRepository
)
from io_rng.infrastructure.runners.python_runner import PythonRNGRunner
from io_rng.infrastructure.runners.exe_runner import ExeRNGRunner


class RNGViewSet(viewsets.ViewSet):
    """
    ViewSet dla RNG.
    Udostępnia CRUD + akcję run_test.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rng_repository = DjangoRNGRepository()
        self.result_repository = DjangoTestResultRepository()
        self.runners = [
            PythonRNGRunner(),
            ExeRNGRunner()  # Obsługa prekompilowanych .exe generatorów
        ]

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
        POST /api/rngs/{id}/run_test/?compressed=true
        Uruchamia test dla RNG - to jest główna akcja!

        Query params:
            compressed (bool): If true, returns base64-compressed bits (default: false)
        """
        from io_rng.utils.compression import compress_bits_to_base64

        # Sprawdź parametr query dla kompresji
        use_compression = request.query_params.get('compressed', 'false').lower() == 'true'

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

            # Modyfikuj response jeśli kompresja jest włączona
            if use_compression and result.generated_bits:
                # Dodaj skompresowaną wersję do response
                result_data = {
                    'id': result.id,
                    'rng_id': result.rng_id,
                    'test_name': result.test_name,
                    'passed': result.passed,
                    'score': result.score,
                    'execution_time_ms': result.execution_time_ms,
                    'samples_count': result.samples_count,
                    'statistics': result.statistics,
                    'error_message': result.error_message,
                    'created_at': result.created_at,
                    # Kompresja zamiast surowej listy
                    'bits_compressed': compress_bits_to_base64(result.generated_bits),
                    'bits_format': 'base64-bitpack',
                    'bits_count': len(result.generated_bits)
                }
                result_serializer = TestResultSerializer(result_data)
            else:
                # Backward compatible - zwróć array
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

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        POST /api/rngs/{id}/generate/?compressed=true
        Generuje ciąg bitów bez testowania - zwraca surowe bity + czas wykonania

        Query params:
            compressed (bool): If true, returns base64-compressed bits (default: false)
        """
        import time
        from io_rng.infrastructure.runners.universal_adapter import UniversalRNGAdapter
        from io_rng.core.entities.test_result import DataType
        from io_rng.utils.compression import compress_bits_to_base64

        # Sprawdź parametr query dla kompresji
        use_compression = request.query_params.get('compressed', 'false').lower() == 'true'

        serializer = GenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        count = data['count']
        seed = data.get('seed')
        parameters = data.get('parameters')

        # Pobierz RNG
        rng = self.rng_repository.get_by_id(int(pk))
        if not rng:
            return Response(
                {"detail": "RNG not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Znajdź odpowiedni runner
        runner = None
        for r in self.runners:
            if r.can_run(rng):
                runner = r
                break

        if not runner:
            return Response(
                {"detail": f"No runner available for {rng.language.value}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Generuj bity
            start_time = time.perf_counter()

            # Załaduj moduł i użyj adaptera
            module = runner._load_module(rng.code_path)
            effective_params = parameters or rng.parameters
            adapter = UniversalRNGAdapter(module, effective_params)

            # Wygeneruj surowe dane
            raw_data, data_type = adapter.generate_raw(count, seed)

            # Konwertuj do bitów jeśli trzeba
            if data_type == DataType.BITS:
                bits = raw_data
            elif data_type == DataType.INTEGERS:
                # Konwertuj integery do bitów
                bits = []
                for num in raw_data:
                    # Weź najmłodszy bit
                    bits.append(num & 1)
            else:
                # Konwertuj floaty [0,1] do bitów
                bits = [1 if x > 0.5 else 0 for x in raw_data]

            execution_time = (time.perf_counter() - start_time) * 1000  # ms

            # Przygotuj odpowiedź z kompresją lub bez
            bits_trimmed = bits[:count]  # Upewnij się że nie ma za dużo

            if use_compression:
                response_data = {
                    'bits_compressed': compress_bits_to_base64(bits_trimmed),
                    'bits_format': 'base64-bitpack',
                    'count': len(bits_trimmed),
                    'execution_time_ms': round(execution_time, 3),
                    'rng_id': rng.id,
                    'rng_name': rng.name,
                    'seed': seed
                }
            else:
                # Backward compatible - zwróć array
                response_data = {
                    'bits': bits_trimmed,
                    'bits_format': 'array',
                    'count': len(bits_trimmed),
                    'execution_time_ms': round(execution_time, 3),
                    'rng_id': rng.id,
                    'rng_name': rng.name,
                    'seed': seed
                }

            response_serializer = GenerateResponseSerializer(response_data)
            return Response(response_serializer.data)

        except Exception as e:
            return Response(
                {"detail": f"Generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def test_results(self, request, pk=None):
        """GET /api/rngs/{id}/test_results/ - Wyniki testów dla RNG"""
        results = self.result_repository.get_by_rng(int(pk))
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='test-custom')
    def test_custom(self, request):
        """
        POST /api/rngs/test-custom/
        Testuje custom bity bez generatora - NIE zapisuje do bazy.

        Body:
        {
            "bits_compressed": "base64string",
            "bits_count": 10000,
            "test_name": "nist_monobit"
        }
        """
        from io_rng.utils.compression import decompress_base64_to_bits
        from io_rng.core.use_cases.test_custom_bits import TestCustomBitsUseCase
        from io_rng.api.serializers import (
            CustomTestRequestSerializer,
            CustomTestResponseSerializer
        )

        # Waliduj request
        serializer = CustomTestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            # Dekompresuj bity
            bits = decompress_base64_to_bits(
                data['bits_compressed'],
                data['bits_count']
            )

            # Wykonaj test
            use_case = TestCustomBitsUseCase()
            result = use_case.execute(
                bits=bits,
                test_name=data['test_name']
            )

            # Zwróć odpowiedź (bez zapisu)
            response_serializer = CustomTestResponseSerializer(result)
            return Response(response_serializer.data)

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Test failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

    def destroy(self, request, pk=None):
        """DELETE /api/test-results/{id}/ - Usuwa wynik testu"""
        success = self.repository.delete(int(pk))
        if not success:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)