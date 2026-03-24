# Guide de Démarrage Rapide

Ce guide explique comment allumer l'usine logicielle en local et utiliser l'orchestrateur Prefect pour piloter les entraînements.

## 1. Démarrage de l'Infrastructure Persistante
L'ensemble des services de base (Bases de données, Serveurs, API, Front) est orchestré par Docker Compose.

```bash
docker compose up -d --build
```
*(Attendez une quinzaine de secondes pour que la base de données de Prefect s'initialise correctement).*

## 2. Démarrage de l'Automatisation (Prefect Worker)
L'entraînement n'est plus manuel. Il est confié à un **Ouvrier Docker (Worker)** qui exécutera le code dans des conteneurs éphémères.

A. Mettez à jour le serveur avec les instructions de déploiement :
```bash
uv run prefect deploy -n production-training-job
```

B. Allumez le Worker (Laissez ce terminal ouvert) :
```bash
uv run prefect worker start --pool 'docker-pool'
```

## 3. Entraînement d'un modèle et Hot-Reloading
Pour générer une nouvelle version du modèle et tester le changement en direct :

1. Ouvrez l'interface Prefect : **[http://localhost:4200](http://localhost:4200)**
2. Allez dans **Deployments** -> `production-training-job`.
3. Cliquez sur la flèche à côté de **Run** -> **Custom Run**.
4. Changez le paramètre `champion_model` (ex: passez de `logistic_regression` à `random_forest`) et validez.
5. Allez sur votre application Streamlit **[http://localhost:8501](http://localhost:8501)** et lancez une prédiction. L'API téléchargera la nouvelle version automatiquement !

*(Note : Pour des tests de développement purs sans Docker, vous pouvez toujours utiliser `uv run src/train/train.py` en local).*