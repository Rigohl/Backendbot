import pytest
from fastapi.testclient import TestClient
import base64
import sys
sys.path.insert(0, '.')
from main import app, rate_limit_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_rate_limit():
    """Limpia el store de rate limiting antes de cada test."""
    rate_limit_store.clear()

def get_basic_auth_header(username: str, password: str) -> dict:
    """Genera header de autenticación básica."""
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}

def test_read_root_valid_auth():
    """Prueba el endpoint raíz con autenticación válida."""
    headers = get_basic_auth_header("admin", "password")
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert "timestamp" in data
    assert data["user"] == "admin"

def test_read_root_invalid_auth():
    """Prueba el endpoint raíz con autenticación inválida."""
    headers = get_basic_auth_header("admin", "wrong_password")
    response = client.get("/", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales inválidas"}

def test_read_root_no_auth():
    """Prueba el endpoint raíz sin autenticación."""
    response = client.get("/")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_read_root_wrong_username():
    """Prueba el endpoint raíz con usuario incorrecto."""
    headers = get_basic_auth_header("wrong_user", "password")
    response = client.get("/", headers=headers)
    assert response.status_code == 401

def test_cors_headers():
    """Prueba que los headers CORS estén presentes."""
    headers = get_basic_auth_header("admin", "password")
    headers["Origin"] = "http://localhost:3000"
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    # Verificar que los headers CORS estén presentes
    assert "access-control-allow-origin" in response.headers or "*" in str(response.headers)

def test_openapi_docs():
    """Prueba que la documentación OpenAPI esté disponible."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_check():
    """Prueba un health check básico."""
    headers = get_basic_auth_header("admin", "password")
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Backendbot API is running!"
    assert "timestamp" in data
    assert "version" in data

def test_response_models():
    """Prueba que las respuestas sigan los modelos Pydantic."""
    headers = get_basic_auth_header("admin", "password")
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Verificar estructura de StatusResponse
    required_fields = ["message", "user", "timestamp"]
    for field in required_fields:
        assert field in data

def test_system_info_structure():
    """Prueba la estructura de la respuesta de /system."""
    headers = get_basic_auth_header("admin", "password")
    response = client.get("/system", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Verificar campos requeridos
    required_fields = ["cpu_percent", "memory_total", "memory_available",
                      "memory_percent", "disk_total", "disk_free", "disk_percent", "user", "timestamp"]
    for field in required_fields:
        assert field in data

    # Verificar tipos de datos
    assert isinstance(data["cpu_percent"], (int, float))
    assert isinstance(data["memory_total"], int)
    assert isinstance(data["memory_available"], int)
    assert data["user"] == "admin"

def test_rate_limiting():
    """Prueba el rate limiting."""
    headers = get_basic_auth_header("admin", "password")
    # Hacer solicitudes para exceder el límite (10 para pruebas)
    for i in range(12):  # Más que el límite de 10
        response = client.get("/", headers=headers)
        if i < 10:
            assert response.status_code == 200
        else:
            # Después del límite, debería devolver 429
            assert response.status_code == 429
            break

def test_invalid_endpoint():
    """Prueba acceso a endpoint inexistente."""
    headers = get_basic_auth_header("admin", "password")
    response = client.get("/nonexistent", headers=headers)
    assert response.status_code == 404

def test_method_not_allowed():
    """Prueba método HTTP no permitido."""
    headers = get_basic_auth_header("admin", "password")
    response = client.post("/", headers=headers)
    assert response.status_code == 405

def test_authentication_edge_cases():
    """Prueba casos edge de autenticación."""
    # Usuario vacío
    headers = get_basic_auth_header("", "password")
    response = client.get("/", headers=headers)
    assert response.status_code == 401

    # Contraseña vacía
    headers = get_basic_auth_header("admin", "")
    response = client.get("/", headers=headers)
    assert response.status_code == 401

    # Credenciales malformadas
    response = client.get("/", headers={"Authorization": "Basic invalid"})
    assert response.status_code == 401
