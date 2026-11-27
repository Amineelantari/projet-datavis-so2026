# Amine : coordination, puis axe 1

Lire d'abord `consignes/commun.md`.

## Partie 1 : coordination du socle

- [x] Structure, README, `chargement.py`, population partie 1, `ORGANISATION.md`
- [ ] Vérifier chaque `git pull` : personne n'a poussé `data/`, `.venv/` ou un CSV
- [ ] Prévenir le groupe quand le socle est prêt : c'est le signal de départ des axes
- [ ] Relire la pull request de Paul, axe 5

## Partie 2 : axe 1, la satisfaction au fil de la carrière

**Question pour la DRH :** à quel moment de la carrière la satisfaction baisse-t-elle ?

**Branche :** `axe-1` · **Fichiers :** `notebooks/axe1_satisfaction.ipynb`, `analyse/axe_1.py`, `pages/1_Satisfaction.py` · **Relu par :** Saad

### Les colonnes

| Colonne | Contenu |
|---|---|
| `JobSat` | Satisfaction de 0 à 10, un nombre |
| `Tranche_experience` | Créée par `preparer` : 0-1, 2-3, 4-6, 7-10, 11-20, 21+ |
| `Secteur` | Créée par `preparer` : ESN, Éditeur de logiciels, Autre secteur |

Environ 3 350 réponses à `JobSat` en France et pays frontaliers.

### Les étapes

1. **Explorer** dans le notebook : satisfaction moyenne par tranche d'expérience, puis la même chose pour les ESN seulement. Noter où se trouve le creux.
2. **Créer la branche** `axe-1`.
3. **Écrire `analyse/axe_1.py`** avec trois fonctions :
   - `satisfaction_par_experience(df)` : pour chaque tranche, la moyenne de `JobSat`, la part de 8 ou plus, et le nombre de répondants ;
   - `satisfaction_par_secteur(df)` : la même chose, avec les tranches en lignes et les secteurs en colonnes ;
   - `comparaison_2025(df_2026, df_2025)` : la moyenne par tranche pour les deux années, en suivant `HARMONISATION.md`. À faire en dernier, quand Toli a fini l'harmonisation.
4. **Écrire `pages/1_Satisfaction.py`** : un filtre propre à l'axe pour choisir l'indicateur, moyenne ou part de 8 ou plus, puis les trois vues.
5. **Vérifier**, puis ouvrir la pull request vers `main`, relecteur : Saad.

### Le visuel attendu

```
Satisfaction au fil de la carrière
Filtre : [ Moyenne sur 10 | Part de 8 ou plus ]

Titre qui affirme, par exemple : « La satisfaction creuse entre 2 et 10 ans d'expérience »
  barres par tranche d'expérience, le creux en ACCENT, le reste en GRIS
  légende de population

Vue 2 : ESN et éditeurs côte à côte, par tranche
Vue 3 : 2025 et 2026, par tranche
```

### Les pièges

- Les écarts entre tranches sont faibles, autour d'un demi-point : toujours afficher le nombre de répondants, et ne pas exagérer dans les titres.
- Les comparaisons avec 2025 ne se font pas par secteur : la catégorie ESN n'existe pas en 2025.
