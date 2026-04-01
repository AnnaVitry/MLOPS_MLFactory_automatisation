# 🌸 MLOps Factory_automatisation - Iris Dataset

[![CI Pipeline](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation/actions/workflows/ci.yml/badge.svg)](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation/actions/workflows/cd.yml/badge.svg)](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation/actions/workflows/cd.yml)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![License](https://img.shields.io/badge/license-MIT-green.svg)

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat&logo=mlflow&logoColor=white)
![Prefect](https://img.shields.io/badge/Prefect-000000?style=flat&logo=prefect&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)

---

##  ʕ•ᴥ•ʔっ · · · ✴ Vision et Architecture (Qui fait quoi ?)

L'**Iris ML Factory_automatisation** est une usine logicielle en pleine évolution vers le standard **MLOps Cloud-Native**. 

1. **L'Orchestrateur (Prefect) :** Planifie et exécute les entraînements dans des conteneurs isolés.
2. **L'Entrepôt de Données (MinIO) :** Stockage physique (S3) pour les binaires des modèles (`.pkl`).
3. **Le Registre (MLflow) :** Trace les métriques expérimentales et gère les alias (ex: `production`).
4. **Le Moteur d'Inférence (FastAPI) :** API REST avec rechargement à chaud (Hot-Reload) du modèle.
5. **Le Tableau de Bord (Streamlit) :** L'interface utilisateur finale.
6. **La Tour de Contrôle (Monitoring) :** *(En cours d'intégration)* Uptime Kuma, Prometheus et Grafana pour l'observabilité.

---

##  ʕ•ᴥ•ʔっ · · · ✴ Guide de Mise en Route (From Scratch)

Ce guide est conçu pour fonctionner sur une machine totalement vierge (aucun volume, aucune base de données préexistante).

### Étape 1 : Préparation de l'Environnement Local
Clonez le dépôt et initialisez l'environnement Python avec `uv` pour installer les dépendances strictement verrouillées :
```bash
git clone [https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git)
cd MLOPS_MLFactory_automatisation
uv venv
source .venv/bin/activate
uv sync
```

### Étape 2 : Allumage de l'Infrastructure de Base (V1)
Démarrez les services fondamentaux (API, Front, MLflow, MinIO, Postgres) :
```bash
docker compose up -d --build
```
*(Attendez environ 15 secondes que les bases de données s'initialisent pour la première fois).*

### Étape 3 : Amorçage de l'Usine (Bootstrapping)
Pour éviter que l'API ne renvoie une erreur 404 (car MLflow et MinIO sont physiquement vides à ce stade), exécutez un premier entraînement manuel pour "nourrir" le registre :
```bash
uv run src/train/train.py
```
*Vérification : Allez sur `http://localhost:8501` et lancez une prédiction pour valider que l'API a bien téléchargé le modèle.*

### Étape 4 : Configuration et Validation de l'Orchestrateur (Prefect)
Pour automatiser l'entraînement, il faut configurer le serveur Prefect en partant de zéro. Respectez scrupuleusement cet ordre :

```bash
# A. Créer la file d'attente (Work Pool) requise par le déploiement
uv run prefect work-pool create "docker-pool" --type docker

# B. Construire l'image du modèle et déployer le pipeline sur le serveur
uv run prefect deploy -n production-training-job

# C. Allumer l'ouvrier qui va écouter la file d'attente (Garder ce terminal ouvert !)
uv run prefect worker start --pool 'docker-pool'
```
*Vérification : Allez sur `http://localhost:4200`, déclenchez un "Quick Run" depuis l'interface Deployments et observez le Hot-Reloading s'activer sur Streamlit.*

### Étape 5 : L'Usine Avancée (En cours de construction)
Une fois la base validée, l'usine peut basculer sur l'infrastructure avancée incluant la stack de monitoring complète et les files d'attente asynchrones :
```bash
# Éteindre l'ancienne base
docker compose down

# Allumer la forge complète (avec Grafana, Prometheus, Uptime Kuma...)
docker compose -f docker-compose.full.yml up -d --build
```

---

##  ʕ•ᴥ•ʔっ · · · ✴ Accès aux Services & Observabilité

| Service | URL | Usage |
| :--- | :--- | :--- |
| **Streamlit UI** | `http://localhost:8501` | Interface utilisateur finale |
| **Prefect Server** | `http://localhost:4200` | Orchestration, Workers et déclenchements manuels |
| **MLflow UI** | `http://localhost:5000` | Suivi des runs expérimentaux et registre des modèles |
| **MinIO Console** | `http://localhost:9001` | Exploration physique des fichiers (.pkl) |
| **FastAPI Docs** | `http://localhost:8000/docs` | Swagger / Documentation interactive de l'API |
| **Grafana** | `http://localhost:3000` | *(Nouveau)* Tableaux de bord de performance |
| **Uptime Kuma** | `http://localhost:3001` | *(Nouveau)* Monitoring de disponibilité |

---

##  ʕ•ᴥ•ʔっ · · · ✴ Intégration et Déploiement Continus (CI/CD)

Le projet applique une discipline logicielle stricte via **GitHub Actions**. Le code doit maintenir une couverture de test supérieure à **80%** pour être déployé.

* **CI (Continuous Integration)** : Scan de sécurité (Gitleaks), linting intransigeant (Ruff), et tests unitaires de l'API (Pytest).
* **CD (Continuous Deployment)** : L'usine compile automatiquement les **Images Docker** vers le GHCR et déploie la **Documentation Technique** (Thème Furo) sur GitHub Pages.

**[Consulter la Documentation Officielle Complète](https://annavitry.github.io/MLOPS_MLFactory_automatisation/)**

---

##  ʕ•ᴥ•ʔっ · · · ✴ Maintenance & Dépannage Radical (Troubleshooting)

Si l'environnement Docker devient instable (conflits de volumes, mots de passe erronés), appliquez la politique de la terre brûlée :

```bash
# 1. Détruire l'infrastructure ET purger les mémoires corrompues (Volumes)
docker compose down -v  

# 2. Nettoyage massif du stockage Docker (Attention, supprime le cache)
docker builder prune -a --force
docker image prune -a -f
docker volume prune -f

# 3. Redémarrage propre
docker compose up -d --build
```
> [!WARNING]
> Le `down -v` ou le `volume prune` détruisent l'historique de MLflow, la base de données Prefect et les fichiers S3 dans MinIO. C'est une remise à zéro totale.
