# Organisation du projet

Ce fichier explique à chaque membre ce qu'il doit faire, dans quel ordre, et avec quelles règles.
Si tu viens de faire `git pull`, commence par lire ce fichier en entier.
Ensuite, lis `consignes/commun.md`, puis ton fichier personnel dans `consignes/` : il dit étape par étape ce que tu dois faire et ce dont tu as besoin.

| Personne | Consignes |
|---|---|
| Amine | `consignes/amine_axe-1.md` |
| Saad | `consignes/saad_axe-2.md` |
| Toli | `consignes/toli_axe-3.md` |
| Gaetan | `consignes/gaetan_axe-4.md` |
| Paul | `consignes/paul_axe-5.md` |

## 1. Le sujet

**Commanditaire :** la DRH d'une ESN lyonnaise de 3 000 personnes, qui perd trop de développeurs après environ 2 ans.

**Sa décision :** savoir où investir en priorité pour garder ses développeurs : évolution de carrière, organisation du travail, charge de travail, télétravail.

**Message de départ, à vérifier :** après quelques années, les développeurs ont le sentiment de stagner. Pour les garder, il faut leur offrir de quoi évoluer, plus que changer la politique de télétravail.

**Limite à toujours garder en tête :** l'enquête ne demande pas aux gens s'ils vont quitter leur entreprise. On ne mesure donc pas les départs, mais des signaux qui les précèdent souvent : la satisfaction, le sentiment de stagnation, ce qui gêne au travail. Il ne faut jamais écrire « voilà pourquoi ils partent ».

**Données :** enquête Stack Overflow 2026, et 2025 pour certaines comparaisons. Les répondants sont des volontaires : on ne présente jamais une part comme celle de tous les développeurs.

## 2. Installer le projet sur son ordinateur

1. Configurer Git, une seule fois, avec le même e-mail que sur GitHub :

        git config --global user.name "Prénom Nom"
        git config --global user.email "email-du-compte-github"

2. Récupérer le projet :

        cd ~/Documents
        git clone https://github.com/Amineelantari/projet-datavis-so2026.git
        cd projet-datavis-so2026

3. Créer l'environnement et installer les bibliothèques :

        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt

4. Vérifier que tout marche. Le premier lancement télécharge les données dans `data/`, environ 120 Mo :

        python3 -c "from analyse.chargement import charger; print(charger(2026).shape)"

    Résultat attendu : `(30903, 213)`.

À chaque séance : `cd` dans le dossier, `source .venv/bin/activate`, puis `git pull`.

## 3. La population commune

Tout le monde utilise la même population, définie dans `analyse/population.py` :

- les personnes qui codent dans leur travail, souvent ou de temps en temps ;
- qui ont un emploi, salariées ou indépendantes ;
- soit 22 839 personnes en 2026, dont 612 en France.

Colonnes ajoutées pour tous les axes :

| Colonne | Valeurs | Fonction |
|---|---|---|
| `Zone` | France, Pays frontaliers, Reste de l'Europe, Reste du monde, Pays non renseigné | `ajouter_zone` |
| `Tranche_experience` | 0-1, 2-3, 4-6, 7-10, 11-20, 21+ ans d'expérience | `ajouter_tranche_experience` |
| `Secteur` | ESN, Éditeur de logiciels, Autre secteur | `ajouter_secteur` |

Pour avoir les données prêtes : `preparer(charger(2026))`.

**Zone par défaut : France et pays frontaliers ensemble.** La France seule n'a que 612 personnes, et beaucoup de chiffres tombent sous le seuil dès qu'on ajoute un filtre. La France seule reste disponible en option.

## 4. Le socle commun, sur la branche main

| Partie | Fichier | Qui | État |
|---|---|---|---|
| Structure, README, chargement | `README.md`, `analyse/chargement.py` | Amine | fait |
| Population, partie 1 : qui on garde, zones | `analyse/population.py` | Amine | fait |
| Population, partie 2 : expérience, secteur, `preparer` | `analyse/population.py`, à la suite | Saad | à faire |
| Correspondance 2025 / 2026 | `HARMONISATION.md` | Toli | à faire |
| Légende de population sous chaque figure | `analyse/affichage.py` | Gaetan | à faire |
| Architecture, puis tableau de bord | `ARCHITECTURE.md`, `app.py` | Paul | à faire |

### Ce que chaque fichier du socle doit contenir

**Population, partie 2.** Écrire à la suite de la partie 1, sans la modifier :

- `ajouter_tranche_experience(df)` : convertir `WorkExp` en nombre avec `pd.to_numeric(..., errors="coerce")`, puis créer `Tranche_experience` avec `pd.cut` ;
- `ajouter_secteur(df)` : « ESN » pour `IT services, consulting, systems integration, or managed services`, « Éditeur de logiciels » pour `Software development`, « Autre secteur » sinon ;
- `preparer(df)` : appliquer dans l'ordre `population_principale`, `ajouter_zone`, `ajouter_tranche_experience`, `ajouter_secteur`.

Chiffres pour vérifier : 22 839 lignes ; tranches 853, 1 707, 2 628, 3 337, 6 189, 4 757, et 3 368 sans expérience ; en France, 102 personnes en ESN et 112 chez des éditeurs.

**Harmonisation.** Comparer les réponses possibles de chaque colonne utilisée en 2025 et en 2026, et écrire un tableau : colonne 2025, colonne 2026, comparable ou non, ce qu'on fait. Points déjà repérés, à vérifier :

- `JobSat` : même échelle de 0 à 10, comparable ;
- `RemoteWork` en 2025 devient `WorkSetting` en 2026, avec les mêmes 5 réponses ;
- `OrgSize` : mêmes réponses ;
- `MainBranch` en 2025 devient `CodeMain` en 2026, avec d'autres réponses : il faut une correspondance ;
- `ICorPM` : 2 réponses en 2025, 4 en 2026, il faut regrouper ;
- la catégorie ESN de `Industry` n'existe pas en 2025 : pas de comparaison ESN avec 2025 ;
- `JobSatComplacent`, `JobEase`, `JobDifficulty`, `LearnAI`, `TechBudget` n'existent qu'en 2026.

**Affichage.** Pas de Streamlit dans ce fichier, il renvoie du texte :

- `SEUIL = 50` : en dessous de 50 répondants, on n'affiche pas de chiffre ;
- `assez_de_reponses(df)` : renvoie `True` s'il y a au moins `SEUIL` lignes ;
- `legende_population(df, qui, annee)` : renvoie par exemple « Développeurs en emploi en France et pays frontaliers · 2026 · 3 376 répondants · volontaires, non représentatifs de tous les développeurs » ;
- `GRIS`, `ACCENT`, `ENCRE` : les couleurs communes.

**Architecture.** `ARCHITECTURE.md` décrit les fonctionnalités, le fichier et la fonction qui portent chacune, le trajet des données du CSV jusqu'aux pages, ce qui est mis en cache avec `@st.cache_data` et ce qui est gardé dans `st.session_state`.

**Tableau de bord.** `app.py` contient :

- une fonction `donnees()` avec `@st.cache_data` qui renvoie `preparer(charger(2026))` ;
- les filtres communs dans la barre latérale, rangés dans `st.session_state["zones"]` et `st.session_state["secteurs"]` pour être gardés d'une page à l'autre ;
- le message pour la DRH en haut de page ;
- 2 ou 3 chiffres clés avec `st.metric`, une ou deux figures, et la légende de population sous chaque figure.

## 5. Les cinq axes

Chaque axe a deux fichiers :

- `analyse/axe_X.py` : les calculs avec pandas, sans Streamlit. Les fonctions prennent un tableau déjà filtré et renvoient un tableau ;
- `pages/X_Nom.py` : l'affichage avec Streamlit. Il lit les filtres communs dans `st.session_state`, ajoute les filtres propres à l'axe, et affiche `legende_population` sous chaque figure.

Pour chaque axe, il faut au minimum : 2 ou 3 vues, des filtres propres à l'axe, la population sous chaque figure, et une phrase qui dit ce que la DRH doit retenir.

### Axe 1 : la satisfaction au fil de la carrière

- **Responsable :** Amine
- **Branche :** `axe-1` · **Fichiers :** `analyse/axe_1.py`, `pages/1_Satisfaction.py`
- **Question pour la DRH :** à quel moment de la carrière la satisfaction baisse-t-elle ?
- **Colonnes :** `JobSat`, de 0 à 10, et `Tranche_experience`
- **Pistes :** satisfaction moyenne et part de 8 ou plus selon l'expérience, comparaison ESN et éditeurs, comparaison avec 2025 en passant par `HARMONISATION.md`
- **Attention :** les écarts entre tranches sont modestes, il faut toujours montrer le nombre de répondants

### Axe 2 : le sentiment de stagnation

- **Responsable :** Saad
- **Branche :** `axe-2` · **Fichiers :** `analyse/axe_2.py`, `pages/2_Stagnation.py`
- **Question pour la DRH :** qui se sent stagner, à quel moment, et pourquoi ?
- **Colonne :** `JobSatComplacent` : pas de stagnation, épuisement, incertitude économique, IA, manque d'évolution, autre
- **Pistes :** part de personnes en stagnation selon l'expérience, causes principales, causes selon le secteur
- **Attention :** seules 45 % des personnes ont répondu à cette question. Il faut l'écrire, car ceux qui se sentent bloqués ont peut-être plus répondu. Pas de comparaison possible avec 2025.

### Axe 3 : ce qui aide et ce qui gêne

- **Responsable :** Toli
- **Branche :** `axe-3` · **Fichiers :** `analyse/axe_3.py`, `pages/3_Ce_qui_aide_et_gene.py`
- **Question pour la DRH :** qu'est-ce qui facilite ou complique le travail au quotidien ?
- **Colonnes :** `JobEase`, `JobDifficulty`, et `JobEaseAI_1` à `_10`, `JobDifficultyAI_1` à `_10` pour savoir si l'IA y a joué un rôle
- **Pistes :** classement des difficultés, satisfaction selon la difficulté principale, comparaison ESN et autres secteurs
- **Attention :** questions nouvelles en 2026, pas de comparaison avec 2025

### Axe 4 : évoluer, le rôle et la formation

- **Responsable :** Gaetan
- **Branche :** `axe-4` · **Fichiers :** `analyse/axe_4.py`, `pages/4_Evoluer.py`
- **Question pour la DRH :** les développeurs qui ont pu évoluer sont-ils plus satisfaits, et se sentent-ils moins bloqués ?
- **Colonnes :** `ICorPM` : développeur, développeur senior, manager ou les deux ; `LearnAI` : se former seul, au travail, ou non
- **Pistes :** satisfaction selon le rôle, rôle selon l'expérience, formation selon le rôle
- **Pourquoi cet axe :** on a d'abord testé la formation seule, mais elle change à peine la satisfaction. Le rôle montre des écarts plus nets et parle directement d'évolution.

### Axe 5 : télétravail et organisation

- **Responsable :** Paul
- **Branche :** `axe-5` · **Fichiers :** `analyse/axe_5.py`, `pages/5_Teletravail.py`
- **Question pour la DRH :** le mode de travail et le contexte de l'équipe changent-ils la satisfaction ?
- **Colonnes :** `WorkSetting`, `OrgSize`, `TechBudget`
- **Pistes :** répartition des modes de travail, satisfaction selon le mode de travail, satisfaction selon l'évolution du budget, comparaison avec 2025 pour le télétravail
- **Attention :** `WorkSetting` s'appelle `RemoteWork` en 2025, `TechBudget` n'existe qu'en 2026

### Qui relit qui

| Axe | Relu par |
|---|---|
| Axe 1, Amine | Saad |
| Axe 2, Saad | Toli |
| Axe 3, Toli | Gaetan |
| Axe 4, Gaetan | Paul |
| Axe 5, Paul | Amine |

## 6. Les branches

Le socle commun se fait sur `main`. Quand il est fini, c'est-à-dire quand `streamlit run app.py` affiche le tableau de bord, chacun crée sa branche :

    git switch main
    git pull
    git switch -c axe-2
    git push -u origin axe-2

Remplacer `axe-2` par le numéro de son axe. Ensuite :

- travailler et pousser normalement, tout part sur sa branche ;
- récupérer les nouveautés du socle avec `git pull origin main` ;
- quand l'axe marche : sur GitHub, « Compare & pull request », choisir son relecteur, puis fusion dans `main` après relecture ;
- après chaque fusion, tout le monde fait `git switch main` puis `git pull`.

## 7. Le visuel final

L'application a six pages : le tableau de bord, puis une page par axe dans le menu de gauche.

```
┌─────────────────────┬──────────────────────────────────────────────────────┐
│ app                 │  Garder ses développeurs                             │
│ 1 Satisfaction      │  Message pour la DRH, en une ou deux phrases         │
│ 2 Stagnation        │                                                      │
│ 3 Ce qui aide/gêne  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│ 4 Évoluer           │  │ satisfact. │ │ stagnation │ │ répondants │        │
│ 5 Télétravail       │  └────────────┘ └────────────┘ └────────────┘        │
│                     │                                                      │
│ FILTRES COMMUNS     │  Titre qui affirme le résultat principal             │
│ Zone                │  ▇▇▇ ▇▇ ▇▇ ▇▇ ▇▇▇ ▇▇▇▇                                │
│ [x] France          │  Qui · quelle année · combien de répondants          │
│ [x] Pays frontal.   │                                                      │
│ Secteur             │  Limites : volontaires, pas de mesure des départs    │
│ [x] ESN [x] Autres  │                                                      │
└─────────────────────┴──────────────────────────────────────────────────────┘
```

- **Le tableau de bord** donne la réponse à la DRH : le message, trois chiffres clés, une ou deux figures.
- **Chaque page d'axe** donne le détail : ses propres filtres en haut, deux ou trois vues, chacune avec un titre qui affirme et sa légende de population.
- **Les filtres communs** restent les mêmes quand on change de page.
- **Une seule couleur forte**, `ACCENT`, pour ce qui compte ; le reste en `GRIS`. Les réponses du sondage sont toujours traduites en français à l'écran.

## 8. Les règles

1. Toujours `git pull` avant de commencer.
2. On ne touche qu'à ses propres fichiers. Pour modifier le socle, on prévient le groupe avant.
3. Après la fin du socle, on ne travaille plus directement sur `main`.
4. On pousse à la fin de chaque séance, avec un message clair, par exemple « Axe 2 : stagnation selon l'expérience ».
5. On ne met jamais `data/`, `.venv/` ou un fichier CSV dans Git.
6. Chaque figure affiche la population : qui, quelle année, combien de répondants.
7. Toute comparaison avec 2025 passe par `HARMONISATION.md`.
8. Chacun doit pouvoir expliquer son axe et le reste de l'application : à la soutenance, le jury tire une partie au sort et demande une modification en direct.

## Annexe : les commandes Streamlit utiles

| Besoin | Commande |
|---|---|
| Lancer l'application | `streamlit run app.py` |
| Titre de page | `st.title("...")` |
| Texte | `st.write("...")` ou `st.markdown("...")` |
| Filtres dans la barre latérale | `st.sidebar.multiselect(...)`, `st.sidebar.selectbox(...)` |
| Garder un choix d'une page à l'autre | `st.session_state["zones"] = ...` |
| Chiffre clé | `st.metric("Satisfaction moyenne", "6,9 / 10")` |
| Figure Plotly | `st.plotly_chart(fig)` |
| Ligne de population sous une figure | `st.caption(legende_population(df, qui, annee))` |
| Mettre le chargement en cache | `@st.cache_data` au-dessus de la fonction |
| Message si trop peu de réponses | `st.info("Effectif trop faible")` |

Chaque fichier du dossier `pages/` devient automatiquement une page dans le menu de l'application. Le chiffre au début du nom fixe l'ordre.
