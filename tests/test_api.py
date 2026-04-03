from fastapi.testclient import TestClient

from src.api.main import app

# Création d'un client de test pour simuler des requêtes HTTP sur notre API
client = TestClient(app)


def test_read_root():
    """Test la route d'accueil de l'API."""
    response = client.get("/")
    assert response.status_code == 200
    # Vérifie que la réponse contient bien un message de bienvenue
    assert "message" in response.json()


def test_predict_async_flow():
    """Test le flux asynchrone complet : envoi d'une tâche puis vérification du statut."""
    # 1. Test de l'envoi de la commande (POST)
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=payload)

    # L'API doit accepter la requête
    assert response.status_code == 200
    data = response.json()

    # L'API doit nous renvoyer un ticket (task_id)
    assert "task_id" in data
    task_id = data["task_id"]

    # 2. Test de la vérification du statut (GET)
    status_response = client.get(f"/predict/status/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()

    # Le statut doit au moins contenir la clé "status" et l'ID du ticket
    assert "status" in status_data
    assert status_data["task_id"] == task_id
