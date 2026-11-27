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
