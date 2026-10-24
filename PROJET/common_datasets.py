import numpy as np

def make_planted_transactions(n_rows=2000, n_items=50, n_patterns=8,
                              min_len=2, max_len=6, density=0.05,
                              noise=0.01, seed=0):
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
