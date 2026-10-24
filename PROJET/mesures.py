import numpy as np


def jaccard(a, b):
    return len(a & b) / len(a | b)


def f1(found, truth):
    if not found:
        return 0.0, 0.0
    exact = 2 * len(set(found) & set(truth)) / (len(found) + len(truth))
    p = np.mean([max(jaccard(f, t) for t in truth) for f in found])
    r = np.mean([max(jaccard(t, f) for f in found) for t in truth])
    return exact, 2 * p * r / (p + r)


def coverage(D, F):
    return D[:, F].sum(axis=1) >= max(2, len(F) / 2)


def auc(score, label):
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    return np.mean([(p > n) + 0.5 * (p == n) for p in pos for n in neg])
