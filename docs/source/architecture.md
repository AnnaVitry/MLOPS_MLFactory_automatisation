# Architecture de la ML Factory

L'infrastructure de la ML Factory repose sur une architecture **MLOps Cloud-Native**, assurant une séparation stricte entre l'orchestration, l'entraînement, le stockage et l'inférence.

## Composants Principaux

### 1. Prefect (Orchestrateur & Docker Worker)
* **Rôle :** Le chef d'orchestre temporel.
* Il remplace l'exécution manuelle des scripts. Il planifie les tâches (via Cron) et ordonne au *Docker Engine* de créer des conteneurs éphémères pour entraîner les modèles dans un environnement vierge avant de les détruire.

### 2. MinIO (S3 Compatible)
* **Rôle :** Stockage physique (Artifact Store).
* Tous les fichiers binaires `.pkl` générés par Scikit-Learn sont sauvegardés de manière pérenne dans le bucket `mlflow`.

### 3. MLflow Tracking & Registry
* **Rôle :** Le centre de contrôle (Model Registry).
* Suivi des métriques (Accuracy), des hyperparamètres, et gestion du cycle de vie des modèles via le système d'Alias (ex: assigner l'étiquette `production` au modèle le plus performant).

### 4. FastAPI (Inférence)
* **Rôle :** Le moteur de prédiction.
* Implémente une logique de **Hot-Reloading** : à chaque requête, il interroge MLflow pour s'assurer que le modèle chargé en RAM correspond bien à l'alias `production`. Si l'alias change, il télécharge silencieusement le nouveau binaire depuis MinIO sans interrompre le service.

### 5. Streamlit (Front-End)
* **Rôle :** Interface utilisateur.
* Communique de manière asynchrone avec FastAPI pour offrir une visualisation en temps réel.

## Arborescence du Projet

```bash
MLOPS_MLFACTORY/
├── data/                   # Fichiers CSV générés pour les tests
├── docs/                   # Documentation technique Sphinx/ReadTheDocs
├── src/
│   ├── api/                # Backend FastAPI (Inférence & Hot-Reloading)
│   ├── front/              # Interface Streamlit (UI)
│   └── train/              # Pipeline d'entraînement métier (Flow Prefect)
├── prefect.yaml            # Plan de vol de Prefect (Déploiement et Worker)
├── .env                    # Variables d'environnement locales (Secrets et URLs)
├── docker-compose.yml      # L'usine (MinIO, MLflow, API, Front, Prefect DB)
└── pyproject.toml          # Gestion stricte des dépendances avec uv
```
