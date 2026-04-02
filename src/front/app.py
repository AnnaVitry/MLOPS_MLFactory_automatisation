"""Module de l'interface utilisateur Streamlit.

Ce module fournit une interface web interactive pour l'usine MLOps.
Il permet à l'utilisateur de saisir les caractéristiques d'une fleur d'Iris,
d'envoyer une requête asynchrone à l'API via RabbitMQ, et de suivre
l'état de la tâche jusqu'à l'obtention de la prédiction finale.
"""

import os
import time

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000")


def init_session_state() -> None:
    """Initialise la mémoire de session Streamlit pour l'historique."""
    if "history" not in st.session_state:
        st.session_state.history = []


def render_sidebar() -> dict[str, float]:
    """Affiche la barre latérale et récupère les paramètres de l'utilisateur.

    Returns:
        dict[str, float]: Un dictionnaire contenant les 4 dimensions de la fleur.
    """
    st.sidebar.header("Paramètres de la fleur")
    return {
        "sepal_length": st.sidebar.slider("Longueur du sépale", 4.0, 8.0, 5.1),
        "sepal_width": st.sidebar.slider("Largeur du sépale", 2.0, 4.5, 3.5),
        "petal_length": st.sidebar.slider("Longueur du pétale", 1.0, 7.0, 1.4),
        "petal_width": st.sidebar.slider("Largeur du pétale", 0.1, 2.5, 0.2),
    }


def display_history() -> None:
    """Affiche l'historique des prédictions stocké dans la session."""
    st.markdown("---")
    st.subheader("📚 Historique de la session")

    if not st.session_state.history:
        st.caption("Vos résultats s'afficheront ici au fur et à mesure.")
    else:
        # On lit la liste à l'envers pour afficher le plus récent en haut
        for item in reversed(st.session_state.history):
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].metric(
                    label=f"Ticket #{item['id']}", value=f"Classe {item['classe']}"
                )
                cols[1].write(
                    f"**Mesures :** {item['params']['sepal_length']}L / {item['params']['sepal_width']}l (Sépale) | "
                    f"{item['params']['petal_length']}L / {item['params']['petal_width']}l (Pétale)"
                )


def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""
    st.set_page_config(page_title="Iris ML Factory", page_icon="🌸")
    init_session_state()

    st.title("🌸 Iris ML Factory (Asynchrone)")
    st.markdown(
        "Cette interface ne calcule rien. Elle délègue le travail à une file "
        "d'attente (RabbitMQ) gérée par des workers (Celery)."
    )

    payload = render_sidebar()

    if st.button("🚀 Lancer la prédiction (Worker)"):
        try:
            with st.spinner("Transmission de la commande à l'API..."):
                response = requests.post(f"{API_URL}/predict", json=payload)
                response.raise_for_status()
                task_id = response.json().get("task_id")

            st.info(f"✅ Commande enregistrée dans RabbitMQ ! Ticket n° : `{task_id}`")

            with st.status(
                "Le Worker Celery traite la demande...", expanded=True
            ) as status:
                while True:
                    res = requests.get(f"{API_URL}/predict/status/{task_id}")
                    res_data = res.json()
                    etat = res_data.get("status")

                    if etat == "terminé":
                        prediction = res_data.get("prediction")
                        status.update(
                            label="Prédiction terminée !",
                            state="complete",
                            expanded=False,
                        )
                        st.session_state.history.append(
                            {
                                "id": task_id[:8],
                                "params": payload,
                                "classe": prediction,
                            }
                        )
                        break

                    elif etat == "erreur":
                        status.update(
                            label="Échec de la tâche", state="error", expanded=False
                        )
                        st.error(
                            f"Le Worker a rencontré un problème : {res_data.get('error')}"
                        )
                        break

                    else:
                        time.sleep(1)

        except Exception as e:
            st.error(f"⚠️ Erreur de communication avec l'API : {str(e)}")

    display_history()


if __name__ == "__main__":
    main()
