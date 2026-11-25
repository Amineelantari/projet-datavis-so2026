"""Chargement des données de l'enquête Stack Overflow.

Ce fichier n'utilise pas Streamlit : il télécharge les fichiers bruts
s'ils sont absents, puis les lit avec pandas. La mise en cache est faite
dans l'application (app.py), avec @st.cache_data.
"""
from pathlib import Path
import urllib.request

import pandas as pd

# dossier des données, à la racine du projet (jamais versionné, voir .gitignore)
DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "data"

ADRESSE = "https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive/"
FICHIERS = {
    2026: "2026/survey_results_public.csv",
    2025: "2025/results.csv",
}


def telecharger(annee):
    """Télécharge le fichier de l'année s'il n'est pas déjà dans data/, et renvoie son chemin."""
    chemin = DOSSIER_DONNEES / f"so_{annee}.csv"
    if not chemin.exists():
        DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)
        print(f"Téléchargement des données {annee}...")
        urllib.request.urlretrieve(ADRESSE + FICHIERS[annee], chemin)
    # le lien "raw" de GitHub ne renvoie qu'un petit fichier pointeur : on vérifie qu'on a bien les données
    if chemin.stat().st_size < 1_000_000:
        chemin.unlink()
        raise RuntimeError(f"Le fichier {annee} téléchargé est trop petit : relancez le chargement.")
    return chemin


def charger(annee=2026):
    """Renvoie les réponses de l'année demandée, avec une colonne Annee."""
    donnees = pd.read_csv(telecharger(annee), low_memory=False)
    donnees["Annee"] = annee
    return donnees
