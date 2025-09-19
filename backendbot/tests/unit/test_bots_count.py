import pytest
from fastapi.testclient import TestClient

from backendbot.apps.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.unit
@pytest.mark.api
def test_bots_count_and_unique(client):
    resp = client.get("/api/v1/bots/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    bots = data.get("bots", [])
    assert len(bots) == 5
    names = [b.get("name") for b in bots]
    assert len(set(names)) == len(names)
