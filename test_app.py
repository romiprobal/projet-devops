from app import app
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_ok_quand_postgres_repond(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"


def test_health_503_quand_postgres_absent(client, monkeypatch):

    monkeypatch.setenv("DATABASE_URL", "postgresql://x:y@127.0.0.1:1/nope")
    response = client.get("/health")
    assert response.status_code == 503
    data = response.get_json()
    assert data["status"] == "degraded"