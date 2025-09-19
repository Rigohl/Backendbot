import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backendbot.main import app

client = TestClient(app)

def test_scan_duplicates():
    """Test starting scan for duplicates."""
    test_path = os.path.dirname(os.path.dirname(__file__))  # Directorio del proyecto
    response = client.post("/api/v1/organizer/scan", json={"path": test_path})
    assert response.status_code == 200
    assert "Escaneo de duplicados iniciado" in response.json()["message"]

def test_get_duplicates_no_data():
    """Test getting duplicates when no data is available."""
    response = client.get("/api/v1/organizer/duplicates")
    assert response.status_code == 200
    assert response.json() == []

def test_delete_duplicates():
    """Test deleting approved duplicates."""
    # Crear archivos temporales para el test
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_test_files")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file1 = os.path.join(temp_dir, "test_file1.txt")
    temp_file2 = os.path.join(temp_dir, "test_file2.txt")
    
    # Crear archivos
    with open(temp_file1, 'w') as f:
        f.write("test content")
    with open(temp_file2, 'w') as f:
        f.write("test content")
    
    response = client.post("/api/v1/organizer/delete_duplicates", json={"files": [temp_file1, temp_file2]})
    assert response.status_code == 200
    assert "Eliminados" in response.json()["message"]
    
    # Limpiar
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

# TODO: Add tests for success cases when Redis is connected