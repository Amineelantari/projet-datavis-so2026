# Correspondance entre les enquêtes 2025 et 2026

Le sujet l'exige : toute comparaison entre 2025 et 2026 s'appuie sur ce fichier.
Les chiffres viennent de `notebooks/harmonisation.ipynb`, qui compare les réponses possibles de chaque colonne avec `value_counts()`.

- 2025 : 49 191 réponses, 172 colonnes (`charger(2025)`).
- 2026 : 30 903 réponses, 213 colonnes avec `Annee` (`charger(2026)`).

Il y a beaucoup moins de répondants en 2026. Ce sont des volontaires les deux années : un écart entre 2025 et 2026 peut venir d'un changement dans les personnes qui ont répondu, et pas seulement d'un changement réel.

## Tableau de correspondance

| Colonne 2025 | Colonne 2026 | Comparable ? | Ce qu'on fait |
|---|---|---|---|
| `MainBranch` | `CodeMain` | Avec correspondance | Voir « Population » plus bas |
| `Employment` | `Employment` | Oui | Mêmes 6 réponses. On garde `Employed` et `Independent contractor, freelancer, or self-employed` |
| `Country` | `Country` | Oui | Mêmes noms de pays. Les 7 pays de nos zones sont écrits pareil les deux années. `ajouter_zone` marche sur 2025 sans changement |
| `WorkExp` | `WorkExp` | Oui | Même question, nombre d'années, de 1 à 100 les deux années. `ajouter_tranche_experience` marche sur 2025 sans changement |
| `JobSat` | `JobSat` | Oui | Même échelle de 0 à 10 |
| `RemoteWork` | `WorkSetting` | Oui, après renommage | Mêmes 5 réponses, écrites à l'identique. Renommer `RemoteWork` en `WorkSetting` dans les données 2025 |
| `OrgSize` | `OrgSize` | Oui | Mêmes 9 réponses, écrites à l'identique |
| `ICorPM` | `ICorPM` | Avec regroupement | Voir « Rôle » plus bas |
| `Industry` | `Industry` | Non pour l'ESN | Voir « Secteur » plus bas |
| — | `JobSatComplacent` | Non | N'existe qu'en 2026 : pas de comparaison (axe 2) |
| — | `JobEase`, `JobDifficulty` | Non | N'existent qu'en 2026 : pas de comparaison (axe 3) |
| — | `JobEaseAI_*`, `JobDifficultyAI_*` | Non | N'existent qu'en 2026 |
| — | `LearnAI` | Non | N'existe qu'en 2026 : pas de comparaison (axe 4) |
| — | `TechBudget` | Non | N'existe qu'en 2026 : pas de comparaison (axe 5) |

## Population : `MainBranch` (2025) et `CodeMain` (2026)

La question a changé : en 2025 on demandait si la personne est développeur, en 2026 si elle crée du code dans son travail.

| Réponse 2025 (`MainBranch`) | Réponse 2026 (`CodeMain`) | Dans la population ? |
|---|---|---|
| `I am a developer by profession` | `I create code as a primary part of my job` | Oui |
| `I am not primarily a developer, but I write code sometimes as part of my work/studies` | `I create code occasionally` | Oui |
| `I work with developers or my work supports developers but am not a developer by profession` | `I manage or support people who create code` | Non |
| `I used to be a developer by profession, but no longer am` | `I do not create code` | Non |
| `I am learning to code` | — | Non |
| `I code primarily as a hobby` | — | Non |
| — | `I review/maintain code but rarely create it` | Non |

Pour 2025, la population se définit donc ainsi :

```python
CODENT_2025 = [
    "I am a developer by profession",
    "I am not primarily a developer, but I write code sometimes as part of my work/studies",
]
```

On applique ensuite le même filtre `Employment` qu'en 2026.

Résultat : 37 629 personnes en 2025, dont 1 127 en France et 5 595 en France et pays frontaliers (4 771 ont répondu à `JobSat`).

**Limite :** la correspondance n'est pas parfaite. « Développeur de métier » en 2025 et « crée du code comme partie principale du travail » en 2026 ne recouvrent pas exactement les mêmes personnes. Il faut le dire à chaque comparaison.

## Rôle : `ICorPM`

| Réponse 2026 | Regroupée en | Réponse 2025 |
|---|---|---|
| `Individual contributor` | Développeur | `Individual contributor` |
| `Individual contributor in a senior or staff-level role` | Développeur | `Individual contributor` |
| `People manager` | Manager | `People manager` |
| `Both people manager and individual contributor` | Manager | `People manager` |

On ne compare avec 2025 que ces deux groupes. La distinction « senior » et « les deux » n'existe qu'en 2026 et sert seulement aux vues 2026 de l'axe 4.

**Choix discutable, à valider par Gaetan :** « les deux » est rangé dans Manager, parce que la personne encadre une équipe. On pourrait aussi le laisser à part et ne pas le comparer à 2025.

## Secteur : `Industry`

La liste des secteurs a changé entre les deux années.

- **ESN :** `IT services, consulting, systems integration, or managed services` n'existe qu'en 2026. La réponse la plus proche en 2025 est `Computer Systems Design and Services` (894 réponses), mais elle ne recouvre pas les mêmes entreprises. **Pas de comparaison ESN avec 2025.**
- **Éditeur de logiciels :** `Software Development` (2025) correspond à `Software development` (2026). Seule la majuscule change. La comparaison est possible, mais en 2025 cette catégorie regroupe 16 282 personnes, contre 3 785 en 2026 : une partie des personnes qui travaillent en ESN se rangeaient sans doute là en 2025, faute de mieux. **À éviter, ou à présenter avec cette réserve.**
- Pour comparer 2025 et 2026, on utilise donc **tous les secteurs ensemble**.

## Ce que chaque axe peut comparer avec 2025

| Axe | Comparaison possible avec 2025 |
|---|---|
| 1. Satisfaction | Oui : `JobSat` selon `Tranche_experience`, tous secteurs |
| 2. Stagnation | Non : `JobSatComplacent` n'existe qu'en 2026 |
| 3. Ce qui aide et ce qui gêne | Non : `JobEase` et `JobDifficulty` n'existent qu'en 2026 |
| 4. Évoluer | Seulement pour le rôle, en deux groupes ; pas pour `LearnAI` |
| 5. Télétravail | Oui : `RemoteWork` renommé en `WorkSetting`, et `OrgSize` |
