"""Page Streamlit de l'axe 5."""
import pandas as pd
import plotly.express as px
import streamlit as st
from analyse.chargement import charger
from analyse.population import preparer, ajouter_zone, EN_EMPLOI
from analyse.affichage import GRIS, ACCENT, ENCRE, SEUIL, legende_population
from analyse.axe_5 import (MODES, BUDGETS, TAILLES, taille_entreprise,
    satisfaction_par_mode, satisfaction_par_budget, modes_2025_2026)

st.set_page_config(page_title='Télétravail et organisation', layout='wide')
st.title('Télétravail et organisation')
st.write('Le mode de travail et le contexte de l’équipe sont-ils associés à la satisfaction ?')

@st.cache_data
def donnees_2026():
    return preparer(charger(2026))

@st.cache_data
def donnees_2025():
    df = charger(2025)
    codent = ['I am a developer by profession',
              'I am not primarily a developer, but I write code sometimes as part of my work/studies']
    return ajouter_zone(df[df['MainBranch'].isin(codent) & df['Employment'].isin(EN_EMPLOI)].copy()).rename(columns={'RemoteWork': 'WorkSetting'})

secteurs_tous = ['ESN', 'Éditeur de logiciels', 'Autre secteur']
zones = st.session_state.get('zones', ['France', 'Pays frontaliers'])
secteurs = st.session_state.get('secteurs', secteurs_tous)
st.sidebar.caption('Filtres communs : à modifier depuis le tableau de bord.')
st.sidebar.write('Zones : ' + (', '.join(zones) or 'Aucune'))
st.sidebar.write('Secteurs : ' + (', '.join(secteurs) or 'Aucun'))
taille = st.selectbox('Taille d’entreprise', ['Toutes'] + TAILLES, key='axe5_taille')

def filtrer_taille(df):
    return df if taille == 'Toutes' else df[taille_entreprise(df).eq(taille).fillna(False)]

base = donnees_2026()
df = filtrer_taille(base[base['Zone'].isin(zones) & base['Secteur'].isin(secteurs)]).copy()
qui = 'Développeurs en emploi · ' + ', '.join(zones) + ' · ' + ', '.join(secteurs) + ' · Taille : ' + taille


def nombre(v):
    return f'{v:.2f}'.replace('.', ',')


def vue_satisfaction(stats, colonne, traductions, nom, accents=()):
    visibles = stats[stats['repondants'] >= SEUIL].sort_values('satisfaction').copy()
    if visibles.empty:
        st.subheader(nom)
        st.info('Effectif trop faible')
        return None
    bas, haut = visibles.iloc[0], visibles.iloc[-1]
    ecart = haut['satisfaction'] - bas['satisfaction'] if len(visibles) >= 2 else None
    st.subheader(f"{nom} : {haut['categorie']} atteint {nombre(haut['satisfaction'])}/10" +
                 (f" contre {nombre(bas['satisfaction'])}/10 pour {bas['categorie']}" if ecart is not None else ''))
    visibles['etiquette'] = visibles['satisfaction'].map(lambda x: nombre(x) + ' / 10')
    fig = px.bar(visibles, x='satisfaction', y='categorie', orientation='h', text='etiquette',
                 custom_data=['repondants'])
    fig.update_traces(marker_color=[ACCENT if c in accents else GRIS for c in visibles['categorie']],
                      textposition='outside', cliponaxis=False,
                      hovertemplate='%{y}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>')
    fig.update_layout(xaxis=dict(range=[0, 10], title='Satisfaction / 10', showgrid=False),
                      yaxis_title=None, plot_bgcolor='white', paper_bgcolor='white', font_color=ENCRE,
                      margin=dict(l=10,r=85,t=50,b=20))
    if ecart is not None:
        fig.add_annotation(xref='paper', yref='paper', x=1, y=1.12, text=f'Écart maximal : {nombre(ecart)} point(s)', showarrow=False)
    st.plotly_chart(fig, use_container_width=True)
    notes = pd.to_numeric(df['JobSat'], errors='coerce')
    valides = df[notes.between(0, 10) & df[colonne].map(traductions).isin(visibles['categorie'])]
    st.caption(legende_population(valides, qui, 2026))
    st.caption('Seules les catégories ayant au moins 50 réponses valides sont affichées.')
    return ecart

em = vue_satisfaction(satisfaction_par_mode(df), 'WorkSetting', MODES, 'Mode de travail')
eb = vue_satisfaction(satisfaction_par_budget(df), 'TechBudget', BUDGETS, 'Budget de l’équipe', ('Baissé', 'Augmenté'))
if em is not None and eb is not None:
    if eb > em:
        st.write(f'L’écart maximal est plus important selon le budget ({nombre(eb)} points) que selon le mode de travail ({nombre(em)} points).')
    elif em > eb:
        st.write(f'L’écart maximal est plus important selon le mode de travail ({nombre(em)} points) que selon le budget ({nombre(eb)} points).')
    else:
        st.write('Les écarts maximaux observés sont identiques.')
    st.caption('Comparaison descriptive : les répondants aux deux questions peuvent être différents.')

st.header('Évolution des modes de travail : 2025–2026')
if set(secteurs) != set(secteurs_tous):
    st.info('La comparaison 2025–2026 est disponible uniquement tous secteurs confondus : les catégories de secteur ont changé.')
else:
    base25 = donnees_2025()
    df25 = filtrer_taille(base25[base25['Zone'].isin(zones)])
    stats = modes_2025_2026(df, df25)
    # On ne compare que les modes ayant au moins 50 réponses dans les deux années.
    communs = stats[stats['repondants'] >= SEUIL].groupby('mode')['annee'].nunique()
    visibles = stats[stats['mode'].isin(communs[communs == 2].index)].copy()
    if visibles.empty:
        st.info('Effectif trop faible pour comparer les deux années.')
    else:
        pivot = visibles.pivot(index='mode', columns='annee', values='part')
        ecarts = pivot['2026'] - pivot['2025']
        mode = ecarts.abs().idxmax()
        st.subheader(f'{mode} : variation de {ecarts.loc[mode]:+.1f} points entre 2025 et 2026'.replace('.', ','))
        visibles['etiquette'] = visibles['part'].map(lambda x: f'{x:.1f} %'.replace('.', ','))
        fig = px.bar(visibles, x='mode', y='part', color='annee', barmode='group', text='etiquette',
                     custom_data=['repondants'], color_discrete_map={'2025': GRIS, '2026': ACCENT},
                     category_orders={'mode': list(MODES.values()), 'annee': ['2025','2026']},
                     labels={'mode':'Mode de travail','part':'Part (%)','annee':'Année'})
        fig.update_traces(textposition='outside', cliponaxis=False, hovertemplate='%{x}<br>%{text}<br>%{customdata[0]} répondants<extra></extra>')
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_color=ENCRE, yaxis=dict(range=[0,100], showgrid=False))
        fig.add_annotation(xref='paper', yref='paper', x=1,y=1.1,text='Plus forte variation : '+mode,showarrow=False)
        st.plotly_chart(fig, use_container_width=True)
        for annee, source in [(2025,df25),(2026,df)]:
            st.caption(legende_population(source[source['WorkSetting'].isin(MODES)], qui + ' · Dénominateur des parts', annee))
        st.caption('Parts calculées sur toutes les réponses valides de chaque année. Modes affichés : au moins 50 réponses chaque année.')
    st.caption('La population 2025 est définie avec MainBranch, celle de 2026 avec CodeMain : la correspondance est imparfaite et les échantillons peuvent différer.')

st.markdown('**À retenir pour la DRH :** examiner les écarts observés avant de décider où agir. Le budget et le mode de travail peuvent être associés à la satisfaction, mais l’enquête ne prouve pas une causalité et ne mesure pas les départs.')
