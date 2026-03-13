"""
gradio_demo/app.py
Démo Gradio — API Futurisys Prédiction Attrition

Lance l'API FastAPI en parallèle avant de démarrer ce script :
    uvicorn app.main:app --reload

Puis lance le démo :
    python gradio_demo/app.py
"""

import gradio as gr
import requests
import os

# ─── Configuration ───────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://127.0.0.1:7860")

# Valeurs possibles en base (issues des CSV SIRH)
POSTES = [
    "", "Consultant", "Représentant Commercial", "Ressources Humaines",
    "Cadre Commercial", "Assistant de Direction", "Tech Lead",
    "Manager", "Senior Manager", "Directeur Technique",
]
DEPARTEMENTS = ["", "Commercial", "Consulting", "RH", "IT", "Direction"]
HEURES_SUP   = ["", "Oui", "Non"]

RISK_EMOJI = {
    "Faible":   "🟢 Faible",
    "Modéré":   "🟡 Modéré",
    "Élevé":    "🔴 Élevé",
    "Critique": "🚨 Critique",
}


# ══════════════════════════════════════════════════════════════
# FONCTIONS APPELÉES PAR L'INTERFACE
# ══════════════════════════════════════════════════════════════

def login(username: str, password: str):
    """
    POST /token → récupère le JWT.
    Retourne (message_statut, token_ou_vide).
    """
    if not username or not password:
        return "⚠️ Identifiants manquants.", ""

    try:
        resp = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            timeout=5,
        )
    except requests.exceptions.ConnectionError:
        return "❌ API non joignable. Lance `uvicorn app.main:app --reload`.", ""

    if resp.status_code == 200:
        token = resp.json()["access_token"]
        return f"✅ Connecté en tant que **{username}**.", token
    else:
        return "❌ Identifiants incorrects.", ""


def predict_filter(token: str, poste: str, departement: str, heure_sup: str):
    """
    GET /predict/filter → prédictions groupées.
    """
    if not token:
        return "⚠️ Connecte-toi d'abord.", None

    params = {}
    if poste:        params["poste"]       = poste
    if departement:  params["departement"] = departement
    if heure_sup:    params["heure_sup"]   = heure_sup

    if not params:
        return "⚠️ Sélectionne au moins un filtre.", None

    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(
            f"{API_URL}/predict/filter",
            params=params,
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return "❌ API non joignable.", None

    if resp.status_code == 404:
        return "ℹ️ Aucun employé trouvé avec ces filtres.", None
    if resp.status_code != 200:
        return f"❌ Erreur API ({resp.status_code}).", None

    data = resp.json()

    # ─── Résumé ───
    summary = (
        f"### 📊 Résultats — {data['filter_used']}\n\n"
        f"- **Employés analysés :** {data['total_employees']}\n"
        f"- **À risque de départ :** {data['total_at_risk']}\n"
        f"- **Taux de risque :** {data['risk_rate']} %\n"
    )

    # ─── Tableau ───
    rows = []
    for p in data["predictions"]:
        rows.append([
            p["employee_id"],
            p["prediction"],
            f"{p['probability'] * 100:.1f} %",
            RISK_EMOJI.get(p["risk_level"], p["risk_level"]),
        ])

    return summary, rows


def predict_employee(token: str, employee_id: int):
    """
    GET /predict/employee/{id} → prédiction individuelle.
    """
    if not token:
        return "⚠️ Connecte-toi d'abord."
    if not employee_id:
        return "⚠️ Saisis un ID employé."

    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(
            f"{API_URL}/predict/employee/{int(employee_id)}",
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return "❌ API non joignable."

    if resp.status_code == 404:
        return f"ℹ️ Employé #{int(employee_id)} introuvable en base."
    if resp.status_code != 200:
        return f"❌ Erreur API ({resp.status_code})."

    p = resp.json()
    risk = RISK_EMOJI.get(p["risk_level"], p["risk_level"])

    return (
        f"## Employé #{p['employee_id']}\n\n"
        f"| Champ | Valeur |\n"
        f"|---|---|\n"
        f"| **Prédiction** | {p['prediction']} |\n"
        f"| **Probabilité de départ** | {p['probability'] * 100:.1f} % |\n"
        f"| **Niveau de risque** | {risk} |\n"
    )


def get_history(token: str, limit: int, employee_id_filter):
    """
    GET /predictions/history → historique paginé.
    """
    if not token:
        return "⚠️ Connecte-toi d'abord.", None

    params = {"limit": int(limit)}
    if employee_id_filter:
        params["employee_id"] = int(employee_id_filter)

    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(
            f"{API_URL}/predictions/history",
            params=params,
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return "❌ API non joignable.", None

    if resp.status_code != 200:
        return f"❌ Erreur API ({resp.status_code}).", None

    data = resp.json()

    if data["total_predictions"] == 0:
        return "ℹ️ Aucune prédiction enregistrée.", None

    summary = f"### 📋 Historique — {data['total_predictions']} prédiction(s)"

    rows = []
    for p in data["predictions"]:
        rows.append([
            p["id"],
            p["employee_id"],
            p["prediction"],
            f"{p['probability'] * 100:.1f} %",
            RISK_EMOJI.get(p["risk_level"], p["risk_level"]),
            p.get("filter_used") or "—",
            p["created_at"][:19].replace("T", " "),  # format lisible
        ])

    return summary, rows


# ══════════════════════════════════════════════════════════════
# INTERFACE GRADIO
# ══════════════════════════════════════════════════════════════

with gr.Blocks(title="Futurisys — Prédiction Attrition", theme=gr.themes.Soft()) as demo:

    # ─── En-tête ───
    gr.Markdown(
        """
        # 🏢 Futurisys — Prédiction d'Attrition RH
        **API de prédiction du risque de départ des employés**
        *Connecte-toi pour accéder aux fonctionnalités.*
        """
    )

    # ─── Token stocké en mémoire (invisible) ───
    token_state = gr.State("")

    # ─── Section Login ───
    with gr.Group():
        gr.Markdown("### 🔐 Connexion")
        with gr.Row():
            inp_username = gr.Textbox(label="Nom d'utilisateur", placeholder="admin")
            inp_password = gr.Textbox(label="Mot de passe", type="password", placeholder="••••••")
            btn_login    = gr.Button("Se connecter", variant="primary")
        out_login_status = gr.Markdown()

    btn_login.click(
        fn=login,
        inputs=[inp_username, inp_password],
        outputs=[out_login_status, token_state],
    )

    gr.Markdown("---")

    # ─── Onglets ───
    with gr.Tabs():

        # ══ Onglet 1 : Prédiction par filtre ══
        with gr.Tab("🔍 Prédiction par filtre"):
            gr.Markdown(
                "Sélectionne un ou plusieurs filtres pour analyser un groupe d'employés."
            )
            with gr.Row():
                dd_poste       = gr.Dropdown(choices=POSTES,       label="Poste",              value="")
                dd_departement = gr.Dropdown(choices=DEPARTEMENTS, label="Département",        value="")
                dd_heure_sup   = gr.Dropdown(choices=HEURES_SUP,   label="Heures supplémentaires", value="")

            btn_filter = gr.Button("🚀 Lancer la prédiction", variant="primary")

            out_filter_summary = gr.Markdown()
            out_filter_table   = gr.Dataframe(
                headers=["ID", "Prédiction", "Probabilité", "Risque"],
                label="Résultats",
                interactive=False,
            )

            btn_filter.click(
                fn=predict_filter,
                inputs=[token_state, dd_poste, dd_departement, dd_heure_sup],
                outputs=[out_filter_summary, out_filter_table],
            )

        # ══ Onglet 2 : Prédiction par employé ══
        with gr.Tab("👤 Prédiction par employé"):
            gr.Markdown("Saisis l'identifiant d'un employé pour obtenir sa prédiction individuelle.")
            with gr.Row():
                inp_employee_id = gr.Number(label="ID Employé", precision=0, minimum=1)
                btn_employee    = gr.Button("🔎 Prédire", variant="primary")

            out_employee_result = gr.Markdown()

            btn_employee.click(
                fn=predict_employee,
                inputs=[token_state, inp_employee_id],
                outputs=[out_employee_result],
            )

        # ══ Onglet 3 : Historique ══
        with gr.Tab("📋 Historique des prédictions"):
            gr.Markdown("Consulte les prédictions enregistrées en base.")
            with gr.Row():
                inp_limit      = gr.Slider(minimum=5, maximum=100, value=20, step=5, label="Nombre de résultats")
                inp_hist_empid = gr.Number(label="Filtrer par ID employé (optionnel)", precision=0, minimum=1, value=None)
                btn_history    = gr.Button("📥 Charger l'historique", variant="primary")

            out_history_summary = gr.Markdown()
            out_history_table   = gr.Dataframe(
                headers=["#", "ID Employé", "Prédiction", "Probabilité", "Risque", "Filtre utilisé", "Date"],
                label="Historique",
                interactive=False,
            )

            btn_history.click(
                fn=get_history,
                inputs=[token_state, inp_limit, inp_hist_empid],
                outputs=[out_history_summary, out_history_table],
            )

    # ─── Footer ───
    gr.Markdown(
        """
        ---
        *P5 — Déploiement ML — Barbara Di Battista — OpenClassrooms IA Engineer*
        """
    )


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
    )