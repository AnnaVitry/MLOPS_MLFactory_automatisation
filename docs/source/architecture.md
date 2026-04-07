# 🏛️ Architecture de la ML Factory

L'infrastructure de la ML Factory repose sur une architecture **MLOps Cloud-Native**, assurant une séparation stricte entre l'orchestration, l'entraînement, le stockage, l'inférence asynchrone et l'observabilité.

## ʕ•ᴥ•ʔっ · · · ✴ Schéma Global (Flux de Données)

```{figure} _static/img/shema_mlfactory2.png
---
width: 100%
align: center
alt: Schéma de l'architecture MLOps
---
```

## ʕ•ᴥ•ʔっ · · · ✴ Composants Principaux

### 1. La Couche d'Entrée (User Facing)
* **Streamlit (UI) :** Interface utilisateur. Communique de manière asynchrone avec FastAPI. Elle capte les mesures, lance la demande, et interroge régulièrement l'API en attendant le résultat.
* **FastAPI (Inférence) :** Le guichetier asynchrone. Au lieu de bloquer le système lors d'une prédiction, il vérifie les données, place un ordre dans la file d'attente, et renvoie immédiatement un "Ticket" (Task ID) à l'utilisateur.

### 2. La Couche Asynchrone (Message Broker & Worker)
* **RabbitMQ :** L'amortisseur de chocs. Gère la file d'attente des prédictions. Si l'API reçoit un pic de requêtes, elles sont empilées ici pour éviter tout crash.
* **Celery Worker :** La force de calcul. Il tourne en arrière-plan, interroge RabbitMQ, récupère une tâche, télécharge la bonne version du modèle depuis MLflow, et exécute l'inférence.
* **Redis :** La mémoire ultra-rapide (Result Backend). Le Worker y dépose la prédiction finale. FastAPI vient lire cette mémoire pour informer Streamlit que le ticket est prêt.

### 3. La Couche Machine Learning & Stockage
* **Prefect (Orchestrateur) :** Le planificateur de l'entraînement. Il orchestre l'exécution du script `train.py` sous forme de graphe (DAG), gérant les tentatives en cas d'échec (retries).
* **MLflow Tracking & Registry :** Le centre de contrôle des modèles. Suivi des métriques (Accuracy), des hyperparamètres, et gestion du cycle de vie via l'assignation de l'alias `production`. Le Celery Worker l'interroge systématiquement pour charger la bonne IA.
* **MinIO (S3 Compatible) :** Stockage physique (Artifact Store). Sauvegarde pérenne des gros fichiers binaires `.pkl`.
* **PostgreSQL :** Base de données relationnelle archivistique stockant les métadonnées de MLflow.

### 4. La Couche d'Observabilité (SRE)
* **Prometheus :** Base de données Time-Series qui *scrape* les métriques matérielles et logicielles des conteneurs (RAM, requêtes HTTP, taille de la file RabbitMQ).
* **Grafana :** L'interface visuelle traduisant les données Prometheus en tableaux de bord dynamiques.
* **Uptime Kuma :** Le système de monitoring par ping qui vérifie la disponibilité en temps réel des différents conteneurs.

### 5. La Couche CI/CD (GitHub Actions)
* **Qualité & Sécurité :** Gitleaks (fuite de secrets) et Ruff (linting).
* **Tests :** Pytest exécuté sur une infrastructure Docker éphémère.
* **Déploiement :** Construction et push automatique des images (API, Worker, Front) vers le GitHub Container Registry (GHCR), et publication de cette documentation sur GitHub Pages.

## ʕ•ᴥ•ʔっ · · · ✴ Arborescence du Projet

```text
MLOPS_MLFACTORY/
├── .github/workflows/      # Pipelines CI/CD (Tests, Build Docker, GH Pages)
├── data/                   # Fichiers CSV générés pour les tests
├── docs/                   # Documentation technique Sphinx/Furo
├── prometheus/             # Configuration du scrapping des métriques
├── src/
│   ├── api/                # Backend FastAPI (Routage et distribution des tâches)
│   ├── front/              # Interface Streamlit asynchrone
│   ├── train/              # Pipeline d'entraînement métier (Flow Prefect)
│   └── worker/             # Logique Celery (Téléchargement MLflow & Inférence)
├── tests/                  # Tests unitaires et d'intégration (Pytest)
├── prefect.yaml            # Plan de vol de Prefect
├── .env.example            # Template des variables d'environnement (Secrets/URLs)
├── docker-compose.yml      # Infrastructure de base
├── docker-compose.full.yml # L'usine complète (Inclus Observabilité & Broker)
└── pyproject.toml          # Gestion stricte des dépendances avec uv
```