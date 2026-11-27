# 2_Stagnation.py
# Axe 2 : le sentiment de stagnation (Saad).
# L'affichage avec Streamlit ; les calculs sont dans analyse/axe_2.py.

import plotly.express as px
import streamlit as st

from analyse.affichage import ACCENT, GRIS, SEUIL, assez_de_reponses, legende_population
from analyse.axe_2 import (
    ORDRE_SECTEURS,
    causes_par_secteur,
    causes_stagnation,
    part_stagnation_par_experience,
    reponses_stagnation,
)
from analyse.chargement import charger
from analyse.population import TRANCHES_EXPERIENCE, preparer

# valeurs par défaut des filtres communs (si la page est ouverte avant le tableau de bord)
ZONES_DEFAUT = ["France", "Pays frontaliers"]
SECTEURS_DEFAUT = ["ESN", "Éditeur de logiciels", "Autre secteur"]

# vue 3 : l'ESN (le secteur de la DRH) en couleur, les autres secteurs en deux gris
COULEURS_SECTEURS = {"ESN": ACCENT, "Éditeur de logiciels": "#8C8C8C", "Autre secteur": GRIS}

PAS_D_EVOLUTION = "Pas de perspective d'évolution"

# les causes dans une phrase, avec leur article
DANS_UNE_PHRASE = {
    "Épuisement": "l'épuisement",
    "Incertitude économique": "l'incertitude économique",
    "L'IA fait les tâches intéressantes": "l'IA qui fait les tâches intéressantes",
    "Pas de perspective d'évolution": "le manque de perspective d'évolution",
    "Autre": "une autre cause",
}


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


def rang(n):
    # 1 -> « 1ʳᵉ », 4 -> « 4ᵉ »
    return "1ʳᵉ" if n == 1 else f"{n}ᵉ"


def sans_decor(fig):
    # pas de décor : les valeurs sont écrites sur les barres, pas besoin d'axe des valeurs
    fig.update_xaxes(visible=False)
    fig.update_yaxes(title=None)
    # marge à droite pour que l'étiquette de la plus longue barre ne soit pas coupée
    fig.update_layout(margin={"t": 10, "b": 0, "l": 0, "r": 50})
    return fig


# même mise en page large que le tableau de bord (app.py)
st.set_page_config(page_title="Stagnation · Garder ses développeurs", layout="wide")

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

df = donnees()
filtre = df[df["Zone"].isin(zones) & df["Secteur"].isin(secteurs)]
reponses = reponses_stagnation(filtre)
qui = f"Développeurs en emploi ({texte_zones(zones)}) ayant répondu à la question"
qui_stagnation = f"Développeurs en emploi ({texte_zones(zones)}) qui se sentent en stagnation"


# Ce que la DRH doit retenir, calculé avec les filtres communs (toutes tranches)
toutes_causes = causes_stagnation(filtre)
if assez_de_reponses(reponses) and len(toutes_causes) >= 2 and toutes_causes["repondants"].iloc[0] >= SEUIL:
    premiere, deuxieme = toutes_causes.iloc[0], toutes_causes.iloc[1]
    message = (
        f"**{pourcent(reponses['En_stagnation'].mean())}** des répondants se sentent en stagnation. "
        f"Les premières causes sont **{DANS_UNE_PHRASE[premiere['Cause']]}** ({pourcent(premiere['part'])}) "
        f"et **{DANS_UNE_PHRASE[deuxieme['Cause']]}** ({pourcent(deuxieme['part'])})"
    )
    evolution = toutes_causes[toutes_causes["Cause"] == PAS_D_EVOLUTION]
    if not evolution.empty:
        position = evolution.index[0] + 1
        message += (
            f" ; le manque de perspective d'évolution n'arrive qu'en {rang(position)} position "
            f"({pourcent(evolution['part'].iloc[0])})."
            if position > 2 else "."
        )
    else:
        message += "."
    st.info(message, title="À retenir pour la DRH", icon=":material/lightbulb:")

# La limite de la question, à toujours afficher
taux = len(reponses) / len(filtre) if len(filtre) else 0
st.warning(
    f"Seules {len(reponses):,} personnes sur {len(filtre):,} ({pourcent(taux)}) ont répondu à cette question. ".replace(",", " ")
    + "Ceux qui se sentent bloqués ont peut-être plus répondu que les autres : la part en stagnation est "
    "peut-être surestimée. Question nouvelle en 2026 : pas de comparaison avec 2025.",
    title="Moins de la moitié des répondants ont répondu" if taux < 0.5 else "Une partie des répondants n'a pas répondu",
    icon=":material/warning:",
)

# Le filtre propre à l'axe : une tranche d'expérience, gardé si on change de page
tranche = st.segmented_control(
    "Tranche d'expérience (en années)",
    ["Toutes"] + TRANCHES_EXPERIENCE,
    default="Toutes",
    required=True,
    key="axe2_tranche",
    persist_state="session",
)
dans_tranche = filtre if tranche == "Toutes" else filtre[filtre["Tranche_experience"] == tranche]
# pour les titres (« chez les 2-3 ans d'expérience ») et les légendes (« , 2-3 ans d'expérience »)
precision = "" if tranche == "Toutes" else f" chez les {tranche} ans d'expérience"
precision_legende = "" if tranche == "Toutes" else f", {tranche} ans d'expérience"


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

st.caption(legende_population(reponses, qui, 2026))


# Vue 2 : les causes, parmi les personnes en stagnation (de la tranche choisie)
en_stagnation = reponses_stagnation(dans_tranche)
en_stagnation = en_stagnation[en_stagnation["En_stagnation"]]
causes = causes_stagnation(dans_tranche)

if not assez_de_reponses(en_stagnation):
    st.info(
        f"Effectif trop faible pour les causes : {len(en_stagnation)} personnes en stagnation{precision_legende} "
        f"(il en faut au moins {SEUIL})."
    )
else:
    premiere = causes.iloc[0]
    st.subheader(
        f"{premiere['Cause']} : la première cause de stagnation, citée par "
        f"{pourcent(premiere['part'])} des personnes concernées{precision}"
    )
    fig = px.bar(
        causes,
        x="part",
        y="Cause",
        orientation="h",
        text=[pourcent(p) for p in causes["part"]],
    )
    # la première cause en couleur, les autres en gris ; la plus citée en haut
    fig.update_traces(
        marker_color=[ACCENT if c == premiere["Cause"] else GRIS for c in causes["Cause"]],
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_yaxes(categoryorder="array", categoryarray=causes["Cause"].tolist()[::-1])
    st.plotly_chart(
        sans_decor(fig),
        alt=f"Causes de stagnation, la première est {DANS_UNE_PHRASE[premiere['Cause']]}",
    )
    st.caption(legende_population(en_stagnation, qui_stagnation + precision_legende, 2026))


# Vue 3 : les causes selon le secteur (de la tranche choisie)
par_secteur = causes_par_secteur(dans_tranche)
# un secteur n'est affiché que s'il a au moins SEUIL personnes en stagnation
secteurs_visibles = [
    s for s in ORDRE_SECTEURS
    if s in par_secteur["Secteur"].astype(str).tolist()
    and par_secteur.loc[par_secteur["Secteur"] == s, "repondants"].iloc[0] >= SEUIL
]
secteurs_caches = [s for s in secteurs if s not in secteurs_visibles]

if len(secteurs_visibles) < 2:
    # il faut au moins deux secteurs assez nombreux pour comparer
    st.info(
        f"Effectif trop faible pour comparer les secteurs{precision} : il faut au moins deux secteurs "
        f"avec {SEUIL} personnes en stagnation ou plus."
    )
else:
    a_tracer = par_secteur[par_secteur["Secteur"].isin(secteurs_visibles)].copy()
    a_tracer["Secteur"] = a_tracer["Secteur"].astype(str)
    if "ESN" in secteurs_visibles:
        esn = a_tracer[a_tracer["Secteur"] == "ESN"].iloc[0]
        cause_esn = DANS_UNE_PHRASE[esn["Cause"]]
        # « aussi » seulement si l'ESN a la même première cause que l'ensemble (vue 2)
        if not causes.empty and esn["Cause"] == causes.iloc[0]["Cause"]:
            titre = f"En ESN aussi, la première cause est {cause_esn} ({pourcent(esn['part'])})"
        else:
            titre = f"En ESN, la première cause est {cause_esn} ({pourcent(esn['part'])})"
    else:
        titre = "Les causes de stagnation selon le secteur"
    st.subheader(titre + precision)

    fig = px.bar(
        a_tracer,
        x="part",
        y="Cause",
        color="Secteur",
        barmode="group",
        orientation="h",
        text=[pourcent(p) for p in a_tracer["part"]],
        color_discrete_map=COULEURS_SECTEURS,
        # Plotly dessine le premier secteur en bas du groupe : on inverse pour avoir l'ESN en haut
        category_orders={"Secteur": secteurs_visibles[::-1]},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    # même ordre des causes que la vue 2
    ordre_causes = causes["Cause"].tolist() if not causes.empty else a_tracer["Cause"].unique().tolist()
    fig.update_yaxes(categoryorder="array", categoryarray=ordre_causes[::-1])
    # la légende garde l'ordre ESN, éditeurs, autres
    fig.update_layout(legend={"title": None, "orientation": "h", "y": -0.05, "traceorder": "reversed"})
    st.plotly_chart(
        sans_decor(fig),
        alt="Causes de stagnation selon le secteur, ESN en couleur",
    )
    if secteurs_caches:
        st.caption(f"Moins de {SEUIL} personnes en stagnation, secteur non affiché : {', '.join(secteurs_caches)}.")
    lignes_visibles = en_stagnation[en_stagnation["Secteur"].isin(secteurs_visibles)]
    st.caption(legende_population(lignes_visibles, qui_stagnation + precision_legende, 2026))
