# Paul : architecture et tableau de bord, puis axe 5

Lire d'abord `consignes/commun.md`.

## Partie 1 : architecture et tableau de bord

### `ARCHITECTURE.md` — peut commencer tout de suite

C'est le premier document que lit le jury. Il doit contenir quatre parties :

1. **Les fonctionnalités** : tableau de bord, cinq pages d'axe, filtres communs, légende de population.
2. **Pour chaque fonctionnalité, le fichier et la fonction qui la portent**, par exemple : filtre de zone → `app.py` ; population → `analyse/population.py`, `preparer`.
3. **Le trajet des données** : CSV dans `data/` → `charger` → `preparer` → filtres → fonctions de `analyse/axe_X.py` → `pages/X_Nom.py`. Un schéma simple en texte suffit.
4. **Le cache et la session** : `@st.cache_data` garde en mémoire les données préparées, pour ne pas relire le CSV de 120 Mo à chaque clic ; `st.session_state` garde les filtres choisis d'une page à l'autre.

### `app.py` — quand `population.py` partie 2 et `affichage.py` sont poussés

1. `git pull`, et vérifier que `preparer` et `legende_population` existent.
2. Une fonction `donnees()` avec `@st.cache_data` qui renvoie `preparer(charger(2026))`.
3. Dans la barre latérale, deux filtres communs :
   - zone, par défaut France et pays frontaliers, rangé dans `st.session_state["zones"]` ;
   - secteur, par défaut tous, rangé dans `st.session_state["secteurs"]`.
4. En haut de la page, le titre et le message pour la DRH, écrits avec le groupe.
5. Trois chiffres clés avec `st.metric` : satisfaction moyenne, part en stagnation, nombre de répondants.
6. Une ou deux figures qui résument le message, avec la légende de population en dessous.
7. Lancer `streamlit run app.py` et vérifier que les filtres changent bien les chiffres.
8. Commit et push sur `main`, puis prévenir le groupe : c'est le signal de départ des axes.

## Partie 2 : axe 5, télétravail et organisation

**Question pour la DRH :** le mode de travail et le contexte de l'équipe changent-ils la satisfaction ?

**Branche :** `axe-5` · **Fichiers :** `notebooks/axe5_teletravail.ipynb`, `analyse/axe_5.py`, `pages/5_Teletravail.py` · **Relu par :** Amine

### Les colonnes et leurs réponses

`WorkSetting`, environ 3 370 réponses en France et pays frontaliers :

| Réponse dans les données | Traduction |
|---|---|
| `Remote` | Télétravail complet |
| `Hybrid (some remote, leans heavy to in-person)` | Hybride, surtout au bureau |
| `Hybrid (some in-person, leans heavy to flexibility)` | Hybride, surtout à distance |
| `Your choice (very flexible, you can come in when you want or just as needed)` | Au choix |
| `In-person` | Au bureau |

`TechBudget`, l'évolution du budget de l'équipe : `Increased` augmenté, `Stayed the same` stable, `Decreased` baissé, `I don't know` ne sait pas.

`OrgSize`, la taille d'entreprise : de `Just me - I am a freelancer...` à `10,000 or more employees`. Regrouper en quatre tailles au maximum, sinon les groupes sont trop petits.

### Les étapes

1. **Explorer** dans le notebook : satisfaction selon le mode de travail, puis selon le budget. Comparer les écarts entre les deux.
2. **Créer la branche** `axe-5`.
3. **Écrire `analyse/axe_5.py`** :
   - `satisfaction_par_mode(df)` : moyenne de `JobSat` par mode de travail, avec le nombre de répondants ;
   - `satisfaction_par_budget(df)` : la même chose selon `TechBudget` ;
   - `modes_2025_2026(df_2026, df_2025)` : la répartition des modes de travail les deux années, en suivant `HARMONISATION.md`.
4. **Écrire `pages/5_Teletravail.py`** : un filtre propre à l'axe pour la taille d'entreprise, puis les trois vues.
5. **Vérifier**, puis pull request vers `main`, relecteur : Amine.

### Le visuel attendu

```
Télétravail et organisation
Filtre : taille d'entreprise [ toutes | moins de 100 | 100 à 999 | 1 000 et plus ]

Titre qui affirme, par exemple : « Le mode de travail change peu la satisfaction »
  barres de satisfaction par mode de travail, toutes en GRIS
  légende de population

Vue 2 : « Le budget de l'équipe pèse beaucoup plus »
  barres de satisfaction selon le budget, « baissé » et « augmenté » en ACCENT

Vue 3 : les modes de travail en 2025 et en 2026
```

### Les pièges

- `WorkSetting` s'appelle `RemoteWork` en 2025.
- `TechBudget` n'existe qu'en 2026.
- Budget et satisfaction vont ensemble, mais ça ne prouve pas que le budget rend satisfait : une équipe en difficulté peut avoir à la fois un budget en baisse et des gens mécontents.
