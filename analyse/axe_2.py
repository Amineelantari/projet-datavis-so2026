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


def causes_stagnation(df):
    # parmi les personnes en stagnation : combien donnent chaque cause, et quelle part ça fait
    reponses = reponses_stagnation(df)
    en_stagnation = reponses[reponses["En_stagnation"]]
    tableau = en_stagnation["Reponse"].value_counts().rename_axis("Cause").reset_index(name="nombre")
    # repondants = toutes les personnes en stagnation, la base de la part
    tableau["repondants"] = len(en_stagnation)
    tableau["part"] = tableau["nombre"] / tableau["repondants"]
    return tableau


# ordre d'affichage des secteurs
ORDRE_SECTEURS = ["ESN", "Éditeur de logiciels", "Autre secteur"]


def causes_par_secteur(df):
    # les causes de stagnation dans chaque secteur, une ligne par secteur et par cause
    # (format long, pratique pour Plotly ; pour avoir les secteurs en colonnes :
    #  tableau.pivot(index="Cause", columns="Secteur", values="part"))
    reponses = reponses_stagnation(df)
    en_stagnation = reponses[reponses["En_stagnation"]]
    tableau = en_stagnation.groupby(["Secteur", "Reponse"]).size().reset_index(name="nombre")
    tableau = tableau.rename(columns={"Reponse": "Cause"})
    # repondants = les personnes en stagnation du secteur, la base de la part
    tableau["repondants"] = tableau.groupby("Secteur")["nombre"].transform("sum")
    tableau["part"] = tableau["nombre"] / tableau["repondants"]
    # secteurs dans l'ordre ESN, éditeurs, autres ; causes de la plus citée à la moins citée
    tableau["Secteur"] = pd.Categorical(tableau["Secteur"], categories=ORDRE_SECTEURS, ordered=True)
    return tableau.sort_values(["Secteur", "part"], ascending=[True, False]).reset_index(drop=True)
