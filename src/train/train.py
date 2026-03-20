# """Script d'entraînement et d'enregistrement des modèles dans le Model Registry."""

# import os

# import boto3
# import mlflow
# import mlflow.sklearn
# from dotenv import load_dotenv
# from mlflow.tracking import MlflowClient
# from sklearn.datasets import load_iris

# # from sklearn.ensemble import RandomForestClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split

# load_dotenv()  # Charge le fichier .env situé à la racine

# # Maintenant os.environ peut lire les valeurs
# os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv(
#     "MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000"
# )
# os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
# os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")

# # Pour MLflow, on utilise set_tracking_uri
# MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
# mlflow.set_tracking_uri(MLFLOW_URI)

# # Le reste de ton code...
# model_alias = os.getenv("MODEL_ALIAS", "production")


# def prepare_minio():
#     """
#     Initialise la connexion Boto3 avec le stockage S3 local (MinIO).

#     Vérifie l'existence du bucket de destination (défini par défaut à 'mlflow').
#     Si le bucket est absent (ex: lors du premier lancement de `docker compose up`),
#     il est créé automatiquement pour éviter le crash du log d'artefacts MLflow.

#     Raises:
#         EndpointConnectionError: Si le conteneur MinIO n'est pas encore prêt à accepter des connexions sur le port 9000.
#     """
#     s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
#     buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
#     if "mlflow" not in buckets:
#         s3.create_bucket(Bucket="mlflow")
#         print("✅ Bucket 'mlflow' créé avec succès.")


# def train_and_register():
#     """
#     Entraîne le modèle de classification et l'archive dans le Model Registry.

#     Ce pipeline effectue les opérations suivantes :
#     1. Chargement et split (80/20) du dataset Iris natif de Scikit-Learn.
#     2. Entraînement d'un RandomForestClassifier.
#     3. Suivi des hyperparamètres (n_estimators) et métriques (accuracy) via MLflow.
#     4. Enregistrement de l'artefact (.pkl) sur le bucket S3 (MinIO).
#     5. Assignation automatique de l'alias de production à cette nouvelle version.

#     Note:
#         Pour tester un modèle linéaire (ex: LogisticRegression), modifiez
#         l'instanciation du modèle dans cette fonction. Le Hot-Reload de l'API
#         détectera le changement dynamiquement lors du prochain appel.
#     """
#     # Configuration du serveur de tracking
#     mlflow.set_tracking_uri(MLFLOW_URI)
#     mlflow.set_experiment("Iris_Factory")

#     # Préparation des données
#     iris = load_iris()
#     X_train, X_test, y_train, y_test = train_test_split(
#         iris.data, iris.target, test_size=0.2
#     )

#     # --- CHOIX DU MODÈLE (Phase 1 vs Phase 2) ---
#     # Phase 1 : LogisticRegression
#     model = LogisticRegression(max_iter=200)
#     model_type = "LogisticRegression"

#     # Phase 2 : Décommentez ceci et commentez la Phase 1
#     # n_trees = 200
#     # model = RandomForestClassifier(n_estimators=n_trees, random_state=42)
#     # model_type = "RandomForest"

#     with mlflow.start_run() as run:
#         run_id = run.info.run_id

#         model.fit(X_train, y_train)
#         accuracy = model.score(X_test, y_test)

#         # Log des métriques
#         mlflow.log_param("model_type", model_type)
#         # mlflow.log_param("n_estimators", n_trees) # Décommenter pour RandomForest
#         mlflow.log_metric("accuracy", accuracy)

#         # Enregistrement dans MinIO ET dans le Model Registry
#         model_name = "iris_model"
#         model_info = mlflow.sklearn.log_model(
#             sk_model=model, artifact_path="model", registered_model_name=model_name
#         )
#         print(
#             # f"📦 Modèle {model_type} (run_id: {run_id}) enregistré.) avec l'accuracy: {accuracy:.2f} | Arbres: {n_trees}" # Décommenter pour Random Forest
#             f"📦 Modèle {model_type} (run_id: {run_id}) enregistré.) avec l'accuracy: {accuracy:.2f}"  # Décommenter pour LinearRegression
#         )

#     # --- GESTION DE L'ALIAS 'PRODUCTION' ---
#     client = MlflowClient()
#     # latest_version = client.get_latest_versions(model_name, stages=["None"])[0].version
#     latest_version = model_info.registered_model_version
#     # ATTENTION : Pour la Phase 2, commentez la ligne ci-dessous
#     client.set_registered_model_alias(model_name, model_alias, str(latest_version))
#     print(f"🚀 Version {latest_version} passée en alias '{model_alias}'.")


# if __name__ == "__main__":
#     prepare_minio()
#     train_and_register()
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

# Maintenant os.environ peut lire les valeurs
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv(
    "MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000"
)
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")

# Pour MLflow, on utilise set_tracking_uri
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

# Le reste de ton code...
model_alias = os.getenv("MODEL_ALIAS", "production")


# L'Unité de Travail résiliente : Si MinIO est injoignable, on réessaie 3 fois toutes les 5 secondes
@task(retries=3, retry_delay_seconds=5)
def prepare_minio():
    """
    Initialise la connexion Boto3 avec le stockage S3 local (MinIO).

    Vérifie l'existence du bucket de destination (défini par défaut à 'mlflow').
    Si le bucket est absent (ex: lors du premier lancement de `docker compose up`),
    il est créé automatiquement pour éviter le crash du log d'artefacts MLflow.

    Raises:
        EndpointConnectionError: Si le conteneur MinIO n'est pas encore prêt à accepter des connexions sur le port 9000.
    """
    s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if "mlflow" not in buckets:
        s3.create_bucket(Bucket="mlflow")
        print("✅ Bucket 'mlflow' créé avec succès.")


# L'Unité de Travail métier
@task
def train_and_register(
    model_choice: str = "logistic_regression", assign_production_alias: bool = True
):
    """
    Entraîne le modèle de classification et l'archive dans le Model Registry.

    Args:
        model_choice (str): "logistic_regression" ou "random_forest".
        assign_production_alias (bool): Si True, le modèle entraîné prend l'alias 'production'.
    """
    # Configuration du serveur de tracking
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("Iris_Factory")

    # Préparation des données
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2
    )

    # --- CHOIX DU MODÈLE DYNAMIQUE ---
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

        # Log des métriques et paramètres dynamiques
        mlflow.log_param("model_type", model_type_str)
        if model_choice == "random_forest":
            mlflow.log_param("n_estimators", n_trees)

        mlflow.log_metric("accuracy", accuracy)

        # Enregistrement dans MinIO ET dans le Model Registry
        model_name = "iris_model"
        model_info = mlflow.sklearn.log_model(
            sk_model=model, artifact_path="model", registered_model_name=model_name
        )

        # Affichage dynamique dans les logs Prefect
        if model_choice == "random_forest":
            print(
                f"📦 Modèle {model_type_str} (run_id: {run_id}) enregistré avec l'accuracy: {accuracy:.2f} | Arbres: {n_trees}"
            )
        else:
            print(
                f"📦 Modèle {model_type_str} (run_id: {run_id}) enregistré avec l'accuracy: {accuracy:.2f}"
            )

    # --- GESTION DE L'ALIAS 'PRODUCTION' ---
    client = MlflowClient()
    latest_version = model_info.registered_model_version

    if assign_production_alias:
        client.set_registered_model_alias(model_name, model_alias, str(latest_version))
        print(
            f"🚀 Version {latest_version} ({model_type_str}) passée en alias '{model_alias}'."
        )
    else:
        print(
            f"ℹ️ Version {latest_version} ({model_type_str}) enregistrée dans MLflow sans modifier la production."
        )


# Le Chef d'Orchestre (Flow) qui exécute les tâches dans le bon ordre
# @flow(name="Pipeline Entrainement Iris", log_prints=True)
# def pipeline_mlops():
#     print("Démarrage du pipeline de modélisation...")
#     prepare_minio()
#     train_and_register()
#     print("Pipeline achevé avec succès.")


# Le Chef d'Orchestre (Flow) qui exécute les tâches dans le bon ordre
@flow(name="Pipeline Entrainement Iris", log_prints=True)
def pipeline_mlops():
    print("Démarrage du pipeline de modélisation...")
    prepare_minio()

    # 1. Le "Champion" : Régression Logistique (mise en production)
    train_and_register(model_choice="logistic_regression", assign_production_alias=True)

    # 2. Le "Challenger" : Random Forest (enregistré dans MLflow pour analyse, mais pas en production)
    train_and_register(model_choice="random_forest", assign_production_alias=False)

    print("Pipeline achevé avec succès.")


if __name__ == "__main__":
    pipeline_mlops()  # Au lieu d'appeler les fonctions séparément, on appelle le Flow
