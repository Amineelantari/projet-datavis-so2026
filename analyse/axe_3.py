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

# réponses qui ne désignent pas un facteur précis : elles restent en gris dans les figures
REPONSES_NEUTRES = [
    "Rien n'a compliqué le travail",
    "Rien n'a facilité le travail",
    "Ne sait pas",
    "Autre",
]

# chaque facteur est rangé dans un levier sur lequel la DRH peut agir
# (le télétravail n'est pas dans ces questions : il est traité dans l'axe 5)
LEVIERS = {
    # ce qui gêne
    "Priorités floues": "Organisation des missions",
    "Organisation inefficace": "Organisation des missions",
    "Changements dans la direction": "Organisation des missions",
    "Manque de temps ou de moyens": "Charge de travail",
    "Documentation insuffisante": "Accompagnement et formation",
    "Manque de soutien": "Accompagnement et formation",
    "Outils peu fiables": "Outils",
    "Pas les bons outils": "Outils",
    # ce qui aide
    "Priorités claires": "Organisation des missions",
    "Meilleure organisation": "Organisation des missions",
    "Assez de temps ou de moyens": "Charge de travail",
    "Bonne documentation": "Accompagnement et formation",
    "Soutien de l'équipe": "Accompagnement et formation",
    "Les bons outils": "Outils",
    "Outils fiables": "Outils",
}
HORS_LEVIER = "Aucun facteur précis"


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


def satisfaction_selon(df, colonne, traductions):
    # satisfaction moyenne (JobSat, de 0 à 10) selon la réponse donnée à colonne,
    # de la plus basse à la plus haute
    avec_reponse = df.dropna(subset=["JobSat", colonne])
    tableau = (
        avec_reponse.groupby(colonne)["JobSat"]
        .agg(satisfaction="mean", repondants="size")
        .reset_index()
        .rename(columns={colonne: "reponse"})
        .sort_values("satisfaction")
        .reset_index(drop=True)
    )
    tableau["satisfaction"] = tableau["satisfaction"].round(2)
    tableau["reponse"] = tableau["reponse"].map(traductions)
    return tableau


def satisfaction_par_difficulte(df):
    # satisfaction moyenne selon la difficulté principale
    return satisfaction_selon(df, "JobDifficulty", DIFFICULTES)


def satisfaction_par_aide(df):
    # satisfaction moyenne selon l'aide principale
    return satisfaction_selon(df, "JobEase", AIDES)


def satisfaction_moyenne(df, colonne="JobDifficulty"):
    # satisfaction moyenne de tous ceux qui ont répondu à JobSat et à colonne :
    # c'est la ligne grise de référence de la vue 2
    avec_reponse = df.dropna(subset=["JobSat", colonne])
    return round(avec_reponse["JobSat"].mean(), 2)


def comparaison_esn(df, colonne, traductions):
    # part de chaque réponse en ESN et dans les autres secteurs, côte à côte
    # (le secteur vient de preparer() : ESN, Éditeur de logiciels, Autre secteur)
    groupes = {
        "ESN": df[df["Secteur"] == "ESN"],
        "Autres secteurs": df[df["Secteur"] != "ESN"],
    }
    morceaux = []
    for nom, groupe in groupes.items():
        tableau = classement(groupe, colonne, traductions)
        tableau["groupe"] = nom
        tableau["total_groupe"] = groupe[colonne].notna().sum()
        morceaux.append(tableau)
    return pd.concat(morceaux, ignore_index=True)


def parts_par_levier(df, colonne, traductions):
    # regroupe les facteurs par levier de la DRH et additionne leurs parts ;
    # « Rien », « Ne sait pas » et « Autre » vont dans HORS_LEVIER, placé en dernier
    tableau = classement(df, colonne, traductions)
    tableau["levier"] = tableau["reponse"].map(LEVIERS).fillna(HORS_LEVIER)
    leviers = (
        tableau.groupby("levier")[["repondants", "part"]].sum()
        .reset_index()
        .sort_values("part", ascending=False)
    )
    leviers["part"] = leviers["part"].round(1)
    # le groupe hors levier passe à la fin, quelle que soit sa taille
    leviers["hors"] = leviers["levier"] == HORS_LEVIER
    return leviers.sort_values("hors", kind="stable").drop(columns="hors").reset_index(drop=True)
