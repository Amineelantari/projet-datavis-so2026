# Garder ses développeurs : ce que dit l'enquête Stack Overflow 2026

## Le commanditaire

La DRH d'une ESN lyonnaise de 3 000 personnes, qui perd trop de développeurs après 2 ans.
Sa décision : où investir en priorité pour les garder (formation, organisation des missions, télétravail, charge de travail).

## Lancer l'application

    git clone https://github.com/Amineelantari/projet-datavis-so2026.git
    cd projet-datavis-so2026
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    streamlit run app.py

Les données sont téléchargées automatiquement au premier lancement dans `data/` (environ 120 Mo).

## Les axes

1. La satisfaction au fil de la carrière
2. Le sentiment de stagnation
3. Ce qui aide et ce qui gêne
4. Évoluer : le rôle et la formation
5. Télétravail et organisation

## Pour le groupe

Tout est expliqué dans [ORGANISATION.md](ORGANISATION.md) : le rôle de chacun, les axes, les branches et les règles.

## Données

Stack Overflow Developer Survey 2026 (et 2025 pour les comparaisons). Les répondants sont des volontaires : les résultats ne représentent pas tous les développeurs.
