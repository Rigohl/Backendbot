import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.backendbot.main import app

client = TestClient(app)

def test_scan_duplicates():
    """Test starting scan for duplicates."""
    response = client.post("/api/v1/organizer/scan", json={"path": "/test/path"})
    assert response.status_code == 200
    assert "Escaneo de duplicados iniciado" in response.json()["message"]

def test_get_duplicates_no_data():
    """Test getting duplicates when no data is available."""
    response = client.get("/api/v1/organizer/duplicates")
    assert response.status_code == 200
    assert response.json() == []

def test_delete_duplicates():
    """Test deleting approved duplicates."""
    response = client.post("/api/v1/organizer/delete_duplicates", json={"files": ["/test/file1", "/test/file2"]})
    assert response.status_code == 200
    assert "Orden de eliminación de duplicados enviada" in response.json()["message"]

# TODO: Add tests for success cases when Redis is connected