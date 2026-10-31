"""Layer B figures."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, RES, FIG = ROOT / "data", ROOT / "results", ROOT / "figs"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
C1, C2, C3, C4, C5 = "#1f4e79", "#c0504d", "#7f7f7f", "#9bbb59", "#f79646"
ARCH_COL = {"L: consolidated leaders": C1, "EW: converging, early wave": C2, "LW: converging, late wave": C5}

long = pd.read_csv(RES / "B_eol_flows_long.csv")
summ = pd.read_csv(RES / "B_country_summary.csv", index_col=0)
gap = pd.read_csv(RES / "B_readiness_gap.csv", index_col=0)
info = json.load(open(RES / "B_summary.json"))
pop = pd.read_csv(DATA / "population.csv", index_col=0).loc[2024]


def fig7_eu_wave():
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.9))
    ax = axes[0]
    for s, col, lab in [("early", C2, "Early-loss (α = 2.49)"), ("central", C1, f"Central (π = {info['pi_early_share']:.2f})"), ("regular", C4, "Regular-loss (α = 5.38)")]:
        d = long[(long.future == "flat") & (long.scenario == s)].groupby("year").eol_t.sum() / 1e3
        ax.plot(d.index, d.values, color=col, lw=2 if s == "central" else 1.3, label=lab)
    d = long[(long.future == "stock_only") & (long.scenario == "central")].groupby("year").eol_t.sum() / 1e3
    ax.plot(d.index, d.values, color=C1, lw=1.2, ls="--", label="Central, 2024 stock only")
    ax.axvspan(2026, 2030, color="#eeeeee", lw=0); ax.axvspan(2031, 2040, color="#e0e0e0", lw=0); ax.axvspan(2041, 2050, color="#d0d0d0", lw=0)
    for x, t in [(2028, "H1"), (2035.5, "H2"), (2045.5, "H3")]:
        ax.text(x, ax.get_ylim()[1] * 0.02 + 30, t, ha="center", fontsize=8, color="#555")
    ax.set_xlim(2015, 2050); ax.set_ylabel("Annual end-of-life PV mass, EU-27 (kt)"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("(a) Annual arisings by loss scenario", fontsize=9, loc="left")
    ax = axes[1]
    for s, col in [("early", C2), ("central", C1), ("regular", C4)]:
        d = long[(long.future == "flat") & (long.scenario == s)].groupby("year").eol_t.sum().cumsum() / 1e6
        ax.plot(d.index, d.values, color=col, lw=2 if s == "central" else 1.3)
    for y in [2030, 2040, 2050]:
        v = info["EU27_cumulative_Mt_flat"]["central"][str(y)]
        ax.annotate(f"{v:.1f} Mt", (y, v), xytext=(-38, 6), textcoords="offset points", fontsize=7.5, color=C1)
        ax.plot([y], [v], "o", color=C1, ms=3)
    ax.set_xlim(2015, 2050); ax.set_ylabel("Cumulative end-of-life PV mass (Mt)")
    ax.set_title("(b) Cumulative arisings (continued deployment at 2022–24 rate)", fontsize=9, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "fig7_eu_wave.png", dpi=300); plt.close(fig)


def fig8_country_heatmap():
    d = long[(long.future == "flat") & (long.scenario == "central") & (long.year >= 2020)]
    M = d.pivot(index="geo", columns="year", values="eol_t")
    M = M.div(pop.reindex(M.index), axis=0) * 1e3  # kg per capita
    order = summ.sort_values(["onset_10pct", "cum_eol_2040_kg_cap"], ascending=[True, False]).index
    M = M.loc[order]
    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    im = ax.imshow(M.values, aspect="auto", cmap="YlOrRd", vmin=0, vmax=np.percentile(M.values, 97))
    ax.set_yticks(range(len(M))); ax.set_yticklabels([f"{g}  ({summ.loc[g,'onset_10pct']})" for g in M.index], fontsize=7.5)
    xs = list(M.columns); ax.set_xticks([xs.index(y) for y in range(2020, 2051, 5)]); ax.set_xticklabels(range(2020, 2051, 5))
    for i, g in enumerate(M.index):
        ax.plot(xs.index(summ.loc[g, "onset_10pct"]), i, marker="|", color="black", ms=9, mew=1.2)
        ax.plot(xs.index(summ.loc[g, "mid_50pct"]), i, marker="|", color=C1, ms=9, mew=1.2)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("Annual end-of-life PV mass (kg per capita)")
    ax.set_title("Country PV waste waves (central scenario). Ticks: onset (black) and midpoint (blue) = 10 % and 50 % of the 2024 stock’s\ncumulative-to-2050 arisings; label = onset year", fontsize=8, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "fig8_country_waves.png", dpi=300); plt.close(fig)


def fig9_validation():
    v = pd.read_csv(RES / "B_validation_weee.csv")
    v = v[v.collected_t > 0]
    hu = (v.geo == "HU") & (v.year == 2018)   # reporting outlier: shown hollow, excluded from the fit
    fig, ax = plt.subplots(figsize=(4.8, 4.4))
    lim = [1, 2e5]
    ax.plot(lim, lim, color="black", lw=0.8, ls="--", label="1 : 1")
    ax.plot(lim, [l / 3 for l in lim], color="#bbb", lw=0.6, ls=":"); ax.plot(lim, [l * 3 for l in lim], color="#bbb", lw=0.6, ls=":")
    fit = (v.collected_t > 100) & ~hu
    for col, c, lab, m in [("early_t", C2, "Early-loss", "^"), ("regular_t", C4, "Regular-loss", "v"), ("central_t", C1, "Central (calibrated)", "o")]:
        ax.scatter(v.collected_t[fit], v[col][fit], color=c, s=16, marker=m, alpha=0.85, label=lab, edgecolor="white", lw=0.3)
        ax.scatter(v.collected_t[~fit & ~hu], v[col][~fit & ~hu], color=c, s=9, marker=m, alpha=0.3, edgecolor="none")
        ax.scatter(v.collected_t[hu], v[col][hu], facecolor="none", edgecolor=c, s=16, marker=m, lw=0.7)
    r = v[hu].iloc[0]; ax.annotate("HU 2018 (excluded)", (r.collected_t, r.central_t), fontsize=6, xytext=(5, -9), textcoords="offset points", color="#666")
    for g, y, dx, dy in [("DE", 2019, 5, -9), ("DE", 2022, 5, 2), ("IT", 2021, 5, -8), ("IT", 2023, 5, 2), ("FR", 2024, 5, -8), ("ES", 2024, -34, -9)]:
        r = v[(v.geo == g) & (v.year == y)]
        if len(r):
            r = r.iloc[0]; ax.annotate(f"{g} {y}", (r.collected_t, r.central_t), fontsize=6.5, xytext=(dx, dy), textcoords="offset points")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("PV panels separately collected, Eurostat (t)\nfaint: < 100 t; hollow: HU 2018 — both excluded from the fit"); ax.set_ylabel("Modelled end-of-life arisings (t)")
    ax.set_title(f"Calibration on 2016–2024 PV collection data\n({len(v)} country-years; {int(fit.sum())} in the fit)", fontsize=8.5, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(FIG / "fig9_validation.png", dpi=300); plt.close(fig)


def fig10_map():
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    for a, col in ARCH_COL.items():
        g = gap[gap.archetype == a]
        ax.errorbar(g.readiness_norm, g.urgency, yerr=[g.urgency - g.urgency_p10, g.urgency_p90 - g.urgency], fmt="none", ecolor=col, alpha=0.4, lw=0.8)
        ax.scatter(g.readiness_norm, g.urgency, s=18 + summ.loc[g.index, "cum_eol_2040_kt"] ** 0.5 * 4, color=col, alpha=0.85, edgecolor="white", lw=0.6, label=a)
        for i, r in g.iterrows():
            ax.annotate(i, (r.readiness_norm, r.urgency), fontsize=7, xytext=(5, 3), textcoords="offset points")
    # iso-gap contours G = urg (1 - rdy): the readiness gap is read along these curves, not from quadrants
    xs = np.linspace(0.01, 0.99, 200)
    for G0 in [0.2, 0.3, 0.4, 0.5, 0.6]:
        ys = G0 / (1 - xs); m = ys <= 1.2
        ax.plot(xs[m], ys[m], color="#bbb", lw=0.7, ls=":")
        if m.any():
            ax.text(xs[m][-1], ys[m][-1], f"G = {G0}", fontsize=6.5, color="#888", ha="right", va="bottom")
    ax.set_ylim(0, 1.2); ax.set_xlim(-0.02, 1.02)
    ax.text(0.01, 0.98, "Dotted curves: equal readiness gap G\n(top three by G: EL, BG, CY in every draw)", transform=ax.transAxes, va="top", fontsize=7.5, color=C2)
    ax.set_xlabel("Circularity readiness (DFSS global score, min–max normalised)"); ax.set_ylabel("PV waste-wave urgency (ratio to the central EU maximum;\np90 can exceed 1)")
    ax.set_title("Urgency–readiness map of EU-27 (marker size ∝ √ cumulative EoL mass by 2040; bars: Monte Carlo p10–p90)", fontsize=8, loc="left")
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(FIG / "fig10_urgency_readiness_map.png", dpi=300); plt.close(fig)


def fig11_gap_and_materials():
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 5.2), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    g = gap.sort_values("gap")
    y = np.arange(len(g))
    ax.barh(y, g.gap, color=[ARCH_COL[a] for a in g.archetype], alpha=0.9)
    ax.errorbar(g.gap, y, xerr=[g.gap - g.gap_lo, g.gap_hi - g.gap], fmt="none", ecolor="black", lw=0.7, capsize=2)
    ax.set_yticks(y); ax.set_yticklabels(g.index, fontsize=7.5); ax.set_xlabel("Readiness gap = urgency × (1 − readiness)")
    ax.set_title("(a) Readiness-gap ranking (bars: Monte Carlo p10–p90)", fontsize=8.5, loc="left")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=a) for a, c in ARCH_COL.items()], fontsize=7, frameon=False, loc="lower right")
    ax = axes[1]
    mats = ["glass", "aluminium", "polymer", "silicon", "copper", "silver", "other"]
    top = summ.sort_values("cum_eol_2050_kt", ascending=False).index[:8]
    bottom = np.zeros(len(top)); cols = ["#9ecae1", "#6baed6", "#c7c7c7", "#3182bd", "#e6550d", "#fdd0a2", "#bdbdbd"]
    for m, c in zip(mats, cols):
        v = summ.loc[top, f"{m}_2050_kt"].values
        ax.bar(range(len(top)), v, bottom=bottom, color=c, label=m); bottom += v
    ax.set_xticks(range(len(top))); ax.set_xticklabels(top, fontsize=7.5); ax.set_ylabel("Cumulative EoL mass by 2050 (kt)")
    ax.set_title("(b) Material streams, eight largest member states", fontsize=8.5, loc="left")
    ax.legend(fontsize=6.5, frameon=False, ncol=2)
    fig.tight_layout(); fig.savefig(FIG / "fig11_gap_materials.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    fig7_eu_wave(); fig8_country_heatmap(); fig9_validation(); fig10_map(); fig11_gap_and_materials(); print("ok")
