import pytest

from app import app


# client de test flask, permet d'appeler les routes sans lancer de vrai serveur
@pytest.fixture
def client():
    # mode test : les erreurs remontent direct dans pytest au lieu d'un 500
    app.config["TESTING"] = True
    with app.test_client() as client:
        # on donne le client au test, il est ferme apres
        yield client


# cas normal : postgres tourne (en ci c'est le service postgres du workflow)
def test_health_ok_quand_postgres_repond(client):
    response = client.get("/health")
    # la bdd repond donc on doit avoir 200
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"


# cas panne : on met une fausse url de bdd pour simuler postgres down
def test_health_503_quand_postgres_absent(client, monkeypatch):
    # monkeypatch remet la vraie valeur a la fin du test
    monkeypatch.setenv("DATABASE_URL", "postgresql://x:y@127.0.0.1:1/nope")
    response = client.get("/health")
    # la bdd est injoignable donc /health doit renvoyer 503
    assert response.status_code == 503
    data = response.get_json()
    assert data["status"] == "degraded"