"""
Tests unitarios para la API Gateway
===================================

Tests para verificar el funcionamiento básico de la API FastAPI.

Autor: BackendBot Team
Versión: 0.1.0
"""

import pytest
from fastapi.testclient import TestClient

from backendbot.apps.api.main import app


@pytest.fixture
def client():
    """Fixture para crear cliente de test de FastAPI."""
    return TestClient(app)


@pytest.mark.unit
@pytest.mark.api
def test_root_endpoint(client):
    """Test del endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "BackendBot API Gateway" in data["message"]
    assert "version" in data
    assert "docs" in data


@pytest.mark.unit
@pytest.mark.api
def test_health_check_endpoint(client):
    """Test del endpoint de health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "uptime" in data


@pytest.mark.unit
@pytest.mark.api
def test_get_bots_endpoint(client):
    """Test del endpoint para obtener bots."""
    response = client.get("/api/v1/bots")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "bots" in data


@pytest.mark.unit
@pytest.mark.api
def test_get_system_info_endpoint(client):
    """Test del endpoint para obtener información del sistema."""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "info" in data["data"]


@pytest.mark.unit
@pytest.mark.api
def test_openapi_docs_available(client):
    """Test que la documentación OpenAPI esté disponible."""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.api
def test_redoc_docs_available(client):
    """Test que la documentación ReDoc esté disponible."""
    response = client.get("/redoc")
    assert response.status_code == 200
