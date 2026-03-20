"""Suite de tests unitaires pour l'API FastAPI."""

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api.main import app, load_production_model, state

# Instanciation du client de test natif de FastAPI
client = TestClient(app)


def test_health_check() -> None:
    """Valide que la route de santé répond correctement."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up"}


# Le décorateur @patch intercepte la fonction load_production_model pour l'isoler de MLflow
@patch("src.api.main.load_production_model")
def test_predict_valid_data(mock_load_model) -> None:
    """Test l'inférence avec des données mathématiquement valides."""

    # 1. Création d'un faux modèle en mémoire
    class MockModel:
        def predict(self, data):
            return [2]  # Simule une prédiction de classe Virginica

    # 2. Configuration du "bouchon" (Mock)
    mock_load_model.return_value = (MockModel(), "v1-mock")

    # 3. Préparation de la requête avec des données réelles
    payload = {
        "sepal_length": 6.1,
        "sepal_width": 2.8,
        "petal_length": 4.7,
        "petal_width": 1.2,
    }

    # 4. Exécution
    response = client.post("/predict", json=payload)

    # 5. Assertions (Vérifications strictes)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["prediction"] == 2
    assert data["model_version"] == "v1-mock"


def test_predict_invalid_data() -> None:
    """Valide que le bouclier Pydantic rejette les données aberrantes."""
    payload = {
        "sepal_length": "Ceci n'est pas un nombre",  # Type incorrect intentionnel
        "sepal_width": 2.8,
        "petal_length": 4.7,
        "petal_width": 1.2,
    }

    response = client.post("/predict", json=payload)

    # FastAPI doit bloquer la requête et renvoyer 422 (Unprocessable Entity)
    assert response.status_code == 422
    assert "detail" in response.json()


# ==========================================
# TESTS DU HOT-RELOADING (Lignes 66-80)
# ==========================================


@patch("src.api.main.mlflow.pyfunc.load_model")
@patch("src.api.main.client.get_model_version_by_alias")
def test_load_production_model_success(mock_get_alias, mock_load_model) -> None:
    """Test le rechargement à chaud quand MLflow répond correctement."""

    # 1. Réinitialisation de l'état en mémoire (pour isoler le test)
    state["model"] = None
    state["version"] = None

    # 2. Simulation de la réponse de MLflow (Alias v2)
    class MockAliasInfo:
        version = "v2"

    mock_get_alias.return_value = MockAliasInfo()
    mock_load_model.return_value = "Faux_Modele_En_Memoire"

    # 3. Exécution de la fonction
    model, version = load_production_model()

    # 4. Assertions
    assert version == "v2"
    assert model == "Faux_Modele_En_Memoire"
    assert state["version"] == "v2"  # Vérifie que le cache global a bien été mis à jour


@patch("src.api.main.client.get_model_version_by_alias")
def test_load_production_model_failure(mock_get_alias) -> None:
    """Test la robustesse si le serveur MLflow est injoignable."""

    # 1. Simulation d'un crash total du serveur MLflow
    mock_get_alias.side_effect = Exception("MLflow Server Down")

    # 2. Vérification que l'erreur est proprement transformée en erreur HTTP 404
    with pytest.raises(HTTPException) as exc_info:
        load_production_model()

    # 3. Validation du code d'erreur
    assert exc_info.value.status_code == 404
    assert "MLflow Server Down" in exc_info.value.detail
