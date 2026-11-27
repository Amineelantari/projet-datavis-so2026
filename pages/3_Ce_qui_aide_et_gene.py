"""Axe 3 : ce qui aide et ce qui gêne au travail."""
import plotly.express as px
import streamlit as st

from analyse.chargement import charger
from analyse.population import preparer, TRANCHES_EXPERIENCE
from analyse.affichage import GRIS, ACCENT, SEUIL, assez_de_reponses, legende_population
from analyse.axe_3 import (
    DIFFICULTES, AIDES, REPONSES_NEUTRES, HORS_LEVIER,
    classement_difficultes, classement_aides,
    satisfaction_par_difficulte, satisfaction_par_aide, satisfaction_moyenne,
    comparaison_esn, parts_par_levier,
)

st.set_page_config(page_title="Ce qui aide et ce qui gêne", layout="wide")


@st.cache_data
def donnees():
    return preparer(charger(2026))


def format_nombre(valeur, decimales=1):
    # 7.01 -> "7,0"
    return f"{valeur:.{decimales}f}".replace(".", ",")


def format_entier(valeur):
    # 3345 -> "3 345"
    return f"{valeur:,}".replace(",", " ")


def mise_en_forme(fig, hauteur=None):
    # pas de décor : fond transparent, pas de grille, pas de légende inutile
    # pas de couleur de texte imposée : Streamlit prend celle du thème, clair ou sombre
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10),
                      height=hauteur)
    fig.update_xaxes(showgrid=False, showticklabels=False, title=None, zeroline=False)
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig


def barres(tableau, x, y, etiquette, couleurs, hauteur=None):
    # barres horizontales, valeur écrite au bout, nombre de répondants au survol
    fig = px.bar(tableau, x=x, y=y, orientation="h", text=etiquette, custom_data=["repondants"])
    fig.update_traces(marker_color=couleurs,
                      hovertemplate="%{y}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>")
    mise_en_forme(fig, hauteur)
    # on laisse de la place à droite pour que les valeurs écrites ne soient pas coupées
    fig.update_xaxes(range=[0, tableau[x].max() * 1.2])
    return fig


# --- Filtres communs : choisis sur le tableau de bord (app.py) ---
# si la page est ouverte avant le tableau de bord, on prend les valeurs par défaut
zones = st.session_state.get("zones", ["France", "Pays frontaliers"])
secteurs = st.session_state.get("secteurs", ["ESN", "Éditeur de logiciels", "Autre secteur"])

# --- En-tête ---
st.title("Ce qui aide et ce qui gêne")
st.write("Qu'est-ce qui facilite ou complique le travail des développeurs au quotidien ? "
         "Chaque personne a choisi **un seul facteur** : celui qui a le plus compté ces 6 derniers mois.")

# --- Filtres propres à l'axe ---
with st.container(border=True):
    gauche, droite = st.columns([1, 2])
    sens = gauche.segmented_control("Afficher", ["Ce qui gêne", "Ce qui aide"], default="Ce qui gêne",
                                    key="axe3_sens")
    tranches = droite.pills("Années d'expérience", TRANCHES_EXPERIENCE, selection_mode="multi",
                            default=TRANCHES_EXPERIENCE, key="axe3_tranches")
    st.caption(f"Filtres communs, à changer sur le tableau de bord · Zones : {', '.join(zones)} · "
               f"Secteurs : {', '.join(secteurs)}")

# si l'utilisateur désélectionne tout, on revient aux valeurs par défaut
sens = sens or "Ce qui gêne"
tranches = tranches or TRANCHES_EXPERIENCE

if sens == "Ce qui gêne":
    colonne, traductions, verbe, action = "JobDifficulty", DIFFICULTES, "gêne", "complique"
    classer, satisfaction = classement_difficultes, satisfaction_par_difficulte
else:
    colonne, traductions, verbe, action = "JobEase", AIDES, "aide", "facilite"
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

# --- Les calculs (analyse/axe_3.py) ---
classement = classer(repondu)
facteurs = classement[~classement["reponse"].isin(REPONSES_NEUTRES)]
premiers = facteurs["reponse"].head(3).tolist()
leviers = parts_par_levier(repondu, colonne, traductions)
levier_1 = leviers.iloc[0]

avec_sat = repondu[repondu["JobSat"].notna()]
resultat = satisfaction(avec_sat)
# en dessous de 50 répondants, on n'affiche pas la moyenne du groupe
affiche = resultat[resultat["repondants"] >= SEUIL].copy()
facteurs_affiches = affiche[~affiche["reponse"].isin(REPONSES_NEUTRES)]
sat_possible = assez_de_reponses(avec_sat) and not facteurs_affiches.empty
if sat_possible:
    moyenne = satisfaction_moyenne(avec_sat, colonne)
    # ce qui gêne : le groupe le moins satisfait ; ce qui aide : le plus satisfait
    point = facteurs_affiches.iloc[0] if sens == "Ce qui gêne" else facteurs_affiches.iloc[-1]

# --- Chiffres clés ---
st.badge(f"{format_entier(len(repondu))} répondants", icon=":material/group:", color="gray")
c1, c2, c3, c4 = st.columns(4)
# le nom du facteur dans l'intitulé, le chiffre en grand
c1.metric(f"Ce qui {verbe} le plus : {facteurs.iloc[0]['reponse']}",
          f"{format_nombre(facteurs.iloc[0]['part'])} %",
          help="Part des répondants qui citent ce facteur en premier", border=True)
c2.metric(f"Levier n°1 : {levier_1['levier']}", f"{format_nombre(levier_1['part'], 0)} %",
          help="Part des réponses qui relèvent de ce levier de la DRH", border=True)
if sat_possible:
    c3.metric("Satisfaction moyenne", f"{format_nombre(moyenne)} / 10",
              help="De 0 à 10, parmi ceux qui ont répondu à la question de l'axe", border=True)
    c4.metric(("Les moins satisfaits : " if sens == "Ce qui gêne" else "Les plus satisfaits : ")
              + point["reponse"],
              f"{format_nombre(point['satisfaction'])} / 10",
              delta=f"{point['satisfaction'] - moyenne:+.1f} point vs la moyenne".replace(".", ","),
              border=True)
else:
    c3.metric("Satisfaction moyenne", "—", border=True)
    c4.metric("Satisfaction par facteur", "—", help="Effectif trop faible", border=True)

# --- Vue 1 : les leviers de la DRH ---
with st.container(border=True):
    st.subheader(f"« {levier_1['levier']} » regroupe {format_nombre(levier_1['part'], 0)} % "
                 f"de ce qui {action} le travail")
    leviers["etiquette"] = leviers["part"].map(lambda v: format_nombre(v) + " %")
    couleurs = [ACCENT if i == 0 else GRIS for i in leviers.index]
    st.plotly_chart(barres(leviers, "part", "levier", "etiquette", couleurs, hauteur=260),
                    width="stretch")
    st.caption(legende_population(repondu, qui, 2026))
    st.caption(f"Chaque facteur est rangé dans un levier (détail dans « Méthode et limites »). "
               f"« {HORS_LEVIER} » regroupe « Rien », « Ne sait pas » et « Autre ».")

# --- Vues 2 et 3, côte à côte : le détail et la satisfaction ---
gauche, droite = st.columns(2)

with gauche.container(border=True):
    st.subheader(f"Dans le détail : « {premiers[0]} » en tête")
    classement["etiquette"] = classement["part"].map(lambda v: format_nombre(v) + " %")
    couleurs = [ACCENT if r in premiers else GRIS for r in classement["reponse"]]
    st.plotly_chart(barres(classement, "part", "reponse", "etiquette", couleurs, hauteur=420),
                    width="stretch")
    st.caption(legende_population(repondu, qui, 2026))
    st.caption("En couleur : les 3 facteurs les plus cités.")

with droite.container(border=True):
    if not sat_possible:
        st.subheader("Satisfaction selon le facteur principal")
        st.info("Effectif trop faible pour comparer la satisfaction")
    else:
        if sens == "Ce qui gêne":
            st.subheader(f"Ceux que gêne surtout « {point['reponse']} » sont les moins satisfaits")
        else:
            st.subheader(f"Ceux qu'aide surtout « {point['reponse']} » sont les plus satisfaits")
        # chaque barre part de la moyenne de tous : à gauche en dessous, à droite au-dessus
        affiche["ecart"] = affiche["satisfaction"] - moyenne
        affiche["etiquette"] = affiche["satisfaction"].map(format_nombre)
        couleurs = [ACCENT if r == point["reponse"] else GRIS for r in affiche["reponse"]]
        fig = px.bar(affiche, x="ecart", y="reponse", orientation="h", text="etiquette",
                     custom_data=["repondants"])
        fig.update_traces(marker_color=couleurs,
                          hovertemplate="%{y}<br>Satisfaction : %{text} / 10<br>"
                                        "%{customdata[0]} répondants<extra></extra>")
        mise_en_forme(fig, hauteur=420)
        limite = affiche["ecart"].abs().max() * 1.5
        fig.update_xaxes(range=[-limite, limite])
        fig.add_vline(x=0, line_color=GRIS, line_width=1)
        fig.add_annotation(x=0, y=1.05, yref="paper", showarrow=False,
                           text=f"Moyenne de tous : {format_nombre(moyenne)} / 10")
        fig.update_layout(margin=dict(t=30))
        st.plotly_chart(fig, width="stretch")
        utilises = avec_sat[avec_sat[colonne].map(traductions).isin(affiche["reponse"])]
        st.caption(legende_population(utilises, qui, 2026))
        st.caption("Satisfaction moyenne de chaque groupe (de 0 à 10), comparée à la moyenne de tous. "
                   "Les réponses de moins de 50 personnes ne sont pas affichées. "
                   "C'est un lien observé, pas une cause.")

# --- Vue 4 : l'ESN comparée aux autres secteurs ---
with st.container(border=True):
    if "ESN" in secteurs and len(secteurs) > 1:
        comparaison = comparaison_esn(repondu, colonne, traductions)
        totaux = comparaison.groupby("groupe")["total_groupe"].first()
        if (totaux < SEUIL).any():
            st.subheader("L'ESN comparée aux autres secteurs")
            st.info("Effectif trop faible pour comparer l'ESN aux autres secteurs")
        else:
            premier = {g: t[~t["reponse"].isin(REPONSES_NEUTRES)].iloc[0]["reponse"]
                       for g, t in comparaison.groupby("groupe")}
            if premier["ESN"] == premier["Autres secteurs"]:
                st.subheader(f"En ESN comme ailleurs, « {premier['ESN']} » arrive en tête")
            else:
                st.subheader(f"En ESN, « {premier['ESN']} » arrive en tête, "
                             f"contre « {premier['Autres secteurs']} » ailleurs")
            # on garde les 5 facteurs les plus cités par tous
            cinq = facteurs["reponse"].head(5).tolist()
            comparaison = comparaison[comparaison["reponse"].isin(cinq)].copy()
            comparaison["etiquette"] = comparaison["part"].map(lambda v: format_nombre(v) + " %")
            fig = px.bar(comparaison, x="part", y="reponse", color="groupe", orientation="h",
                         barmode="group", text="etiquette", custom_data=["repondants"],
                         category_orders={"reponse": cinq, "groupe": ["ESN", "Autres secteurs"]},
                         color_discrete_map={"ESN": ACCENT, "Autres secteurs": GRIS})
            fig.update_traces(hovertemplate="%{y}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>")
            mise_en_forme(fig, hauteur=380)
            fig.update_yaxes(autorange=None)
            fig.update_layout(showlegend=True, legend=dict(title=None, orientation="h", y=1.1))
            st.plotly_chart(fig, width="stretch")
            st.caption(legende_population(repondu, qui, 2026) +
                       f" · dont {format_entier(totaux['ESN'])} en ESN et "
                       f"{format_entier(totaux['Autres secteurs'])} dans les autres secteurs")
    else:
        st.subheader("L'ESN comparée aux autres secteurs")
        st.info("Pour comparer, sélectionnez l'ESN et au moins un autre secteur sur le tableau de bord.")

# --- Ce que la DRH doit retenir ---
with st.container(border=True):
    st.markdown("#### :material/lightbulb: À retenir pour la DRH")
    st.markdown(
        "- En France et dans les pays frontaliers, **ce qui gêne le plus, c'est l'organisation des missions** "
        "(priorités floues, organisation inefficace) : près de la moitié des réponses, bien plus que les outils.\n"
        "- **Ceux qui manquent de soutien sont les moins satisfaits**, alors que ce qui aide le plus vient "
        "des bons outils et du soutien de l'équipe.\n"
        "- Piste d'action : **clarifier les priorités des missions et accompagner les développeurs** "
        "(managers, mentors) avant d'investir dans de nouveaux outils."
    )

# --- Méthode et limites ---
with st.expander("Méthode et limites"):
    st.markdown(
        "- **Questions :** `JobDifficulty` (ce qui a le plus compliqué le travail) et `JobEase` "
        "(ce qui l'a le plus facilité), un seul choix par personne, sur les 6 derniers mois.\n"
        "- **Leviers :** organisation des missions = priorités, organisation, changements dans la direction ; "
        "charge de travail = temps et moyens ; accompagnement et formation = soutien et documentation ; "
        "outils = outils adaptés et fiables. Le télétravail n'est pas dans ces questions (voir l'axe 5).\n"
        "- **Seuil :** aucun chiffre n'est affiché pour un groupe de moins de 50 répondants.\n"
        "- **Limites :** les répondants sont des volontaires, non représentatifs de tous les développeurs. "
        "L'enquête ne mesure pas les départs. Les liens avec la satisfaction ne sont pas des causes. "
        "Questions nouvelles en 2026 : pas de comparaison avec 2025."
    )
