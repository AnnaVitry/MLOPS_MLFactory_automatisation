"""Script d'entraînement et d'enregistrement des modèles dans le Model Registry."""

import os

import boto3
import mlflow
import mlflow.sklearn
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
from prefect import flow, task
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

load_dotenv()  # Charge le fichier .env situé à la racine

# Variables d'environnement pour l'infrastructure
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv(
    "MLFLOW_S3_ENDPOINT_URL", "http://127.0.0.1:9000"
)
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

model_alias = os.getenv("MODEL_ALIAS", "production")


@task(retries=3, retry_delay_seconds=5)
def prepare_minio():
    """Initialise le stockage S3 local (MinIO)."""
    s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if "mlflow" not in buckets:
        s3.create_bucket(Bucket="mlflow")
        print("Bucket 'mlflow' créé avec succès.")


@task
def train_and_register(
    model_choice: str = "logistic_regression", assign_production_alias: bool = True
):
    """Entraîne et enregistre dynamiquement le modèle choisi."""
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("Iris_Factory")

    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2
    )

    # --- SÉLECTION DYNAMIQUE DU MODÈLE ---
    if model_choice == "random_forest":
        n_trees = 200
        model = RandomForestClassifier(n_estimators=n_trees, random_state=42)
        model_type_str = "RandomForest"
    else:
        model = LogisticRegression(max_iter=200)
        model_type_str = "LogisticRegression"

    with mlflow.start_run() as run:
        run_id = run.info.run_id
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)

        mlflow.log_param("model_type", model_type_str)
        if model_choice == "random_forest":
            mlflow.log_param("n_estimators", n_trees)
        mlflow.log_metric("accuracy", accuracy)

        model_name = "iris_model"
        model_info = mlflow.sklearn.log_model(
            sk_model=model, artifact_path="model", registered_model_name=model_name
        )

        msg_extra = f" | Arbres: {n_trees}" if model_choice == "random_forest" else ""
        print(
            f"Modèle {model_type_str} (run_id: {run_id}) enregistré avec l'accuracy: {accuracy:.2f}{msg_extra}"
        )

    # --- GESTION DYNAMIQUE DE L'ALIAS ---
    client = MlflowClient()
    latest_version = model_info.registered_model_version

    if assign_production_alias:
        client.set_registered_model_alias(model_name, model_alias, str(latest_version))
        print(
            f"🚀 Version {latest_version} ({model_type_str}) est désormais le Champion ('{model_alias}')."
        )
    else:
        print(
            f"Version {latest_version} ({model_type_str}) enregistrée comme Challenger (pas en production)."
        )


# --- LE NOUVEAU CHEF D'ORCHESTRE DYNAMIQUE ---
@flow(name="Pipeline Entrainement Iris", log_prints=True)
def pipeline_mlops(
    champion_model: str = "logistic_regression", run_challenger: bool = True
):
    """
    Exécute le pipeline. Les paramètres de cette fonction deviennent
    automatiquement des champs modifiables dans l'interface UI de Prefect !
    """
    print(f"Démarrage du pipeline... Modèle cible en production : {champion_model}")
    prepare_minio()

    # 1. Le "Champion" : Celui que l'utilisateur a choisi de mettre en production
    train_and_register(model_choice=champion_model, assign_production_alias=True)

    # 2. Le "Challenger" : On entraîne automatiquement l'autre modèle pour comparer
    if run_challenger:
        challenger_model = (
            "random_forest"
            if champion_model == "logistic_regression"
            else "logistic_regression"
        )
        train_and_register(model_choice=challenger_model, assign_production_alias=False)

    print("Pipeline achevé avec succès.")


if __name__ == "__main__":
    # Ce bloc ne sert plus qu'à tester localement sans Docker ni Prefect Server
    print("Exécution manuelle locale du pipeline (Mode Test)...")
    pipeline_mlops()
