# population.py
# On choisit ici les personnes qu'on étudie et on ajoute la zone géographique.
# Pas de Streamlit dans ce fichier, juste pandas.

import pandas as pd

# Partie 1 : qui on garde et d'où ils viennent

# on garde les gens qui codent dans leur travail, souvent ou de temps en temps
CODENT = [
    "I create code as a primary part of my job",
    "I create code occasionally",
]

# on garde les salariés et les freelances, une ESN travaille avec les deux
EN_EMPLOI = [
    "Employed",
    "Independent contractor, freelancer, or self-employed",
]

# pays proches de Lyon où un développeur peut partir travailler
PAYS_FRONTALIERS = ["Switzerland", "Germany", "Belgium", "Luxembourg", "Italy", "Spain"]

# le reste de l'Europe
RESTE_EUROPE = [
    "Austria", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
    "Estonia", "Finland", "Greece", "Hungary", "Ireland", "Latvia", "Lithuania",
    "Malta", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Sweden", "United Kingdom of Great Britain and Northern Ireland",
]


def population_principale(df):
    # garde seulement les gens qui codent et qui ont un travail
    return df[df["CodeMain"].isin(CODENT) & df["Employment"].isin(EN_EMPLOI)].copy()


def ajouter_zone(df):
    # crée la colonne Zone à partir du pays
    df = df.copy()
    df["Zone"] = "Reste du monde"
    # ceux qui n'ont pas donné leur pays sont mis à part
    df.loc[df["Country"].isna(), "Zone"] = "Pays non renseigné"
    df.loc[df["Country"].isin(RESTE_EUROPE), "Zone"] = "Reste de l'Europe"
    df.loc[df["Country"].isin(PAYS_FRONTALIERS), "Zone"] = "Pays frontaliers"
    df.loc[df["Country"] == "France", "Zone"] = "France"
    return df


# Partie 2 : le profil des personnes et la préparation finale

# bornes des tranches d'expérience, en années : (0, 1], (1, 3], (3, 6], ...
BORNES_EXPERIENCE = [0, 1, 3, 6, 10, 20, float("inf")]
TRANCHES_EXPERIENCE = ["0-1", "2-3", "4-6", "7-10", "11-20", "21+"]


def ajouter_tranche_experience(df):
    # crée la colonne Tranche_experience à partir des années d'expérience (WorkExp)
    df = df.copy()
    # en nombre ; ce qui n'est pas un nombre devient vide (NaN)
    annees = pd.to_numeric(df["WorkExp"], errors="coerce")
    # ceux qui n'ont pas répondu restent vides, et ne sont dans aucune tranche
    df["Tranche_experience"] = pd.cut(
        annees,
        bins=BORNES_EXPERIENCE,
        labels=TRANCHES_EXPERIENCE,
        include_lowest=True,
    )
    return df


# réponses exactes du sondage (colonne Industry)
INDUSTRIE_ESN = "IT services, consulting, systems integration, or managed services"
INDUSTRIE_EDITEUR = "Software development"


def ajouter_secteur(df):
    # crée la colonne Secteur à partir du secteur d'activité (Industry)
    df = df.copy()
    # par défaut, et aussi pour ceux qui n'ont pas répondu
    df["Secteur"] = "Autre secteur"
    df.loc[df["Industry"] == INDUSTRIE_ESN, "Secteur"] = "ESN"
    df.loc[df["Industry"] == INDUSTRIE_EDITEUR, "Secteur"] = "Éditeur de logiciels"
    return df


def preparer(df):
    # la population de l'étude, prête pour tous les axes : preparer(charger(2026))
    df = population_principale(df)
    df = ajouter_zone(df)
    df = ajouter_tranche_experience(df)
    df = ajouter_secteur(df)
    return df
