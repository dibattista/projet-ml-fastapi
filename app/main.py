from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional


from app.database import get_db
from app.predict import (
    get_employee_dataframe,
    encode_employee_data,
    predict_employees,
    log_predictions,
)
from app.schemas import (
    PredictionResult,
    PredictionGroupResponse,
    PredictionHistory,
    HistoryResponse,
)
from app.auth import get_current_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

app = FastAPI(
    title="Futurisys - API Prédiction Attrition",
    description="API de prédiction du risque de départ des employés (POC)",
    version="1.0.0",
)


# ─── ENDPOINT 1 : Prédiction par filtre ───
@app.get("/predict/filter", response_model=PredictionGroupResponse)
def predict_by_filter(
    poste: Optional[str] = Query(None),
    heure_sup: Optional[str] = Query(None),
    departement: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # ── Validation manuelle ──────────────────────────────
    POSTES_VALIDES = {
        "Cadre Commercial", "Assistant de Direction", "Consultant",
        "Tech Lead", "Manager", "Senior Manager",
        "Représentant Commercial", "Directeur Technique", "Ressources Humaines"
    }
    DEPARTEMENTS_VALIDES = {"Consulting", "Commercial", "Ressources Humaines"}
    HEURES_SUP_VALIDES = {"Oui", "Non"}

    if not any([poste, heure_sup, departement]):
        raise HTTPException(status_code=422, detail="Au moins un filtre requis")

    if poste and poste not in POSTES_VALIDES:
        raise HTTPException(status_code=422, detail=f"Poste '{poste}' invalide")

    if departement and departement not in DEPARTEMENTS_VALIDES:
        raise HTTPException(status_code=422, detail=f"Département '{departement}' invalide")

    if heure_sup and heure_sup not in HEURES_SUP_VALIDES:
        raise HTTPException(status_code=422, detail=f"heure_sup '{heure_sup}' invalide. Valeurs : Oui, Non")

    # ── Suite inchangée ──────────────────────────────────
    filters = {}
    if poste: filters["poste"] = poste
    if heure_sup: filters["heure_supplementaires"] = heure_sup
    if departement: filters["departement"] = departement


    # 1. Jointure des 3 tables + filtre
    df = get_employee_dataframe(db, filters=filters)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun employé trouvé avec ces filtres : {filters}"
        )

    # 2. Encoder
    df_encoded = encode_employee_data(df)

    # 3. Prédire
    results = predict_employees(df_encoded)

    # 4. Logger
    filter_str = ", ".join(f"{k}={v}" for k, v in filters.items())
    log_predictions(db, results, filter_used=filter_str)

    # 5. Réponse
    total_at_risk = len(results[results["prediction"] == "Part"])
    return PredictionGroupResponse(
        filter_used=filter_str,
        total_employees=len(results),
        total_at_risk=total_at_risk,
        risk_rate=round(total_at_risk / len(results) * 100, 1),
        predictions=results.to_dict("records"),
    )


# ─── ENDPOINT 2 : Prédiction par employé ───
@app.get("/predict/employee/{employee_id}", response_model=PredictionResult)
def predict_by_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Prédit le risque de départ pour un employé spécifique.
    """
    # 1. Jointure + filtre par ID
    df = get_employee_dataframe(db, employee_id=employee_id)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Employé {employee_id} non trouvé"
        )

    # 2. Encoder
    df_encoded = encode_employee_data(df)

    # 3. Prédire
    results = predict_employees(df_encoded)

    # 4. Logger
    log_predictions(db, results, filter_used=f"employee_id={employee_id}")

    # 5. Réponse (1 seul résultat)
    return results.iloc[0].to_dict()


# ─── ENDPOINT 3 : Historique des prédictions ───
@app.get("/predictions/history", response_model=HistoryResponse)
def get_predictions_history(
    limit: int = Query(50, description="Nombre max de résultats"),
    employee_id: Optional[int] = Query(None, description="Filtrer par employé"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user), 
):
    """
    Consulte l'historique des prédictions loggées.
    """
    query = "SELECT * FROM predictions"
    params = {}

    if employee_id:
        query += " WHERE employee_id = :employee_id"
        params["employee_id"] = employee_id

    query += " ORDER BY created_at DESC LIMIT :limit"
    params["limit"] = limit

    result = db.execute(text(query), params)
    columns = result.keys()
    rows = result.fetchall()

    predictions = [dict(zip(columns, row)) for row in rows]

    return HistoryResponse(
        total_predictions=len(predictions),
        predictions=predictions,
    )


# ─── Endpoint racine (santé) ───
@app.get("/")
def root():
    return {
        "message": "API Futurisys - Prédiction Attrition",
        "version": "1.0.0",
        "endpoints": [
            "GET /predict/filter?poste=Consultant",
            "GET /predict/employee/{id}",
            "GET /predictions/history",
        ],
    }

# ─── ENDPOINT LOGIN ───
@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
