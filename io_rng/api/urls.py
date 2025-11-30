"""
API URLs - Routing
Definicja endpointów REST API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import RNGViewSet, TestResultViewSet

# Router automatycznie generuje URLe dla ViewSetów
router = DefaultRouter()
router.register(r'rngs', RNGViewSet, basename='rng')
router.register(r'test-results', TestResultViewSet, basename='testresult')

urlpatterns = [
    path('', include(router.urls)),
]

# Wygenerowane endpointy:
# GET    /api/rngs/                    - lista RNG
# POST   /api/rngs/                    - stwórz RNG
# GET    /api/rngs/{id}/               - szczegóły RNG
# PUT    /api/rngs/{id}/               - aktualizuj RNG
# DELETE /api/rngs/{id}/               - usuń RNG
# POST   /api/rngs/{id}/run_test/      - uruchom test
# GET    /api/rngs/{id}/test_results/  - wyniki testów RNG
# GET    /api/test-results/            - lista wyników
# GET    /api/test-results/{id}/       - szczegóły wyniku