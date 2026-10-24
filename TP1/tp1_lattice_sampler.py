"""
TP1 (skeleton) -- Metropolis-Hastings random-walk sampler on the itemset lattice.

Fill in the three functions marked  # TODO .  Everything else (support oracle,
exact enumeration, diagnostics, CLI, plotting) is provided.  Check your work
against tp1_lattice_sampler_solution.py.

Run:
    python tp1_lattice_sampler.py --dataset td1 --minsup 2 --target uniform --exact
    python tp1_lattice_sampler.py --dataset synth --minsup 0.03 --target support --plot
"""
from __future__ import annotations
import argparse
import numpy as np
from common_datasets import get_transaction_dataset


class SupportOracle:
    def __init__(self, D: np.ndarray):
        self.n_rows, self.n_items = D.shape
        self.tid = [D[:, j].astype(bool) for j in range(self.n_items)]
        self._cache = {frozenset(): self.n_rows}

    def support(self, itemset: frozenset) -> int:
        if itemset in self._cache:
            return self._cache[itemset]
        mask = np.ones(self.n_rows, dtype=bool)
        for j in itemset:
            mask &= self.tid[j]
        s = int(mask.sum())
        self._cache[itemset] = s
        return s


def frequent_neighbours(F: frozenset, oracle: SupportOracle, minsup: int):
    up = [F | {j} for j in range(oracle.n_items)
          if j not in F and oracle.support(F | {j}) >= minsup]
    down = [F - {j} for j in F]
    return up, down


def mh_acceptance(cur, nxt, q_fwd, q_bwd, oracle, target):
    if target == "uniform":
        s_cur = s_nxt = 1
    else:
        s_cur, s_nxt = max(oracle.support(cur), 1), max(oracle.support(nxt), 1)
    return min(1.0, (s_nxt * q_bwd) / (s_cur * q_fwd))


def propose(cur, up, down, target, alpha, rng, oracle, minsup):
    if target == "uniform":
        nbrs = up + down
        nxt = nbrs[rng.integers(len(nbrs))]
        up2, down2 = frequent_neighbours(nxt, oracle, minsup)
        return nxt, 1 / len(nbrs), 1 / (len(up2) + len(down2)), up2, down2
    go_up = rng.random() < alpha
    side = up if go_up else down
    if not side:
        return cur, 1.0, 1.0, up, down
    nxt = side[rng.integers(len(side))]
    up2, down2 = frequent_neighbours(nxt, oracle, minsup)
    if go_up:
        return nxt, alpha / len(up), (1 - alpha) / len(down2), up2, down2
    return nxt, (1 - alpha) / len(down), alpha / len(up2), up2, down2


# --------- provided: walker loop, enumeration, diagnostics, main ----------
def mh_walk(oracle, minsup, target="uniform", alpha=0.5, steps=200_000,
            burn_in=10_000, thin=50, seed=0, lazy=0.5, start=None):
    rng = np.random.default_rng(seed)
    cur = frozenset(start) if start is not None else frozenset()
    up, down = frequent_neighbours(cur, oracle, minsup)
    samples, visits = [], {}
    n_accept = n_prop = 0
    for t in range(steps):
        if rng.random() >= lazy and (up or down):
            nxt, q_fwd, q_bwd, up2, down2 = propose(cur, up, down, target, alpha,
                                                    rng, oracle, minsup)
            n_prop += 1
            if rng.random() < mh_acceptance(cur, nxt, q_fwd, q_bwd, oracle, target):
                cur, up, down = nxt, up2, down2
                n_accept += 1
        if t >= burn_in and (t - burn_in) % thin == 0:
            samples.append(cur)
            visits[cur] = visits.get(cur, 0) + 1
    return samples, n_accept / max(n_prop, 1), visits


def enumerate_frequent(oracle, minsup):
    frequent = {frozenset(): oracle.n_rows}
    frontier = [frozenset()]
    while frontier:
        nxt = []
        for F in frontier:
            mx = max(F) if F else -1
            for j in range(mx + 1, oracle.n_items):
                G = frozenset(F | {j})
                if G in frequent:
                    continue
                if oracle.support(G) >= minsup:
                    frequent[G] = oracle.support(G)
                    nxt.append(G)
        frontier = nxt
    return frequent


def l1_distance(visits, target_pmf):
    total = sum(visits.values())
    emp = {k: v / total for k, v in visits.items()}
    keys = set(emp) | set(target_pmf)
    return 0.5 * sum(abs(emp.get(k, 0.0) - target_pmf.get(k, 0.0)) for k in keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="synth")
    ap.add_argument("--minsup", type=float, default=0.03)
    ap.add_argument("--target", choices=["uniform", "support"], default="uniform")
    ap.add_argument("--alpha", type=float, default=0.5)
    ap.add_argument("--steps", type=int, default=200_000)
    ap.add_argument("--burn-in", type=int, default=10_000)
    ap.add_argument("--thin", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()

    D, items, _ = get_transaction_dataset(args.dataset, seed=args.seed)
    oracle = SupportOracle(D)
    minsup = int(args.minsup * oracle.n_rows) if args.minsup < 1 else int(args.minsup)
    print(f"rows={oracle.n_rows} items={oracle.n_items} minsup={minsup}")

    samples, acc, visits = mh_walk(oracle, minsup, args.target, args.alpha,
                                   args.steps, args.burn_in, args.thin, args.seed)
    print(f"samples={len(samples)} accept_rate={acc:.3f} distinct={len(visits)}")

    if args.exact:
        exact = enumerate_frequent(oracle, minsup)
        if args.target == "uniform":
            tgt = {k: 1 / len(exact) for k in exact}
        else:
            Z = sum(exact.values()); tgt = {k: v / Z for k, v in exact.items()}
        print(f"|F|={len(exact)}  L1={l1_distance(visits, tgt):.4f}")

    if args.plot:
        import matplotlib.pyplot as plt
        counts = np.array(sorted(visits.values(), reverse=True))
        plt.bar(range(len(counts)), counts, width=1.0, color="#102D69")
        plt.savefig("tp1_visit_histogram.png", dpi=130)
        print("saved tp1_visit_histogram.png")


if __name__ == "__main__":
    main()
