import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.backendbot.main import app

client = TestClient(app)

def test_get_history():
    response = client.get("/api/v1/history/")
    assert response.status_code == 200
    # Check if the response is a list (as per the placeholder)
    assert isinstance(response.json(), list)
