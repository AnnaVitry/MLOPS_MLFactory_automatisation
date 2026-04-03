# 🌸 MLOps Factory - Asynchronous & Monitored Architecture (Iris Dataset)

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
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=flat&logo=rabbitmq&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=flat&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)

---

## ʕ•ᴥ•ʔっ · · · ✴ Architecture & Rôle des Composants

### ✴ Schéma d'Architecture Globale (Flux de Données)

```text
       [ 👩‍💻 Utilisateur / Data Scientist ]
                   │
                   ├──(Entraînement)───────▶ [ 🧠 Prefect (Orchestrateur) ]
                   │                                     │
                   ▼                                     ▼
        [ 🖥️ Streamlit (Front-end) ]            (Script train.py)
                   │                                     │
         (Requête POST JSON)                             │
                   │                                     │
                   ▼                                     │
          [ ⚙️ FastAPI (API) ]                           │
                   │                                     │
      (Publie un Ticket de Tâche)                        │
                   │                                     │
┌──────────────────▼─────────────────────────────────────▼──────────────────┐
│                   MESSAGE BROKER & ASYNCHRONE                             │
│                                                                           │
│ [ 🐇 RabbitMQ ] ◀────────(Dépile la file d'attente)──────── [ 👷 Celery ] │
│  (File / Queue)                                              (Worker ML)  │
│                                                                   │       │
│ [ 🔴 Redis ] ◀───────────(Dépose le résultat final)───────────────┘       │
│ (Result Backend)                                                          │
└──────────────────▲────────────────────────────────────────────────────────┘
                   │                                                │
   (Vérifie le statut du Ticket)                       (Télécharge le modèle)
                   │                                                ▼
          [ ⚙️ FastAPI (API) ]                       [ 📦 MLflow (Registry) ]
                   ▲                                                │
                   │                                                │
                   │ (Pousse un nouveau modèle Champion) ◀──────────┘
                   │
┌──────────────────▼────────────────────────────────────────────────────────┐
│                      PERSISTANCE & STOCKAGE                               │
│                                                                           │
│ ├── [ 🐘 PostgreSQL ] (Sauvegarde les métadonnées : Runs, UUIDs, Alias)   │
│ └── [ 🪣 MinIO / S3 ] (Sauvegarde les gros fichiers binaires : model.pkl) │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITÉ & MONITORING (Tour de contrôle)          │
│                                                                           │
│ ├── [ 👁️ Prometheus ] (Aspire les métriques de RabbitMQ, API, Celery)     │
│ ├── [ 📊 Grafana ]    (Connecté à Prometheus pour dessiner les graphiques)│
│ └── [ 💓 Uptime Kuma] (Ping HTTP pour vérifier que tout est en ligne)     │
└───────────────────────────────────────────────────────────────────────────┘
```
 Cette usine MLOps est conçue pour être robuste, asynchrone et hautement observable. Voici la fonction exacte de chaque brique de l'infrastructure :

###  1. Le Cœur Métier (Front & Back)
* **Front-end (Streamlit - Port `8501`)** : L'interface utilisateur. Elle ne calcule rien. Elle capte les mesures de la fleur saisies par l'utilisateur, les envoie à l'API, et écoute le statut du "ticket" jusqu'à l'obtention du résultat.
* **API (FastAPI - Port `8000`)** : Le point d'entrée du système. Elle reçoit la requête, mais au lieu de bloquer le système pour faire la prédiction, elle crée une tâche asynchrone, la donne à RabbitMQ, et renvoie un `task_id` (un numéro de ticket) à l'utilisateur.
* **Worker (Celery)** : L'ouvrier de l'usine. Il tourne en arrière-plan, télécharge le modèle ML depuis MLflow, récupère les tâches en attente dans RabbitMQ, exécute la prédiction (`model.predict()`), et range le résultat dans Redis.

### 2. Le Système de File d'Attente (Message Broker)
* **RabbitMQ (Port `5672` / UI `15672`)** : Le gestionnaire de file d'attente (Broker). Si 1000 utilisateurs cliquent sur "Prédire" en même temps, RabbitMQ stocke les requêtes proprement et les distribue au(x) Worker(s) Celery à leur rythme, évitant ainsi le crash de l'API.
* **Redis (Port `6379`)** : Le backend de résultats (Result Backend). Une fois que Celery a fini son calcul, il dépose la réponse (ex: "Classe 0") dans la mémoire ultra-rapide de Redis. L'API consulte Redis pour savoir si la tâche est terminée.

### 3. La Gestion du Machine Learning (Model Registry)
* **Modèle ML (Scikit-Learn)** : L'algorithme d'Intelligence Artificielle entraîné à classifier les fleurs d'Iris.
* **MLflow (Port `5000`)** : Le registre des modèles. Il versionne les expériences, stocke les hyperparamètres, et définit quel modèle possède l'alias `production`. Le Worker Celery interroge toujours MLflow pour utiliser la bonne version de l'IA.
* **MinIO (Port `9000` / UI `9001`)** : Le disque dur (compatible Amazon S3). MLflow n'est qu'un catalogue ; les fichiers physiques volumineux des modèles (`model.pkl`) sont stockés de manière sécurisée dans MinIO.
* **PostgreSQL** : La base de données relationnelle qui stocke toutes les métadonnées (qui a fait quoi, quand, et quelles étaient les métriques) pour MLflow et potentiellement l'orchestrateur de CI/CD.

### 4. L'Observabilité & Le Monitoring
* **Prometheus (Port `9090`)** : L'aspirateur à métriques (Time-Series Database). Toutes les 15 secondes, il se connecte à RabbitMQ, Redis, et aux APIs pour "scrapper" (récupérer) les données d'utilisation (CPU, RAM, nombre de requêtes, erreurs).
* **Grafana (Port `3000`)** : L'outil de visualisation. Il se branche sur la base de données Prometheus et transforme les chiffres bruts en tableaux de bord (Dashboards) graphiques dynamiques.
* **Uptime Kuma (Port `3001`)** : Le gardien de disponibilité. Il "ping" (vérifie) régulièrement si l'API, le Front ou MLflow sont vivants. En cas de crash d'un conteneur, il peut envoyer des alertes.

---

## ʕ•ᴥ•ʔっ · · · ✴ Guide de Démarrage (From Scratch)

Si vous partez d'une machine vierge, suivez ces étapes rigoureusement dans l'ordre.

### Étape 1 : Prérequis de la machine hôte
1. Installez **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (ou Docker Engine & Docker Compose).
2. Installez **[Git](https://git-scm.com/)**.
3. Installez **[uv](https://github.com/astral-sh/uv)** (le gestionnaire de paquets Python ultra-rapide) :
   * *Mac/Linux :* `curl -LsSf https://astral.sh/uv/install.sh | sh`
   * *Windows :* `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

### Étape 2 : Clonage et Environnement
Clonez le dépôt, placez-vous sur la bonne branche, et créez le fichier d'environnement :

```bash
git clone [https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git)
cd MLOPS_MLFactory_automatisation
git checkout feature/advanced-mlops-monitoring
```

Créez un fichier `.env` à la racine du projet contenant la configuration de base :
```env
# Configuration MLflow & MinIO
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
MLFLOW_TRACKING_URI=http://localhost:5000
AWS_ACCESS_KEY_ID=admin
AWS_SECRET_ACCESS_KEY=password123

#Configuration du Cerveau Prefect (Orchestrateur)
PREFECT_API_URL=http://127.0.0.1:4200/api
POSTGRES_PASSWORD=un_mot_de_passe_robuste

# Configuration API
MODEL_NAME=iris_model
MODEL_ALIAS=production
```
> *Un fichier .env.example éxiste à la racine pour pouvoir l'utiliser comme base*

### Étape 3 : Lancement de l'Infrastructure Docker
Construisez et lancez l'usine complète en arrière-plan :

```bash
docker compose -f docker-compose.full.yml up -d --build
```
> *Patientez 30 secondes pour laisser le temps aux bases de données (Postgres, MinIO, RabbitMQ) de s'initialiser correctement.*

### Étape 4 : Entraînement et Mise en Production du Modèle
L'usine est prête, mais ses étagères (MLflow) sont vides. Il faut entraîner le modèle initial.

```bash
# 1. Synchronisation de l'environnement Python local
uv sync --python 3.12

# 2. Lancement du script d'entraînement (création du bucket et log dans MLflow)
uv run python src/train/train.py
```

**L'étape finale manuelle cruciale :**
1. Ouvrez MLflow dans votre navigateur : **http://localhost:5000**
2. Allez dans l'onglet **Models**, cliquez sur `iris_model`.
3. Cliquez sur la version qui vient d'être générée (ex: Version 1).
4. Ajoutez l'alias **`production`** (cliquez sur "Add alias").

### Étape 5 : Testez l'Usine !
Ouvrez l'interface Streamlit sur **http://localhost:8501**, ajustez les curseurs et lancez une prédiction !

---

## ʕ•ᴥ•ʔっ · · · ✴ Créer des Dashboards sur Grafana

Une fois l'usine en marche, vous devez la surveiller.

**Accès :** http://localhost:3000 (Identifiants par défaut : `admin` / `admin`).

### 1. Connecter la source de données (Prometheus)
1. Dans le menu de gauche, allez dans **Connections** > **Data Sources**.
2. Cliquez sur **Add data source** et sélectionnez **Prometheus**.
3. Dans le champ URL, entrez : `http://prometheus:9090` (C'est le nom du conteneur Docker).
4. Descendez en bas et cliquez sur **Save & Test**.

### 2. Créer les Panels de surveillance

Cliquez sur **Dashboards** > **New Dashboard** > **Add Visualization** (choisissez Prometheus).

Voici les requêtes (PromQL) à utiliser pour créer vos graphiques :

* **Surveiller RabbitMQ (Les messages en attente) :**
    * *Savoir si l'usine est surchargée.*
    * **Requête PromQL :** `rabbitmq_queue_messages{queue="celery"}`
    * *Type de Panel :* Stat ou Time series.

* **Surveiller l'API (Nombre de requêtes HTTP) :**
    * *Savoir combien d'utilisateurs utilisent le système.*
    * **Requête PromQL :** `rate(http_requests_total[5m])` *(Nécessite que FastAPI expose ses métriques via `prometheus-fastapi-instrumentator`)*.
    * *Type de Panel :* Time series.

* **Surveiller la santé des Conteneurs (Optionnel - via cAdvisor) :**
    * **Requête PromQL (RAM) :** `container_memory_usage_bytes{name="mlfactory_worker_celery"}`

> **Astuce :** Au lieu de créer les panels un par un, vous pouvez importer des dashboards pré-faits créés par la communauté. Dans *Dashboards*, cliquez sur *Import* et entrez l'ID `10991` (pour RabbitMQ) pour générer instantanément un tableau de bord complet !

---

## ʕ•ᴥ•ʔっ · · · ✴ Intégration et Déploiement Continus (CI/CD)

Le projet applique une discipline logicielle stricte via **GitHub Actions** pour garantir que le code en production est fiable.

* **CI (Continuous Integration - `ci.yml`)** : À chaque `push` ou `pull request` vers `main`, GitHub déclenche :
    * Un scan de sécurité (Gitleaks) pour éviter la fuite de mots de passe.
    * Un linting intransigeant (Ruff) pour formater le code.
    * Des tests unitaires (Pytest) simulés sur un environnement Docker jetable.
* **CD (Continuous Deployment - `cd.yml`)** : Si la CI est verte, l'usine compile automatiquement les **Images Docker** vers le GitHub Container Registry (GHCR) et déploie la **Documentation Technique** (Sphinx/Thème Furo) sur GitHub Pages.

**[Consulter la Documentation Officielle Complète](https://annavitry.github.io/MLOPS_MLFactory_automatisation/)**

---

## ʕ•ᴥ•ʔっ · · · ✴ Accès aux Services & Observabilité

| Service | URL / Accès | Identifiants par défaut | Rôle & Usage |
| :--- | :--- | :--- | :--- |
| **Streamlit UI** | [http://localhost:8501](http://localhost:8501) | *Aucun* | Interface utilisateur finale pour lancer les prédictions asynchrones. |
| **FastAPI Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | *Aucun* | Documentation Swagger interactive pour tester l'API directement. |
| **MLflow UI** | [http://localhost:5000](http://localhost:5000) | *Aucun* | Registre des modèles (Model Registry), gestion des alias et suivi des runs. |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | `admin` / `password123` | Console d'exploration (type AWS S3) pour voir les fichiers physiques (`.pkl`). |
| **RabbitMQ UI** | [http://localhost:15672](http://localhost:15672) | `guest` / `guest` | Console d'administration du Message Broker (suivi des files d'attente Celery). |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` | Dashboards de performance (consommation RAM, flux de l'API, charge RabbitMQ). |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | *Aucun* | Base de données de métriques brutes et cibles de scrapping. |
| **Uptime Kuma** | [http://localhost:3001](http://localhost:3001) | *À créer au 1er accès* | Monitoring du statut (Up/Down) des conteneurs avec historique de disponibilité. |
| **Prefect Server** | [http://localhost:4200](http://localhost:4200) | *Aucun* | Orchestrateur des pipelines d'entraînement locaux (Train/Deploy). |
| **Celery Worker** | *Processus en arrière-plan* | - | *Worker asynchrone* : récupère le modèle, dépile les tâches et calcule. |
| **Redis** | `localhost:6379` (Port) | *Aucun* | *Result Backend* : Stockage ultra-rapide temporaire des résultats de prédiction. |
| **PostgreSQL** | `localhost:5432` (Port) | `mlflow` / `mlflow` | *Database* : Stockage relationnel des métadonnées de l'infrastructure. |

---

## ʕ•ᴥ•ʔっ · · · ✴ Maintenance & Dépannage Radical (Troubleshooting)

Si l'environnement Docker devient instable (conflits de volumes, mots de passe erronés), appliquez la politique de la terre brûlée :

```bash
# 1. Détruire l'infrastructure ET purger les mémoires corrompues (Volumes)
docker compose -f docker-compose.full.yml down -v  

# 2. Nettoyage massif du stockage Docker (Attention, supprime le cache)
docker builder prune -a --force
docker image prune -a -f
docker volume prune -f

# 3. Redémarrage propre
docker compose -f docker-compose.full.yml up -d --build
```
