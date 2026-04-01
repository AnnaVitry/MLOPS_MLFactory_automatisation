"""Module de l'API FastAPI pour l'inférence MLOps.

Ce module expose les routes REST permettant aux utilisateurs de
soumettre des données pour prédiction. Il délègue le calcul lourd
à un worker asynchrone via Celery et RabbitMQ.
"""

import sys

from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.worker.tasks import app as celery_app
from src.worker.tasks import predict_task

# --- 1. CONFIGURATION LOGURU ---
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <blue>API</blue> - <level>{message}</level>",
    colorize=True,
)

app = FastAPI(
    title="ML Factory API Asynchrone",
    description="API de prédiction avec délégation asynchrone via Celery",
    version="2.0.0",
)


# --- 2. MODÈLES DE DONNÉES (Pydantic) ---
class Features(BaseModel):
    """Représente les caractéristiques d'une fleur d'Iris.

    Attributes:
        sepal_length (float): La longueur du sépale en cm.
        sepal_width (float): La largeur du sépale en cm.
        petal_length (float): La longueur du pétale en cm.
        petal_width (float): La largeur du pétale en cm.
    """

    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


# --- 3. ROUTES ---
@app.get("/")
async def root():
    """Route d'accueil de l'API."""
    logger.info("Requête reçue sur la racine (/)")
    return {"message": "Bienvenue sur l'API ML Factory Asynchrone"}


@app.get("/health")
async def health_check():
    """Sonde de vie pour le monitoring (Uptime Kuma/Kubernetes)."""
    logger.debug("Sonde de santé interrogée")
    return {"status": "ok", "message": "API opérationnelle"}


@app.post("/predict")
async def create_prediction_task(features: Features):
    """Soumet une tâche de prédiction au broker de messages.

    Au lieu de réaliser la prédiction de manière synchrone, cette route
    envoie les données au worker Celery et retourne immédiatement un
    identifiant de tâche (Task ID) au client.

    Args:
        features (Features): Les mesures de la fleur envoyées par le client.

    Returns:
        dict: Un dictionnaire contenant un message de confirmation et
            le `task_id` permettant de suivre l'avancement.

    Raises:
        HTTPException: Si le broker (RabbitMQ/Redis) est injoignable (Erreur 503).
    """
    logger.info(f"📥 Demande de prédiction reçue : {features}")

    # Transformation de l'objet Pydantic en liste pour le modèle
    feature_list = [
        [
            features.sepal_length,
            features.sepal_width,
            features.petal_length,
            features.petal_width,
        ]
    ]

    try:
        # Envoi de la tâche à Celery (RabbitMQ)
        task = predict_task.delay(feature_list)

        logger.success(f"📤 Tâche envoyée au Broker avec l'ID : {task.id}")

        # On retourne le "ticket de caisse"
        return {"message": "Prédiction en cours de traitement", "task_id": task.id}

    except Exception as e:
        logger.error(f"❌ Impossible de contacter le Broker : {str(e)}")
        raise HTTPException(
            status_code=503, detail="Service de file d'attente indisponible"
        )


@app.get("/predict/status/{task_id}")
async def get_prediction_status(task_id: str):
    """Vérifie le statut d'une tâche de prédiction asynchrone.

    Cette route est interrogée par le client (ex: Streamlit) pour
    savoir si le worker Celery a terminé son calcul.

    Args:
        task_id (str): L'identifiant unique de la tâche retourné par /predict.

    Returns:
        dict: L'état actuel de la tâche (`en cours`, `terminé`, ou `erreur`)
            ainsi que la prédiction si elle est terminée.
    """
    logger.debug(f"🔍 Vérification du statut pour la tâche : {task_id}")

    # On interroge Celery (Redis) pour connaître l'état de la tâche
    task_result = celery_app.AsyncResult(task_id)

    if task_result.ready():
        if task_result.successful():
            result = task_result.result
            logger.info(f"✅ Résultat disponible pour la tâche {task_id} : {result}")
            return {
                "task_id": task_id,
                "status": "terminé",
                "prediction": result.get("prediction"),
            }
        else:
            logger.warning(f"⚠️ La tâche {task_id} a échoué.")
            return {
                "task_id": task_id,
                "status": "erreur",
                "error": str(task_result.info),
            }
    else:
        logger.debug(f"⏳ La tâche {task_id} est toujours en cours de traitement.")
        return {"task_id": task_id, "status": "en cours"}
