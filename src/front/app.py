"""Module de l'interface utilisateur Streamlit.

Ce module fournit une interface web interactive pour l'usine MLOps.
Il permet à l'utilisateur de saisir les caractéristiques d'une fleur d'Iris,
d'envoyer une requête asynchrone à l'API via RabbitMQ, et de suivre
l'état de plusieurs tâches simultanément.
"""

import os
import time

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000")


def init_session_state() -> None:
    """Initialise la mémoire de session Streamlit."""
    if "history" not in st.session_state:
        st.session_state.history = []
    # NOUVEAU : Une liste pour stocker les tickets en cours de calcul
    if "pending" not in st.session_state:
        st.session_state.pending = []


def render_sidebar() -> dict[str, float]:
    """Affiche la barre latérale et récupère les paramètres de l'utilisateur."""
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
    st.subheader("📚 Historique des prédictions")

    if not st.session_state.history:
        st.caption("Vos résultats s'afficheront ici au fur et à mesure.")
    else:
        for item in reversed(st.session_state.history):
            with st.container(border=True):
                cols = st.columns([1, 3])
                cols[0].metric(
                    label=f"Ticket #{item['id']}",
                    value=f"Classe {item['classe']}",
                )
                cols[1].write(
                    f"**Résultat :** {item.get('nom', 'Inconnu')} (ID: {item['classe']}) | "
                    f"**Mesures :** {item['params']['sepal_length']}L / {item['params']['sepal_width']}l (Sépale) | "
                    f"{item['params']['petal_length']}L / {item['params']['petal_width']}l (Pétale)"
                )


def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""
    st.set_page_config(page_title="Iris ML Factory", page_icon="🌸")
    init_session_state()

    st.title("🌸 Iris ML Factory (100% Asynchrone)")
    st.markdown("Spammez le bouton ! RabbitMQ gère la file d'attente.")

    payload = render_sidebar()

    # 1. ACTION : ENVOI DE LA COMMANDE (Instantané)
    if st.button("🚀 Lancer la prédiction"):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload)
            response.raise_for_status()
            task_id = response.json().get("task_id")

            # On range le ticket dans la salle d'attente et on libère l'interface
            st.session_state.pending.append({"id": task_id, "params": payload})
        except Exception as e:
            st.error(f"⚠️ Erreur d'envoi : {str(e)}")

    # 2. ÉCOUTE : VÉRIFICATION DE LA SALLE D'ATTENTE
    if st.session_state.pending:
        st.markdown("### ⏳ Tâches en cours...")

        # On lit une copie de la liste [:] pour pouvoir la modifier en direct
        for task in st.session_state.pending[:]:
            task_id = task["id"]
            try:
                res = requests.get(f"{API_URL}/predict/status/{task_id}")
                res_data = res.json()
                etat = res_data.get("status")

                if etat == "terminé":
                    # Déplacement vers l'historique
                    st.session_state.history.append(
                        {
                            "id": task_id[:8],
                            "params": task["params"],
                            "classe": res_data.get("prediction"),
                            "nom": res_data.get("flower_name"),
                        }
                    )
                    st.session_state.pending.remove(task)

                elif etat == "erreur":
                    st.error(
                        f"❌ Échec du ticket #{task_id[:8]} : {res_data.get('error')}"
                    )
                    st.session_state.pending.remove(task)

                else:
                    st.info(f"🔄 Ticket #{task_id[:8]} est dans la machine...")

            except Exception:
                pass  # On ignore les erreurs de réseau temporaires

        # Si la salle d'attente n'est pas vide, on force Streamlit à relancer
        # le script dans 1 seconde pour mettre à jour l'affichage
        if st.session_state.pending:
            time.sleep(1)
            st.rerun()

    display_history()


if __name__ == "__main__":
    main()
