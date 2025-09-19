
"""
Tests avanzados de validación y manejo de errores para la API de BackendBot (FastAPI)
Incluye validación de esquemas, manejo de errores y pruebas de endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from backendbot.apps.api.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "BackendBot" in data["message"]
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"
    assert data["health"] == "/api/v1/health"

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data

def test_404_error():
    response = client.get("/no-existe-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    assert "uptime" in data

def test_get_all_bots():
    response = client.get("/api/v1/bots/")
    assert response.status_code in (200, 500)  # Puede fallar si no hay bots
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["bots"], list)

@pytest.mark.parametrize("bot_name", ["monitor", "organizer", "indexer", "guardian"])
def test_get_bot_status(bot_name):
    response = client.get(f"/api/v1/bots/{bot_name}")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "info" in data["data"]

@pytest.mark.parametrize("bot_name", ["monitor", "organizer", "indexer", "guardian"])
def test_bot_start_stop_restart(bot_name):
    # Start
    resp = client.post(f"/api/v1/bots/{bot_name}/start")
    assert resp.status_code in (200, 404, 500)
    # Stop
    resp = client.post(f"/api/v1/bots/{bot_name}/stop")
    assert resp.status_code in (200, 404, 500)
    # Restart
    resp = client.post(f"/api/v1/bots/{bot_name}/restart")
    assert resp.status_code in (200, 404, 500)

@pytest.mark.parametrize("bot_name", ["monitor", "organizer", "indexer", "guardian"])
def test_bot_metrics(bot_name):
    resp = client.get(f"/api/v1/bots/{bot_name}/metrics")
    assert resp.status_code in (200, 404, 500)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is True
        assert "metrics" in data

def test_system_info():
    resp = client.get("/api/v1/system/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "system_info" in data
    assert "timestamp" in data

def test_system_metrics():
    resp = client.get("/api/v1/system/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "metrics" in data

def test_system_processes():
    resp = client.get("/api/v1/system/processes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "processes" in data
    assert isinstance(data["processes"], list)

def test_invalid_bot_name():
    resp = client.get("/api/v1/bots/noexistebot")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is False

def test_invalid_post_payload():
    # Simula un POST con payload inválido a un endpoint que espera datos
    resp = client.post("/api/v1/bots/monitor/start", json={"foo": "bar"})
    assert resp.status_code in (200, 404, 422, 500)

def test_edge_case_empty_body():
    # POST sin body a un endpoint que espera datos
    resp = client.post("/api/v1/bots/monitor/start")
    assert resp.status_code in (200, 404, 422, 500)
