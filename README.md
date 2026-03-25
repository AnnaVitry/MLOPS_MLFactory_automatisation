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
![MinIO](https://img.shields.io/badge/MinIO-C7202C?style=flat&logo=minio&logoColor=white)
![Prefect](https://img.shields.io/badge/Prefect-000000?style=flat&logo=prefect&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)

---

##  ʕ•ᴥ•ʔっ · · · ✴ Vision et Architecture (Qui fait quoi et pourquoi ?)

L'**Iris ML Factory_automatisation** n'est pas un simple script d'apprentissage automatique. C'est une usine logicielle complète, **totalement découplée** et **supervisée**, conçue pour démontrer les standards du **MLOps Cloud-Native**. 

Chaque composant a un rôle strict et isolé. Voici le casting de l'architecture :

1. **L'Orchestrateur (Prefect) :** Le cerveau temporel. Il remplace les scripts manuels. Il planifie les entraînements (cron) et ordonne au *Docker Engine* de créer des conteneurs éphémères pour exécuter le code Python dans un environnement vierge et isolé, avant de les détruire.
2. **L'Entrepôt de Données et Modèles (MinIO) :** L'espace de stockage physique (compatible S3). Il conserve les binaires bruts des modèles générés (`.pkl`).
3. **Le Registre et Traceur (MLflow) :** Le centre de contrôle. Il ne stocke pas les fichiers, mais trace les métriques (Accuracy), les paramètres, et gère le cycle de vie des modèles via un système d'alias (ex: tagguer la Version 37 comme `production`).
4. **Le Moteur d'Inférence (FastAPI) :** L'API REST. Elle interroge MLflow pour savoir quelle est la version en `production`, puis télécharge le binaire correspondant depuis MinIO pour répondre aux requêtes.
5. **Le Tableau de Bord (Streamlit) :** L'interface utilisateur finale pour soumettre des données et visualiser les prédictions en temps réel.
6. **L'Aspirateur de Métriques (Prometheus) :** Le système de télémétrie "Boîte Blanche". Il aspire silencieusement les données internes de l'usine (RAM consommée par l'API, nombre de prédictions effectuées, poids des modèles stockés sur MinIO).
7. **La Tour de Contrôle (Grafana) :** L'interface d'analyse visuelle. Elle traduit les données complexes de Prometheus en tableaux de bord compréhensibles pour suivre la santé métier et système de l'usine.
8. **Le Gardien (Uptime Kuma) :** Le système d'alerte "Boîte Noire". Il surveille la disponibilité des points d'entrée critiques (API, Streamlit, MLflow) comme le ferait un utilisateur externe, et déclenche instantanément une alerte Discord en cas de crash.

```text
MLOPS_MLFACTORY_automatisation/
├── data/                   # Fichiers CSV générés pour les tests
├── docs/                   # Documentation technique Sphinx/ReadTheDocs
├── src/
│   ├── api/                # Backend FastAPI (Inférence, Hot-Reloading & Métriques)
│   ├── front/              # Interface Streamlit (UI)
│   └── train/              # Pipeline d'entraînement métier (Agnostique de l'infrastructure)
├── prometheus/             # Configuration des cibles de scraping (Télémétrie)
├── prefect.yaml            # Le plan de vol de Prefect (Déploiement et configuration du DockerWorker)
├── .env                    # Fichier VITAL (Variables locales : 127.0.0.1)
├── docker-compose.yml      # L'usine complète (MinIO, MLflow, API, Front, Prefect, DB, Monitoring)
└── pyproject.toml          # Gestion des dépendances avec uv
```

---

##  ʕ•ᴥ•ʔっ · · · ✴ Démarrage Rapide & Pilotage de l'Usine

L'infrastructure persistante est gérée par Docker Compose, tandis que l'exécution métier est confiée aux Workers Prefect.

### 1. Préparation des Fondations
Clonez le dépôt et assurez-vous que votre fichier `.env` est correctement configuré.
**Attention :** Le fichier `.env` lu par votre terminal local doit pointer vers `127.0.0.1` (et non `host.docker.internal` ou `minio`, qui sont réservés au réseau interne Docker).
```bash
git clone [https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git)
cd MLOPS_MLFactory_automatisation
```

### 2. Allumage de l'Infrastructure Persistante
Lancez les bases de données, les serveurs de tracking, les API et le monitoring :
```bash
docker compose up -d --build
```
*(Attendez environ 15 secondes que la base de données de Prefect s'initialise correctement).*

### 3. Activer l'Automatisation MLOps (Prefect)
Plutôt que d'exécuter l'entraînement sur un terminal local, nous allons compiler une image dédiée et allumer un ouvrier (Worker) qui attendra les ordres :

```bash
# A. Construit l'image Docker du Worker et met à jour le serveur Prefect
uv run prefect deploy -n production-training-job

# B. (Si besoin) Crée la file d'attente Docker
uv run prefect work-pool create "docker-pool" --type docker

# C. Allume l'ouvrier (Garde ce terminal ouvert !)
uv run prefect worker start --pool 'docker-pool'
```

---

##  ʕ•ᴥ•ʔっ · · · ✴ Observabilité & Chaos Engineering (Nouveau !)

Pour garantir une disponibilité totale en production, l'usine intègre un système d'observabilité de pointe.

**1. Tableaux de bord en direct (Grafana)**
Grafana lit les données de Prometheus pour afficher en temps réel :
* Le nombre de prédictions effectuées par l'API (et la distribution des modèles utilisés).
* La consommation RAM et CPU du conteneur d'inférence (pour anticiper les *OOM Kills*).
* Le nombre d'artefacts ML stockés et l'empreinte disque sur MinIO.

**2. Alerting & Sécurité (Test du Chaos)**
L'infrastructure utilise **Uptime Kuma** pour surveiller la santé de la stack. 
Vous pouvez simuler une panne (Chaos Engineering) pour tester le routage des alertes vers Discord :
```bash
# Simuler le crash du Front-End et de l'API
docker stop ml_api ml_front
```
*-> Dans les 60 secondes, Uptime Kuma détectera le Timeout et enverra une notification Discord critique. Utilisez `docker start ml_api ml_front` pour rétablir les services et recevoir le message de résolution ("Service is UP").*

---

##  ʕ•ᴥ•ʔっ · · · ✴ Fonctionnement du Rechargement à Chaud (Hot Reload)

L'API (`src/api/main.py`) utilise un mécanisme de cache intelligent pour éviter les redémarrages manuels du serveur FastApi lorsque le modèle change :

1. **Vérification de l'Alias** : À chaque requête de prédiction, l'API demande à MLflow : *"Quelle version porte l'alias 'production' ?"*.
2. **Comparaison de Version** : 
   - Si `prod_version == state["version"]`, l'API utilise le modèle déjà en mémoire RAM (réponse ultra-rapide).
   - Si `prod_version != state["version"]`, l'API télécharge silencieusement le nouveau fichier `.pkl` depuis MinIO sans couper le serveur.
3. **Mise à jour Front** : L'interface Streamlit récupère la clé `model_version` renvoyée par l'API et met à jour son affichage instantanément.

---

##  ʕ•ᴥ•ʔっ · · · ✴  Expérimentation : Comment changer de modèle en 3 clics

L'un des plus grands accomplissements de cette architecture MLOps est son dynamisme. 

**Étape 1 : Demander un nouveau modèle au Cerveau (Prefect)**
1. Ouvrez l'interface Prefect : [http://localhost:4200](http://localhost:4200)
2. Allez dans **Deployments** et sélectionnez `production-training-job`.
3. Cliquez sur **Custom Run**. Dans le champ `champion_model`, tapez `random_forest`, puis validez.
*Le Docker Worker s'allume en arrière-plan, entraîne le Random Forest, et MLflow déplace l'alias `production`.*

**Étape 2 : La magie du Hot-Reload (Streamlit & FastAPI)**
1. Allez sur votre interface utilisateur : [http://localhost:8501](http://localhost:8501)
2. Cliquez simplement sur **🚀 Lancer la prédiction**.
3. L'API FastAPI détecte le changement d'alias, télécharge le nouveau modèle depuis MinIO, et exécute la prédiction. Le numéro de version sur le Front-End se met à jour automatiquement !

---

##  ʕ•ᴥ•ʔっ · · · ✴ Accès aux Services

| Service | URL | Usage |
| :--- | :--- | :--- |
| **Streamlit UI** | `http://localhost:8501` | Interface utilisateur finale (Front-End) |
| **Grafana** | `http://localhost:3002` | **[NOUVEAU]** Tableaux de bord de supervision MLOps |
| **Uptime Kuma** | `http://localhost:3001` | **[NOUVEAU]** Gestion des sondes et alertes Discord |
| **Prefect Server** | `http://localhost:4200` | Orchestration, Workers, logs et déclenchements manuels |
| **MLflow UI** | `http://localhost:5000` | Suivi des runs expérimentaux et registre des modèles |
| **MinIO Console** | `http://localhost:9001` | Exploration physique des fichiers (Artefacts .pkl) |
| **FastAPI Docs** | `http://localhost:8000/docs` | Swagger / Documentation interactive de l'API |
| **Prometheus** | `http://localhost:9090` | Base de données temporelle interne (Requêtes brutes) |

---

##  ʕ•ᴥ•ʔっ · · · ✴ Intégration et Déploiement Continus (CI/CD)

Le projet applique une discipline logicielle stricte via **GitHub Actions** :

* **CI (Continuous Integration)** : À chaque `push`, le code est audité contre les fuites de secrets (Gitleaks) et soumis à une analyse statique intransigeante (Linting PEP 8) par **Ruff**. Le pipeline échoue si le code n'est pas clinique.
* **CD (Continuous Deployment)** : Une fois la CI validée, l'usine compile automatiquement :
  1. Les **Images Docker** (API & Front) poussées sur le *GitHub Container Registry* (GHCR).
  2. La **Documentation Technique** (Sphinx/Diátaxis) compilée et déployée dynamiquement sur GitHub Pages.

**[Consulter la Documentation Officielle Complète](https://annavitry.github.io/MLOPS_MLFactory_automatisation/)**

---

##  ʕ•ᴥ•ʔっ · · · ✴ Maintenance & Dépannage Radical (Troubleshooting)

L'architecture Docker peut parfois s'emmêler les pinceaux avec le cache ou les volumes. Si l'environnement devient instable, appliquez la politique de la terre brûlée :

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
> Le `down -v` ou le `volume prune` détruisent l'historique de MLflow, la base de données Prefect, les tableaux Grafana, les alertes Kuma et les fichiers S3 dans MinIO. C'est une remise à zéro complète de l'usine.

* **Erreur "404 Client Error: Not Found... fromImage=mlfactory-worker" :** Votre Worker Prefect tente de télécharger l'image depuis Internet au lieu de l'ordinateur local. Assurez-vous d'avoir bien mis `image_pull_policy: "Never"` dans votre `prefect.yaml` au niveau de `job_variables`, et relancez la commande `uv run prefect deploy`.

