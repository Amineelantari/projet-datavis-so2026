# axe_1.py
# Les calculs de l'axe 1 : la satisfaction au fil de la carrière (colonne JobSat, de 0 à 10).
# Pas de Streamlit dans ce fichier, juste pandas.
# Chaque fonction prend un tableau déjà filtré (preparer + filtres de la page)
# et renvoie un tableau avec une colonne repondants.

import pandas as pd

from analyse.population import EN_EMPLOI, ajouter_zone, ajouter_tranche_experience

# à partir de 8 sur 10, on considère la personne comme très satisfaite
SEUIL_TRES_SATISFAIT = 8

# population 2025, d'après HARMONISATION.md : les deux réponses de MainBranch qui correspondent à CODENT
CODENT_2025 = [
    "I am a developer by profession",
    "I am not primarily a developer, but I write code sometimes as part of my work/studies",
]


def satisfaction_par_experience(df):
    # pour chaque tranche d'expérience : la satisfaction moyenne, la part de très satisfaits et le nombre de répondants
    notes = df[df["JobSat"].notna()]
    tableau = (
        notes.groupby("Tranche_experience", observed=False)["JobSat"]
        .agg(
            moyenne="mean",
            part_tres_satisfaits=lambda s: (s >= SEUIL_TRES_SATISFAIT).mean(),
            repondants="size",
        )
        .reset_index()
    )
    return tableau


def satisfaction_par_secteur(df):
    # la même chose, mais pour chaque tranche ET chaque secteur (ESN, éditeur, autre)
    notes = df[df["JobSat"].notna()]
    tableau = (
        notes.groupby(["Tranche_experience", "Secteur"], observed=False)["JobSat"]
        .agg(
            moyenne="mean",
            part_tres_satisfaits=lambda s: (s >= SEUIL_TRES_SATISFAIT).mean(),
            repondants="size",
        )
        .reset_index()
    )
    return tableau


def population_2025(df_2025):
    # la population de 2025 définie comme celle de 2026, d'après HARMONISATION.md
    df = df_2025[df_2025["MainBranch"].isin(CODENT_2025) & df_2025["Employment"].isin(EN_EMPLOI)].copy()
    df = ajouter_zone(df)
    df = ajouter_tranche_experience(df)
    return df


def comparaison_2025(df_2026, df_2025):
    # satisfaction moyenne par tranche d'expérience, pour 2025 et 2026
    # les deux tableaux doivent déjà être filtrés sur les mêmes zones
    # pas de filtre par secteur : la catégorie ESN n'existe pas en 2025 (HARMONISATION.md)
    deux_annees = pd.concat([df_2025, df_2026])
    notes = deux_annees[deux_annees["JobSat"].notna()]
    tableau = (
        notes.groupby(["Tranche_experience", "Annee"], observed=False)["JobSat"]
        .agg(moyenne="mean", repondants="size")
        .reset_index()
    )
    return tableau
