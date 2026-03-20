# 🌸 MLOps Factory - Iris Dataset

[![CI Pipeline](https://github.com/AnnaVitry/MLOPS_MLFactory/actions/workflows/ci.yml/badge.svg)](https://github.com/AnnaVitry/MLOPS_MLFactory/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/AnnaVitry/MLOPS_MLFactory/actions/workflows/cd.yml/badge.svg)](https://github.com/AnnaVitry/MLOPS_MLFactory/actions/workflows/cd.yml)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![License](https://img.shields.io/badge/license-MIT-green.svg)

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat&logo=mlflow&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C7202C?style=flat&logo=minio&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)

---

##  ʕ•ᴥ•ʔっ · · · ✴ Vision et Architecture

L'**Iris ML Factory** n'est pas un simple script d'apprentissage automatique. C'est une usine logicielle complète conçue pour démontrer les standards du **MLOps**. Le projet sépare strictement l'entraînement, le stockage et l'inférence via une architecture de microservices conteneurisés.

```bash
MLOPS_MLFACTORY/
├── data/                   # Données générées pour les tests (partagé via volume Docker)
│   └── iris_test.csv       # Fichier CSV utilisé par le Front-end
├── src/
│   ├── api/                # Backend FastAPI
│   │   ├── main.py         # Logique de rechargement à chaud et inférence
│   │   └── Dockerfile      # Image pour l'API
│   ├── front/              # Interface Streamlit
│   │   ├── app.py          # Visualisation et interaction utilisateur
│   │   └── Dockerfile      # Image pour le Front-end
│   └── train/              # Pipeline d'entraînement
│       └── train.py        # Entraînement, log MLflow et gestion des alias
├── .env                    # Variables d'environnement (Secrets et URLs)
├── docker-compose.yml      # Orchestration des services (MinIO, MLflow, API, Front)
├── generate_data.py        # Script de création du dataset de test
└── pyproject.toml          # Gestion des dépendances avec uv
```

---

### Composants de l'Usine
1. **L'Entrepôt de Données et Modèles** : **MinIO** (compatible S3) agit comme un Data/Model Lake pour stocker les binaires générés (`.pkl`).
2. **Le Centre de Contrôle** : **MLflow** trace les expériences, enregistre les métriques et gère le cycle de vie (via les Alias comme `production`).
3. **Le Moteur d'Inférence** : Une API REST robuste développée avec **FastAPI**, dotée d'un système de *Hot-Reloading* pour interroger dynamiquement le Model Registry sans redémarrer le serveur.
4. **Le Tableau de Bord** : Une interface utilisateur interactive sous **Streamlit** pour soumettre des données et visualiser les prédictions en temps réel.

##  ʕ•ᴥ•ʔっ · · · ✴ Démarrage Rapide (Développement Local) et Commandes de Pilotage

L'intégralité de l'infrastructure est orchestrée par Docker Compose pour garantir la reproductibilité.

### 1. Cloner le dépôt
```bash
git clone [https://github.com/AnnaVitry/MLOPS_MLFactory.git](https://github.com/AnnaVitry/MLOPS_MLFactory.git)
cd MLOPS_MLFactory
```
### 2. Démarrage de l'infrastructure
Pour lancer tous les services (MinIO, MLflow, API, Front) :
```bash
docker compose up -d --build
```

### 3. Gestion des données
Pour générer un fichier `iris_test.csv` avec un échantillonnage aléatoire :
```bash
uv run generate_data.py
```

### 4. Cycle d'entraînement (CI/CD ML)
Chaque exécution crée une nouvelle version du modèle dans MLflow :
```bash
uv run src/train/train.py
```

### 5. Maintenance et Nettoyage Radical
En cas de problème de daemon ou pour tout remettre à zéro :
```bash
docker compose down -v  # Supprime tout, y compris les volumes (données MinIO)
docker ps               # Vérifie que les 4 conteneurs sont "Up"
```
 
Si ton environnement Docker devient instable ou si tu manques d'espace disque, utilise ces commandes. 

> [!WARNING]
> **Attention :** Le nettoyage des volumes supprimera toutes les données persistantes (historique MLflow et fichiers dans MinIO) qui ne sont pas activement liées à un conteneur en cours d'exécution.  
```bash
systemctl --user restart docker-desktop # Relance le moteur Docker Desktop (Utile en cas d'erreur "docker.sock")
docker builder prune -a --force # Supprime l'intégralité du cache de build (Force une reconstruction "neuve" des images)
docker image prune -a -f # Supprime toutes les images non utilisées (Nettoyage massif du stockage)
docker volume prune -f # Supprime les volumes orphelins (Efface les données MinIO/MLflow non actives) 
docker container prune -f # Supprime tous les conteneurs arrêtés
```

---

##  ʕ•ᴥ•ʔっ · · · ✴ Accès aux Services

| Service | URL | Usage |
| :--- | :--- | :--- |
| **Streamlit UI (Front-end)** | `http://localhost:8501` | Interface utilisateur finale |
| **MLflow UI** | `http://localhost:5000` | Suivi des runs et registre de modèles |
| **MinIO Console** | `http://localhost:9001` | Exploration des fichiers (Artefacts) |
| **FastAPI Docs** | `http://localhost:8000/docs` | Documentation interactive de l'API |

---

##  ʕ•ᴥ•ʔっ · · · ✴ Intégration et Déploiement Continus (CI/CD)

Le projet applique une discipline logicielle stricte via **GitHub Actions** :

* **CI (Continuous Integration)** : À chaque `push`, le code est audité contre les fuites de secrets (Gitleaks) et soumis à une analyse statique intransigeante (Linting PEP 8) par **Ruff**. Le pipeline échoue si le code n'est pas clinique.
* **CD (Continuous Deployment)** : Une fois la CI validée, l'usine compile automatiquement :
  1. Les **Images Docker** (API & Front) qui sont poussées sur le *GitHub Container Registry* (GHCR).
  2. La **Documentation Technique** (Sphinx/Diátaxis) qui est déployée dynamiquement sur GitHub Pages.

**[Consulter la Documentation Officielle Complète](https://annavitry.github.io/MLOPS_MLFactory/)**

---

##  ʕ•ᴥ•ʔっ · · · ✴ Fonctionnement du Rechargement à Chaud (Hot Reload)

L'API (`src/api/main.py`) utilise un mécanisme de cache intelligent pour éviter les redémarrages manuels :

1. **Vérification de l'Alias** : À chaque requête de prédiction, l'API demande à MLflow : *"Quelle version porte l'alias 'production' ?"*.
2. **Comparaison de Version** : 
   - Si `prod_version == state["version"]`, l'API utilise le modèle déjà en mémoire (ultra-rapide).
   - Si `prod_version != state["version"]`, l'API télécharge automatiquement le nouveau fichier `.pkl` depuis MinIO.
3. **Mise à jour Front** : L'interface Streamlit récupère la clé `model_version` renvoyée par l'API et met à jour l'affichage instantanément.

---

##  ʕ•ᴥ•ʔっ · · · ✴ Troubleshooting (Dépannage)

* **Erreur Connection Refused (9000)** :
  - Le conteneur MinIO n'est pas prêt. Attends 10 secondes ou vérifie `docker ps`.
* **Les changements de code ne s'affichent pas** :
  - Si tu n'utilises pas les volumes dans Docker Compose, tu dois reconstruire l'image : `docker compose up -d --build front`.

---

<!-- 

### Comment changer de modèle ?
Ouvre `src/train/train.py` et localise le bloc de sélection du modèle :

#### **Option A : Régression Logistique (Modèle Linéaire)**
```python
# Décommentez ces lignes :
model = LogisticRegression(max_iter=200)
model_type = "LogisticRegression"

# Commentez ces lignes :
# model = RandomForestClassifier(n_estimators=200, random_state=42)
# model_type = "RandomForest"
```

#### **Option B : Random Forest (Modèle d'Ensemble)**
```python
# Commentez ces lignes :
# model = LogisticRegression(max_iter=200)
# model_type = "LogisticRegression"

# Décommentez ces lignes :
model = RandomForestClassifier(n_estimators=100, random_state=42)
model_type = "RandomForest"
```
et décommenter toutes les lignes qui ont le commentaire "*# Décommenter pour RandomForest*". ***𝑶𝒃-𝒗𝒊𝒐𝒖𝒔-𝒍𝒚.*** ⟶\**deadass, with a Severus Snape voice*\*

>**Note sur la traçabilité :** Pense à modifier `n_estimators` pour créer des versions (V1, V2, V3) et observer le changement dynamique sur l'interface. -->
