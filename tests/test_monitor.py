import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.backendbot.main import app

client = TestClient(app)

def test_get_monitor_stats_with_data():
    """Test the monitor stats endpoint returns system stats."""
    response = client.get("/api/v1/monitor/stats")
    # Should return 200 with system stats
    assert response.status_code == 200
    data = response.json()
    assert "cpu_usage" in data
    assert "ram_usage_percent" in data
    assert "ram_used_gb" in data
    assert "ram_total_gb" in data
    assert isinstance(data["cpu_usage"], (int, float))
    assert isinstance(data["ram_usage_percent"], (int, float))

# TODO: Add test for when Redis is connected and has data
# def test_get_monitor_stats_with_data():
#     # This would require Redis running and data set
#     pass