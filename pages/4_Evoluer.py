# 4_Evoluer.py
# Axe 4 : évoluer, le rôle et la formation (Gaetan).
# L'affichage avec Streamlit ; les calculs sont dans analyse/axe_4.py.

import plotly.express as px
import streamlit as st

from analyse.affichage import ACCENT, GRIS, SEUIL, legende_population
from analyse.axe_4 import (
    ORDRE_FORMATION,
    ORDRE_ROLES,
    ajouter_role,
    formation_par_role,
    role_par_experience,
    satisfaction_par_role,
)
from analyse.chargement import charger
from analyse.population import TRANCHES_EXPERIENCE, preparer

# valeurs par défaut des filtres communs (si la page est ouverte avant le tableau de bord)
ZONES_DEFAUT = ["France", "Pays frontaliers"]
SECTEURS_DEFAUT = ["ESN", "Éditeur de logiciels", "Autre secteur"]

# une couleur par rôle : le gris pour le contexte, ACCENT pour les managers
GRIS_CLAIR = "#E0E0E0"
COULEURS_ROLES = {"Développeur": GRIS, "Développeur senior": GRIS_CLAIR, "Manager": ACCENT}
# le rôle au pluriel, pour les titres
PLURIEL = {"Développeur": "développeurs", "Développeur senior": "développeurs seniors", "Manager": "managers"}


@st.cache_data
def donnees():
    # chargé une seule fois, puis gardé en mémoire
    return preparer(charger(2026))


def virgule(nombre, decimales=1):
    # 6.87 -> « 6,9 »
    return f"{nombre:.{decimales}f}".replace(".", ",")


def pourcent(part):
    # 0.605 -> « 61 % »
    return f"{part * 100:.0f} %"


# Les filtres communs, choisis sur le tableau de bord (app.py)
zones = st.session_state.get("zones", ZONES_DEFAUT)
secteurs = st.session_state.get("secteurs", SECTEURS_DEFAUT)

st.title("Évoluer : le rôle et la formation")
st.write(
    "Les développeurs qui ont pu évoluer, en devenant senior ou manager, "
    "sont-ils plus satisfaits, et se sentent-ils moins bloqués ?"
)
st.caption(f"Filtres du tableau de bord : {', '.join(zones) or 'aucune zone'} · {', '.join(secteurs) or 'aucun secteur'}")

if not zones or not secteurs:
    st.info("Choisissez au moins une zone et un secteur sur le tableau de bord.")
    st.stop()

# Les filtres propres à l'axe
roles = st.multiselect("Rôles affichés", ORDRE_ROLES, default=ORDRE_ROLES, key="axe4_roles")
tranche = st.selectbox(
    "Comparer à expérience égale (années d'expérience)",
    ["Toutes"] + TRANCHES_EXPERIENCE,
    key="axe4_tranche",
)

if not roles:
    st.info("Choisissez au moins un rôle.")
    st.stop()

base = donnees()
# tous_roles : pour calculer les parts sur 100 % de la population, même si on masque un rôle
tous_roles = ajouter_role(base[base["Zone"].isin(zones) & base["Secteur"].isin(secteurs)])
filtre = tous_roles[tous_roles["Role"].isin(roles)]
qui = f"Développeurs en emploi ({', '.join(zones)}) ayant indiqué leur rôle"


# Vue 1 : satisfaction et stagnation selon le rôle
st.header("1. Satisfaction et stagnation selon le rôle")

vue1 = filtre if tranche == "Toutes" else filtre[filtre["Tranche_experience"] == tranche]
if tranche != "Toutes":
    st.caption(f"Seulement les personnes qui ont {tranche} ans d'expérience.")

sat = satisfaction_par_role(vue1)
sat = sat[sat["Role"].isin(roles)]
sat_ok = sat[sat["repondants"] >= SEUIL]

if sat_ok.empty:
    st.info("Effectif trop faible : moins de 50 répondants par rôle avec ces filtres.")
else:
    haut = sat_ok.loc[sat_ok["satisfaction"].idxmax()]
    bas = sat_ok.loc[sat_ok["satisfaction"].idxmin()]
    if len(sat_ok) > 1:
        st.subheader(
            f"Les {PLURIEL[haut['Role']]} sont les plus satisfaits : {virgule(haut['satisfaction'])} / 10, "
            f"contre {virgule(bas['satisfaction'])} pour les {PLURIEL[bas['Role']]}"
        )
    else:
        st.subheader(f"Satisfaction des {PLURIEL[haut['Role']]} : {virgule(haut['satisfaction'])} / 10")

    fig = px.bar(sat_ok, x="Role", y="satisfaction", labels={"Role": "", "satisfaction": "Satisfaction (0 à 10)"})
    fig.update_traces(
        marker_color=[ACCENT if r == haut["Role"] else GRIS for r in sat_ok["Role"]],
        text=[virgule(s) for s in sat_ok["satisfaction"]],
        textposition="outside",
        cliponaxis=False,
    )
    # pas de décor : les valeurs sont écrites sur les barres
    fig.update_yaxes(visible=False, range=[0, 10])
    fig.update_layout(margin={"t": 30, "b": 0})
    st.plotly_chart(fig)
    st.caption(legende_population(vue1[vue1["Role"].isin(sat_ok["Role"])], qui, 2026))

    masques = sat.loc[sat["repondants"] < SEUIL, "Role"].tolist()
    if masques:
        st.caption(f"Moins de {SEUIL} répondants, chiffre non affiché : {', '.join(masques)}.")

    # la stagnation, sur ceux qui ont répondu à la question (moins de la moitié)
    stag_ok = sat[sat["repondants_stagnation"] >= SEUIL]
    if len(stag_ok) > 1:
        ecart = stag_ok["part_stagnation"].max() - stag_ok["part_stagnation"].min()
        if ecart < 0.05:
            st.subheader("Mais tous les rôles se sentent autant en stagnation")
        else:
            plus = stag_ok.loc[stag_ok["part_stagnation"].idxmax()]
            st.subheader(f"La stagnation est la plus forte chez les {PLURIEL[plus['Role']]}")
        colonnes = st.columns(len(stag_ok))
        for colonne, (_, ligne) in zip(colonnes, stag_ok.iterrows()):
            colonne.metric(f"En stagnation : {PLURIEL[ligne['Role']]}", pourcent(ligne["part_stagnation"]))
            colonne.caption(f"{int(ligne['repondants_stagnation'])} répondants à la question")
        st.caption(
            "En stagnation : toute réponse sauf « pas de sentiment de stagnation » (même règle que l'axe 2). "
            "Moins de la moitié des personnes ont répondu à cette question."
        )


# Vue 2 : à quel moment devient-on senior ou manager ?
st.header("2. À quel moment devient-on senior ou manager ?")

rpe = role_par_experience(tous_roles)
rpe = rpe[rpe["Role"].isin(roles) & (rpe["repondants"] >= SEUIL)]

if rpe.empty:
    st.info("Effectif trop faible : moins de 50 répondants par tranche d'expérience avec ces filtres.")
else:
    debut = rpe[rpe["Tranche_experience"] == "2-3"]
    if not debut.empty and "Développeur" in roles:
        part_dev = debut.loc[debut["Role"] == "Développeur", "part"].sum()
        st.subheader(f"À 2-3 ans d'expérience, {pourcent(part_dev)} sont encore simples développeurs")
    else:
        st.subheader("Le passage à senior ou manager arrive tard dans la carrière")

    fig = px.bar(
        rpe,
        x="Tranche_experience",
        y="part",
        color="Role",
        color_discrete_map=COULEURS_ROLES,
        category_orders={"Role": ORDRE_ROLES, "Tranche_experience": TRANCHES_EXPERIENCE},
        labels={"Tranche_experience": "Années d'expérience", "part": "", "Role": ""},
    )
    fig.update_traces(texttemplate="%{y:.0%}", textposition="inside")
    fig.update_yaxes(visible=False)
    fig.update_xaxes(type="category")
    fig.update_layout(barmode="stack", margin={"t": 30, "b": 0}, legend={"orientation": "h", "y": -0.2})
    # l'annotation sur le moment où la DRH perd ses développeurs
    if not debut.empty:
        fig.add_annotation(x="2-3", y=1.04, text="départs vers 2 ans", showarrow=False)
    st.plotly_chart(fig)
    affichees = tous_roles[tous_roles["Tranche_experience"].isin(rpe["Tranche_experience"])]
    st.caption(legende_population(affichees, qui, 2026))
    st.caption("On compare des personnes différentes à un même moment : ce n'est pas le parcours d'une même personne.")


# Vue 3 : la formation à l'IA selon le rôle
st.header("3. La formation à l'IA selon le rôle")

fpr = formation_par_role(tous_roles)
fpr = fpr[fpr["Role"].isin(roles) & (fpr["repondants"] >= SEUIL)]

if fpr.empty:
    st.info("Effectif trop faible : moins de 50 répondants par rôle avec ces filtres.")
else:
    non = fpr[fpr["Formation"] == "Non"]
    moins_forme = non.loc[non["part"].idxmax()]
    st.subheader(
        f"Les {PLURIEL[moins_forme['Role']]} sont les moins formés à l'IA : "
        f"{pourcent(moins_forme['part'])} ne se sont pas formés cette année"
    )

    fig = px.bar(
        fpr,
        x="part",
        y="Role",
        color="Formation",
        orientation="h",
        color_discrete_map={"Non": ACCENT, "Seul": GRIS_CLAIR, "Au travail": GRIS, "Seul et au travail": "#8C8C8C"},
        category_orders={"Formation": ORDRE_FORMATION, "Role": ORDRE_ROLES},
        labels={"part": "", "Role": "", "Formation": ""},
    )
    fig.update_traces(texttemplate="%{x:.0%}", textposition="inside")
    fig.update_xaxes(visible=False)
    fig.update_layout(barmode="stack", margin={"t": 30, "b": 0}, legend={"orientation": "h", "y": -0.2})
    st.plotly_chart(fig)
    st.caption(legende_population(filtre[filtre["LearnAI"].notna()], qui, 2026))
    st.caption(
        "En France et pays frontaliers, la formation seule change peu la satisfaction (de 6,8 à 7,1 / 10 selon la réponse) : "
        "c'est le rôle qui montre les écarts les plus nets."
    )


# Ce que la DRH doit retenir
st.header("Ce que la DRH doit retenir")
st.caption("Conclusion tirée sur la France et les pays frontaliers, tous secteurs (3 376 répondants).")
st.write(
    "Les managers sont plus satisfaits, y compris à expérience égale à partir de 7 ans, "
    "mais ils se sentent autant en stagnation que les autres. Vers 2-3 ans d'expérience, "
    "presque personne n'a encore changé de rôle, et les simples développeurs sont les moins formés. "
    "Ouvrir plus tôt des perspectives d'évolution et de formation est une piste, "
    "sans garantie qu'elle suffise à lever le sentiment de stagnation."
)
st.caption(
    "Limites : les répondants sont des volontaires, l'enquête ne mesure pas les départs, "
    "et une différence entre rôles ne prouve pas que changer de rôle rend plus satisfait."
)
