#Ce test va nous permettre de voir si tout nos code fonctionnen bien

#on import notre serveur web grace au variable app
from app import app
#moteur de test, lire ce fichier et voir si c ok
import pytest 

#fonction de preration configurer env pret à l'emploi av test (un fixture doit executer avant le test (preparation du terrain))
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

#test ici c'est qu'on va simuler une requete GET sur url /health
def test_health_endpoint(client):
    "Test : /health code 200 status healthy"
    response = client.get('/health')

    assert response.status_cde == 200

    data = response.get_json()
    assert data["status"] == "healthy"