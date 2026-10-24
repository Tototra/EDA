import time
from pathlib import Path
import numpy as np
from common_datasets import make_planted_transactions
from binaps import BinaPs
from donnees import load
from boucle import recommend, play, found_round
from mesures import jaccard, f1, coverage

OUTPUT = Path(__file__).parent / "resultats"
OUTPUT.mkdir(exist_ok=True)

BASE = {"lr": 1e-2, "epochs": 10, "batch": 64, "capacity": 1.0, "alpha": None, "thresh": 0.5}
VARIATIONS = [("pas d'apprentissage", "lr", [1e-3, 1e-2, 5e-2]),
              ("epoques", "epochs", [5, 10, 20]),
              ("taille de lot", "batch", [32, 64, 128]),
              ("neurones (x nombre de films)", "capacity", [0.35, 1.0, 1.75]),
              ("alpha de la perte (None = densite)", "alpha", [None, 0.2, 0.3]),
              ("seuil de lecture", "thresh", [0.2, 0.3, 0.4, 0.5, 0.6, 0.7])]

D, movies, users = load()
synthetic = [make_planted_transactions(noise=0.02, seed=seed) for seed in range(3)]
models = {}


def train(X, settings, seed=0):
    k = round(settings["capacity"] * X.shape[1])
    model = BinaPs(X.shape[1], capacity=k, seed=seed)
    return model.fit(X, settings["epochs"], settings["batch"], settings["lr"], settings["alpha"])


def universes(model, thresh):
    return [sorted(F) for F in set(model.patterns(thresh)) if len(F) >= 4]


def movielens(settings, seed=0):
    key = (settings["lr"], settings["epochs"], settings["batch"], settings["capacity"], settings["alpha"], seed)
    if key not in models:
        start = time.time()
        models[key] = (train(D, settings, seed), time.time() - start)
    return models[key]


def loop(X, P):
    likes_pattern = np.array([coverage(X, F) for F in P]).T
    eligible = np.flatnonzero(likes_pattern.sum(axis=1) >= 3)
    sample = np.random.default_rng(0).choice(eligible, size=min(150, len(eligible)), replace=False)
    sets = [set(F) for F in P]
    found, liked_top = [], []
    for u in sample:
        history = play(P, likes_pattern[u], X.shape[1], np.random.default_rng(u))
        found.append(found_round(history, likes_pattern[u]) is not None)
        liked_top.append(likes_pattern[u][recommend(history[-1][0], sets)].mean())
    return likes_pattern.any(axis=1).mean(), np.mean(found), np.mean(liked_top)


def row(settings):
    model, seconds = movielens(settings)
    P = universes(model, settings["thresh"])
    sizes = [len(F) for F in P] or [0]
    covered = np.any([coverage(D, F) for F in P], axis=0).mean() if P else 0
    soft = np.mean([f1(list(set(train(X, settings, seed).patterns(settings["thresh"]))), truth)[1]
                    for seed, (X, truth) in enumerate(synthetic)])
    return (f"{model.history[-1][0]:.2f} | {len(P)} | {np.median(sizes):.0f} ({max(sizes)}) | "
            f"{len(set().union(*map(set, P))) if P else 0} | {covered:.0%} | {soft:.2f} | {seconds:.1f} s")


lines = ["# Comportement de BinaPs selon les hyperparametres", "",
         "Reglage de reference = code des auteurs (pas 0.01 divise par 10 apres les epoques 5 et 7, 10 epoques, "
         "lots de 64, un neurone par film, alpha = densite) + seuil de lecture 0.5. On fait varier un hyperparametre "
         "a la fois. MovieLens : univers = motifs d'au moins 4 films. Synthetique : 8 motifs caches, bruit 2 %, 3 graines.", "",
         "| hyperparametre | valeur | perte finale | univers | taille mediane (max) | films dans un univers | utilisateurs couverts | F1 soft synthetique | temps |",
         "|---|---|---|---|---|---|---|---|---|"]
for label, key, values in VARIATIONS:
    for value in values:
        settings = dict(BASE, **{key: value})
        lines.append(f"| {label} | {value} | {row(settings)} |")
        print(lines[-1], flush=True)

model, _ = movielens(BASE)
lines += ["", "## Convergence (reglage de reference)", "", "| epoque | perte | motifs (>= 2 films, seuil 0.5) |", "|---|---|---|"]
lines += [f"| {ep + 1} | {loss:.2f} | {n} |" for ep, (loss, n) in enumerate(model.history)]

seeds = [universes(movielens(BASE, seed)[0], 0.5) for seed in range(5)]
shared = [np.mean([max(jaccard(set(F), set(G)) for G in seeds[b]) >= 0.5 for F in seeds[a]])
          for a in range(5) for b in range(5) if a != b]
lines += ["", "## Stabilite selon la graine (reglage de reference)", "",
          f"Part des univers d'une graine retrouves dans une autre (Jaccard >= 0.5) : {np.mean(shared):.0%}", "",
          "| graine | univers | utilisateurs couverts | trouve 3 univers aimes | Pour toi qui plait |", "|---|---|---|---|---|"]
for seed, P in enumerate(seeds):
    covered, found, liked_top = loop(D, P)
    lines.append(f"| {seed} | {len(P)} | {covered:.0%} | {found:.0%} | {liked_top:.0%} |")

lines += ["", "## Pretraitement : seuil de popularite des films", "",
          "Films aimes par au moins une part donnee des utilisateurs ; boucle simulee sur 150 utilisateurs, alpha = 0.3.", "",
          "| seuil | films | univers | taille mediane (max) | utilisateurs couverts | trouve 3 univers aimes | Pour toi qui plait |",
          "|---|---|---|---|---|---|---|"]
for share in [0.10, 0.07, 0.05, 0.03, 0.01]:
    X, _, _ = load(min_share=share)
    P = universes(train(X, BASE), 0.5)
    sizes = [len(F) for F in P]
    covered, found, liked_top = loop(X, P)
    lines.append(f"| {share:.0%} | {X.shape[1]} | {len(P)} | {np.median(sizes):.0f} ({max(sizes)}) | "
                 f"{covered:.0%} | {found:.0%} | {liked_top:.0%} |")
    print(lines[-1], flush=True)

(OUTPUT / "hyperparametres.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
