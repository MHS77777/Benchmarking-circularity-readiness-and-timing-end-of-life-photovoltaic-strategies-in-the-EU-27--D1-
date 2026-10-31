"""Layer C figures."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES, FIG = ROOT / "results", ROOT / "figs"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
import sys; sys.path.insert(0, str(ROOT / "code"))
from layer_c import ALTS, ALT_NAMES, HOR, HOR_LAB, ARCH, ARCH_LAB, A_T

LABEL = "proxy"
R = pd.read_csv(RES / f"C_local_scores_{LABEL}.csv")
G = pd.read_csv(RES / f"C_global_scores_{LABEL}.csv")
TAG = ""
ACOL = {"a1": "#1f4e79", "a2": "#4f81bd", "a3": "#c0504d", "a4": "#7f7f7f", "a5": "#9bbb59", "a6": "#f79646", "a7": "#404040"}


def fig12_timeline():
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.6), sharey=True)
    for ax, g in zip(axes, ARCH):
        d = R[R.archetype == g]
        rk = d.pivot(index="alternative", columns="horizon", values="rank").loc[ALTS, HOR]
        sc = d.pivot(index="alternative", columns="horizon", values="score").loc[ALTS, HOR]
        ax.imshow(rk.values, cmap="RdYlGn_r", vmin=1, vmax=7, aspect="auto")
        for i, a in enumerate(ALTS):
            for j, h in enumerate(HOR):
                ax.text(j, i, f"{int(rk.iloc[i, j])}\n{sc.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7.5,
                        fontweight="bold" if rk.iloc[i, j] <= 2 else "normal")
        ax.set_xticks(range(3)); ax.set_xticklabels([f"{h}\n{HOR_LAB[h]}\n|$A_t$| = {len(A_T[h])}" for h in HOR], fontsize=7.5)
        ax.set_title(f"{ARCH_LAB[g]}", fontsize=9, loc="left")
        gl = G[G.archetype == g].set_index("alternative")["rank"].loc[ALTS]
        for i, a in enumerate(ALTS):
            ax.text(2.62, i, f"Σ {int(gl[a])}", va="center", fontsize=7, color="#333")
    axes[0].set_yticks(range(7)); axes[0].set_yticklabels([f"$a_{a[1]}$ {ALT_NAMES[a]}" for a in ALTS], fontsize=7.5)
    fig.suptitle("Strategy-activation timeline: DFSS local rank (and score) per horizon; Σ = global (Phase 3) rank" + TAG, fontsize=8, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(FIG / "fig12_activation_timeline.png", dpi=300); plt.close(fig)


def fig13_fuzzy_bands():
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.9), sharey=True)
    for ax, h in zip(axes, HOR):
        for k, g in enumerate(ARCH):
            d = R[(R.archetype == g) & (R.horizon == h)].set_index("alternative").loc[ALTS]
            x = np.arange(7) + (k - 1) * 0.27
            ax.errorbar(x, d.m, yerr=[d.m - d.l, d.u - d.m], fmt="o", ms=4, color=["#1f4e79", "#c0504d", "#f79646"][k],
                        capsize=2, lw=0.9, label=ARCH_LAB[g])
        ax.set_xticks(range(7)); ax.set_xticklabels([f"$a_{a[1]}$" for a in ALTS]); ax.set_title(f"{h} ({HOR_LAB[h]})", fontsize=9, loc="left")
        ax.grid(axis="y", lw=0.3, alpha=0.5)
    axes[0].set_ylabel("Fuzzy local score (l, m, r)"); axes[0].legend(fontsize=7, frameon=False, loc="upper right")
    fig.suptitle("Triangular fuzzy local scores by horizon and archetype (support l–u, mode m)" + TAG, fontsize=8, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(FIG / "fig13_fuzzy_scores.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    fig12_timeline(); fig13_fuzzy_bands(); print("ok", LABEL)
