"""
gradio_demo/app.py
"""
import sys
import os

# Ajoute la racine du projet au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gradio as gr
from sqlalchemy.orm import Session

# ── Imports directs depuis l'app ──────────────────────────────
from app.database import SessionLocal
from app.auth import authenticate_user
from app.predict import (
    get_employee_dataframe,
    encode_employee_data,
    predict_employees,
    log_predictions,
)

# ══════════════════════════════════════════════════════════════
# HELPERS — session DB
# ══════════════════════════════════════════════════════════════

def get_db_session() -> Session:
    """Retourne une session DB à fermer manuellement."""
    return SessionLocal()


# ══════════════════════════════════════════════════════════════
# LOGIQUE MÉTIER — fonctions appelées par Gradio
# ══════════════════════════════════════════════════════════════

def login(username: str, password: str):
    """
    Authentifie l'utilisateur directement via la DB.
    Retourne (message_ui, username_state)
    """
    if not username or not password:
        return "⚠️ Remplis les deux champs.", None

    db = get_db_session()
    try:
        user = authenticate_user(db, username, password)
        if user:
            return f"✅ Connecté en tant que **{username}**", username
        else:
            return "❌ Identifiants incorrects.", None
    finally:
        db.close()


def predict_filter(
    poste: str,
    heure_sup: str,
    nb_exp: int,
    annee_exp: int,
    username_state: str,
):
    """Prédiction par filtre — appel direct aux fonctions predict."""
    if not username_state:
        return "🔒 Connecte-toi d'abord.", None

    # Construire les filtres (ignorer les valeurs vides)
    filters = {}
    if poste and poste != "Tous":
        filters["poste"] = poste
    if heure_sup and heure_sup != "Tous":
        filters["heure_supplementaires"] = heure_sup
    if nb_exp is not None and nb_exp > 0:
        filters["nombre_experiences_precedentes"] = nb_exp
    if annee_exp is not None and annee_exp < 31:
        filters["annee_experience_totale"] = annee_exp

    if not filters:
        return "⚠️ Sélectionne au moins un filtre.", None

    db = get_db_session()
    try:
        df = get_employee_dataframe(db, filters=filters)

        if df.empty:
            return f"ℹ️ Aucun employé trouvé avec : {filters}", None

        df_encoded = encode_employee_data(df)
        results = predict_employees(df_encoded)

        filter_str = ", ".join(f"{k}={v}" for k, v in filters.items())
        log_predictions(db, results, filter_used=filter_str)

        total = len(results)
        at_risk = len(results[results["prediction"] == "Part"])
        rate = round(at_risk / total * 100, 1)

        summary = f"👥 {total} employés | ⚠️ {at_risk} à risque ({rate}%)"
        return summary, results[["employee_id", "prediction", "probability"]].to_dict("records")

    except Exception as e:
        return f"❌ Erreur : {str(e)}", None
    finally:
        db.close()


def predict_employee(employee_id_str: str, username_state: str):
    """Prédiction pour un employé individuel."""
    if not username_state:
        return "🔒 Connecte-toi d'abord."

    try:
        employee_id = int(employee_id_str)
    except (ValueError, TypeError):
        return "⚠️ L'ID doit être un entier."

    db = get_db_session()
    try:
        df = get_employee_dataframe(db, employee_id=employee_id)

        if df.empty:
            return f"ℹ️ Employé {employee_id} non trouvé."

        df_encoded = encode_employee_data(df)
        results = predict_employees(df_encoded)
        log_predictions(db, results, filter_used=f"employee_id={employee_id}")

        row = results.iloc[0]
        pred = row["prediction"]
        prob = round(row["probability"] * 100, 1)
        emoji = "🔴" if pred == "Part" else "🟢"

        return f"{emoji} Employé {employee_id} — Prédiction : **{pred}** ({prob}%)"

    except Exception as e:
        return f"❌ Erreur : {str(e)}"
    finally:
        db.close()


def get_history(limit_str: str, username_state: str):
    """Récupère l'historique des prédictions."""
    if not username_state:
        return "🔒 Connecte-toi d'abord.", None

    try:
        limit = int(limit_str)
    except (ValueError, TypeError):
        limit = 10

    db = get_db_session()
    try:
        from sqlalchemy import text
        result = db.execute(
            text("SELECT * FROM predictions ORDER BY created_at DESC LIMIT :limit"),
            {"limit": limit}
        )
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

        if not rows:
            return "ℹ️ Aucune prédiction enregistrée.", None

        return f"📋 {len(rows)} prédiction(s)", rows

    except Exception as e:
        return f"❌ Erreur : {str(e)}", None
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════
# INTERFACE GRADIO
# ══════════════════════════════════════════════════════════════

with gr.Blocks(title="Futurisys — Prédiction Attrition") as demo:

    # ── State — stocke le username après login ──
    username_state = gr.State(value=None)

    gr.Markdown("# 🏢 Futurisys — Prédiction Attrition")
    gr.Markdown("Démo du modèle Random Forest de prédiction de départ d'employés.")

    # ── Onglet Login ──────────────────────────────────────────
    with gr.Tab("🔐 Connexion"):
        with gr.Row():
            username_input = gr.Textbox(label="Nom d'utilisateur")
            password_input = gr.Textbox(label="Mot de passe", type="password")
        login_btn = gr.Button("Se connecter")
        login_msg = gr.Markdown()

        login_btn.click(
            fn=login,
            inputs=[username_input, password_input],
            outputs=[login_msg, username_state],
        )

    # ── Onglet Filtre ─────────────────────────────────────────
    with gr.Tab("🔍 Prédiction par filtre"):
        with gr.Row():
            poste_dd = gr.Dropdown(
                label="Poste",
                choices=["Tous", "Consultant", "Manager", "Développeur", "Commercial"],
                value="Tous",
            )
            nb_exp_slider = gr.Slider(
                label="Nb expériences précédentes — min",
                minimum=0, maximum=9, value=0, step=1,
            )
            annee_exp_slider = gr.Slider(
                label="Années d'expérience totale — max",
                minimum=1, maximum=31, value=31, step=1,
            )
            heure_dd = gr.Dropdown(
                label="Heures supplémentaires",
                choices=["Tous", "Oui", "Non"],
                value="Tous",
            )

        filter_btn = gr.Button("Lancer la prédiction")
        filter_summary = gr.Markdown()
        filter_table = gr.JSON(label="Résultats détaillés")

        filter_btn.click(
            fn=predict_filter,
            inputs=[poste_dd, heure_dd, nb_exp_slider, annee_exp_slider, username_state],
            outputs=[filter_summary, filter_table],
        )

    # ── Onglet Employé ────────────────────────────────────────
    with gr.Tab("👤 Prédiction par employé"):
        emp_id_input = gr.Textbox(label="ID Employé", placeholder="Ex: 42")
        emp_btn = gr.Button("Prédire")
        emp_result = gr.Markdown()

        emp_btn.click(
            fn=predict_employee,
            inputs=[emp_id_input, username_state],
            outputs=[emp_result],
        )

    # ── Onglet Historique ─────────────────────────────────────
    with gr.Tab("📋 Historique"):
        limit_input = gr.Textbox(label="Nombre de résultats", value="10")
        history_btn = gr.Button("Charger l'historique")
        history_summary = gr.Markdown()
        history_table = gr.JSON(label="Historique")

        history_btn.click(
            fn=get_history,
            inputs=[limit_input, username_state],
            outputs=[history_summary, history_table],
        )


if __name__ == "__main__":
    demo.launch()