"""
Insertion des données dans les 3 tables : sirh, evaluation, sondage.
Lit les 3 CSV bruts du P4.
"""
import os
import pandas as pd
from sqlalchemy import create_engine


def seed_database():
    """Insère les données des 3 CSV dans les tables."""

    # Connexion
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "attrition_db")

    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(database_url)

    # ============================================
    # Table 1 : sirh
    # ============================================
    df_sirh = pd.read_csv("notebooks/data/extrait_sirh.csv")
    df_sirh.to_sql("sirh", engine, if_exists="append", index=False)
    print(f"sirh : {len(df_sirh)} lignes insérées")

    # ============================================
    # Table 2 : evaluation
    # Conversion eval_number : "E_42" → 42
    # ============================================
    df_eval = pd.read_csv("notebooks/data/extrait_eval.csv")
    df_eval["eval_number"] = df_eval["eval_number"].str.replace("E_", "").astype(int)
    df_eval.to_sql("evaluation", engine, if_exists="append", index=False)
    print(f"evaluation : {len(df_eval)} lignes insérées")

    # ============================================
    # Table 3 : sondage
    # ============================================
    df_sondage = pd.read_csv("notebooks/data/extrait_sondage.csv")
    df_sondage.to_sql("sondage", engine, if_exists="append", index=False)
    print(f"sondage : {len(df_sondage)} lignes insérées")

    print("\nToutes les données insérées avec succès !")


if __name__ == "__main__":
    seed_database()