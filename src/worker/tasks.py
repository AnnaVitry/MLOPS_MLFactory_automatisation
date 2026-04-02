"""Module du Worker Asynchrone (Celery).

Ce module contient les tâches de fond exécutées par les workers.
Il est chargé de télécharger le modèle optimal depuis MLflow et
d'effectuer les prédictions réelles en dehors du flux de l'API.
"""

import os
import sys
import time
from typing import Any

import mlflow.pyfunc
from celery import Celery
from dotenv import load_dotenv
from loguru import logger

# --- 1. CONFIGURATION LOGURU ---
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>WORKER</cyan> - <level>{message}</level>",
    colorize=True,
)

load_dotenv()

# --- 2. CONFIGURATION CELERY ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery("ml_tasks", broker=BROKER_URL, backend=RESULT_BACKEND)

# --- 3. CHARGEMENT DU MODÈLE (Côté Worker) ---
MODEL_NAME = os.getenv("MODEL_NAME", "iris_model")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "production")
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

mlflow.set_tracking_uri(MLFLOW_URI)

_loaded_model = None


def get_model() -> Any:
    """Récupère le modèle en cache ou le télécharge depuis MLflow.

    Returns:
        Any: L'objet modèle MLflow (PyFunc).
    """
    global _loaded_model
    if _loaded_model is None:
        logger.info(
            f"📥 Téléchargement du modèle {MODEL_NAME}@{MODEL_ALIAS} depuis MLflow..."
        )
        model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
        _loaded_model = mlflow.pyfunc.load_model(model_uri)
        logger.success("Modèle chargé en mémoire avec succès !")
    return _loaded_model


# --- 4. LA TÂCHE ASYNCHRONE ---
@app.task(name="predict_task")
def predict_task(features: list[list[float]]) -> dict[str, Any]:
    """Réalise une prédiction à partir des features fournies.

    Cette tâche est appelée par l'API de manière asynchrone. Elle charge
    le modèle depuis le cache (ou MLflow si c'est la première exécution),
    effectue l'inférence, et retourne le résultat dans le backend Redis.

    Args:
        features (list[list[float]]): Une matrice contenant les dimensions
            de la fleur d'Iris (ex: [[5.1, 3.5, 1.4, 0.2]]).

    Returns:
        dict[str, Any]: Un dictionnaire contenant le statut de la tâche (`complete`
            ou `error`) et la classe prédite (0, 1, ou 2).
    """
    logger.info(f"🚀 Nouvelle tâche de prédiction reçue avec les features: {features}")

    try:
        processing_time = int(os.getenv("MODEL_LATENCY", "2"))
        logger.debug(f"Simulation de latence de {processing_time}s...")
        time.sleep(processing_time)

        model = get_model()
        prediction = model.predict(features)
        result = int(prediction[0])

        logger.success(f"✅ Prédiction terminée : Classe {result}")
        return {"status": "complete", "prediction": result}

    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction : {str(e)}")
        return {"status": "error", "message": str(e)}
