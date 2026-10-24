import numpy as np


class Adam:
    def __init__(self, shapes, lr=1e-2, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps, self.t = lr, b1, b2, eps, 0
        self.m = [np.zeros(s) for s in shapes]
        self.v = [np.zeros(s) for s in shapes]

    def step(self, grads):
        self.t += 1
        steps = []
        for i, g in enumerate(grads):
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g ** 2
            m = self.m[i] / (1 - self.b1 ** self.t)
            v = self.v[i] / (1 - self.b2 ** self.t)
            steps.append(self.lr * m / (np.sqrt(v) + self.eps))
        return steps


class BinaPs:
    def __init__(self, m, capacity=None, seed=0, gated_ste=True, sparsity_loss=True):
        self.m = m
        self.k = capacity or m
        self.rng = np.random.default_rng(seed)
        self.W = np.full((self.k, m), 1.0 / m)
        self.b = np.full(self.k, -1.0)
        self.gated_ste = gated_ste
        self.sparsity_loss = sparsity_loss
        self.opt = Adam([self.W.shape, self.W.shape, self.b.shape], lr=1e-2)

    def _binarise(self):
        Wb = (self.rng.random(self.W.shape) < self.W).astype(np.float64)
        bd = np.trunc(np.minimum(self.b, -1.0))
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

        if self.sparsity_loss:
            w = np.where(S == 1, 1.0 - self.density, self.density)
        else:
            w = np.ones_like(S)
        loss = float(np.sum(w * np.abs(z - S)) / B)

        g_pre2 = w * np.sign(z - S) / B
        g_y = g_pre2 @ self.W.T
        g_W_dec = y.T @ g_pre2

        if self.gated_ste:
            g_a1 = y * g_y
            g_b = (1 - y).sum(axis=0) * np.minimum(g_y, 0).sum(axis=0) + y.sum(axis=0) * g_y.sum(axis=0)
        else:
            g_a1 = g_y
            g_b = g_y.sum(axis=0)
        g_W_enc = g_a1.T @ S
        return loss, g_W_enc, g_W_dec, g_b

    def fit(self, D, epochs=10, batch=64, lr=1e-2, alpha=None, verbose=False):
        n = D.shape[0]
        self.density = D.mean() if alpha is None else alpha
        self.history = []
        for ep in range(epochs):
            self.opt.lr = lr if ep < 5 else (lr / 10 if ep < 7 else lr / 100)
            perm = self.rng.permutation(n)
            total = 0.0
            for s in range(0, n, batch):
                S = D[perm[s:s + batch]].astype(np.float64)
                Wb, bd = self._binarise()
                loss, g_enc, g_dec, g_b = self.loss_and_grads(S, Wb, bd)
                step_enc, step_dec, step_b = self.opt.step([g_enc, g_dec, g_b])
                self.W = np.clip(self.W - step_enc - step_dec, 1.0 / self.m, 1.0)
                self.b = np.minimum(self.b - step_b, -1.0)
                total += loss * len(S)
            self.history.append((total / n, len(self.patterns())))
            if verbose:
                print(f"epoch {ep:3d}  loss {self.history[-1][0]:.4f}  patterns {self.history[-1][1]}")
        return self

    def patterns(self, thresh=0.5):
        Wb = (self.W > thresh).astype(int)
        return [frozenset(np.nonzero(r)[0].tolist()) for r in Wb if r.sum() >= 2]
