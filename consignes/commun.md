# Ce qui est commun à tous les axes

À lire avant ton fichier de consignes personnel.

## Ce dont tout le monde a besoin

- Le projet installé et à jour : voir la section 2 de `ORGANISATION.md`.
- Les fonctions communes, toutes dans `analyse/` :

| Fonction | Fichier | Ce qu'elle donne |
|---|---|---|
| `charger(annee)` | `chargement.py` | Les réponses brutes de 2026 ou 2025 |
| `preparer(df)` | `population.py` | La population de l'étude, avec `Zone`, `Tranche_experience` et `Secteur` |
| `legende_population(df, qui, annee)` | `affichage.py` | La phrase à mettre sous chaque figure |
| `assez_de_reponses(df)` | `affichage.py` | `True` s'il y a au moins 50 répondants |
| `GRIS`, `ACCENT`, `ENCRE` | `affichage.py` | Les couleurs communes |

- Les filtres communs, créés par Paul dans `app.py` et lus dans chaque page :
  `st.session_state["zones"]` et `st.session_state["secteurs"]`.
  Si la page est ouverte avant le tableau de bord, ces clés n'existent pas encore : prendre alors la valeur par défaut, France et pays frontaliers, tous les secteurs.

## Le déroulé d'un axe, pour tout le monde

1. **Attendre le signal de départ** : `streamlit run app.py` affiche le tableau de bord avec ses filtres. En attendant, faire l'étape 2.
2. **Explorer dans un notebook** `notebooks/axeX_nom.ipynb` : charger `preparer(charger(2026))`, regarder ses colonnes, faire quelques graphiques rapides avec « je remarque / je me demande ». Pousser le notebook.
3. **Créer sa branche** `axe-X` à partir de `main`.
4. **Écrire les calculs** dans `analyse/axe_X.py` : une fonction par vue, qui prend un tableau déjà filtré et renvoie un tableau avec une colonne `repondants`. Pas de Streamlit dans ce fichier.
5. **Tester les calculs** dans le notebook, en important ses fonctions.
6. **Écrire la page** `pages/X_Nom.py` : lire les filtres communs, ajouter ses filtres, appeler ses fonctions, afficher les figures avec la légende de population.
7. **Vérifier** : la page marche avec plusieurs combinaisons de filtres, le message « effectif trop faible » s'affiche quand il faut, chaque titre de figure dit ce qu'il faut retenir.
8. **Ouvrir une pull request** vers `main` et demander la relecture à la personne prévue.

## Les règles des figures

Ce sont les cinq gestes vus en cours :

1. Un titre qui **affirme** le résultat, pas qui décrit le graphique.
2. Du **gris** pour le contexte, une seule couleur, `ACCENT`, pour ce qui compte.
3. Une **annotation** sur le point important.
4. Pas de décor inutile : pas de bordures, valeurs écrites directement sur les barres.
5. La **légende de population** sous la figure : qui, quelle année, combien de répondants.

Et toujours les réponses traduites en français dans les graphiques : jamais `Burnout/tech fatigue` à l'écran, mais « Épuisement ».
