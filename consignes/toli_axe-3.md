# Toli : harmonisation 2025 / 2026, puis axe 3

Lire d'abord `consignes/commun.md`.

## Partie 1 : harmonisation — peut commencer tout de suite

**Fichier :** `HARMONISATION.md`, à la racine du projet. C'est une exigence du sujet : toute comparaison avec 2025 doit s'appuyer sur une correspondance écrite dans le dépôt.

1. Dans un notebook, charger `charger(2025)` et `charger(2026)`.
2. Pour chaque colonne utilisée par un axe, comparer les réponses possibles des deux années avec `value_counts()`.
3. Écrire un tableau avec : colonne en 2025, colonne en 2026, comparable ou non, ce qu'on fait.
4. Points déjà repérés, à vérifier et à détailler :
   - `JobSat` : de 0 à 10 les deux années, comparable ;
   - `RemoteWork` en 2025 devient `WorkSetting` en 2026, avec les mêmes 5 réponses ;
   - `OrgSize` : mêmes réponses ;
   - `MainBranch` en 2025 devient `CodeMain` en 2026, avec d'autres réponses : écrire la correspondance, pour que la population de 2025 ressemble à celle de 2026 ;
   - `ICorPM` : 2 réponses en 2025, `Individual contributor` et `People manager`, contre 4 en 2026 : proposer un regroupement ;
   - la catégorie ESN de `Industry` n'existe pas en 2025 ;
   - `JobSatComplacent`, `JobEase`, `JobDifficulty`, `LearnAI`, `TechBudget` n'existent qu'en 2026.
5. Commit et push sur `main`, puis prévenir Amine et Paul, qui en ont besoin pour leurs comparaisons.

## Partie 2 : axe 3, ce qui aide et ce qui gêne

**Question pour la DRH :** qu'est-ce qui facilite ou complique le travail au quotidien ?

**Branche :** `axe-3` · **Fichiers :** `notebooks/axe3_ce_qui_gene.ipynb`, `analyse/axe_3.py`, `pages/3_Ce_qui_aide_et_gene.py` · **Relu par :** Gaetan

### Les colonnes et leurs réponses

`JobDifficulty`, ce qui a le plus compliqué le travail, environ 3 350 réponses en France et pays frontaliers :

| Réponse dans les données | Traduction pour l'affichage |
|---|---|
| `Unclear priorities or requirements` | Priorités floues |
| `Inefficient processes, workflows, or coordination` | Organisation inefficace |
| `Not enough time, staffing, or resources` | Manque de temps ou de moyens |
| `Leadership activity or organizational changes` | Changements dans la direction |
| `Nothing has made my job harder in the past 6 months` | Rien n'a compliqué le travail |
| `Unreliable systems, infrastructure, or environments` | Outils peu fiables |
| `Poor documentation or knowledge sharing` | Documentation insuffisante |
| `Lack of support from teammates, managers, or mentors` | Manque de soutien |
| `Lack of access to the right tools or platforms` | Pas les bons outils |
| `I'm not sure` | Ne sait pas |
| `Other, please specify` | Autre |

`JobEase`, ce qui a le plus facilité le travail : mêmes thèmes, à l'endroit, par exemple `Supportive teammates, managers, or mentors` donne « Soutien de l'équipe ».

`JobDifficultyAI_1` à `JobDifficultyAI_10` : pour chaque difficulté, l'IA y a-t-elle joué un rôle ? Le numéro suit l'ordre des difficultés dans le fichier `survey_results_schema.csv`, colonne `sub`. Peu de réponses par difficulté : à garder pour une vue secondaire.

### Les étapes

1. **Explorer** dans le notebook : classement des difficultés, puis satisfaction moyenne selon la difficulté principale.
2. **Créer la branche** `axe-3`.
3. **Écrire `analyse/axe_3.py`** :
   - `classement_difficultes(df)` : part de chaque difficulté et nombre de répondants ;
   - `satisfaction_par_difficulte(df)` : moyenne de `JobSat` selon la difficulté principale ;
   - `classement_aides(df)` : la même chose que la première, pour `JobEase`.
4. **Écrire `pages/3_Ce_qui_aide_et_gene.py`** : un filtre propre à l'axe pour basculer entre « ce qui gêne » et « ce qui aide », puis les vues.
5. **Vérifier**, puis pull request vers `main`, relecteur : Gaetan.

### Le visuel attendu

```
Ce qui aide et ce qui gêne
Filtre : [ Ce qui gêne | Ce qui aide ]

Titre qui affirme, par exemple : « Les priorités floues gênent plus que les outils »
  barres horizontales, de la plus citée à la moins citée, les 3 premières en ACCENT
  légende de population

Vue 2 : satisfaction moyenne selon la difficulté principale
  avec une ligne grise pour la satisfaction moyenne de tous
```

### Les pièges

- Questions nouvelles en 2026 : pas de comparaison avec 2025.
- Certaines difficultés ont moins de 100 réponses : appliquer le seuil de 50 dès qu'on ajoute un filtre.
