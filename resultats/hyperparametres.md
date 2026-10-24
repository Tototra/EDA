# Comportement de BinaPs selon les hyperparametres

Reglage de reference = code des auteurs (pas 0.01 divise par 10 apres les epoques 5 et 7, 10 epoques, lots de 64, un neurone par film, alpha = densite) + seuil de lecture 0.5. On fait varier un hyperparametre a la fois. MovieLens : univers = motifs d'au moins 4 films. Synthetique : 8 motifs caches, bruit 2 %, 3 graines.

| hyperparametre | valeur | perte finale | univers | taille mediane (max) | films dans un univers | utilisateurs couverts | F1 soft synthetique | temps |
|---|---|---|---|---|---|---|---|---|
| pas d'apprentissage | 0.001 | 25.75 | 0 | 0 (0) | 0 | 0% | 0.00 | 4.1 s |
| pas d'apprentissage | 0.01 | 23.98 | 41 | 5 (12) | 241 | 70% | 0.86 | 3.8 s |
| pas d'apprentissage | 0.05 | 23.15 | 30 | 6 (14) | 209 | 62% | 0.83 | 3.7 s |
| epoques | 5 | 23.42 | 40 | 5 (11) | 226 | 71% | 0.82 | 1.9 s |
| epoques | 10 | 23.98 | 41 | 5 (12) | 241 | 70% | 0.86 | 3.8 s |
| epoques | 20 | 24.38 | 43 | 5 (12) | 250 | 71% | 0.86 | 7.4 s |
| taille de lot | 32 | 25.29 | 41 | 7 (17) | 302 | 69% | 0.91 | 6.7 s |
| taille de lot | 64 | 23.98 | 41 | 5 (12) | 241 | 70% | 0.86 | 3.8 s |
| taille de lot | 128 | 24.49 | 27 | 6 (12) | 170 | 59% | 0.43 | 2.3 s |
| neurones (x nombre de films) | 0.35 | 25.23 | 40 | 6 (16) | 242 | 70% | 0.82 | 1.4 s |
| neurones (x nombre de films) | 1.0 | 23.98 | 41 | 5 (12) | 241 | 70% | 0.86 | 3.8 s |
| neurones (x nombre de films) | 1.75 | 24.39 | 34 | 6 (19) | 249 | 67% | 0.88 | 6.9 s |
| alpha de la perte (None = densite) | None | 23.98 | 41 | 5 (12) | 241 | 70% | 0.86 | 3.8 s |
| alpha de la perte (None = densite) | 0.2 | 31.89 | 20 | 5 (8) | 106 | 68% | 0.88 | 3.8 s |
| alpha de la perte (None = densite) | 0.3 | 34.70 | 3 | 4 (6) | 14 | 23% | 0.81 | 3.7 s |
| seuil de lecture | 0.2 | 23.98 | 75 | 12 (34) | 547 | 69% | 0.68 | 3.8 s |
| seuil de lecture | 0.3 | 23.98 | 68 | 10 (24) | 506 | 66% | 0.82 | 3.8 s |
| seuil de lecture | 0.4 | 23.98 | 60 | 8 (18) | 407 | 68% | 0.86 | 3.8 s |
| seuil de lecture | 0.5 | 23.98 | 41 | 5 (12) | 241 | 70% | 0.86 | 3.8 s |
| seuil de lecture | 0.6 | 23.98 | 19 | 5 (8) | 98 | 59% | 0.81 | 3.8 s |
| seuil de lecture | 0.7 | 23.98 | 6 | 4 (6) | 27 | 43% | 0.61 | 3.8 s |

## Convergence (reglage de reference)

| epoque | perte | motifs (>= 2 films, seuil 0.5) |
|---|---|---|
| 1 | 26.07 | 3 |
| 2 | 24.36 | 28 |
| 3 | 24.07 | 41 |
| 4 | 23.81 | 47 |
| 5 | 23.42 | 56 |
| 6 | 23.51 | 58 |
| 7 | 23.54 | 58 |
| 8 | 23.72 | 58 |
| 9 | 23.93 | 58 |
| 10 | 23.98 | 58 |

## Stabilite selon la graine (reglage de reference)

Part des univers d'une graine retrouves dans une autre (Jaccard >= 0.5) : 33%

| graine | univers | utilisateurs couverts | trouve 3 univers aimes | Pour toi qui plait |
|---|---|---|---|---|
| 0 | 41 | 70% | 67% | 86% |
| 1 | 45 | 71% | 67% | 85% |
| 2 | 44 | 69% | 63% | 83% |
| 3 | 39 | 69% | 66% | 85% |
| 4 | 49 | 73% | 62% | 81% |

## Pretraitement : seuil de popularite des films

Films aimes par au moins une part donnee des utilisateurs ; boucle simulee sur 150 utilisateurs, alpha = 0.3.

| seuil | films | univers | taille mediane (max) | utilisateurs couverts | trouve 3 univers aimes | Pour toi qui plait |
|---|---|---|---|---|---|---|
| 10% | 231 | 13 | 5 (10) | 63% | 100% | 100% |
| 7% | 390 | 26 | 6 (10) | 70% | 95% | 99% |
| 5% | 572 | 41 | 5 (12) | 70% | 67% | 86% |
| 3% | 887 | 51 | 7 (14) | 65% | 49% | 74% |
| 1% | 1634 | 66 | 9 (25) | 51% | 43% | 58% |
