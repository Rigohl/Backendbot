import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.backendbot.main import app

client = TestClient(app)

def test_get_monitor_stats_no_data():
    """Test the monitor stats endpoint when no data is available in DB."""
    response = client.get("/api/v1/monitor/stats")
    # Should return 404 if no stats available
    assert response.status_code == 404
    assert "No hay estadísticas de monitoreo disponibles todavía" in response.json()["detail"]

# TODO: Add test for when Redis is connected and has data
# def test_get_monitor_stats_with_data():
#     # This would require Redis running and data set
#     pass