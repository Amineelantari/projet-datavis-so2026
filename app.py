"""Tableau de bord principal de l'étude Stack Overflow 2026."""
import pandas as pd
import plotly.express as px
import streamlit as st

from analyse.chargement import charger
from analyse.affichage import GRIS, ACCENT, ENCRE, SEUIL, assez_de_reponses, legende_population

st.set_page_config(page_title="Garder ses développeurs", layout="wide")
st.title("Garder ses développeurs")

try:
    from analyse.population import preparer
except ImportError:
    st.info("La préparation commune des données (preparer) n'est pas encore disponible.")
    st.stop()


@st.cache_data
def donnees():
    return preparer(charger(2026))


ZONES = ["France", "Pays frontaliers", "Reste de l'Europe", "Reste du monde", "Pays non renseigné"]
SECTEURS = ["ESN", "Éditeur de logiciels", "Autre secteur"]

# Les clés des widgets sont distinctes des clés persistantes de session.
# Streamlit peut supprimer les clés des widgets en changeant de page.
def memoriser(cle):
    st.session_state[cle] = st.session_state["_" + cle].copy()


st.sidebar.header("Filtres communs")
for cle, titre, options, defaut in [
    ("zones", "Zone", ZONES, ZONES[:2]),
    ("secteurs", "Secteur", SECTEURS, SECTEURS),
]:
    st.session_state.setdefault(cle, defaut.copy())
    st.session_state["_" + cle] = st.session_state[cle].copy()
    st.sidebar.multiselect(titre, options, key="_" + cle,
                           on_change=memoriser, args=(cle,))

base = donnees()
df = base[base["Zone"].isin(st.session_state["zones"]) &
          base["Secteur"].isin(st.session_state["secteurs"])].copy()
qui = ("Développeurs en emploi · Zones : " + ", ".join(st.session_state["zones"]) +
       " · Secteurs : " + ", ".join(st.session_state["secteurs"]))

# Message provisoire, à valider avec le groupe après exploration.
st.write("À quel moment de la carrière faut-il agir ? La satisfaction et le sentiment de stagnation permettent d'examiner les pistes d'action pour la DRH.")
if not assez_de_reponses(df):
    st.info("Effectif trop faible")
    st.stop()

# Chaque indicateur utilise uniquement les réponses valides à sa question.
df["JobSat"] = pd.to_numeric(df["JobSat"], errors="coerce")
sat = df[df["JobSat"].between(0, 10)].copy()
stag = df[df["JobSatComplacent"].notna() & df["JobSatComplacent"].astype(str).str.strip().ne("")].copy()
stag["stagnation"] = stag["JobSatComplacent"].ne("I do not feel complacent")


def format_nombre(valeur, decimales=1):
    return f"{valeur:.{decimales}f}".replace(".", ",")


c1, c2, c3 = st.columns(3)
c1.metric("Satisfaction moyenne", format_nombre(sat["JobSat"].mean()) + " / 10" if assez_de_reponses(sat) else "—")
c2.metric("Part en stagnation", format_nombre(100 * stag["stagnation"].mean()) + " %" if assez_de_reponses(stag) else "—")
c3.metric("Nombre de répondants", f"{len(df):,}".replace(",", " "))
c1.caption(f"{len(sat)} réponses valides" if assez_de_reponses(sat) else "Effectif trop faible")
c2.caption(f"{len(stag)} réponses valides ({100 * len(stag) / len(df):.0f} % de la sélection)" if assez_de_reponses(stag) else "Effectif trop faible")
c3.caption("Population après les filtres communs")


def figure_experience(source, colonne, pourcentage=False):
    # On ne montre que les tranches comportant au moins 50 réponses valides.
    source = source.dropna(subset=["Tranche_experience"])
    stats = (source.groupby("Tranche_experience", observed=True, sort=True)[colonne]
             .agg(valeur="mean", repondants="size").reset_index())
    stats = stats[stats["repondants"] >= SEUIL].copy()
    if stats.empty:
        st.info("Effectif trop faible par tranche d'expérience")
        return
    maximum = 100 if pourcentage else 10
    stats["valeur"] *= 100 if pourcentage else 1
    suffixe = " %" if pourcentage else " / 10"
    stats["etiquette"] = stats["valeur"].map(lambda v: format_nombre(v) + suffixe)
    # Titre calculé à partir des données filtrées, pas d'affirmation prédéfinie.
    indice = stats["valeur"].idxmax() if pourcentage else stats["valeur"].idxmin()
    point = stats.loc[indice]
    tranche = str(point["Tranche_experience"])
    titre = ("La stagnation est la plus fréquente" if pourcentage else "La satisfaction est la plus faible")
    st.subheader(f"{titre} dans la tranche {tranche}")
    fig = px.bar(stats, x="Tranche_experience", y="valeur", text="etiquette",
                 custom_data=["repondants"], labels={"Tranche_experience": "Expérience"})
    fig.update_traces(marker_color=[ACCENT if i == indice else GRIS for i in stats.index],
                      textposition="outside", cliponaxis=False,
                      hovertemplate="%{x}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>")
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font=dict(color=ENCRE),
                      margin=dict(t=45, b=20, l=15, r=15),
                      yaxis=dict(range=[0, maximum], showgrid=False, title=None),
                      xaxis=dict(showline=False, title="Années d'expérience"))
    fig.add_annotation(x=point["Tranche_experience"], y=point["valeur"],
                       text="Point à examiner", showarrow=True, ay=-40, ax=0)
    st.plotly_chart(fig, use_container_width=True)
    affichees = source[source["Tranche_experience"].isin(stats["Tranche_experience"])]
    st.caption(legende_population(affichees, qui, 2026))
    st.caption("Les tranches de moins de 50 réponses valides ne sont pas affichées.")


figure_experience(sat, "JobSat")
figure_experience(stag, "stagnation", pourcentage=True)
st.caption("Limites : les réponses sont volontaires. L'enquête ne mesure pas les départs et ne permet pas de conclure à une causalité. La question sur la stagnation n'a pas été renseignée par tous les répondants.")
