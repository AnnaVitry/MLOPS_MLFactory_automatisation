# Guide de Démarrage Rapide

Ce guide explique comment lancer l'usine en local pour le développement.

## 1. Démarrage de l'infrastructure
L'ensemble des services est orchestré par Docker Compose.
```bash
docker compose up -d --build
```

## 2. Entraînement d'un modèle
Pour générer une nouvelle version du modèle et l'envoyer dans MLflow :
```bash
uv run src/train/train.py
```
> Note : Modifiez les hyperparamètres dans le script pour observer la création d'une nouvelle version.