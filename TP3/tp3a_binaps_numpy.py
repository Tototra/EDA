"""
TP3a (skeleton) -- BinaPs from scratch in NumPy.

Fill in the forward pass and the GATED straight-through backward pass
(methods marked  # TODO ).  Adam, the training loop, pattern extraction,
the F1 metric, the noise sweep and the ablations are all provided by the
solution module and imported here.

Test with:
    python tp3a_binaps_numpy.py --noise 0.01 --epochs 15
    python tp3a_binaps_numpy.py --ablation

Reference: tp3a_binaps_numpy_solution.py
"""
from __future__ import annotations
import argparse
import numpy as np

from tp3a_binaps_numpy_solution import (
    Adam, f1_exact, f1_soft, one_run, make_planted_transactions)


class BinaPs:
    def __init__(self, m, capacity=None, seed=0, gated_ste=True, sparsity_loss=True):
        self.m = m
        self.k = capacity or m
        self.rng = np.random.default_rng(seed)
        self.W = np.full((self.k, m), 1.0 / m)
        self.b = np.full(self.k, -1.0)
        self.gated_ste = gated_ste
        self.sparsity_loss = sparsity_loss
        self.opt = Adam([self.W.shape, self.b.shape], lr=1e-2)

    def _binarise(self):
        Wc = np.clip(self.W, 1.0 / self.m, 1.0)
        Wb = (self.rng.random(Wc.shape) < Wc).astype(np.float64)
        bd = np.minimum(np.ceil(self.b), -1.0)
        return Wb, bd

    def forward(self, S, Wb, bd):
        pre1 = S @ Wb.T
        a1 = pre1 + bd
        y = np.round(np.clip(a1, 0, 1))
        pre2 = y @ Wb
        z = np.round(np.clip(pre2, 0, 1))
        return pre1, a1, y, pre2, z

    def loss_and_grads(self, S, Wb, bd):
        B = S.shape[0]
        pre1, a1, y, pre2, z = self.forward(S, Wb, bd)

        # ---- sparsity-aware loss --------------------------------------
        if self.sparsity_loss:
            alpha = S.mean()
            w = np.where(S == 1, 1.0 - alpha, alpha)
        else:
            w = np.ones_like(S)
        loss = float(np.sum(w * np.abs(z - S)) / B)

        # ---- backward ---------------------------------------------------
        g_z = w * np.sign(z - S) / B
        # decoder activation: plain straight-through
        g_pre2 = g_z
        g_y = g_pre2 @ Wb.T
        g_Wb_dec = y.T @ g_pre2

        if self.gated_ste:
            g_a1_x = np.where(y == 1, g_y, np.maximum(0, g_y))
            g_b = np.where(y == 1, g_y, 0).sum(axis=0)
        else:
            g_a1_x = g_y
            g_b = g_y.sum(axis=0)
        g_Wb_enc = g_a1_x.T @ S
        g_W = g_Wb_dec + g_Wb_enc + 3e-4 * self.W
        return loss, g_W, g_b

    def fit(self, D, epochs=15, batch=64, verbose=False):
        n = D.shape[0]
        for ep in range(epochs):
            self.opt.lr = 1e-2 if ep < epochs * .5 else (1e-3 if ep < epochs * .8 else 1e-4)
            perm = self.rng.permutation(n)
            tot = 0.0
            for s in range(0, n, batch):
                S = D[perm[s:s + batch]].astype(np.float64)
                Wb, bd = self._binarise()
                loss, gW, gb = self.loss_and_grads(S, Wb, bd)
                self.W, self.b = self.opt.step([self.W, self.b], [gW, gb])
                self.W = np.clip(self.W, 1.0 / self.m, 1.0)
                self.b = np.minimum(self.b, -1.0)
                tot += loss * len(S)
            if verbose and (ep % 2 == 0 or ep == epochs - 1):
                print(f"  epoch {ep:3d}  loss {tot/n:.4f}  |patterns| {len(self.patterns())}")
        return self

    def patterns(self, thresh=0.2):
        Wb = (self.W > thresh).astype(int)
        return [frozenset(np.nonzero(r)[0].tolist()) for r in Wb if r.sum() >= 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--noise", type=float, default=0.01)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--ablation", action="store_true")
    args = ap.parse_args()

    import tp3a_binaps_numpy_solution as sol
    sol.BinaPs = BinaPs

    if args.ablation:
        for name, g, s in [("full", True, True), ("vanilla STE", False, True),
                           ("plain L1", True, False), ("neither", False, False)]:
            f1 = np.mean([sol.one_run(noise=0.02, seed=k, gated=g, sparsity=s,
                                      epochs=args.epochs)["f1_soft"] for k in range(3)])
            print(f"  {name:<14} F1(soft) {f1:.3f}")
    else:
        print(sol.one_run(noise=args.noise, seed=args.seed,
                          epochs=args.epochs, verbose=True))


if __name__ == "__main__":
    main()
