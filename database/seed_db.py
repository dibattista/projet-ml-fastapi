"""
Insertion des données employees dans la base de données.
Lit le CSV nettoyé du P4 et insère les 1470 employés.
"""
import os
import pandas as pd
from sqlalchemy import create_engine


def seed_employees():
    """Insère les données du CSV dans la table employees."""

    # Connexion à la base
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "attrition_db")

    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(database_url)

    # Lire le CSV nettoyé du P4
    csv_path = "notebooks/resultats/DiBattista_Barbara_4_csv_resultat_nettoyage_122025.csv"
    df = pd.read_csv(csv_path)

    print(f"CSV chargé : {len(df)} lignes, {len(df.columns)} colonnes")

    # Insérer dans PostgreSQL
    df.to_sql(
        "employees",        # nom de la table
        engine,
        if_exists="append", # ajoute sans supprimer
        index=False         # pas d'index pandas
    )

    print(f"{len(df)} employés insérés avec succès !")


if __name__ == "__main__":
    seed_employees()