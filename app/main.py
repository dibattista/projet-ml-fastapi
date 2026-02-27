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

app = FastAPI(
    title="Futurisys - API Prédiction Attrition",
    description="API de prédiction du risque de départ des employés (POC)",
    version="1.0.0",
)


# ─── ENDPOINT 1 : Prédiction par filtre ───
@app.get("/predict/filter", response_model=PredictionGroupResponse)
def predict_by_filter(
    poste: Optional[str] = Query(None, description="Filtrer par poste"),
    heure_supplementaires: Optional[str] = Query(None, alias="heure_sup", description="Oui ou Non"),
    departement: Optional[str] = Query(None, description="Filtrer par département"),
    db: Session = Depends(get_db),
):
    """
    Filtre les employés selon des critères,
    puis prédit le risque de départ pour chacun.
    """
    # Construire les filtres
    filters = {}
    if poste:
        filters["poste"] = poste
    if heure_supplementaires:
        filters["heure_supplementaires"] = heure_supplementaires
    if departement:
        filters["departement"] = departement

    if not filters:
        raise HTTPException(
            status_code=400,
            detail="Au moins un filtre requis : poste, heure_sup, departement"
        )

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