# Configuration file for the Sphinx documentation builder.
import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

# -- Project information -----------------------------------------------------
project = "ML Factory"
copyright = "2026, AnnaVitry"
author = "AnnaVitry"
release = "1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",  # Génère la doc à partir du code (lit les docstrings)
    "sphinx.ext.napoleon",  # Supporte les docstrings style Google/NumPy (plus lisibles)
    "sphinx.ext.viewcode",  # Ajoute un bouton "[source]" pour voir le code Python depuis la doc web
    "sphinx.ext.duration",  # Mesure et affiche le temps de compilation (utile pour optimiser la CI/CD)
    "sphinx.ext.doctest",  # Exécute les exemples de code dans la doc pour vérifier qu'ils ne sont pas obsolètes
    "sphinx.ext.mathjax",  # Rend les formules mathématiques (LaTeX) lisibles (très utile en Machine Learning)
    "myst_parser",  # Permet d'écrire des pages de doc en Markdown (.md) en plus du .rst classique
    # "sphinxcontrib.bibtex", # (Désactivé) Servirait à gérer une bibliographie pour citer des papiers de recherche
]

autodoc_mock_imports = [
    "fastapi",
    "pydantic",
    "mlflow",
    "sklearn",
    "streamlit",
    "boto3",
    "requests",
    "dotenv",
    "prefect",
]

templates_path = ["_templates"]
exclude_patterns = []
language = "fr"

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_logo = "_static/img/favicon.svg"  # Affiche ton logo en haut de la barre de navigation gauche
html_favicon = (
    "_static/img/favicon.svg"  # Affiche l'icône dans l'onglet du navigateur web
)
html_title = "ML Factory"  # Personnalise le titre de la page web (balise <title>)
