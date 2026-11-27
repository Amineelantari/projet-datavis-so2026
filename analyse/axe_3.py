# axe_3.py
# Axe 3 : ce qui aide et ce qui gêne au travail.
# Pas de Streamlit dans ce fichier, juste pandas.
# Chaque fonction prend un tableau déjà filtré (zones, secteurs...) et renvoie un tableau
# avec une colonne repondants.

import pandas as pd

# réponses exactes du sondage (colonne JobDifficulty) et leur traduction pour l'affichage
# attention : "I’m not sure" s'écrit avec une apostrophe typographique dans les données
DIFFICULTES = {
    "Unclear priorities or requirements": "Priorités floues",
    "Inefficient processes, workflows, or coordination": "Organisation inefficace",
    "Not enough time, staffing, or resources": "Manque de temps ou de moyens",
    "Leadership activity or organizational changes": "Changements dans la direction",
    "Nothing has made my job harder in the past 6 months": "Rien n'a compliqué le travail",
    "Unreliable systems, infrastructure, or environments": "Outils peu fiables",
    "Poor documentation or knowledge sharing": "Documentation insuffisante",
    "Lack of support from teammates, managers, or mentors": "Manque de soutien",
    "Lack of access to the right tools or platforms": "Pas les bons outils",
    "I’m not sure": "Ne sait pas",
    "Other, please specify": "Autre",
}

# réponses exactes du sondage (colonne JobEase) : les mêmes thèmes, à l'endroit
AIDES = {
    "Access to the right tools or platforms": "Les bons outils",
    "Supportive teammates, managers, or mentors": "Soutien de l'équipe",
    "Clear priorities or requirements": "Priorités claires",
    "Better processes, workflows, or coordination": "Meilleure organisation",
    "Enough time, staffing, or resources": "Assez de temps ou de moyens",
    "Helpful documentation or knowledge sharing": "Bonne documentation",
    "Reliable systems, infrastructure, or environments": "Outils fiables",
    "Leadership activity or organizational changes": "Changements dans la direction",
    "Nothing has made my job easier in the past 6 months": "Rien n'a facilité le travail",
    "I’m not sure": "Ne sait pas",
    "Other, please specify": "Autre",
}


def classement(df, colonne, traductions):
    # part de chaque réponse parmi ceux qui ont répondu, de la plus citée à la moins citée
    reponses = df[colonne].dropna()
    tableau = reponses.value_counts().rename("repondants").reset_index()
    tableau.columns = ["reponse", "repondants"]
    tableau["part"] = (tableau["repondants"] / len(reponses) * 100).round(1)
    tableau["reponse"] = tableau["reponse"].map(traductions)
    return tableau


def classement_difficultes(df):
    # ce qui a le plus compliqué le travail ces 6 derniers mois
    return classement(df, "JobDifficulty", DIFFICULTES)


def classement_aides(df):
    # ce qui a le plus facilité le travail ces 6 derniers mois
    return classement(df, "JobEase", AIDES)


def satisfaction_par_difficulte(df):
    # satisfaction moyenne (JobSat, de 0 à 10) selon la difficulté principale,
    # de la plus basse à la plus haute
    avec_reponse = df.dropna(subset=["JobSat", "JobDifficulty"])
    tableau = (
        avec_reponse.groupby("JobDifficulty")["JobSat"]
        .agg(satisfaction="mean", repondants="size")
        .reset_index()
        .rename(columns={"JobDifficulty": "difficulte"})
        .sort_values("satisfaction")
        .reset_index(drop=True)
    )
    tableau["satisfaction"] = tableau["satisfaction"].round(2)
    tableau["difficulte"] = tableau["difficulte"].map(DIFFICULTES)
    return tableau


def satisfaction_moyenne(df):
    # satisfaction moyenne de tous ceux qui ont répondu à JobSat et à JobDifficulty :
    # c'est la ligne grise de référence de la vue 2
    avec_reponse = df.dropna(subset=["JobSat", "JobDifficulty"])
    return round(avec_reponse["JobSat"].mean(), 2)
