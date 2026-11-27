# Gaetan : affichage de la population, puis axe 4

Lire d'abord `consignes/commun.md`.

## Partie 1 : affichage — à faire en premier, tout le monde en a besoin

**Fichier :** `analyse/affichage.py`. Pas de Streamlit dans ce fichier : il renvoie du texte, que les pages affichent avec `st.caption`.

1. `git pull`.
2. Écrire en haut du fichier `SEUIL = 50` et les couleurs communes, celles des TP : `GRIS = "#BDBDBD"`, `ACCENT = "#C2410C"`, `ENCRE = "#1A2331"`.
3. Écrire `assez_de_reponses(df)` : renvoie `True` si le tableau a au moins `SEUIL` lignes.
4. Écrire `legende_population(df, qui, annee)` : renvoie une phrase comme « Développeurs en emploi en France et pays frontaliers · 2026 · 3 376 répondants · volontaires, non représentatifs de tous les développeurs ». Le nombre de répondants vient de `len(df)`, écrit avec une espace pour les milliers.
5. Tester dans un notebook sur la population France et pays frontaliers, puis sur un groupe de moins de 50 personnes.
6. Commit et push sur `main`, puis prévenir Paul, qui en a besoin pour `app.py`.

## Partie 2 : axe 4, évoluer : le rôle et la formation

**Question pour la DRH :** les développeurs qui ont pu évoluer sont-ils plus satisfaits, et se sentent-ils moins bloqués ?

**Branche :** `axe-4` · **Fichiers :** `notebooks/axe4_evoluer.ipynb`, `analyse/axe_4.py`, `pages/4_Evoluer.py` · **Relu par :** Paul

### Les colonnes et leurs réponses

`ICorPM`, le rôle, environ 3 360 réponses en France et pays frontaliers :

| Réponse dans les données | Traduction | Effectif |
|---|---|---|
| `Individual contributor` | Développeur | 1 788 |
| `Individual contributor in a senior or staff-level role` | Développeur senior | 1 076 |
| `Both people manager and individual contributor` | Manager qui code | 441 |
| `People manager` | Manager | 55 |

« Manager » seul n'a que 55 personnes : le regrouper avec « Manager qui code ».

`LearnAI`, la formation à l'IA au cours de l'année :

| Réponse dans les données | Traduction |
|---|---|
| `Yes, both on my own and at work` | Seul et au travail |
| `Yes, at work` | Au travail |
| `Yes, on my own` | Seul |
| `No` | Non |

### Les étapes

1. **Explorer** dans le notebook : satisfaction selon le rôle, rôle selon la tranche d'expérience, part en stagnation selon le rôle.
2. **Créer la branche** `axe-4`.
3. **Écrire `analyse/axe_4.py`** :
   - `satisfaction_par_role(df)` : moyenne de `JobSat` et part en stagnation pour chaque rôle, avec le nombre de répondants ;
   - `role_par_experience(df)` : pour chaque tranche d'expérience, la part de développeurs, de seniors et de managers ;
   - `formation_par_role(df)` : pour chaque rôle, la répartition des réponses à `LearnAI`.
4. **Écrire `pages/4_Evoluer.py`** : un filtre propre à l'axe pour choisir les rôles affichés, puis les trois vues.
5. **Vérifier**, puis pull request vers `main`, relecteur : Paul.

### Le visuel attendu

```
Évoluer : le rôle et la formation
Filtre : rôles [x] Développeur [x] Développeur senior [x] Manager

Titre qui affirme, par exemple : « Ceux qui encadrent sont plus satisfaits »
  barres de satisfaction par rôle, managers en ACCENT
  légende de population

Vue 2 : à quel moment devient-on senior ou manager ? barres empilées par tranche d'expérience
Vue 3 : la formation selon le rôle
```

### Les pièges

- Être manager et être satisfait vont ensemble, mais ça ne prouve pas que devenir manager rend satisfait : les managers ont aussi plus d'expérience. Comparer à expérience égale avant de conclure.
- Pour comparer avec 2025, suivre le regroupement d'`ICorPM` écrit dans `HARMONISATION.md`.
