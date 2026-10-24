import numpy as np


def film_scores(likes, dislikes):
    score = 2.0 ** (likes - dislikes)
    return score / score.max()


def scores(patterns, likes, dislikes):
    film_score = film_scores(likes, dislikes)
    return np.array([np.prod(film_score[F]) for F in patterns])


def diversity(i, sets, shown):
    return 1 - max((len(sets[i] & sets[j]) / len(sets[i] | sets[j]) for j in shown), default=0)


def first_round(sets, shown, k, rng):
    chosen = []
    for _ in range(k):
        div = np.array([-1 if i in shown else diversity(i, sets, shown) for i in range(len(sets))])
        i = int(rng.choice(np.flatnonzero(div == div.max())))
        shown.append(i)
        chosen.append(i)
    return chosen


def recommend(s, sets, n=3):
    chosen = []
    for i in np.argsort(-s):
        if all(not sets[i] & sets[j] for j in chosen):
            chosen.append(int(i))
        if len(chosen) == n:
            break
    return chosen


def draw(s, sets, shown, alpha, k, rng):
    chosen = []
    for _ in range(k):
        left = [i for i in range(len(sets)) if i not in shown]
        if not left:
            break
        weight = np.array([(1 - alpha) * s[i] + alpha * diversity(i, sets, shown) for i in left]) + 1e-9
        i = left[rng.choice(len(left), p=weight / weight.sum())]
        shown.append(i)
        chosen.append(i)
    return chosen


def play(patterns, liked, m, rng, alpha=0.3, k=4, rounds=6, uniform=False):
    sets = [set(F) for F in patterns]
    likes = np.zeros(m)
    dislikes = np.zeros(m)
    shown = []
    chosen = first_round(sets, shown, k, rng)
    history = []
    for t in range(rounds):
        for i in chosen:
            if liked[i]:
                likes[patterns[i]] += 1
            else:
                dislikes[patterns[i]] += 1
        s = scores(patterns, likes, dislikes)
        history.append((s, list(shown)))
        if t < rounds - 1:
            chosen = draw(np.zeros(len(patterns)) if uniform else s, sets, shown, 0 if uniform else alpha, k, rng)
    return history


def found_round(history, liked):
    for t, (s, shown) in enumerate(history):
        if liked[shown].sum() >= 3:
            return t + 1
    return None
