"""Calculs de l'axe 5, sans Streamlit."""
import pandas as pd

MODES = {
    "Remote": "Télétravail complet",
    "Hybrid (some remote, leans heavy to in-person)": "Hybride, surtout au bureau",
    "Hybrid (some in-person, leans heavy to flexibility)": "Hybride, surtout à distance",
    "Your choice (very flexible, you can come in when you want or just as needed)": "Au choix",
    "In-person": "Au bureau",
}
BUDGETS = {"Increased": "Augmenté", "Stayed the same": "Stable",
           "Decreased": "Baissé", "I don't know": "Ne sait pas"}
TAILLES = ["Moins de 100", "100 à 999", "1 000 et plus"]


def taille_entreprise(df):
    """Regroupe les tailles connues ; les non-réponses restent vides."""
    tailles = df['OrgSize'].astype('string')
    petits = tailles.str.match(r'^Just me\b|^(?:2 to 9|10 to 19|20 to 99) employees$', na=False)
    moyens = tailles.str.match(r'^(?:100 to 499|500 to 999) employees$', na=False)
    grands = tailles.str.match(r'^(?:1,000 to 4,999|5,000 to 9,999|10,000 or more) employees$', na=False)
    resultat = pd.Series(pd.NA, index=df.index, dtype='string')
    for masque, nom in zip([petits, moyens, grands], TAILLES):
        resultat.loc[masque] = nom
    return resultat


def _satisfaction(df, colonne, traductions):
    notes = pd.to_numeric(df['JobSat'], errors='coerce')
    masque = notes.between(0, 10) & df[colonne].isin(traductions)
    valides = pd.DataFrame({'categorie': df.loc[masque, colonne].map(traductions),
                            'JobSat': notes.loc[masque]})
    return (valides.groupby('categorie', sort=False)['JobSat']
            .agg(satisfaction='mean', repondants='size').reset_index())


def satisfaction_par_mode(df):
    return _satisfaction(df, 'WorkSetting', MODES)


def satisfaction_par_budget(df):
    return _satisfaction(df, 'TechBudget', BUDGETS)


def modes_2025_2026(df_2026, df_2025):
    """Parts parmi les réponses valides de chaque année, sans filtrage des petits groupes."""
    tableaux = []
    for annee, df in [(2025, df_2025), (2026, df_2026)]:
        colonne = 'RemoteWork' if annee == 2025 and 'WorkSetting' not in df else 'WorkSetting'
        valeurs = df[colonne].map(MODES).dropna()
        effectifs = valeurs.value_counts().reindex(list(MODES.values()), fill_value=0)
        tableaux.append(pd.DataFrame({'annee': str(annee), 'mode': effectifs.index,
            'repondants': effectifs.to_numpy(),
            'part': 100 * effectifs.to_numpy() / len(valeurs) if len(valeurs) else float('nan')}))
    return pd.concat(tableaux, ignore_index=True)
