# axe_2.py
# Les calculs de l'axe 2 : le sentiment de stagnation (colonne JobSatComplacent).
# Pas de Streamlit dans ce fichier, juste pandas.
# Chaque fonction prend un tableau déjà filtré (preparer + filtres de la page)
# et renvoie un tableau avec une colonne repondants.

import pandas as pd

# réponse exacte du sondage pour ceux qui ne se sentent pas en stagnation
PAS_DE_STAGNATION = "I do not feel complacent"

# réponses exactes du sondage -> texte affiché à l'écran
TRADUCTION = {
    "I do not feel complacent": "Pas de sentiment de stagnation",
    "Burnout/tech fatigue": "Épuisement",
    "Economic uncertainty making me hesitant to switch roles": "Incertitude économique",
    "AI automating the challenging parts of my job": "L'IA fait les tâches intéressantes",
    "Lack of upward mobility due to corporate tightening": "Pas de perspective d'évolution",
    "Other, please specify": "Autre",
}


def reponses_stagnation(df):
    # garde seulement ceux qui ont répondu à la question (moins de la moitié des gens)
    df = df[df["JobSatComplacent"].notna()].copy()
    # la réponse en français, pour les graphiques
    df["Reponse"] = df["JobSatComplacent"].map(TRADUCTION)
    # en stagnation = a donné une cause, donc toute réponse sauf « pas de stagnation »
    df["En_stagnation"] = df["JobSatComplacent"] != PAS_DE_STAGNATION
    return df


def part_stagnation_par_experience(df):
    # pour chaque tranche d'expérience : la part en stagnation et le nombre de répondants à la question
    reponses = reponses_stagnation(df)
    # observed=False garde toutes les tranches, même vides après un filtre (0 répondant)
    tableau = (
        reponses.groupby("Tranche_experience", observed=False)["En_stagnation"]
        .agg(part="mean", repondants="size")
        .reset_index()
    )
    return tableau
