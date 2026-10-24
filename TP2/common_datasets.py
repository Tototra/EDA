"""
common_datasets.py -- shared data utilities for the EDA practical labs.

Provides:
  * synthetic transaction data with planted itemset patterns
  * synthetic numeric data with planted interval structure + anomalies
  * a tolerant loader for FIMI-style `.dat` files (one transaction per line,
    space-separated integer items) if present next to the scripts
  * a couple of tiny hand datasets matching the TD exercise sheets
"""
from __future__ import annotations
import os
import numpy as np


# --------------------------------------------------------------------------
# Tiny hand datasets (match the TD slides)
# --------------------------------------------------------------------------
TD1_DB = [set("abc"), set("ab"), set("abd"), set("ac"), set("bcd")]          # E = a,b,c,d
TD2_DB = [set("abc"), set("ab"), set("ac"), set("bc"), set("c")]            # labels below
TD2_LABELS = np.array([1, 1, 1, 0, 0])                                      # 1 = positive


# --------------------------------------------------------------------------
# Synthetic transaction data with planted patterns
# --------------------------------------------------------------------------
def make_planted_transactions(n_rows=2000, n_items=50, n_patterns=8,
                              min_len=2, max_len=6, density=0.05,
                              noise=0.01, seed=0):
    """
    Return (D, patterns) where
      D        : (n_rows, n_items) binary ndarray
      patterns : list of frozenset(item indices)

    Each pattern is planted in a random ~`density` fraction of the rows; then a
    fraction `noise` of all matrix entries is flipped.
    """
    rng = np.random.default_rng(seed)
    patterns = []
    for _ in range(n_patterns):
        L = rng.integers(min_len, max_len + 1)
        patterns.append(frozenset(rng.choice(n_items, size=L, replace=False).tolist()))

    D = np.zeros((n_rows, n_items), dtype=np.int8)
    for p in patterns:
        k = max(1, int(rng.normal(density * n_rows, 0.1 * density * n_rows)))
        rows = rng.choice(n_rows, size=min(k, n_rows), replace=False)
        for j in p:
            D[rows, j] = 1

    if noise > 0:
        flip = rng.random(D.shape) < noise
        D[flip] ^= 1
    return D, patterns


# --------------------------------------------------------------------------
# Synthetic numeric data with planted interval structure + anomalies
# --------------------------------------------------------------------------
def make_interval_anomaly_data(n_inliers=500, n_anom=50, d=6,
                               n_informative=2, seed=0):
    """
    Inliers: `n_informative` features pinned to a tight band around 0; the
    rest spread over a couple of Gaussian blobs.  Anomalies break one of the
    informative features.  Returns X (float), y (0 inlier / 1 anomaly),
    already scaled to roughly [-1, 1].
    """
    rng = np.random.default_rng(seed)
    X = np.zeros((n_inliers + n_anom, d))
    # blobs on the non-informative features
    centers = rng.uniform(-0.45, 0.45, size=(2, d))
    for i in range(n_inliers):
        c = centers[i % 2]
        X[i] = c + rng.normal(0, 0.06, size=d)
    # pin informative features near 0
    X[:n_inliers, :n_informative] = rng.normal(0, 0.03, size=(n_inliers, n_informative))
    # anomalies: start from an inlier, push one informative feature out
    for k in range(n_anom):
        i = n_inliers + k
        c = centers[k % 2]
        X[i] = c + rng.normal(0, 0.06, size=d)
        j = k % n_informative
        X[i, j] = rng.choice([-1, 1]) * rng.uniform(0.6, 0.95)
    y = np.r_[np.zeros(n_inliers), np.ones(n_anom)].astype(int)
    X = np.clip(X, -1, 1)
    return X, y


# --------------------------------------------------------------------------
# FIMI .dat loader
# --------------------------------------------------------------------------
def load_fimi(path):
    """Load a FIMI transaction file -> list[set[int]], or None if not found."""
    if not os.path.exists(path):
        return None
    txns = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            txns.append(set(int(t) for t in line.split()))
    return txns


def transactions_to_matrix(txns):
    items = sorted({i for t in txns for i in t})
    idx = {it: k for k, it in enumerate(items)}
    D = np.zeros((len(txns), len(items)), dtype=np.int8)
    for r, t in enumerate(txns):
        for it in t:
            D[r, idx[it]] = 1
    return D, items


def get_transaction_dataset(name, seed=0):
    """name in {synth, td1, <path to .dat>}."""
    if name == "td1":
        D, items = transactions_to_matrix(TD1_DB)
        return D, items, None
    if name == "synth":
        D, patterns = make_planted_transactions(seed=seed)
        return D, list(range(D.shape[1])), patterns
    txns = load_fimi(name)
    if txns is None:
        raise FileNotFoundError(f"no dataset '{name}' (try 'synth', 'td1', or a .dat path)")
    D, items = transactions_to_matrix(txns)
    return D, items, None
