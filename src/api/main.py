"""Module principal de l'API FastAPI pour l'inférence MLOps."""

import os

import mlflow
import mlflow.pyfunc
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from mlflow.tracking import MlflowClient
from pydantic import BaseModel

# Dans src/api/main.py


load_dotenv()  # Charge les variables du .env

app = FastAPI(title="ML Factory API")

# Configuration via variables d'environnement
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris_model")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "production")
model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

# Initialisation du client
client = MlflowClient(tracking_uri=MLFLOW_URI)

# Cache en mémoire pour éviter de recharger si la version n'a pas changé [cite: 101]
state = {"model": None, "version": None}


class IrisData(BaseModel):
    """
    Schéma de validation des données d'entrée.

    Attributes:
        sepal_length (float): Longueur du sépale en cm.
        sepal_width (float): Largeur du sépale en cm.
        petal_length (float): Longueur du pétale en cm.
        petal_width (float): Largeur du pétale en cm.
    """

    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


def load_production_model():
    """
    Charge ou met à jour le modèle MLflow en mémoire vive (Hot-Reloading).

    Cette fonction vérifie l'alias défini dans l'environnement (ex: 'production').
    Si la version sur le serveur MLflow est plus récente que celle en cache,
    elle télécharge le nouveau binaire. Sinon, elle conserve le modèle actuel pour
    minimiser la latence.

    Returns:
        tuple: Un tuple contenant :
            - model (mlflow.pyfunc.PyFuncModel): Le modèle Scikit-Learn prêt pour l'inférence.
            - version (str): Le numéro de version actuellement chargé (ex: "v3").

    Raises:
        HTTPException: Erreur 404 si le serveur MLflow est injoignable ou si l'alias n'existe pas.
    """
    try:
        # 1. On demande quelle est la version actuelle de l'alias 'Production' [cite: 108]
        alias_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        prod_version = alias_info.version

        # 2. Si le modèle n'est pas en cache ou si la version a changé [cite: 109]
        if state["model"] is None or prod_version != state["version"]:
            print(f"🔄 Rechargement à chaud : Passage à la version {prod_version}")
            model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
            state["model"] = mlflow.pyfunc.load_model(model_uri)
            state["version"] = prod_version

        return state["model"], state["version"]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Erreur MLflow: {str(e)}")


@app.post("/predict")
def predict(data: IrisData):
    """
    Exécute une inférence sur les dimensions d'une fleur Iris.

    Args:
        data (IrisData): Objet Pydantic contenant les 4 dimensions de la fleur en centimètres.

    Returns:
        dict: Le résultat de la prédiction, incluant la classe, la version du modèle et le statut.

    Example:
        Voici un exemple de requête valide, basé sur une fleur de type Virginica issue de notre dataset de test :

        .. code-block:: python

            import requests

            payload = {
                "sepal_length": 7.7,
                "sepal_width": 2.6,
                "petal_length": 6.9,
                "petal_width": 2.3
            }
            response = requests.post("http://localhost:8000/predict", json=payload)
            print(response.json())
            # Output attendu : {"prediction": 2, "model_version": "1", "status": "success"}
    """
    # Récupération dynamique du modèle
    model, version = load_production_model()

    # Préparation des données pour scikit-learn
    features = [
        [data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]
    ]

    # Inférence
    prediction = model.predict(features)

    # On renvoie la prédiction ET la version pour la traçabilité
    return {
        "prediction": int(prediction[0]),
        "model_version": version,
        "status": "success",
    }


@app.get("/health")
def health():
    """
    Vérifie l'état de santé de l'API.

    Returns:
        dict: Un dictionnaire confirmant que l'API est en ligne.
    """
    return {"status": "up"}
