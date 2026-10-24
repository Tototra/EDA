import json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
FOLDER = ROOT / "data" / "ml-1m"
PATTERNS_FILE = ROOT / "data" / "motifs.json"


def read(name, columns):
    return pd.read_csv(FOLDER / name, sep="::", engine="python", names=columns, encoding="latin-1")


def load(min_rating=4, min_share=0.05):
    ratings = read("ratings.dat", ["user", "movie", "rating", "timestamp"])
    movies = read("movies.dat", ["movie", "title", "genres"])
    users = read("users.dat", ["user", "gender", "age", "occupation", "zip"])

    liked = ratings[ratings.rating >= min_rating]
    n_fans = liked.groupby("movie").user.nunique()
    kept = sorted(n_fans[n_fans >= min_share * len(users)].index)
    liked = liked[liked.movie.isin(kept)]

    row = {u: i for i, u in enumerate(users.user)}
    col = {m: j for j, m in enumerate(kept)}
    D = np.zeros((len(users), len(kept)), dtype=np.int8)
    D[liked.user.map(row).values, liked.movie.map(col).values] = 1

    movies = movies.set_index("movie").loc[kept].reset_index()
    return D, movies, users


def load_patterns(movies):
    output = json.loads(PATTERNS_FILE.read_text())
    col = {m: j for j, m in enumerate(movies.movie)}
    return [[col[m] for m in p] for p in output["patterns"]], output["seconds"]


def name(F, movies):
    genres = [g for g, _ in Counter(g for j in F for g in movies.genres[j].split("|")).most_common(2)]
    years = sorted(int(movies.title[j][-5:-1]) for j in F)
    decade = years[len(years) // 2] // 10 * 10
    return f"{' & '.join(genres)} des années {decade % 100 if decade < 2000 else decade}"
