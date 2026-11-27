# Saad : population partie 2, puis axe 2

Lire d'abord `consignes/commun.md`.

## Partie 1 : population, partie 2 — à faire en premier, tout le monde en a besoin

**Fichier :** `analyse/population.py`, à la suite de la partie 1 d'Amine. Ne pas utiliser `cat >`, qui effacerait la partie 1 : ouvrir le fichier dans VS Code.

1. `git pull`, puis vérifier que la partie 1 marche :
   `python3 -c "from analyse.chargement import charger; from analyse.population import population_principale, ajouter_zone; print(len(ajouter_zone(population_principale(charger(2026)))))"`
   doit afficher `22839`.
2. Sous `ajouter_zone`, ajouter le titre `# Partie 2 : le profil des personnes et la préparation finale`.
3. Écrire `ajouter_tranche_experience(df)` : `WorkExp` en nombre avec `pd.to_numeric(..., errors="coerce")`, puis `pd.cut` en 0-1, 2-3, 4-6, 7-10, 11-20, 21+, dans une colonne `Tranche_experience`.
4. Écrire `ajouter_secteur(df)` : colonne `Secteur` qui vaut « ESN » pour `IT services, consulting, systems integration, or managed services`, « Éditeur de logiciels » pour `Software development`, « Autre secteur » sinon. Même méthode que `ajouter_zone`.
5. Écrire `preparer(df)` : appliquer dans l'ordre `population_principale`, `ajouter_zone`, `ajouter_tranche_experience`, `ajouter_secteur`.
6. Vérifier : 22 839 lignes ; tranches 853, 1 707, 2 628, 3 337, 6 189, 4 757, et 3 368 sans expérience ; en France, 102 en ESN et 112 chez des éditeurs.
7. `git pull`, puis commit et push sur `main`, puis prévenir le groupe.

## Partie 2 : axe 2, le sentiment de stagnation

**Question pour la DRH :** qui se sent stagner, à quel moment, et pourquoi ?

**Branche :** `axe-2` · **Fichiers :** `notebooks/axe2_stagnation.ipynb`, `analyse/axe_2.py`, `pages/2_Stagnation.py` · **Relu par :** Toli

### La colonne et ses réponses

`JobSatComplacent` : 1 608 réponses en France et pays frontaliers, moins de la moitié de la population.

| Réponse dans les données | Traduction pour l'affichage |
|---|---|
| `I do not feel complacent` | Pas de sentiment de stagnation |
| `Burnout/tech fatigue` | Épuisement |
| `Economic uncertainty making me hesitant to switch roles` | Incertitude économique |
| `AI automating the challenging parts of my job` | L'IA fait les tâches intéressantes |
| `Lack of upward mobility due to corporate tightening` | Pas de perspective d'évolution |
| `Other, please specify` | Autre |

### Les étapes

1. **Explorer** dans le notebook : part de personnes en stagnation, c'est-à-dire toutes les réponses sauf « Pas de sentiment de stagnation », selon l'expérience, puis la répartition des causes.
2. **Créer la branche** `axe-2`.
3. **Écrire `analyse/axe_2.py`** :
   - `part_stagnation_par_experience(df)` : pour chaque tranche, la part en stagnation et le nombre de répondants à la question ;
   - `causes_stagnation(df)` : parmi les personnes en stagnation, la part de chaque cause ;
   - `causes_par_secteur(df)` : les causes, avec les secteurs en colonnes.
4. **Écrire `pages/2_Stagnation.py`** : un filtre propre à l'axe pour choisir une tranche d'expérience, puis les trois vues.
5. **Vérifier**, puis pull request vers `main`, relecteur : Toli.

### Le visuel attendu

```
Le sentiment de stagnation
Filtre : tranche d'expérience [ toutes | 0-1 | 2-3 | ... ]

Titre qui affirme, par exemple : « Dès 2 ans d'expérience, deux sur trois se sentent bloqués »
  courbe ou barres de la part en stagnation par tranche, en ACCENT
  légende de population

Vue 2 : les causes, en barres horizontales, la première en ACCENT
Vue 3 : les causes par secteur
Encadré : « Moins de la moitié des répondants ont répondu à cette question »
```

### Les pièges

- Question nouvelle en 2026 : pas de comparaison avec 2025.
- Moins de la moitié des gens ont répondu. Il faut l'écrire sur la page : ceux qui se sentent bloqués ont peut-être plus répondu, ce qui gonflerait la part en stagnation.
