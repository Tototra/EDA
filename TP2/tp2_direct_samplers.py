"""
TP2 (skeleton) -- Direct two-step pattern samplers (Boley et al., KDD 2011).

Implement the four samplers in the class below (methods marked # TODO).
The exact-target computation, the chi^2 / L1 check and the classification
pipeline are all imported from the solution module so you can test
incrementally:

    python tp2_direct_samplers.py --check                 # goodness of fit
    python tp2_direct_samplers.py --classify --dataset tic-tac-toe

Reference: tp2_direct_samplers_solution.py
"""
from __future__ import annotations
import argparse
from math import comb
import numpy as np

from common_datasets import TD2_DB, TD2_LABELS
from tp2_direct_samplers_solution import (
    to_records, exact_target, chi2_check, run_classification)


class DirectSampler:
    def __init__(self, records, labels=None, seed=0):
        self.recs = [frozenset(r) for r in records]
        self.m = len(self.recs)
        self.labels = None if labels is None else np.asarray(labels)
        self.rng = np.random.default_rng(seed)
        self.E = sorted({i for r in self.recs for i in r})

    def _subset(self, D):
        return frozenset(i for i in sorted(D) if self.rng.random() < 0.5)

    # ---- Algorithm 1 : frequency  (pi propto support) --------------------
    def _prep_frequency(self):
        w = np.array([2.0 ** len(D) for D in self.recs])
        self.w1 = w / w.sum()

    def sample_frequency(self):
        return self._subset(self.recs[self.rng.choice(self.m, p=self.w1)])

    # ---- Algorithm 2 : area  (pi propto |F| * support) ------------------
    def _prep_area(self):
        w = np.array([len(D) * 2.0 ** (len(D) - 1) for D in self.recs])
        self.w2 = w / w.sum()

    def sample_area(self):
        D = sorted(self.recs[self.rng.choice(self.m, p=self.w2)])
        p = np.array([comb(len(D), s) * s for s in range(len(D) + 1)], dtype=float)
        s = self.rng.choice(len(D) + 1, p=p / p.sum())
        return frozenset(D[i] for i in self.rng.choice(len(D), size=s, replace=False))

    # ---- Algorithm 4 : squared frequency  (pi propto support**2) --------
    def _prep_sqfreq(self):
        w = np.array([2.0 ** len(Di & Dj) for Di in self.recs for Dj in self.recs])
        self.w4 = w / w.sum()

    def sample_sqfreq(self):
        k = self.rng.choice(self.m * self.m, p=self.w4)
        return self._subset(self.recs[k // self.m] & self.recs[k % self.m])

    # ---- Algorithm 3 : discriminativity --------------------------------
    def _prep_disc(self):
        self.pos = [D for D, y in zip(self.recs, self.labels) if y == 1]
        self.neg = [D for D, y in zip(self.recs, self.labels) if y != 1]
        w = np.array([(2.0 ** len(Dp - Dn) - 1) * 2.0 ** len(Dp & Dn)
                      for Dp in self.pos for Dn in self.neg])
        self.w3 = w / w.sum()

    def sample_disc(self):
        k = self.rng.choice(len(self.w3), p=self.w3)
        Dp, Dn = self.pos[k // len(self.neg)], self.neg[k % len(self.neg)]
        F = frozenset()
        while not F:
            F = self._subset(Dp - Dn)
        return F | self._subset(Dp & Dn)

    # ---- dispatch -----------------------------------------------------
    def prepare(self, measure):
        {"frequency": self._prep_frequency, "area": self._prep_area,
         "sqfreq": self._prep_sqfreq, "disc": self._prep_disc}[measure]()

    def sample(self, measure):
        return {"frequency": self.sample_frequency, "area": self.sample_area,
                "sqfreq": self.sample_sqfreq, "disc": self.sample_disc}[measure]()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--measure", default="all",
                    choices=["all", "frequency", "area", "sqfreq", "disc"])
    ap.add_argument("--n", type=int, default=150_000)
    ap.add_argument("--classify", action="store_true")
    ap.add_argument("--dataset", default="tic-tac-toe")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.check:
        ms = ["frequency", "area", "sqfreq", "disc"] if args.measure == "all" else [args.measure]
        for meas in ms:
            s = DirectSampler(TD2_DB, labels=TD2_LABELS, seed=args.seed)
            stat, dof, p, l1 = chi2_check(s, meas, n=args.n)
            print(f"{meas:<12} chi2={stat:7.2f} dof={dof} p={p:.3f} L1={l1:.4f}"
                  f"  {'OK' if l1 < 0.01 else '!!'}")

    if args.classify:
        # NB: run_classification in the solution module builds its own sampler;
        # to grade YOUR sampler, monkey-patch it:
        import tp2_direct_samplers_solution as sol
        sol.DirectSampler = DirectSampler
        for k, v in run_classification(args.dataset, seed=args.seed).items():
            print(f"  {k:<14} {v:.4f}")


if __name__ == "__main__":
    main()
