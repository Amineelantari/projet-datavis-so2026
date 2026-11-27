# axe_4.py
# Les calculs de l'axe 4 : évoluer, le rôle (ICorPM) et la formation (LearnAI).
# Pas de Streamlit dans ce fichier, juste pandas.
# Chaque fonction prend un tableau déjà filtré (preparer + filtres de la page)
# et renvoie un tableau avec une colonne repondants.

import pandas as pd

# réponses exactes du sondage -> rôle affiché à l'écran
# « People manager » seul (55 personnes en France et pays frontaliers) est regroupé avec « Manager qui code »
ROLES = {
    "Individual contributor": "Développeur",
    "Individual contributor in a senior or staff-level role": "Développeur senior",
    "Both people manager and individual contributor": "Manager",
    "People manager": "Manager",
}
ORDRE_ROLES = ["Développeur", "Développeur senior", "Manager"]

# réponses exactes du sondage -> formation affichée à l'écran
FORMATION = {
    "Yes, both on my own and at work": "Seul et au travail",
    "Yes, at work": "Au travail",
    "Yes, on my own": "Seul",
    "No": "Non",
}
ORDRE_FORMATION = ["Non", "Seul", "Au travail", "Seul et au travail"]

# même règle que l'axe 2 (Saad) : en stagnation = toute réponse sauf celle-ci
PAS_DE_STAGNATION = "I do not feel complacent"


def ajouter_role(df):
    # crée la colonne Role en français ; ceux qui n'ont pas répondu sont retirés
    df = df.copy()
    df["Role"] = pd.Categorical(df["ICorPM"].map(ROLES), categories=ORDRE_ROLES, ordered=True)
    return df[df["Role"].notna()]


def satisfaction_par_role(df):
    # pour chaque rôle : satisfaction moyenne (0 à 10) et part en stagnation, avec leurs répondants
    df = ajouter_role(df)
    df["JobSat"] = pd.to_numeric(df["JobSat"], errors="coerce")
    satisfaction = df.groupby("Role", observed=False)["JobSat"].agg(
        satisfaction="mean", repondants="count"
    )
    # la stagnation se calcule seulement sur ceux qui ont répondu à la question
    reponses = df[df["JobSatComplacent"].notna()]
    en_stagnation = reponses["JobSatComplacent"] != PAS_DE_STAGNATION
    stagnation = en_stagnation.groupby(reponses["Role"], observed=False).agg(
        part_stagnation="mean", repondants_stagnation="size"
    )
    return satisfaction.join(stagnation).reset_index()


def role_par_experience(df):
    # pour chaque tranche d'expérience : la part de chaque rôle (chaque tranche fait 100 %)
    df = ajouter_role(df)
    tableau = (
        df.groupby(["Tranche_experience", "Role"], observed=False)
        .size()
        .reset_index(name="nombre")
    )
    tableau["repondants"] = tableau.groupby("Tranche_experience", observed=False)["nombre"].transform("sum")
    tableau["part"] = tableau["nombre"] / tableau["repondants"]
    return tableau


def formation_par_role(df):
    # pour chaque rôle : la part de chaque réponse à LearnAI (chaque rôle fait 100 %)
    df = ajouter_role(df)
    df["Formation"] = pd.Categorical(df["LearnAI"].map(FORMATION), categories=ORDRE_FORMATION, ordered=True)
    df = df[df["Formation"].notna()]
    tableau = (
        df.groupby(["Role", "Formation"], observed=False)
        .size()
        .reset_index(name="nombre")
    )
    tableau["repondants"] = tableau.groupby("Role", observed=False)["nombre"].transform("sum")
    tableau["part"] = tableau["nombre"] / tableau["repondants"]
    return tableau
