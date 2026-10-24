from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from common_datasets import make_planted_transactions
from binaps import BinaPs
from donnees import load, load_patterns, name
from boucle import recommend, play, found_round
from mesures import jaccard, f1, coverage, auc
from personas import PERSONAS, liked_patterns

OUTPUT = Path(__file__).parent.parent / "resultats"
OUTPUT.mkdir(exist_ok=True)

lines = ["# Resultats", "", "## 1. BinaPs sur donnees synthetiques (8 motifs plantes, 3 graines, seuil 0.5)", "",
         "| bruit | STE | motifs trouves | F1 exact | F1 soft |", "|---|---|---|---|---|"]
noises = [0, 0.01, 0.02, 0.03, 0.05]
plt.figure(figsize=(5, 3.5))
for gated in [True, False]:
    curve = []
    for noise in noises:
        results = []
        for seed in range(3):
            X, truth = make_planted_transactions(noise=noise, seed=seed)
            found = list(set(BinaPs(X.shape[1], seed=seed, gated_ste=gated).fit(X).patterns()))
            results.append((len(found), *f1(found, truth)))
        n, f1_exact, f1_soft = np.mean(results, axis=0)
        curve.append(f1_soft)
        lines.append(f"| {noise} | {'gated' if gated else 'simple'} | {n:.1f} | {f1_exact:.2f} | {f1_soft:.2f} |")
    plt.plot(noises, curve, marker="o", label="STE gated" if gated else "STE simple")
plt.xlabel("bruit (part des cases inversees)")
plt.ylabel("F1 soft")
plt.ylim(0, 1)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT / "f1_bruit.png", dpi=130)

D, movies, users = load()
patterns, seconds = load_patterns(movies)
sets = [set(F) for F in patterns]
fans = D.sum(axis=0)
sizes = np.array([len(F) for F in patterns])
frequency = np.array([coverage(D, F).mean() for F in patterns])
covered = np.any([coverage(D, F) for F in patterns], axis=0)
redundancy = np.mean([jaccard(sets[i], b) for i in range(len(sets)) for b in sets[i + 1:]])
lines += ["", "## 2. BinaPs sur MovieLens", "",
          f"- donnees : {D.shape[0]} utilisateurs x {D.shape[1]} films, densite {D.mean():.3f}",
          f"- temps d'entrainement : {seconds:.1f} s",
          f"- nombre de motifs : {len(patterns)} (capacite {D.shape[1]})",
          f"- taille des motifs : min {sizes.min()}, mediane {np.median(sizes):.0f}, max {sizes.max()}",
          f"- frequence (au moins la moitie des films aimes) : mediane {np.median(frequency):.3f}, max {frequency.max():.3f}",
          f"- redondance (Jaccard moyen entre motifs) : {redundancy:.3f}",
          f"- utilisateurs couverts par au moins un motif : {covered.mean():.1%}"]

likes_pattern = np.array([coverage(D, F) for F in patterns]).T
eligible = np.flatnonzero(likes_pattern.sum(axis=1) >= 3)
sample = np.random.default_rng(0).choice(eligible, size=200, replace=False)


def summary(history, liked):
    s, shown = history[-1]
    unseen = [i for i in np.argsort(-s) if i not in shown][:3]
    return found_round(history, liked), liked[recommend(s, sets)].mean(), liked[unseen].mean()


lines += ["", "## 3. Boucle interactive (utilisateurs simules)", "",
          f"Un utilisateur MovieLens simule aime un univers s'il aime au moins la moitie de ses films. "
          f"{len(eligible)} utilisateurs en aiment au moins 3 ; on en tire 200. 6 tours de 4 univers.", "",
          "| methode | trouve 3 univers aimes | tours necessaires (moyenne) | Pour toi qui plait | 3 univers jamais vus qui plaisent |",
          "|---|---|---|---|---|"]
for method, alpha, uniform in [("boucle, alpha = 0", 0, False), ("boucle, alpha = 0.3 (appli)", 0.3, False),
                               ("boucle, alpha = 1 (diversite seule)", 1, False), ("tirage au hasard", 0, True)]:
    runs = [summary(play(patterns, likes_pattern[u], D.shape[1], np.random.default_rng(u), alpha, uniform=uniform),
                    likes_pattern[u]) for u in sample]
    found = [r[0] for r in runs if r[0]]
    lines.append(f"| {method} | {len(found) / len(runs):.0%} | {np.mean(found):.1f} | "
                 f"{np.mean([r[1] for r in runs]):.0%} | {np.mean([r[2] for r in runs]):.0%} |")
popular = np.argsort(-frequency)[:3]
lines.append(f"| 3 univers les plus populaires, sans interaction | - | - | {likes_pattern[sample][:, popular].mean():.0%} | - |")
lines.append(f"| 3 univers au hasard | - | - | {likes_pattern[sample].mean():.0%} | - |")

lines += ["", "## 4. Personas (20 parties chacun, alpha = 0.3 comme dans l'appli)", "",
          "Un persona aime un univers si au moins la moitie de ses films font partie de ses films preferes.", "",
          "| persona | univers aimes sur " + str(len(patterns)) + " | trouve 3 univers aimes | tours necessaires | Pour toi qui plait |",
          "|---|---|---|---|---|"]
examples = []
for persona, words in PERSONAS.items():
    liked = liked_patterns(words, movies, patterns)
    histories = [play(patterns, liked, D.shape[1], np.random.default_rng(seed)) for seed in range(20)]
    runs = [summary(h, liked) for h in histories]
    found = [r[0] for r in runs if r[0]]
    lines.append(f"| {persona} | {liked.sum()} | {len(found) / len(runs):.0%} | {np.mean(found) if found else 0:.1f} | "
                 f"{np.mean([r[1] for r in runs]):.0%} |")
    top = recommend(histories[0][-1][0], sets)
    examples.append(f"- {persona} : " + " / ".join(", ".join(movies.title[j] for j in patterns[i][:3]) for i in top))
lines += ["", "Pour toi de la premiere partie de chaque persona :", ""] + examples

lines += ["", "## 5. Le modele de preference capture-t-il les gouts ?", "",
          "Memes 200 utilisateurs, alpha = 0.3. Apres chaque tour, on compare le score WPM des univers a ce que "
          "l'utilisateur aime vraiment dans MovieLens. AUC = probabilite qu'un univers aime ait un meilleur score "
          "qu'un univers non aime (0.5 = hasard, 1 = parfait).", "",
          "| tour | AUC univers montres | AUC univers jamais vus : WPM | jamais vus : popularite | jamais vus : petite taille d'abord | jamais vus partageant un film avec un univers montre |",
          "|---|---|---|---|---|---|"]
per_round = [[] for _ in range(6)]
for u in sample:
    liked = likes_pattern[u]
    for t, (s, shown) in enumerate(play(patterns, liked, D.shape[1], np.random.default_rng(u))):
        unseen = np.array([i for i in range(len(patterns)) if i not in shown])
        linked = np.mean([any(sets[i] & sets[j] for j in shown) for i in unseen])
        per_round[t].append((auc(s[shown], liked[shown]), auc(s[unseen], liked[unseen]),
                             auc(frequency[unseen], liked[unseen]), auc(-sizes[unseen], liked[unseen]), linked))
for t, values in enumerate(per_round):
    m = np.nanmean(values, axis=0)
    lines.append(f"| {t + 1} | {m[0]:.2f} | {m[1]:.2f} | {m[2]:.2f} | {m[3]:.2f} | {m[4]:.0%} |")


def label(i):
    best = sorted(patterns[i], key=lambda j: -fans[j])[:2]
    return f"{name(patterns[i], movies)} ({', '.join(movies.title[j][:-7] for j in best)})"


lines += ["", "## 6. Traces d'interaction (utilisateurs reels, alpha = 0.3)", ""]
games = {u: play(patterns, likes_pattern[u], D.shape[1], np.random.default_rng(u)) for u in sample}
quick = [u for u in sample if found_round(games[u], likes_pattern[u]) == 2]
slow = [u for u in sample if found_round(games[u], likes_pattern[u]) is None]
for u in [quick[0], slow[0]]:
    liked = likes_pattern[u]
    history = games[u]
    lines += [f"### Utilisateur {users.user[u]} ({D[u].sum()} films aimes, {liked.sum()} univers aimes)", "",
              "Univers qu'il aime d'apres MovieLens : " + " ; ".join(label(i) for i in np.flatnonzero(liked)), ""]
    for t, (s, shown) in enumerate(history):
        before = history[t - 1][1] if t > 0 else []
        answers = ", ".join(f"{label(i)} {'+' if liked[i] else '-'}" for i in shown[len(before):])
        unseen = [i for i in np.argsort(-s) if i not in shown][:3]
        guesses = ", ".join(f"{label(i)} [{D[u, patterns[i]].sum()}/{len(patterns[i])} films aimes]" for i in unseen)
        lines += [f"- tour {t + 1} : {answers}", f"  - meilleurs scores parmi les jamais vus : {guesses}"]
    lines += ["- Pour toi : " + " ; ".join(f"{label(i)} {'+' if liked[i] else '-'}" for i in recommend(history[-1][0], sets)), ""]

(OUTPUT / "resultats.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
