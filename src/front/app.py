"""Interface utilisateur Streamlit pour l'usine MLOps Iris."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv
from requests.exceptions import RequestException

load_dotenv()

# L'URL de l'API est récupérée depuis l'environnement, sinon on pointe sur le localhost Docker
API_URL = os.getenv("API_URL", "http://localhost:8000/predict")


def get_prediction(data: dict) -> dict | None:
    """
    Gère la communication HTTP entre l'interface Streamlit et l'API FastAPI.

    Args:
        data (dict): Un dictionnaire contenant les dimensions capturées via le formulaire UI.
            Doit correspondre strictement au schéma Pydantic `IrisData` de l'API.

    Returns:
        dict | None: Le dictionnaire JSON renvoyé par l'API si le code HTTP est 200.
            Retourne `None` si une exception réseau se produit (timeout, connection refused).

    Example:
        .. code-block:: python

            payload = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
            result = get_prediction(payload)
            if result:
                print(result["model_version"])
    """
    try:
        # Un timeout est crucial en production pour ne pas bloquer l'interface
        response = requests.post(API_URL, json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"⚠️ Erreur de communication avec l'API : {e}")
        return None


def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""
    st.set_page_config(page_title="Iris ML Factory", page_icon="🌸")
    st.title("🌸 Prédiction d'Iris - ML Factory")
    st.write("Entrez les dimensions de la fleur pour deviner son espèce.")

    # Création d'un formulaire pour éviter de recharger la page à chaque chiffre tapé
    with st.form("iris_form"):
        col1, col2 = st.columns(2)

        with col1:
            sepal_length = st.number_input(
                "Longueur du sépale", min_value=0.0, value=5.1
            )
            sepal_width = st.number_input("Largeur du sépale", min_value=0.0, value=3.5)

        with col2:
            petal_length = st.number_input(
                "Longueur du pétale", min_value=0.0, value=1.4
            )
            petal_width = st.number_input("Largeur du pétale", min_value=0.0, value=0.2)

        submit = st.form_submit_button("🚀 Lancer la prédiction")

    if submit:
        payload = {
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width,
        }

        with st.spinner("Interrogation du Model Registry..."):
            result = get_prediction(payload)

        if result:
            version = result.get("model_version", "Inconnue")
            prediction_idx = result.get("prediction", 0)

            target_names = ["Setosa", "Versicolor", "Virginica"]
            flower_name = target_names[prediction_idx]

            st.success(f"### Résultat : {flower_name}")
            st.caption(
                f"ID Classe : {prediction_idx} | Source : MLflow Registry v{version}"
            )


# Exécution standard en Python
if __name__ == "__main__":
    main()
