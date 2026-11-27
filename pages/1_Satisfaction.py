# 1_Satisfaction.py
# Axe 1 : la satisfaction au fil de la carrière (Amine).
# L'affichage avec Streamlit ; les calculs sont dans analyse/axe_1.py.

import plotly.express as px
import streamlit as st

from analyse.affichage import ACCENT, GRIS, SEUIL, legende_population
from analyse.axe_1 import (
    comparaison_2025,
    population_2025,
    satisfaction_par_experience,
    satisfaction_par_secteur,
)
from analyse.chargement import charger
from analyse.population import TRANCHES_EXPERIENCE, preparer

# valeurs par défaut des filtres communs, si la page est ouverte avant le tableau de bord
ZONES_DEFAUT = ["France", "Pays frontaliers"]
SECTEURS_DEFAUT = ["ESN", "Éditeur de logiciels", "Autre secteur"]


@st.cache_data
def donnees_2026():
    # chargé une seule fois, puis gardé en mémoire
    return preparer(charger(2026))


@st.cache_data
def donnees_2025():
    # population 2025 définie comme en 2026, d'après HARMONISATION.md
    return population_2025(charger(2025))


def virgule(nombre):
    # 6.84 -> « 6,8 »
    return f"{nombre:.1f}".replace(".", ",")


def pourcent(part):
    # 0.42 -> « 42 % »
    return f"{part * 100:.0f} %"


def texte_zones(zones):
    # ["France", "Pays frontaliers"] -> « France et pays frontaliers »
    noms = [z if z == "France" else z[0].lower() + z[1:] for z in zones]
    return " et ".join(noms) if len(noms) <= 2 else ", ".join(noms[:-1]) + " et " + noms[-1]


def mise_en_forme(fig):
    # désencombrer : fond blanc, pas de grille verticale, pas de titre d'axe inutile
    fig.update_layout(
        plot_bgcolor="white",
        margin=dict(t=40, b=10),
        legend_title_text="",
        legend=dict(orientation="h", x=0, y=1.1),
        separators=", ",  # virgule pour les décimales, à la française
    )
    fig.update_yaxes(showgrid=True, gridcolor="#E5E5E5")
    return fig


# Les filtres communs, choisis sur le tableau de bord (app.py)
zones = st.session_state.get("zones", ZONES_DEFAUT)
secteurs = st.session_state.get("secteurs", SECTEURS_DEFAUT)

st.title("La satisfaction au fil de la carrière")
st.caption(f"Filtres du tableau de bord : {texte_zones(zones) or 'aucune zone'} · {', '.join(secteurs) or 'aucun secteur'}")

if not zones or not secteurs:
    st.info("Choisissez au moins une zone et un secteur sur le tableau de bord.")
    st.stop()

# Le filtre propre à l'axe : l'indicateur affiché
indicateur = st.radio(
    "Indicateur",
    ["Satisfaction moyenne sur 10", "Part de très satisfaits (8 ou plus)"],
    horizontal=True,
    key="axe1_indicateur",
)
colonne = "moyenne" if indicateur.startswith("Satisfaction") else "part_tres_satisfaits"
formater = virgule if colonne == "moyenne" else pourcent

df = donnees_2026()
filtre = df[df["Zone"].isin(zones) & df["Secteur"].isin(secteurs)]
qui = f"Développeurs en emploi ({texte_zones(zones)}) ayant donné leur satisfaction"


# Vue 1 : la satisfaction selon l'expérience
par_experience = satisfaction_par_experience(filtre)
assez = par_experience["repondants"] >= SEUIL
par_experience["valeur"] = par_experience[colonne].where(assez)

if par_experience["valeur"].notna().sum() < 2:
    st.info("Effectif trop faible pour comparer les tranches d'expérience avec ces filtres.")
else:
    # la tranche la plus basse en ACCENT, le reste en GRIS
    plus_basse = par_experience.loc[par_experience["valeur"].idxmin(), "Tranche_experience"]
    par_experience["couleur"] = ["Plus basse" if t == plus_basse else "Autres" for t in par_experience["Tranche_experience"]]
    par_experience["texte"] = [formater(v) if v == v else "trop peu" for v in par_experience["valeur"]]

    st.subheader(f"La satisfaction est au plus bas vers {plus_basse} ans d'expérience")
    fig = px.bar(
        par_experience,
        x="Tranche_experience",
        y="valeur",
        text="texte",
        color="couleur",
        color_discrete_map={"Plus basse": ACCENT, "Autres": GRIS},
        category_orders={"Tranche_experience": TRANCHES_EXPERIENCE},
        labels={"Tranche_experience": "Années d'expérience", "valeur": indicateur},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    # les barres partent de 0 : un axe coupé grossirait des écarts d'un demi-point
    fig.update_yaxes(range=[0, 10] if colonne == "moyenne" else [0, 1], tickformat=None if colonne == "moyenne" else ".0%")
    st.plotly_chart(mise_en_forme(fig), use_container_width=True)
    st.caption(legende_population(filtre[filtre["JobSat"].notna()], qui, 2026) + f" · tranches de moins de {SEUIL} répondants masquées")


# Vue 2 : ESN, éditeurs et autres secteurs
par_secteur = satisfaction_par_secteur(filtre)
par_secteur = par_secteur[par_secteur["Secteur"].isin(secteurs)]
par_secteur["valeur"] = par_secteur[colonne].where(par_secteur["repondants"] >= SEUIL)

st.subheader("Les ESN suivent-elles la même courbe que les autres secteurs ?")
if par_secteur["valeur"].notna().sum() == 0:
    st.info("Effectif trop faible pour comparer les secteurs avec ces filtres.")
else:
    fig = px.bar(
        par_secteur,
        x="Tranche_experience",
        y="valeur",
        color="Secteur",
        barmode="group",
        color_discrete_map={"ESN": ACCENT, "Éditeur de logiciels": "#8C8C8C", "Autre secteur": GRIS},
        category_orders={"Tranche_experience": TRANCHES_EXPERIENCE},
        labels={"Tranche_experience": "Années d'expérience", "valeur": indicateur},
    )
    fig.update_yaxes(range=[0, 10] if colonne == "moyenne" else [0, 1], tickformat=None if colonne == "moyenne" else ".0%")
    st.plotly_chart(mise_en_forme(fig), use_container_width=True)
    st.caption(
        legende_population(filtre[filtre["JobSat"].notna()], qui, 2026)
        + f" · groupes de moins de {SEUIL} répondants masqués, souvent en ESN avant 4 ans"
    )


# Vue 3 : comparaison avec 2025, tous secteurs (la catégorie ESN n'existe pas en 2025)
d2025 = donnees_2025()
filtre_2025 = d2025[d2025["Zone"].isin(zones)]
filtre_2026_tous = df[df["Zone"].isin(zones)]
comparaison = comparaison_2025(filtre_2026_tous, filtre_2025)
comparaison = comparaison[comparaison["repondants"] >= SEUIL]

if comparaison["Annee"].nunique() < 2:
    st.info("Effectif trop faible pour comparer 2025 et 2026 avec ces filtres.")
else:
    ecarts = comparaison.pivot(index="Tranche_experience", columns="Annee", values="moyenne").dropna()
    ecarts["baisse"] = ecarts[2025] - ecarts[2026]
    plus_forte = ecarts["baisse"].idxmax()

    st.subheader(f"Par rapport à 2025, c'est vers {plus_forte} ans que la satisfaction a le plus baissé")
    comparaison["Année"] = comparaison["Annee"].astype(str)
    fig = px.bar(
        comparaison,
        x="Tranche_experience",
        y="moyenne",
        color="Année",
        barmode="group",
        color_discrete_map={"2025": GRIS, "2026": ACCENT},
        category_orders={"Tranche_experience": TRANCHES_EXPERIENCE},
        labels={"Tranche_experience": "Années d'expérience", "moyenne": "Satisfaction moyenne sur 10"},
    )
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside")
    fig.update_yaxes(range=[0, 10])
    st.plotly_chart(mise_en_forme(fig), use_container_width=True)
    st.caption(
        legende_population(filtre_2025[filtre_2025["JobSat"].notna()], f"Développeurs en emploi ({texte_zones(zones)})", 2025)
        + " | "
        + legende_population(filtre_2026_tous[filtre_2026_tous["JobSat"].notna()], "Même population", 2026)
    )
    st.caption(
        "Comparaison tous secteurs : la catégorie ESN n'existe pas en 2025. "
        "La population 2025 est définie d'après HARMONISATION.md, la correspondance n'est pas parfaite."
    )

st.info(
    "À retenir : l'enquête ne mesure pas les départs. Elle montre à quel moment de la carrière "
    "la satisfaction est la plus basse, un signal qui précède souvent un départ."
)
