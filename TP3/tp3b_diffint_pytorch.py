"""
TP3b (skeleton) -- DiffInt soft-interval bottleneck in PyTorch.

Fill in the three methods marked  # TODO .  Autograd handles the backward pass;
your job is the soft-box forward pass, the competition softmax, and LFI.
Test with:
    python tp3b_diffint_pytorch.py --worked-example
    python tp3b_diffint_pytorch.py --dataset synth --epochs 300

Reference: tp3b_diffint_pytorch_solution.py
"""
from __future__ import annotations
import argparse
import numpy as np
import torch
import torch.nn as nn

from common_datasets import make_interval_anomaly_data
from tp3b_diffint_pytorch_solution import train, run_worked_example, run_synth


class SoftIntervalBottleneck(nn.Module):
    def __init__(self, d, K=8, tau=0.1):
        super().__init__()
        self.tau = tau
        self.centre = nn.Parameter(torch.zeros(K, d).uniform_(-0.3, 0.3))
        self.log_hw = nn.Parameter(torch.zeros(K, d))

    def half_width(self):
        return torch.nn.functional.softplus(self.log_hw) + 1e-3

    def memberships(self, x):
        a = self.centre - self.half_width()
        b = self.centre + self.half_width()
        x = x.unsqueeze(1)
        return torch.sigmoid((x - a) / self.tau) * torch.sigmoid((b - x) / self.tau)

    def forward(self, x):
        I = self.memberships(x).clamp_min(1e-6)
        f = torch.softmax(I.log().sum(dim=-1), dim=-1)
        return f, I


class DiffInt(nn.Module):
    def __init__(self, d, K=8, tau=0.1, hidden=32):
        super().__init__()
        self.bottleneck = SoftIntervalBottleneck(d, K, tau)
        self.decoder = nn.Sequential(
            nn.Linear(K, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, d))

    def forward(self, x):
        f, I = self.bottleneck(x)
        return self.decoder(f), f, I

    @torch.no_grad()
    def score(self, x):
        xhat, _, _ = self.forward(x)
        return (x - xhat).abs().mean(dim=1)

    @torch.no_grad()
    def boxes(self):
        m = self.bottleneck.centre.cpu().numpy()
        d = self.bottleneck.half_width().cpu().numpy()
        return m - d, m + d

    @torch.no_grad()
    def lfi(self, X_inliers, feat_range=2.0):
        X = torch.as_tensor(X_inliers, dtype=torch.float32)
        support = self.bottleneck.memberships(X).mean(dim=0)
        tightness = (1 - 2 * self.bottleneck.half_width() / feat_range).clamp(0, 1)
        return support * tightness


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="synth")
    ap.add_argument("--d", type=int, default=6)
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--worked-example", action="store_true")
    args = ap.parse_args()

    # monkey-patch the solution helpers to use YOUR classes
    import tp3b_diffint_pytorch_solution as sol
    sol.DiffInt = DiffInt
    sol.SoftIntervalBottleneck = SoftIntervalBottleneck

    if args.worked_example:
        run_worked_example()
    else:
        run_synth(d=args.d, K=args.K, epochs=args.epochs, seed=args.seed)


if __name__ == "__main__":
    main()
