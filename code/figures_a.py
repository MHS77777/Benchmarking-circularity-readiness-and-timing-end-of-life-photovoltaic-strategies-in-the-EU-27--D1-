"""Layer A figures (matplotlib only, 300 dpi, journal-ready)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, RES, FIG = ROOT / "data", ROOT / "results", ROOT / "figs"
FIG.mkdir(exist_ok=True)
T = [2012, 2016, 2020, 2023]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
C1, C2, C3, C4 = "#1f4e79", "#c0504d", "#7f7f7f", "#9bbb59"

meta = pd.read_csv(DATA / "indicators.csv").set_index("ind")
avail = pd.read_csv(DATA / "availability.csv", index_col=0)
S1 = {int(k): v for k, v in json.load(open(DATA / "active_sets_S1.json")).items()}
S2 = {int(k): v for k, v in json.load(open(DATA / "active_sets_S2.json")).items()}
DIMN = {"PC": "Production & consumption", "WM": "Waste management", "SRM": "Secondary raw materials",
        "CIE": "Competitiveness & innovation", "GSR": "Global sustainability & resilience"}


def fig1_availability():
    inds = list(meta.index)
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 6.2), sharey=True, gridspec_kw={"width_ratios": [1.15, 1]})
    # left: coverage counts
    M = avail[[str(t) for t in T]].loc[inds].values.astype(float)
    ax = axes[0]
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=27, aspect="auto")
    for i in range(len(inds)):
        for j in range(4):
            ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=8, color="white" if M[i, j] > 15 else "black")
    ax.set_xticks(range(4)); ax.set_xticklabels([f"{t}\n({t-1}–{t+1})" if t != 2023 else "2023\n(2022–24)" for t in T], fontsize=7.5)
    ax.set_yticks(range(len(inds)))
    ax.set_yticklabels([f"{i} — {meta.loc[i,'name']}" for i in inds], fontsize=7.5)
    ax.set_title("(a) EU-27 countries reporting (of 27)", fontsize=9, loc="left")
    # dimension separators
    dims = meta.loc[inds, "dim"].values
    for i in range(1, len(inds)):
        if dims[i] != dims[i - 1]:
            ax.axhline(i - 0.5, color="black", lw=0.8)
    # right: active sets S1/S2
    ax = axes[1]
    Z = np.zeros((len(inds), 4))
    for j, t in enumerate(T):
        for i, e in enumerate(inds):
            Z[i, j] = (1 if e in S1[t] else 0) + (2 if e in S2[t] else 0)
    cmap = matplotlib.colors.ListedColormap(["#f2f2f2", "#c6dbef", "#fdd0a2", C1])
    ax.imshow(Z, cmap=cmap, vmin=0, vmax=3, aspect="auto")
    lab = {0: "", 1: "S1", 2: "S2", 3: "S1+S2"}
    for i in range(len(inds)):
        for j in range(4):
            ax.text(j, i, lab[int(Z[i, j])], ha="center", va="center", fontsize=7, color="white" if Z[i, j] == 3 else "black")
    for i in range(1, len(inds)):
        if dims[i] != dims[i - 1]:
            ax.axhline(i - 0.5, color="black", lw=0.8)
    ax.set_xticks(range(4)); ax.set_xticklabels([f"$A_{{{t}}}$" for t in T])
    ax.set_title("(b) Active parameter sets", fontsize=9, loc="left")
    # dimension labels on the right
    ymid = {}
    for i, d in enumerate(dims):
        ymid.setdefault(d, []).append(i)
    for d, ii in ymid.items():
        ax.text(3.62, np.mean(ii), d, va="center", ha="left", fontsize=7.5, fontweight="bold")
    fig.text(0.5, 0.005, "S1: availability-driven (≥ 22 of 27 countries reporting).  S2: framework-faithful "
             "(2018 framework for 2012–2020; 2023 revision for 2023).  Both require availability.\n"
             "PC production & consumption; WM waste management; SRM secondary raw materials; CIE competitiveness & innovation; GSR global sustainability & resilience.", ha="center", fontsize=6.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "fig1_availability_active_sets.png", dpi=300); plt.close(fig)


def fig2_bump(sc="S2"):
    lr = pd.read_csv(RES / f"{sc}_local_ranks.csv", index_col=0)
    D = pd.read_csv(RES / f"{sc}_dfss_scores.csv", index_col=0)
    clus = pd.read_csv(RES / f"{sc}_clusters.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(7.2, 7.4))
    x = np.arange(len(T))
    for g in lr.index:
        y = lr.loc[g, [str(t) for t in T]].values
        col = C1 if clus.loc[g, "cluster"] == 0 else C3
        ax.plot(x, y, "-o", color=col, lw=1.4 if col == C1 else 0.9, ms=3.5, alpha=0.95 if col == C1 else 0.6)
        ax.text(-0.15, y[0], g, ha="right", va="center", fontsize=7.5)
        ax.text(3.15, y[-1], g, ha="left", va="center", fontsize=7.5)
    ax.axvspan(2.5, 3.5, color="#fdd0a2", alpha=0.35, lw=0)
    ax.text(3.0, 28.9, "2023 framework revision applies", ha="center", va="bottom", fontsize=7.5, color="#b35806")
    ax.set_xticks(x); ax.set_xticklabels([f"$t$ = {t}\n|$A_t$| = {len(S2[t])}" for t in T])
    ax.set_ylim(29.4, 0.2); ax.set_ylabel("Local DFSS rank $P_t(u)$ (1 = most circular)")
    ax.set_xlim(-0.6, 3.6)
    ax.set_title("Period-wise circularity ranks of EU-27 under the framework in force (Scenario S2)", fontsize=9, loc="left")
    ax.plot([], [], color=C1, label="Cluster 0 (consolidated leaders)"); ax.plot([], [], color=C3, label="Cluster 1")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=7.5, frameon=False)
    fig.tight_layout(); fig.savefig(FIG / f"fig2_bump_{sc}.png", dpi=300); plt.close(fig)


def fig3_decomposition(sc="S2"):
    d = pd.read_csv(RES / f"{sc}_activation_decomposition.csv")
    x = d[d["to"] == 2023].sort_values("structural_effect")
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    y = np.arange(len(x))
    ax.barh(y + 0.2, x.structural_effect, height=0.4, color=C2, label="Structural effect (indicators entering $A_{2023}$)")
    ax.barh(y - 0.2, x.value_effect, height=0.4, color=C1, alpha=0.75, label="Value effect (performance change 2020→2023)")
    ax.set_yticks(y); ax.set_yticklabels(x.geo, fontsize=7.5)
    ax.axvline(0, color="black", lw=0.8)
    for yi, (g, s, v, r0, r1) in enumerate(zip(x.geo, x.structural_effect, x.value_effect, x.rank_t0, x.rank_t1)):
        ax.text(max(s, v, 0) + 0.004, yi, f"{r0}→{r1}", va="center", fontsize=6.5, color="#444")
    ax.set_xlabel("Change in local DFSS score $P_t(u)$, 2020 → 2023")
    share = x.structural_effect.abs().sum() / (x.structural_effect.abs() + x.value_effect.abs()).sum()
    ax.set_title(f"Decomposition of the 2020→2023 score change: {share:.0%} of total absolute change is structural", fontsize=9, loc="left")
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(FIG / f"fig3_decomposition_{sc}.png", dpi=300); plt.close(fig)


def fig4_baselines(sc="S2"):
    R = pd.read_csv(RES / f"{sc}_ranks.csv", index_col=0)
    summ = json.load(open(RES / f"{sc}_summary.json"))
    R = R.sort_values("DFSS")
    names = {"DFSS": "DFSS\n(this study)", "B1_pooled": "B1 pooled\ncomposite", "B2_imputed": "B2 imputed\nfull set",
             "B3_listwise": "B3 listwise\ncommon set", "B4_topsis": "B4 fuzzy\nTOPSIS"}
    fig, ax = plt.subplots(figsize=(7.2, 6.8))
    M = R.values.astype(float)
    ax.imshow(M, cmap="RdYlBu_r", vmin=1, vmax=27, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            d = M[i, j] - M[i, 0]
            ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=7.5,
                    fontweight="bold" if abs(d) >= 3 and j > 0 else "normal")
    ax.set_yticks(range(len(R))); ax.set_yticklabels(R.index, fontsize=7.5)
    xt = []
    for c in R.columns:
        if c == "DFSS":
            xt.append(names[c])
        else:
            a = summ["baseline_agreement"][c]
            xt.append(f"{names[c]}\nτ = {a['kendall_tau']:.2f}")
    ax.set_xticks(range(len(R.columns))); ax.set_xticklabels(xt, fontsize=7.5)
    ax.set_title("Global rank by method (bold: shift ≥ 3 positions vs DFSS)", fontsize=9, loc="left")
    fig.tight_layout(); fig.savefig(FIG / f"fig4_baselines_{sc}.png", dpi=300); plt.close(fig)


def fig5_clusters(sc="S2"):
    clus = pd.read_csv(RES / f"{sc}_clusters.csv", index_col=0)
    D = pd.read_csv(RES / f"{sc}_dfss_scores.csv", index_col=0)
    info = json.load(open(RES / f"{sc}_summary.json"))["clusters"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    ax = axes[0]
    cols = [C1, C3, C2, C4]
    for k in sorted(clus.cluster.unique()):
        s = clus[clus.cluster == k]
        ax.scatter(s.pc1, s.pc2, color=cols[k], s=36, label=f"Cluster {k} (n = {len(s)})", edgecolor="white", lw=0.5)
        for g, r in s.iterrows():
            ax.annotate(g, (r.pc1, r.pc2), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel(f"PC1 ({info['pca_explained'][0]:.0%} of variance)"); ax.set_ylabel(f"PC2 ({info['pca_explained'][1]:.0%})")
    ax.set_title(f"(a) Trajectory clusters (k = {info['k']}, silhouette = {info['silhouette'][str(info['k'])]:.2f}, "
                 f"bootstrap Jaccard = {info['bootstrap_jaccard_mean']:.2f})", fontsize=8, loc="left")
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    for k in sorted(clus.cluster.unique()):
        members = clus[clus.cluster == k].index
        for g in members:
            ax.plot(T, D.loc[g, [str(t) for t in T]], color=cols[k], alpha=0.35, lw=0.8)
        ax.plot(T, D.loc[members, [str(t) for t in T]].mean(), color=cols[k], lw=2.5, label=f"Cluster {k} mean")
    ax.set_xticks(T); ax.set_ylabel("Local DFSS score $P_t(u)$"); ax.set_title("(b) Score trajectories by cluster", fontsize=8, loc="left")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(FIG / f"fig5_clusters_{sc}.png", dpi=300); plt.close(fig)


def fig6_sensitivity(sc="S2"):
    """Rank stability across the 36-run sensitivity grid + S1 alternative."""
    import itertools
    import sys
    sys.path.insert(0, str(ROOT / "code"))
    from layer_a import dfss
    A = {int(k): v for k, v in json.load(open(DATA / f"active_sets_{sc}.json")).items()}
    A1 = {int(k): v for k, v in json.load(open(DATA / "active_sets_S1.json")).items()}
    base = dfss(A)["rank"]
    runs = {}
    for norm, w, conf, pw in itertools.product(["ref", "minmax"], ["dimension", "equal", "entropy"], [True, False], ["equal", "recency", "entropy"]):
        runs[(norm, w, conf, pw)] = dfss(A, norm, w, conf, pw)["rank"]
    runs[("S1", "dimension", True, "equal")] = dfss(A1)["rank"]
    R = pd.DataFrame(runs)
    order = base.sort_values().index
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    pos = np.arange(len(order))
    data = [R.loc[g].values for g in order]
    bp = ax.boxplot(data, positions=pos, widths=0.6, patch_artist=True, showfliers=True,
                    flierprops=dict(marker=".", ms=3, alpha=0.5), medianprops=dict(color="black"))
    for b in bp["boxes"]:
        b.set(facecolor="#c6dbef", edgecolor=C1)
    ax.plot(pos, base[order], "o", color=C2, ms=4, label="Primary specification")
    ax.set_xticks(pos); ax.set_xticklabels(order, fontsize=7.5, rotation=0)
    ax.set_ylabel("Global rank across specifications"); ax.invert_yaxis()
    ax.set_title(f"Rank stability over {len(runs)-1} alternative specifications (normalisation × weights × confidence × period weights, + S1) and the primary", fontsize=8, loc="left")
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(FIG / f"fig6_sensitivity_{sc}.png", dpi=300); plt.close(fig)
    stab = pd.DataFrame({"primary": base, "min": R.min(axis=1), "max": R.max(axis=1), "iqr": R.quantile(0.75, axis=1) - R.quantile(0.25, axis=1)})
    stab.to_csv(RES / f"{sc}_rank_stability.csv")
    return stab


if __name__ == "__main__":
    fig1_availability(); fig2_bump(); fig3_decomposition(); fig4_baselines(); fig5_clusters()
    st = fig6_sensitivity()
    print(st.sort_values("primary").to_string())
