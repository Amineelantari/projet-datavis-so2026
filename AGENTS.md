# Consignes pour les assistants IA

Ce fichier s'adresse aux assistants IA utilisés par les membres du groupe : Claude, ChatGPT, Copilot ou autre.
Lis aussi `ORGANISATION.md` : il décrit le sujet, la population commune, les cinq axes et les règles Git.

## Le contexte à connaître

- Projet étudiant noté, réalisé en groupe de cinq. Chaque membre porte une partie du socle commun et un axe.
- La note est en partie individuelle. Le jury lit l'historique Git pour voir qui a fait quoi. À la soutenance, chaque membre explique son axe et une partie de l'application tirée au sort, puis le jury demande une modification en direct.
- Le membre avec qui tu travailles doit donc comprendre et pouvoir défendre tout ce qu'il pousse.

## Comment aider

1. Commence par demander au membre son prénom, puis lis `consignes/commun.md` et son fichier `consignes/<prénom>_axe-X.md` : il contient ses étapes, ses colonnes, les réponses exactes à utiliser et le visuel attendu.
2. Avance par petites étapes : une fonction ou une vue à la fois, testée avant de passer à la suite.
3. Explique chaque étape en français simple : ce que fait le code, pourquoi ce choix, ce qu'il faut vérifier dans le résultat.
4. Fais d'abord explorer les données dans un notebook de `notebooks/` avant d'écrire le code de l'application.
5. Ne donne jamais un chiffre de mémoire : calcule-le sur les données, et montre la commande qui le produit.
6. Si un choix d'analyse est discutable, présente les options et laisse le membre décider.
7. Les commits et les `git push` sont faits par le membre lui-même, sous son nom.

## Les conventions du projet à respecter

- Les données se chargent avec `charger(annee)` de `analyse/chargement.py`, puis `preparer(df)` de `analyse/population.py`. Ne jamais télécharger les données autrement, ne jamais les mettre dans Git.
- L'analyse est séparée de l'interface : pas de Streamlit dans `analyse/`. Les fonctions de `analyse/axe_X.py` prennent un tableau filtré et renvoient un tableau.
- L'affichage est dans `pages/X_Nom.py`. Les filtres communs sont lus dans `st.session_state["zones"]` et `st.session_state["secteurs"]`.
- Sous chaque figure : `st.caption(legende_population(df, qui, annee))` depuis `analyse/affichage.py`.
- En dessous de 50 répondants, on n'affiche pas de chiffre : utiliser `assez_de_reponses(df)`.
- Zone par défaut : France et pays frontaliers ensemble.
- Toute comparaison avec 2025 suit `HARMONISATION.md`.
- Les textes en anglais dans le code sont les réponses exactes du sondage : il faut les recopier tels quels.
- Tout ce qui est créé par le groupe est en français : noms de fonctions, colonnes ajoutées, libellés, commentaires.
- Un membre ne modifie que ses propres fichiers. Pour changer le socle commun, il prévient le groupe.

## Les pièges déjà repérés

- L'enquête ne mesure pas les départs : parler de satisfaction et de stagnation, jamais de « raisons de départ ».
- Les répondants sont des volontaires : ne jamais présenter une part comme celle de tous les développeurs.
- `JobSatComplacent` n'a que 45 % de réponses : le signaler dans l'axe 2.
- Plusieurs questions ont changé entre 2025 et 2026 : voir la section harmonisation de `ORGANISATION.md`.
