"""Axe 3 : ce qui aide et ce qui gêne au travail."""
import plotly.express as px
import streamlit as st

from analyse.chargement import charger
from analyse.population import preparer, TRANCHES_EXPERIENCE
from analyse.affichage import GRIS, ACCENT, ENCRE, SEUIL, assez_de_reponses, legende_population
from analyse.axe_3 import (
    DIFFICULTES, AIDES, REPONSES_NEUTRES,
    classement_difficultes, classement_aides,
    satisfaction_par_difficulte, satisfaction_par_aide, satisfaction_moyenne,
    comparaison_esn,
)

st.set_page_config(page_title="Ce qui aide et ce qui gêne", layout="wide")
st.title("Ce qui aide et ce qui gêne")
st.write("Qu'est-ce qui facilite ou complique le travail des développeurs au quotidien ? "
         "Chaque personne a choisi un seul facteur : celui qui a le plus compté ces 6 derniers mois.")


@st.cache_data
def donnees():
    return preparer(charger(2026))


def format_nombre(valeur, decimales=1):
    # 7.01 -> "7,0"
    return f"{valeur:.{decimales}f}".replace(".", ",")


def mise_en_forme(fig):
    # pas de décor : fond transparent, pas de grille, pas de légende inutile
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font=dict(color=ENCRE),
                      margin=dict(t=20, b=20, l=15, r=15))
    fig.update_xaxes(showgrid=False, showticklabels=False, title=None, zeroline=False)
    fig.update_yaxes(title=None, autorange="reversed")
    return fig


# --- Filtres communs : choisis sur le tableau de bord (app.py) ---
# si la page est ouverte avant le tableau de bord, on prend les valeurs par défaut
zones = st.session_state.get("zones", ["France", "Pays frontaliers"])
secteurs = st.session_state.get("secteurs", ["ESN", "Éditeur de logiciels", "Autre secteur"])
st.caption(f"Filtres communs, à changer sur le tableau de bord · Zones : {', '.join(zones)} · "
           f"Secteurs : {', '.join(secteurs)}")

# --- Filtres propres à l'axe ---
colonne_gauche, colonne_droite = st.columns(2)
sens = colonne_gauche.radio("Afficher", ["Ce qui gêne", "Ce qui aide"], horizontal=True)
tranches = colonne_droite.multiselect("Années d'expérience", TRANCHES_EXPERIENCE,
                                      default=TRANCHES_EXPERIENCE)

if sens == "Ce qui gêne":
    colonne, traductions, verbe = "JobDifficulty", DIFFICULTES, "gêne"
    classer, satisfaction = classement_difficultes, satisfaction_par_difficulte
else:
    colonne, traductions, verbe = "JobEase", AIDES, "aide"
    classer, satisfaction = classement_aides, satisfaction_par_aide

# --- Population ---
base = donnees()
df = base[base["Zone"].isin(zones) & base["Secteur"].isin(secteurs)]
qui = f"Développeurs en emploi · Zones : {', '.join(zones)} · Secteurs : {', '.join(secteurs)}"
# toutes les tranches cochées : on garde aussi ceux qui n'ont pas donné leur expérience
if len(tranches) < len(TRANCHES_EXPERIENCE):
    df = df[df["Tranche_experience"].isin(tranches)]
    qui += f" · Expérience : {', '.join(tranches)} ans"

# seuls ceux qui ont répondu à la question de l'axe comptent
repondu = df[df[colonne].notna()]
if not assez_de_reponses(repondu):
    st.info("Effectif trop faible")
    st.stop()

# --- Vue 1 : le classement ---
classement = classer(repondu)
facteurs = classement[~classement["reponse"].isin(REPONSES_NEUTRES)]
premiers = facteurs["reponse"].head(3).tolist()

st.subheader(f"« {premiers[0]} » et « {premiers[1]} » : ce qui {verbe} le plus")
classement["etiquette"] = classement["part"].map(lambda v: format_nombre(v) + " %")
fig = px.bar(classement, x="part", y="reponse", orientation="h", text="etiquette",
             custom_data=["repondants"])
fig.update_traces(marker_color=[ACCENT if r in premiers else GRIS for r in classement["reponse"]],
                  textposition="outside", cliponaxis=False,
                  hovertemplate="%{y}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>")
haut = facteurs.iloc[0]
fig.add_annotation(x=haut["part"], y=haut["reponse"], xshift=45,
                   text=f"{format_nombre(haut['part'], 0)} % le citent en premier",
                   showarrow=False, xanchor="left", font=dict(color=ACCENT))
st.plotly_chart(mise_en_forme(fig), width="stretch")
st.caption(legende_population(repondu, qui, 2026))
st.caption("En couleur : les 3 facteurs les plus cités. « Rien », « Ne sait pas » et « Autre » restent en gris.")

# --- Vue 2 : la satisfaction selon le facteur principal ---
avec_sat = repondu[repondu["JobSat"].notna()]
resultat = satisfaction(avec_sat)
# en dessous de 50 répondants, on n'affiche pas la moyenne du groupe
affiche = resultat[resultat["repondants"] >= SEUIL].copy()
facteurs_affiches = affiche[~affiche["reponse"].isin(REPONSES_NEUTRES)]

if not assez_de_reponses(avec_sat) or facteurs_affiches.empty:
    st.info("Effectif trop faible pour comparer la satisfaction")
else:
    moyenne = satisfaction_moyenne(avec_sat, colonne)
    if sens == "Ce qui gêne":
        point = facteurs_affiches.iloc[0]  # la satisfaction la plus basse
        st.subheader(f"Ceux que gêne surtout « {point['reponse']} » sont les moins satisfaits "
                     f"({format_nombre(point['satisfaction'])} / 10)")
    else:
        point = facteurs_affiches.iloc[-1]  # la satisfaction la plus haute
        st.subheader(f"Ceux qu'aide surtout « {point['reponse']} » sont les plus satisfaits "
                     f"({format_nombre(point['satisfaction'])} / 10)")

    affiche["etiquette"] = affiche["satisfaction"].map(lambda v: format_nombre(v) + " / 10")
    fig = px.bar(affiche, x="satisfaction", y="reponse", orientation="h", text="etiquette",
                 custom_data=["repondants"])
    fig.update_traces(marker_color=[ACCENT if r == point["reponse"] else GRIS for r in affiche["reponse"]],
                      textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>")
    fig.add_vline(x=moyenne, line_color=GRIS, line_dash="dash")
    fig.add_annotation(x=moyenne, y=1.02, yref="paper", showarrow=False,
                       text=f"Moyenne de tous : {format_nombre(moyenne)}")
    mise_en_forme(fig)
    fig.update_layout(margin=dict(t=40))
    fig.update_xaxes(range=[0, 10.5])
    st.plotly_chart(fig, width="stretch")
    utilises = avec_sat[avec_sat[colonne].map(traductions).isin(affiche["reponse"])]
    st.caption(legende_population(utilises, qui, 2026))
    st.caption("Satisfaction de 0 à 10. Les réponses citées par moins de 50 personnes ne sont pas affichées. "
               "C'est un lien observé, pas une cause.")

# --- Vue 3 : l'ESN comparée aux autres secteurs ---
if "ESN" in secteurs and len(secteurs) > 1:
    comparaison = comparaison_esn(repondu, colonne, traductions)
    totaux = comparaison.groupby("groupe")["total_groupe"].first()
    if (totaux < SEUIL).any():
        st.info("Effectif trop faible pour comparer l'ESN aux autres secteurs")
    else:
        # on garde les 5 facteurs les plus cités par tous
        cinq = facteurs["reponse"].head(5).tolist()
        comparaison = comparaison[comparaison["reponse"].isin(cinq)]
        premier = {g: t[~t["reponse"].isin(REPONSES_NEUTRES)].iloc[0]["reponse"]
                   for g, t in comparaison_esn(repondu, colonne, traductions).groupby("groupe")}
        if premier["ESN"] == premier["Autres secteurs"]:
            st.subheader(f"En ESN comme ailleurs, « {premier['ESN']} » arrive en tête")
        else:
            st.subheader(f"En ESN, « {premier['ESN']} » arrive en tête, "
                         f"contre « {premier['Autres secteurs']} » ailleurs")
        comparaison["etiquette"] = comparaison["part"].map(lambda v: format_nombre(v) + " %")
        fig = px.bar(comparaison, x="part", y="reponse", color="groupe", orientation="h",
                     barmode="group", text="etiquette", custom_data=["repondants"],
                     category_orders={"reponse": cinq, "groupe": ["ESN", "Autres secteurs"]},
                     color_discrete_map={"ESN": ACCENT, "Autres secteurs": GRIS})
        fig.update_traces(textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>")
        mise_en_forme(fig)
        fig.update_yaxes(autorange=None)
        fig.update_layout(showlegend=True, legend=dict(title=None, orientation="h", y=1.08))
        st.plotly_chart(fig, width="stretch")
        st.caption(legende_population(repondu, qui, 2026) +
                   f" · dont {totaux['ESN']} en ESN et {totaux['Autres secteurs']} dans les autres secteurs")
else:
    st.info("Pour comparer l'ESN aux autres secteurs, sélectionnez l'ESN et au moins un autre secteur "
            "sur le tableau de bord.")

# --- Ce que la DRH doit retenir ---
st.markdown("**À retenir pour la DRH :** en France et dans les pays frontaliers, ce qui gêne le plus "
            "les développeurs, c'est l'organisation des missions (priorités floues, organisation "
            "inefficace), bien plus que les outils. Ceux qui manquent de soutien sont les moins satisfaits. "
            "Clarifier les priorités et soutenir les équipes (managers, mentors) passe avant les outils.")
st.caption("Limites : les répondants sont des volontaires, non représentatifs de tous les développeurs. "
           "L'enquête ne mesure pas les départs. Questions nouvelles en 2026 : pas de comparaison avec 2025.")
