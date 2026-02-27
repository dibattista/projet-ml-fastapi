"""
Fonctions de feature engineering pour le pipeline ML.
Utilisé par le notebook (sauvegarde) ET par l'API (chargement).
"""
import pandas as pd


# Configuration des features actives
FEATURES_CONFIG = {
    'junior_poste_risque': True,
    'commercial_distance': True,
    'Job_changing': True,
    'commercial_junior': False,
    'celibataire_distance': False,
    'commercial_celibataire': False,
}


def creer_features(df, config):
    """
    Crée les features engineering selon la configuration.
    """
    df_new = df.copy()
    features_ajoutees = []

    postes_commerciaux = ['Représentant Commercial', 'Cadre Commercial']
    postes_risque = ['Représentant Commercial', 'Cadre Commercial', 'Consultant']

    if config.get('junior_poste_risque', False):
        df_new['feat_junior_poste_risque'] = (
            (df_new['poste'].isin(postes_risque)) &
            (df_new['annee_experience_totale'] <= 7)
        ).astype(int)
        features_ajoutees.append('feat_junior_poste_risque')

    if config.get('commercial_distance', False):
        df_new['feat_commercial_distance'] = (
            (df_new['poste'].isin(postes_commerciaux)) &
            (df_new['distance_domicile_travail'] > 20)
        ).astype(int)
        features_ajoutees.append('feat_commercial_distance')

    if config.get('commercial_junior', False):
        df_new['feat_commercial_junior'] = (
            (df_new['poste'].isin(postes_commerciaux)) &
            (df_new['annee_experience_totale'] <= 7)
        ).astype(int)
        features_ajoutees.append('feat_commercial_junior')

    if config.get('celibataire_distance', False):
        df_new['feat_celibataire_distance'] = (
            (df_new['statut_marital'] == 'Celibataire') &
            (df_new['distance_domicile_travail'] > 20)
        ).astype(int)
        features_ajoutees.append('feat_celibataire_distance')

    if config.get('commercial_celibataire', False):
        df_new['feat_commercial_celibataire'] = (
            (df_new['poste'].isin(postes_commerciaux)) &
            (df_new['statut_marital'] == 'Celibataire')
        ).astype(int)
        features_ajoutees.append('feat_commercial_celibataire')

    if config.get('Job_changing', False):
        df_new['job_changing'] = (
            (df_new['nombre_experiences_precedentes'] >= 4) &
            (df_new['annee_experience_totale'] <= 6)
        ).astype(int)
        features_ajoutees.append('job_changing')

    return df_new, features_ajoutees


def add_features(df):
    """Version pipeline de creer_features()."""
    df_result, _ = creer_features(df, FEATURES_CONFIG)
    return df_result