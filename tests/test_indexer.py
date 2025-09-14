import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.backendbot.main import app

client = TestClient(app)

def test_search_files_no_data():
    """Test searching files when no data is available."""
    response = client.get("/api/v1/indexer/search?query=test")
    assert response.status_code == 200
    assert response.json() == []

def test_start_indexing():
    """Test starting indexing."""
    response = client.post("/api/v1/indexer/start_indexing", json={"path": "/test/path"})
    assert response.status_code == 200
    assert "Indexación de /test/path iniciada" in response.json()["message"]

# TODO: Add tests for success cases when Redis is connected and has indexed data