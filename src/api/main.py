"""Module principal de l'API FastAPI pour l'inférence MLOps."""

import os
import sys

import mlflow
import mlflow.pyfunc
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger
from mlflow.tracking import MlflowClient
from prometheus_client import Counter, make_asgi_app
from pydantic import BaseModel

# --- 1. CONFIGURATION DES LOGS (LOGURU) ---
logger.remove()  # Supprime le logger par défaut
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    colorize=True,
)
logger.add("logs/api.log", rotation="10 MB", retention="10 days", level="INFO")

load_dotenv()  # Charge les variables du .env

app = FastAPI(title="Iris ML Factory API")

# --- 2. CONFIGURATION PROMETHEUS ---
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
PREDICTION_COUNTER = Counter(
    "ml_predictions_total", "Nombre total de prédictions effectuées", ["model_version"]
)

# Configuration via variables d'environnement
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris_model")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "production")

# Initialisation du client
client = MlflowClient(tracking_uri=MLFLOW_URI)
state = {"model": None, "version": None}


class IrisData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


def load_production_model():
    try:
        alias_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        prod_version = alias_info.version

        if state["model"] is None or prod_version != state["version"]:
            # On utilise logger.info au lieu du simple print
            logger.info(
                f"🔄 Rechargement à chaud : Passage à la version {prod_version}"
            )
            model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
            state["model"] = mlflow.pyfunc.load_model(model_uri)
            state["version"] = prod_version

        return state["model"], state["version"]
    except Exception as e:
        logger.error(f"Erreur MLflow: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Erreur MLflow: {str(e)}")


@app.post("/predict")
def predict(data: IrisData):
    # Récupération dynamique du modèle
    model, version = load_production_model()

    # Préparation des données et Inférence
    features = [
        [data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]
    ]
    prediction = model.predict(features)

    # --- 3. INCRÉMENTATION PROMETHEUS ET LOG DE SUCCÈS ---
    PREDICTION_COUNTER.labels(model_version=version).inc()
    logger.info(
        f"Prédiction réussie (Classe {int(prediction[0])}) avec le modèle v{version}"
    )

    return {
        "prediction": int(prediction[0]),
        "model_version": version,
        "status": "success",
    }


# --- 4. SONDE DE VIE (UPTIME KUMA) ---
@app.get("/health")
async def health_check():
    """Endpoint ultra-léger que Kuma va pinger toutes les 60s"""
    logger.debug("Sonde Uptime Kuma reçue")
    return {"status": "ok", "service": "api"}
