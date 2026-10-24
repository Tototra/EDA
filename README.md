# CinéSwipe : analyse interactive de motifs sur MovieLens 1M

BinaPs (extraction différentiable de motifs) + score WPM appris par feedback + une interface web au style des plateformes de streaming.

Le rapport est dans `rapport.typ` (Typst).

## Installation

```bash
cd PROJET
pip install -r requirements.txt
```

Télécharger MovieLens 1M (https://grouplens.org/datasets/movielens/1m/) et le décompresser dans `PROJET/data/`, pour obtenir `data/ml-1m/ratings.dat`, `movies.dat` et `users.dat`. Les données ne sont pas fournies (licence GroupLens).

## Utilisation

Toutes les commandes se lancent depuis `PROJET/`.

```bash
python3 extraire.py          # entraîne BinaPs et écrit motifs.json (41 univers, environ 5 s)
python3 evaluation.py        # écrit resultats/resultats.md et resultats/f1_bruit.png (environ 10 s)
python3 hyperparametres.py   # écrit resultats/hyperparametres.md (environ 2 min)
export TMDB_API_KEY="ta_clé"  # facultatif : affiches des films (clé gratuite sur themoviedb.org)
python3 server.py            # lance CinéSwipe sur http://127.0.0.1:8000
```

Sans clé TMDB, l'appli fonctionne : le titre du film remplace l'affiche.

## Fonctionnement

1. **Extraction** : BinaPs (aligné sur le code officiel des auteurs) apprend des motifs de films aimés ensemble. On garde les films de poids supérieur à 0,5 et les motifs d'au moins 4 films : ce sont les « univers ».
2. **Découvrir** : à chaque tour, 4 univers sont proposés sous forme de rangées d'affiches ; on répond « J'aime », « Pas pour moi » ou rien. Le premier tour montre les 4 univers les plus différents.
3. **Score (WPM)** : chaque film vaut 2^(likes − dislikes), divisé par le plus grand score de film ; un univers vaut le produit des scores de ses films.
4. **Tirage** : les tours suivants tirent les univers avec une probabilité proportionnelle à (1 − α) × score + α × diversité, la diversité étant 1 − Jaccard maximal avec les univers déjà montrés (α = 0,3).
5. **Pour toi** : dès 3 univers aimés, l'appli recommande les 3 univers de meilleur score qui ne partagent aucun film.
6. **Personas** : l'onglet rejoue, tour par tour, la partie d'un des trois spectateurs types.

## Fichiers (dossier PROJET)

| fichier | rôle |
|---|---|
| `donnees.py` | MovieLens → matrice binaire utilisateurs × films aimés (note ≥ 4, films aimés par ≥ 5 % des utilisateurs) ; lecture de `motifs.json` |
| `binaps.py` | BinaPs en NumPy et optimiseur Adam |
| `extraire.py` | entraîne BinaPs et sauvegarde les univers dans `motifs.json` |
| `boucle.py` | boucle interactive : scores WPM, diversité, premier tour, tirage, recommandation, partie simulée |
| `personas.py` | les trois personas (films préférés) et les univers qu'ils aiment |
| `server.py` | serveur Flask de CinéSwipe |
| `web/` | interface CinéSwipe (HTML, CSS, JavaScript) |
| `affiches.py` | affiches via l'API TMDB, mises en cache dans `affiches.json` |
| `evaluation.py` | évaluation : BinaPs sur données synthétiques, statistiques MovieLens, boucle simulée, personas, modèle de préférence tour par tour, traces d'interaction |
| `hyperparametres.py` | comportement de BinaPs selon ses hyperparamètres, stabilité selon la graine, seuil de popularité des films |
| `mesures.py` | mesures communes : Jaccard, F1, couverture, AUC |
| `common_datasets.py` | données synthétiques à motifs cachés (fourni avec les TP) |
| `resultats/` | résultats de l'évaluation |

## Références

- J. Fischer, J. Vreeken. *Differentiable Pattern Set Mining*. KDD 2021, et code officiel (GPL v3).
- F. M. Harper, J. A. Konstan. *The MovieLens Datasets: History and Context*. ACM TiiS 5(4), 2015.
- Affiches : This product uses the TMDB API but is not endorsed or certified by TMDB.
