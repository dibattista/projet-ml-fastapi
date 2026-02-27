-- ============================================
-- P5 - Initialisation de la base de données
-- ============================================

CREATE DATABASE attrition_db;

\c attrition_db;

-- ============================================
-- Table 1 : sirh (données RH - table principale)
-- ============================================
CREATE TABLE IF NOT EXISTS sirh (
    id_employee INTEGER PRIMARY KEY,
    age INTEGER NOT NULL,
    genre VARCHAR(10) NOT NULL,
    revenu_mensuel INTEGER NOT NULL,
    statut_marital VARCHAR(20) NOT NULL,
    departement VARCHAR(30) NOT NULL,
    poste VARCHAR(40) NOT NULL,
    nombre_experiences_precedentes INTEGER NOT NULL,
    nombre_heures_travailless INTEGER NOT NULL,
    annee_experience_totale INTEGER NOT NULL,
    annees_dans_l_entreprise INTEGER NOT NULL,
    annees_dans_le_poste_actuel INTEGER NOT NULL
);

-- ============================================
-- Table 2 : evaluation (notes et satisfaction)
-- eval_number converti de "E_42" → 42
-- ============================================
CREATE TABLE IF NOT EXISTS evaluation (
    eval_number INTEGER PRIMARY KEY,
    satisfaction_employee_environnement INTEGER NOT NULL,
    note_evaluation_precedente INTEGER NOT NULL,
    niveau_hierarchique_poste INTEGER NOT NULL,
    satisfaction_employee_nature_travail INTEGER NOT NULL,
    satisfaction_employee_equipe INTEGER NOT NULL,
    satisfaction_employee_equilibre_pro_perso INTEGER NOT NULL,
    note_evaluation_actuelle INTEGER NOT NULL,
    heure_supplementaires VARCHAR(5) NOT NULL,
    augementation_salaire_precedente VARCHAR(10) NOT NULL
);

-- ============================================
-- Table 3 : sondage (bien-être et contexte)
-- ============================================
CREATE TABLE IF NOT EXISTS sondage (
    code_sondage INTEGER PRIMARY KEY,
    a_quitte_l_entreprise VARCHAR(5) NOT NULL,
    nombre_participation_pee INTEGER NOT NULL,
    nb_formations_suivies INTEGER NOT NULL,
    nombre_employee_sous_responsabilite INTEGER NOT NULL,
    distance_domicile_travail INTEGER NOT NULL,
    niveau_education INTEGER NOT NULL,
    domaine_etude VARCHAR(40) NOT NULL,
    ayant_enfants VARCHAR(5) NOT NULL,
    frequence_deplacement VARCHAR(20) NOT NULL,
    annees_depuis_la_derniere_promotion INTEGER NOT NULL,
    annes_sous_responsable_actuel INTEGER NOT NULL
);

-- ============================================
-- Table 4 : predictions (logs API)
-- ============================================
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    prediction VARCHAR(10) NOT NULL,
    probability FLOAT NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    filter_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES sirh(id_employee)
);