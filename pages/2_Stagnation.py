# 2_Stagnation.py
# Axe 2 : le sentiment de stagnation (Saad).
# L'affichage avec Streamlit ; les calculs sont dans analyse/axe_2.py.

import plotly.express as px
import streamlit as st

from analyse.axe_2 import part_stagnation_par_experience, reponses_stagnation
from analyse.chargement import charger
from analyse.population import TRANCHES_EXPERIENCE, preparer

try:
    from analyse.affichage import ACCENT, GRIS, SEUIL, legende_population
except ImportError:
    # PROVISOIRE : en attendant analyse/affichage.py (Gaetan).
    # Quand son fichier est sur main, ce bloc ne sert plus : on pourra le supprimer.
    SEUIL = 50
    GRIS, ACCENT = "#B0B0B0", "#C0392B"

    def legende_population(df, qui, annee):
        nombre = f"{len(df):,}".replace(",", " ")
        return f"{qui} · {annee} · {nombre} répondants · volontaires, non représentatifs de tous les développeurs"


# valeurs par défaut des filtres communs (si la page est ouverte avant le tableau de bord)
ZONES_DEFAUT = ["France", "Pays frontaliers"]
SECTEURS_DEFAUT = ["ESN", "Éditeur de logiciels", "Autre secteur"]


@st.cache_data
def donnees():
    # chargé une seule fois, puis gardé en mémoire
    return preparer(charger(2026))


def pourcent(part):
    # 0.678 -> « 68 % »
    return f"{part * 100:.0f} %"


def texte_zones(zones):
    # ["France", "Pays frontaliers"] -> « France et pays frontaliers »
    noms = [z if z == "France" else z[0].lower() + z[1:] for z in zones]
    return " et ".join(noms) if len(noms) <= 2 else ", ".join(noms[:-1]) + " et " + noms[-1]


# Les filtres communs, choisis sur le tableau de bord (app.py)
zones = st.session_state.get("zones", ZONES_DEFAUT)
secteurs = st.session_state.get("secteurs", SECTEURS_DEFAUT)

st.title("Le sentiment de stagnation")
st.caption(
    f"Filtres du tableau de bord : {texte_zones(zones) or 'aucune zone'} · {', '.join(secteurs) or 'aucun secteur'}"
)

if not zones or not secteurs:
    st.info("Choisissez au moins une zone et un secteur sur le tableau de bord.")
    st.stop()

# Le filtre propre à l'axe : une tranche d'expérience, gardé si on change de page
tranche = st.segmented_control(
    "Tranche d'expérience (en années)",
    ["Toutes"] + TRANCHES_EXPERIENCE,
    default="Toutes",
    required=True,
    key="axe2_tranche",
    persist_state="session",
)

df = donnees()
filtre = df[df["Zone"].isin(zones) & df["Secteur"].isin(secteurs)]
qui = f"Développeurs en emploi ({texte_zones(zones)}) ayant répondu à la question"


# Vue 1 : la part en stagnation selon l'expérience
par_experience = part_stagnation_par_experience(filtre)
# sous le seuil, on n'affiche pas de chiffre
assez = par_experience["repondants"] >= SEUIL
par_experience["part_affichee"] = par_experience["part"].where(assez)

if not assez.any():
    st.info("Effectif trop faible : moins de 50 répondants dans chaque tranche avec ces filtres.")
else:
    visibles = par_experience[assez]
    haut = visibles.loc[visibles["part"].idxmax()]
    masquees = par_experience.loc[~assez, "Tranche_experience"].tolist()
    # si des tranches sont cachées, le titre ne parle que de celles qu'on voit
    debut = "Parmi les tranches assez nombreuses, le" if masquees else "Le"
    st.subheader(
        f"{debut} sentiment de stagnation culmine chez les {haut['Tranche_experience']} ans "
        f"d'expérience : {pourcent(haut['part'])} des répondants"
    )

    # la tranche choisie en couleur (ou la plus haute si « Toutes »), le reste en gris
    en_couleur = haut["Tranche_experience"] if tranche == "Toutes" else tranche
    couleurs = [ACCENT if t == en_couleur else GRIS for t in par_experience["Tranche_experience"]]
    etiquettes = [pourcent(p) if ok else "" for p, ok in zip(par_experience["part"], assez)]

    fig = px.bar(
        par_experience,
        x="Tranche_experience",
        y="part_affichee",
        labels={"Tranche_experience": "Années d'expérience", "part_affichee": "Part en stagnation"},
    )
    fig.update_traces(marker_color=couleurs, text=etiquettes, textposition="outside", cliponaxis=False)
    # pas de décor : les valeurs sont écrites sur les barres
    fig.update_yaxes(visible=False, range=[0, haut["part"] * 1.25])
    fig.update_xaxes(type="category")
    # pas de couleur imposée au texte : il suit le thème clair ou sombre
    fig.add_annotation(
        x=haut["Tranche_experience"], y=haut["part"], yshift=32,
        text="le plus haut", showarrow=False,
    )
    fig.update_layout(margin={"t": 40, "b": 0})
    st.plotly_chart(
        fig,
        alt=f"Part en stagnation par tranche d'expérience, la plus haute à {haut['Tranche_experience']} ans",
    )

    if masquees:
        st.caption(f"Moins de {SEUIL} répondants, chiffre non affiché : {', '.join(masquees)} ans.")

st.caption(legende_population(reponses_stagnation(filtre), qui, 2026))
