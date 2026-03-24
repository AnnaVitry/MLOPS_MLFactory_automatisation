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

---

##  ʕ•ᴥ•ʔっ · · · ✴ Vision et Architecture (Qui fait quoi et pourquoi ?)

L'**Iris ML Factory_automatisation** n'est pas un simple script d'apprentissage automatique. C'est une usine logicielle complète et **totalement découplée** conçue pour démontrer les standards du **MLOps Cloud-Native**. 

Chaque composant a un rôle strict et isolé. Voici le casting de l'architecture :

1. **L'Orchestrateur (Prefect) :** Le cerveau temporel. Il remplace les scripts manuels. Il planifie les entraînements (cron) et ordonne au *Docker Engine* de créer des conteneurs éphémères pour exécuter le code Python dans un environnement vierge et isolé, avant de les détruire.
2. **L'Entrepôt de Données et Modèles (MinIO) :** L'espace de stockage physique (compatible S3 S3). Il conserve les binaires bruts des modèles générés (`.pkl`).
3. **Le Registre et Traceur (MLflow) :** Le centre de contrôle. Il ne stocke pas les fichiers, mais trace les métriques (Accuracy), les paramètres, et gère le cycle de vie des modèles via un système d'alias (ex: tagguer la Version 37 comme `production`).
4. **Le Moteur d'Inférence (FastAPI) :** L'API REST. Elle interroge MLflow pour savoir quelle est la version en `production`, puis télécharge le binaire correspondant depuis MinIO pour répondre aux requêtes.
5. **Le Tableau de Bord (Streamlit) :** L'interface utilisateur finale pour soumettre des données et visualiser les prédictions en temps réel.

```bash
MLOPS_MLFACTORY_automatisation/
├── data/                   # Fichiers CSV générés pour les tests
├── src/
│   ├── api/                # Backend FastAPI (Inférence & Hot-Reloading)
│   ├── front/              # Interface Streamlit (UI)
│   └── train/              # Pipeline d'entraînement métier (Agnostique de l'infrastructure)
├── prefect.yaml            # Le plan de vol de Prefect (Déploiement et configuration du DockerWorker)
├── .env                    # Fichier VITAL (Variables locales : 127.0.0.1)
├── docker-compose.yml      # L'usine (MinIO, MLflow, API, Front, Prefect Server, DB)
└── pyproject.toml          # Gestion des dépendances avec uv
```

---

##  ʕ•ᴥ•ʔっ · · · ✴ Démarrage Rapide & Pilotage de l'Usine

L'infrastructure persistante est gérée par Docker Compose, tandis que l'exécution métier est confiée aux Workers Prefect.

### 1. Préparation des Fondations
Clone le dépôt et assure-toi que ton fichier `.env` est correctement configuré.
**Attention :** Le fichier `.env` lu par ton terminal local doit pointer vers `127.0.0.1` (et non `host.docker.internal` ou `minio`, qui sont réservés au réseau interne Docker).
```bash
git clone [https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git](https://github.com/AnnaVitry/MLOPS_MLFactory_automatisation.git)
cd MLOPS_MLFactory_automatisation
```

### 2. Allumage de l'Infrastructure Persistante
Lance les bases de données, les serveurs de tracking et les interfaces web :
```bash
docker compose up -d --build
```
*(Attends environ 15 secondes que la base de données de Prefect s'initialise correctement).*

### 3. Activer l'Automatisation MLOps (Prefect)
Plutôt que d'exécuter l'entraînement sur ton propre terminal, nous allons compiler une image dédiée et allumer un ouvrier (Worker) qui attendra les ordres :

```bash
# A. Construit l'image Docker du Worker et met à jour le serveur Prefect
uv run prefect deploy -n production-training-job

# B. (Si besoin) Crée la file d'attente Docker
uv run prefect work-pool create "docker-pool" --type docker

# C. Allume l'ouvrier (Garde ce terminal ouvert !)
uv run prefect worker start --pool 'docker-pool'
```
*Le pipeline s'exécutera désormais tout seul, dans un conteneur éphémère (`mlfactory-worker`), selon la fréquence définie dans `prefect.yaml` (ex: toutes les 5 minutes).*

---

##  ʕ•ᴥ•ʔっ · · · ✴ Fonctionnement du Rechargement à Chaud (Hot Reload)

L'API (`src/api/main.py`) utilise un mécanisme de cache intelligent pour éviter les redémarrages manuels du serveur FastApi lorsque le modèle change :

1. **Vérification de l'Alias** : À chaque requête de prédiction, l'API demande à MLflow : *"Quelle version porte l'alias 'production' ?"*.
2. **Comparaison de Version** : 
   - Si `prod_version == state["version"]`, l'API utilise le modèle déjà en mémoire RAM (réponse ultra-rapide).
   - Si `prod_version != state["version"]`, l'API télécharge silencieusement le nouveau fichier `.pkl` depuis MinIO sans couper le serveur.
3. **Mise à jour Front** : L'interface Streamlit récupère la clé `model_version` renvoyée par l'API et met à jour son affichage instantanément.

---

##  ʕ•ᴥ•ʔっ · · · ✴  Expérimentation : Comment changer de modèle en 3 clics (Sans coder)

L'un des plus grands accomplissements de cette architecture MLOps est son dynamisme. Le pipeline d'entraînement a été paramétré via Prefect. Cela signifie que **vous n'avez plus besoin de modifier le code Python pour mettre un nouvel algorithme en production**. 

Voici comment tester le *Hot-Reloading* (rechargement à chaud) de l'application web en direct :

**Étape 1 : Demander un nouveau modèle au Cerveau (Prefect)**
1. Ouvrez l'interface Prefect : [http://localhost:4200](http://localhost:4200)
2. Allez dans l'onglet **Deployments** et sélectionnez `production-training-job`.
3. En haut à droite, cliquez sur la flèche à côté du bouton **Run** et choisissez **Custom Run**.
4. Un formulaire généré automatiquement apparaît ! Dans le champ `champion_model`, tapez `random_forest` (au lieu de `logistic_regression`), puis validez.

**Étape 2 : L'Usine travaille toute seule**
* Le **Docker Worker** s'allume en arrière-plan, instancie un conteneur isolé, entraîne le Random Forest, et le taggue comme le nouveau Champion.
* **MLflow** déplace l'alias `production` sur cette nouvelle version.

**Étape 3 : La magie du Hot-Reload (Streamlit & FastAPI)**
1. Allez sur votre interface utilisateur : [http://localhost:8501](http://localhost:8501)
2. L'interface n'a pas été redémarrée, mais cliquez simplement sur **🚀 Lancer la prédiction**.
3. Observez le résultat : l'API FastAPI a détecté le changement d'alias, a téléchargé le nouveau modèle Random Forest depuis MinIO, et l'a exécuté. **Le numéro de version affiché en gris s'est mis à jour automatiquement !**

---

##  ʕ•ᴥ•ʔっ · · · ✴ Accès aux Services

| Service | URL | Usage |
| :--- | :--- | :--- |
| **Prefect Server** | `http://localhost:4200` | Orchestration, Workers, logs et déclenchements manuels |
| **Streamlit UI** | `http://localhost:8501` | Interface utilisateur finale |
| **MLflow UI** | `http://localhost:5000` | Suivi des runs expérimentaux et registre des modèles |
| **MinIO Console** | `http://localhost:9001` | Exploration physique des fichiers (Artefacts .pkl) |
| **FastAPI Docs** | `http://localhost:8000/docs` | Swagger / Documentation interactive de l'API |

---

##  ʕ•ᴥ•ʔっ · · · ✴ Intégration et Déploiement Continus (CI/CD)

Le projet applique une discipline logicielle stricte via **GitHub Actions** :

* **CI (Continuous Integration)** : À chaque `push`, le code est audité contre les fuites de secrets (Gitleaks) et soumis à une analyse statique intransigeante (Linting PEP 8) par **Ruff**. Le pipeline échoue si le code n'est pas clinique.
* **CD (Continuous Deployment)** : Une fois la CI validée, l'usine compile automatiquement :
  1. Les **Images Docker** (API & Front) poussées sur le *GitHub Container Registry* (GHCR).
  2. La **Documentation Technique** (Sphinx/Diátaxis) déployée dynamiquement sur GitHub Pages.

**[Consulter la Documentation Officielle Complète](https://annavitry.github.io/MLOPS_MLFactory_automatisation/)**

---

##  ʕ•ᴥ•ʔっ · · · ✴ Maintenance & Dépannage Radical (Troubleshooting)

L'architecture Docker peut parfois s'emmêler les pinceaux avec le cache ou les volumes (ex: conflits de mots de passe de base de données). Si l'environnement devient instable, applique la politique de la terre brûlée :

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
> Le `down -v` ou le `volume prune` détruisent l'historique de MLflow, la base de données Prefect et les fichiers S3 dans MinIO. C'est une remise à zéro complète de l'usine.

* **Erreur "404 Client Error: Not Found... fromImage=mlfactory-worker" :** Ton Worker Prefect tente de télécharger l'image depuis Internet au lieu de l'ordinateur local. Assure-toi d'avoir bien mis `image_pull_policy: "Never"` dans ton `prefect.yaml` au niveau de `job_variables`, et relance la commande `prefect deploy`.