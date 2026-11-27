# Architecture de l'application

## 1. Les fonctionnalités

L'application Streamlit aide la DRH d'une ESN lyonnaise à identifier les pistes d'action pour améliorer la satisfaction des développeurs. Elle s'appuie sur les enquêtes Stack Overflow 2026 et, lorsque les questions sont comparables, 2025.

Le tableau de bord présente le message principal, la satisfaction moyenne, la part des répondants qui se sentent stagner, le nombre de répondants et une ou deux figures de synthèse.

Les cinq pages permettent d'approfondir les résultats :

- Axe 1 : la satisfaction au fil de la carrière.
- Axe 2 : le sentiment de stagnation.
- Axe 3 : ce qui aide et ce qui gêne au travail.
- Axe 4 : évoluer, le rôle et la formation.
- Axe 5 : le télétravail et l'organisation.

Les filtres communs portent sur la zone géographique et le secteur. Par défaut, on étudie la France et les pays frontaliers, tous secteurs confondus. Chaque axe peut ajouter ses propres filtres. Une légende sous chaque figure précise la population, l'année et le nombre de répondants. En dessous de 50 réponses valides, le chiffre concerné n'est pas affiché.

## 2. Les fichiers et les fonctions

Le projet sépare les calculs, réalisés avec pandas dans `analyse/`, et l'affichage, réalisé avec Streamlit et Plotly dans `app.py` et `pages/`.

| Fonctionnalité | Fichier | Fonction ou élément |
|---|---|---|
| Téléchargement et lecture des CSV | `analyse/chargement.py` | `telecharger(annee)`, `charger(annee)` |
| Sélection de la population en emploi qui code | `analyse/population.py` | `population_principale(df)` |
| Zones géographiques | `analyse/population.py` | `ajouter_zone(df)` |
| Tranches d'expérience | `analyse/population.py` | `ajouter_tranche_experience(df)` |
| Secteurs d'activité | `analyse/population.py` | `ajouter_secteur(df)` |
| Préparation commune | `analyse/population.py` | `preparer(df)` |
| Chargement préparé et mis en cache | `app.py` | `donnees()` |
| Filtres de zone et de secteur | `app.py` | `st.sidebar.multiselect`, `st.session_state` |
| Tableau de bord et chiffres clés | `app.py` | `st.metric`, figures Plotly |
| Satisfaction et expérience | `analyse/axe_1.py`, `pages/1_Satisfaction.py` | Fonctions de calcul de l'axe 1 et affichage |
| Stagnation | `analyse/axe_2.py`, `pages/2_Stagnation.py` | Fonctions de calcul de l'axe 2 et affichage |
| Difficultés et aides | `analyse/axe_3.py`, `pages/3_Ce_qui_aide_et_gene.py` | Fonctions de calcul de l'axe 3 et affichage |
| Rôle et formation | `analyse/axe_4.py`, `pages/4_Evoluer.py` | Fonctions de calcul de l'axe 4 et affichage |
| Satisfaction selon le mode de travail | `analyse/axe_5.py` | `satisfaction_par_mode(df)` |
| Satisfaction selon le budget | `analyse/axe_5.py` | `satisfaction_par_budget(df)` |
| Comparaison des modes de travail | `analyse/axe_5.py` | `modes_2025_2026(df_2026, df_2025)` |
| Filtre de taille d'entreprise et vues de l'axe 5 | `pages/5_Teletravail.py` | Filtre local et affichage Plotly |
| Légende de population | `analyse/affichage.py` | `legende_population(df, qui, annee)` |
| Seuil d'effectif | `analyse/affichage.py` | `assez_de_reponses(df)`, `SEUIL` |
| Couleurs communes | `analyse/affichage.py` | `GRIS`, `ACCENT`, `ENCRE` |
| Correspondances entre les années | `HARMONISATION.md` | Règles de comparaison 2025-2026 |

Ce tableau décrit l'architecture cible : les noms des fonctions des axes 1 à 4 seront précisés au fur et à mesure de leur développement.

## 3. Le trajet des données

```text
CSV dans data/ (téléchargés si absents)
              |
              v
analyse/chargement.py : charger(2026)
              |
              v
analyse/population.py : preparer(df)
              |
              v
Données préparées (cache)
              |
              v
Filtres communs : zone et secteur
              |
              +--> app.py : chiffres clés et figures de synthèse
              |
              v
Filtres propres à chaque axe
              |
              v
analyse/axe_X.py : calculs et agrégations pandas
              |
              v
pages/X_Nom.py : figures Plotly et affichage Streamlit
              |
              v
Légende de population et limites de l'analyse
```

La fonction `preparer` sélectionne la population puis ajoute `Zone`, `Tranche_experience` et `Secteur`. Les fonctions d'axe reçoivent des données déjà filtrées et renvoient des tableaux agrégés contenant les effectifs `repondants`. Les valeurs manquantes sont exclues des calculs qui nécessitent les réponses correspondantes ; la légende porte sur la population effectivement utilisée.

Les comparaisons avec 2025 utilisent les correspondances de `HARMONISATION.md`. Pour l'axe 5, `RemoteWork` devient `WorkSetting`. Les comparaisons sont effectuées tous secteurs confondus, avec les mêmes zones et tailles d'entreprise. Le budget n'est analysé qu'en 2026.

## 4. Le cache et la session

La fonction `donnees()` utilise `@st.cache_data` pour conserver le résultat de `preparer(charger(2026))`. Ainsi, Streamlit ne relit pas et ne prépare pas le CSV d'environ 120 Mo à chaque interaction. Les filtres sont appliqués après le chargement mis en cache : leur modification ne nécessite pas de relire les données. Les données 2025 peuvent également être mises en cache pour les comparaisons.

Les choix communs sont conservés dans `st.session_state["zones"]` et `st.session_state["secteurs"]`. Les pages lisent ces valeurs pour utiliser la même population que le tableau de bord. Si aucune valeur n'a encore été définie, elles prennent les valeurs par défaut : France et pays frontaliers, tous secteurs. Les choix communs doivent rester disponibles lors de la navigation entre les pages ; les clés des widgets peuvent être distinctes des clés persistantes de session.

Les fichiers CSV ne sont pas versionnés dans Git. Ils sont téléchargés dans `data/` lors du premier chargement.

L'enquête repose sur des volontaires et ne mesure pas directement les départs de l'entreprise. Les résultats décrivent les répondants et des associations entre variables, pas des relations de causalité ni l'ensemble des développeurs.
