"""
Testy API dla endpointów RNG
"""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestRNGListEndpoint:
    """Testy dla endpointu GET /api/rngs"""

    def test_get_rngs_empty_list(self):
        """Test pobierania pustej listy RNG"""
        client = Client()
        response = client.get("/api/rngs")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_rngs_returns_json(self):
        """Test czy endpoint zwraca JSON"""
        client = Client()
        response = client.get("/api/rngs")

        assert response["Content-Type"] == "application/json"


@pytest.mark.django_db
class TestRNGDetailEndpoint:
    """Testy dla endpointu GET /api/rngs/{id}"""

    def test_get_nonexistent_rng_returns_404(self):
        """Test pobierania nieistniejącego RNG"""
        client = Client()
        response = client.get("/api/rngs/999999")

        assert response.status_code == 404


@pytest.mark.django_db
class TestRunTestEndpoint:
    """Testy dla endpointu POST /api/rngs/{id}/run_test"""

    def test_run_test_requires_post(self):
        """Test czy endpoint wymaga metody POST"""
        client = Client()
        response = client.get("/api/rngs/1/run_test")

        assert response.status_code in [404, 405]  # Method not allowed or not found

    def test_run_test_with_missing_data(self):
        """Test uruchomienia testu bez wymaganych danych"""
        client = Client()
        response = client.post(
            "/api/rngs/1/run_test", data={}, content_type="application/json"
        )

        # Oczekujemy błędu walidacji (400) lub not found (404)
        assert response.status_code in [400, 404]


@pytest.mark.django_db
class TestCustomBitsEndpoint:
    """Testy dla endpointu POST /api/rngs/test-custom"""

    def test_custom_bits_requires_post(self):
        """Test czy endpoint wymaga metody POST"""
        client = Client()
        response = client.get("/api/rngs/test-custom")

        assert response.status_code == 405  # Method not allowed

    def test_custom_bits_with_invalid_data(self):
        """Test z nieprawidłowymi danymi"""
        client = Client()
        response = client.post(
            "/api/rngs/test-custom",
            data={"invalid": "data"},
            content_type="application/json",
        )

        assert response.status_code == 400  # Bad request
