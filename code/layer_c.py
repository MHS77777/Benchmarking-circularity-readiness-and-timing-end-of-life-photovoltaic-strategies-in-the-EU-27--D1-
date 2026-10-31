"""Layer C - Circular end-of-life PV strategy selection per archetype and horizon.

DFSS over U = {a1..a7} alternatives, E = {C1..C9} criteria, T = {H1, H2, H3},
with fuzzy (triangular) values carried through normalisation and weighted
aggregation; defuzzified by graded mean (l + 4m + u)/6 for ranking.

Institutional criteria C1-C4 come from the Delphi panel (file
data/expert_ratings.csv). Until responses arrive, data/expert_ratings_PLACEHOLDER.csv
is used and every output is labelled PLACEHOLDER.
"""
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

ROOT = Path(__file__).resolve().parent.parent
DATA, RES = ROOT / "data", ROOT / "results"

ALTS = ["a1", "a2", "a3", "a4", "a5", "a6", "a7"]
ALT_NAMES = {"a1": "Repair & refurbish (reuse)", "a2": "Cascaded second use", "a3": "Export for second life",
             "a4": "Bulk mechanical recycling", "a5": "High-value recycling", "a6": "Formalised take-back", "a7": "Landfill / incineration"}
CRIT = {"C1": ("Regulatory readiness", "benefit", "inst"), "C2": ("Enforcement feasibility", "benefit", "inst"),
        "C3": ("Actor & market readiness", "benefit", "inst"), "C4": ("Social acceptance", "benefit", "inst"),
        "C5": ("Net treatment cost (EUR/t)", "cost", "econ"), "C6": ("Quality-weighted recovery (%)", "benefit", "env"),
        "C7": ("Avoided GHG (kg CO2e/t)", "benefit", "env"), "C8": ("CRM recovery Si/Ag (%)", "benefit", "env"),
        "C9": ("Employment (FTE per kt)", "benefit", "soc")}
HOR = ["H1", "H2", "H3"]
HOR_LAB = {"H1": "2026–2030", "H2": "2031–2040", "H3": "2041–2050"}
ARCH = ["L", "EW", "LW"]
ARCH_LAB = {"L": "Consolidated leaders", "EW": "Converging, early wave", "LW": "Converging, late wave"}

# Time-varying active criteria: C8 (CRM recovery) becomes a binding criterion from H2
# (CRMA 2030 benchmarks, WEEE/Ecodesign PV requirements); C1 (regulatory readiness) no longer
# discriminates in H3 once the revised framework is assumed harmonised.
A_T = {"H1": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C9"],
       "H2": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"],
       "H3": ["C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]}

# Linguistic scale -> TFN (as in questionnaire)
LING = {"VL": (0, 0, 0.25), "L": (0, 0.25, 0.5), "M": (0.25, 0.5, 0.75), "H": (0.5, 0.75, 1), "VH": (0.75, 1, 1)}

# Literature-informed indicative TFNs for quantified criteria, by horizon (PROVISIONAL - cite/verify)
LIT = {
    # C5 net treatment cost (EUR/t). Anchors: D'Adamo et al. (2017) recycling cost 8-19 EUR/m2 (~500-1200 EUR/t at
    # 16 kg/m2); Markert et al. (2020) FRELP private EoL cost USD 6.7/m2 vs recovered-material value USD 13.6/m2
    # (net benefit when revenue counted); Cucchiella et al. (2015); Deng et al. (2019). Reuse pathways: resale
    # revenue exceeds testing/logistics (Tsanakas et al. 2020). Landfill: gate fees plus rising landfill taxes.
    "C5": {"H1": {"a1": (-300, -50, 200), "a2": (-200, 0, 250), "a3": (-400, -150, 100), "a4": (50, 200, 400), "a5": (-200, 400, 1100), "a6": (150, 300, 500), "a7": (50, 120, 250)},
           "H2": {"a1": (-250, 0, 250), "a2": (-150, 50, 300), "a3": (-350, -100, 150), "a4": (30, 170, 350), "a5": (-300, 200, 800), "a6": (120, 250, 420), "a7": (100, 200, 350)},
           "H3": {"a1": (-150, 50, 300), "a2": (-100, 100, 350), "a3": (-300, -50, 200), "a4": (20, 150, 320), "a5": (-400, 100, 600), "a6": (100, 200, 350), "a7": (150, 300, 500)}},
    # C6 quality-weighted material/value retention (%). FRELP demonstrated yields: Al 96 %, glass 98 %, Cu 75 %,
    # Si 39 %, Ag 11 % (Latunussa et al. 2016; Markert et al. 2020); bulk mechanical recovers glass/Al only,
    # glass downcycled (Deng et al. 2019; Heath et al. 2020); reuse retains full function for a shorter residual life.
    "C6": {"H1": {"a1": (70, 85, 95), "a2": (60, 75, 90), "a3": (50, 70, 85), "a4": (45, 55, 70), "a5": (65, 80, 90), "a6": (55, 65, 80), "a7": (0, 5, 15)},
           "H2": {"a1": (60, 75, 90), "a2": (55, 70, 85), "a3": (45, 65, 80), "a4": (50, 60, 72), "a5": (75, 85, 93), "a6": (60, 70, 82), "a7": (0, 5, 15)},
           "H3": {"a1": (45, 60, 80), "a2": (45, 60, 78), "a3": (40, 55, 75), "a4": (55, 65, 75), "a5": (80, 90, 96), "a6": (65, 75, 85), "a7": (0, 5, 15)}},
    # C7 avoided GHG (kg CO2e/t), relative ranges anchored on LCAs showing recycling credits exceed process burdens
    # (Latunussa et al. 2016; Maani et al. 2020) and reuse displacing new-module production (Tsanakas et al. 2020).
    "C7": {"H1": {"a1": (2000, 4000, 7000), "a2": (1500, 3000, 5000), "a3": (1000, 2500, 4500), "a4": (300, 600, 1000), "a5": (800, 1500, 2500), "a6": (400, 800, 1400), "a7": (-100, 0, 100)},
           "H2": {"a1": (1500, 3000, 5500), "a2": (1200, 2500, 4200), "a3": (800, 2000, 3800), "a4": (300, 600, 1000), "a5": (900, 1700, 2800), "a6": (450, 900, 1500), "a7": (-100, 0, 100)},
           "H3": {"a1": (1000, 2000, 4000), "a2": (800, 1800, 3200), "a3": (500, 1500, 3000), "a4": (300, 600, 1000), "a5": (1000, 1900, 3000), "a6": (500, 1000, 1600), "a7": (-100, 0, 100)}},
    # C8 CRM recovery Si/Ag (%). FRELP baseline Si 39 %, Ag 11 % (Latunussa et al. 2016); higher yields reported for
    # newer delamination/hydrometallurgical routes (Fiandra et al. 2019; Heath et al. 2020); reuse retains in use.
    "C8": {"H1": {"a1": (50, 70, 90), "a2": (40, 60, 80), "a3": (0, 10, 30), "a4": (0, 5, 12), "a5": (20, 45, 75), "a6": (10, 30, 50), "a7": (0, 0, 5)},
           "H2": {"a1": (45, 65, 85), "a2": (40, 55, 75), "a3": (0, 10, 30), "a4": (0, 8, 15), "a5": (40, 65, 90), "a6": (15, 35, 55), "a7": (0, 0, 5)},
           "H3": {"a1": (35, 55, 75), "a2": (30, 50, 70), "a3": (0, 10, 30), "a4": (5, 10, 20), "a5": (60, 80, 95), "a6": (20, 40, 60), "a7": (0, 0, 5)}},
    # C9 employment (FTE/kt), indicative: repair/refurbishment labour-intensive; recycling 3-14 (IRENA/IEA-PVPS 2016).
    "C9": {"H1": {"a1": (8, 15, 25), "a2": (5, 10, 18), "a3": (2, 5, 10), "a4": (3, 5, 8), "a5": (5, 8, 12), "a6": (4, 8, 14), "a7": (0.5, 1, 2)},
           "H2": {"a1": (7, 13, 22), "a2": (5, 9, 16), "a3": (2, 5, 10), "a4": (3, 5, 8), "a5": (5, 9, 13), "a6": (4, 8, 14), "a7": (0.5, 1, 2)},
           "H3": {"a1": (5, 10, 18), "a2": (4, 8, 14), "a3": (2, 4, 8), "a4": (3, 5, 8), "a5": (6, 10, 14), "a6": (4, 8, 14), "a7": (0.5, 1, 2)}},
}
# Scale multiplier on net cost by archetype (market volume / economies of scale)
COST_SCALE = {"L": 0.90, "EW": 1.00, "LW": 1.15}


def scale_cost(t, factor):
    """Archetype cost factor applied asymmetrically: positive net costs are multiplied by the
    factor (treatment is dearer where the system is less mature); negative net costs (net
    revenues) are divided by it (less revenue is realised in such contexts). Bounds are kept
    in order after the transformation."""
    t = np.asarray(t, dtype=float)
    out = np.where(t >= 0, t * factor, t / factor)
    return np.sort(out)
# Criterion-group weights (placeholder until Delphi section 6): institutional 0.40, economic 0.15, environmental 0.30, social 0.15
GROUP_W = {"inst": 0.40, "econ": 0.15, "env": 0.30, "soc": 0.15}


# ------------------------------------------------------------ fuzzy helpers
def tfn(x):
    return np.array(x, dtype=float)


def gmean(t):  # graded mean integration
    return (t[0] + 4 * t[1] + t[2]) / 6.0


def norm_benefit(t, umax):
    return tfn((t[0] / umax, t[1] / umax, t[2] / umax))


def norm_cost(t, lmin):
    """Ratio normalisation for cost TFNs; values are shifted to be positive first."""
    return tfn((lmin / t[2], lmin / t[1], lmin / t[0]))


def read_expert(path):
    """Columns: expert_id, horizon, archetype, alternative, criterion, rating(VL..VH)."""
    df = pd.read_csv(path)
    df["l"], df["m"], df["u"] = zip(*df.rating.map(LING))
    return df


def expert_tfn(df, h, g, a, c):
    s = df[(df.horizon == h) & (df.archetype == g) & (df.alternative == a) & (df.criterion == c)]
    if len(s) == 0:
        raise KeyError((h, g, a, c))
    return tfn((s.l.mean(), s.m.mean(), s.u.mean()))  # fuzzy average across experts


def consensus_index(df):
    """Mean absolute deviation of graded means across experts per item (0 = full consensus)."""
    df = df.copy(); df["gm"] = (df.l + 4 * df.m + df.u) / 6
    return df.groupby(["horizon", "archetype", "alternative", "criterion"]).gm.agg(lambda x: (x - x.mean()).abs().mean())


_PROXY = None


def proxy_tfn(h, g, a, c):
    global _PROXY
    if _PROXY is None:
        _PROXY = pd.read_csv(RES / "C_institutional_proxy.csv").set_index(["horizon", "archetype", "alternative", "criterion"])
    r = _PROXY.loc[(h, g, a, c)]
    return tfn((r.l, r.m, r.u))


def decision_matrix(df, h, g):
    """Return dict criterion -> {alt: TFN} for horizon h, archetype g, active criteria only.
    Institutional criteria come from the expert panel (df) or, when df is None, from public-data proxies."""
    D = {}
    for c in A_T[h]:
        if CRIT[c][2] == "inst":
            D[c] = {a: (proxy_tfn(h, g, a, c) if df is None else expert_tfn(df, h, g, a, c)) for a in ALTS}
        else:
            D[c] = {a: (scale_cost(LIT[c][h][a], COST_SCALE[g]) if c == "C5" else tfn(LIT[c][h][a])) for a in ALTS}
    return D


def weights(active, scheme="group"):
    if scheme == "equal":
        return {c: 1.0 / len(active) for c in active}
    groups = {c: CRIT[c][2] for c in active}
    present = {gname: [c for c in active if groups[c] == gname] for gname in GROUP_W}
    present = {k: v for k, v in present.items() if v}
    tot = sum(GROUP_W[k] for k in present)
    w = {}
    for k, cs in present.items():
        for c in cs:
            w[c] = GROUP_W[k] / tot / len(cs)
    if scheme == "inst_heavy":
        w = {c: (w[c] * 1.5 if groups[c] == "inst" else w[c]) for c in active}; s = sum(w.values()); w = {c: v / s for c, v in w.items()}
    return w


def local_scores(D, active, wscheme="group"):
    """Phase 1-2: normalise TFNs, weighted fuzzy sum -> TFN score per alternative."""
    w = weights(active, wscheme)
    N = {}
    for c in active:
        vals = D[c]
        if CRIT[c][1] == "benefit":
            umax = max(v[2] for v in vals.values()); N[c] = {a: norm_benefit(v, umax) for a, v in vals.items()}
        else:
            shift = min(v[0] for v in vals.values()) - 1.0 if min(v[0] for v in vals.values()) <= 0 else 0.0
            sh = {a: v - shift for a, v in vals.items()}; lmin = min(v[0] for v in sh.values())
            N[c] = {a: norm_cost(v, lmin) for a, v in sh.items()}
    S = {a: sum(w[c] * N[c][a] for c in active) for a in ALTS}
    return S, N, w


def fuzzy_topsis(N, w):
    """Fuzzy TOPSIS (Chen 2000) on normalised TFN matrix."""
    V = {a: {c: w[c] * N[c][a] for c in N} for a in ALTS}
    fpis = {c: tfn((1, 1, 1)) * w[c] for c in N}; fnis = {c: tfn((0, 0, 0)) for c in N}
    d = lambda x, y: np.sqrt(((x - y) ** 2).mean())
    cc = {}
    for a in ALTS:
        dp = sum(d(V[a][c], fpis[c]) for c in N); dn = sum(d(V[a][c], fnis[c]) for c in N)
        cc[a] = dn / (dp + dn)
    return pd.Series(cc)


def run(expert_file, label):
    df = read_expert(expert_file) if expert_file is not None else None
    n_exp = df.expert_id.nunique() if df is not None else 0
    rows, topsis_rows, pooled = [], [], {g: [] for g in ARCH}
    for g in ARCH:
        for h in HOR:
            D = decision_matrix(df, h, g)
            S, N, w = local_scores(D, A_T[h])
            cc = fuzzy_topsis(N, w)
            for a in ALTS:
                rows.append({"archetype": g, "horizon": h, "alternative": a, "l": S[a][0], "m": S[a][1], "u": S[a][2],
                             "score": gmean(S[a]), "topsis_cc": cc[a]})
            pooled[g].append((N, w))
    R = pd.DataFrame(rows)
    R["rank"] = R.groupby(["archetype", "horizon"]).score.rank(ascending=False).astype(int)
    R["topsis_rank"] = R.groupby(["archetype", "horizon"]).topsis_cc.rank(ascending=False).astype(int)
    # Phase 3 global per archetype (equal horizon weights) vs static pooled (all horizon-criteria pooled, cardinality-weighted)
    G = R.groupby(["archetype", "alternative"]).agg(l=("l", "mean"), m=("m", "mean"), u=("u", "mean"), score=("score", "mean")).reset_index()
    G["rank"] = G.groupby("archetype").score.rank(ascending=False).astype(int)
    pooled_rows = []
    for g in ARCH:
        allN = {}; allw = {}
        for i, (N, w) in enumerate(pooled[g]):
            for c in N:
                allN[f"{HOR[i]}_{c}"] = N[c]; allw[f"{HOR[i]}_{c}"] = w[c]
        tot = sum(allw.values())
        for a in ALTS:
            s = sum(allw[k] * allN[k][a] for k in allN) / tot
            pooled_rows.append({"archetype": g, "alternative": a, "pooled_score": gmean(s)})
    P = pd.DataFrame(pooled_rows); P["pooled_rank"] = P.groupby("archetype").pooled_score.rank(ascending=False).astype(int)
    G = G.merge(P, on=["archetype", "alternative"])
    # sensitivity: weight scheme, defuzzification, +-20 % literature perturbation
    sens = []
    rng = np.random.default_rng(0)
    base = R.set_index(["archetype", "horizon", "alternative"])["rank"]
    for ws in ["group", "equal", "inst_heavy"]:
        for k in range(30 if ws == "group" else 1):
            pert = None if k == 0 else rng.uniform(0.8, 1.2, size=1000)
            rr = []
            for g in ARCH:
                for h in HOR:
                    D = decision_matrix(df, h, g)
                    if pert is not None:
                        D = {c: {a: np.clip(v * rng.uniform(0.8, 1.2), 0, None) for a, v in vals.items()} for c, vals in D.items()}
                    S, _, _ = local_scores(D, A_T[h], ws)
                    for a in ALTS:
                        rr.append({"archetype": g, "horizon": h, "alternative": a, "score": gmean(S[a]) if k % 2 == 0 else S[a][1]})
            rr = pd.DataFrame(rr); rr["rank"] = rr.groupby(["archetype", "horizon"]).score.rank(ascending=False).astype(int)
            rk = rr.set_index(["archetype", "horizon", "alternative"])["rank"].reindex(base.index)
            sens.append({"weights": ws, "run": k, "tau": kendalltau(base, rk).statistic,
                         "top1_agree": float((rk[rk == 1].index.isin(base[base == 1].index)).mean())})
    sens = pd.DataFrame(sens)
    # leave-one-expert-out
    loo = []
    for e in (df.expert_id.unique() if df is not None else []):
        sub = df[df.expert_id != e]
        if sub.expert_id.nunique() == 0:
            continue
        rr = []
        for g in ARCH:
            for h in HOR:
                S, _, _ = local_scores(decision_matrix(sub, h, g), A_T[h])
                for a in ALTS:
                    rr.append({"archetype": g, "horizon": h, "alternative": a, "score": gmean(S[a])})
        rr = pd.DataFrame(rr); rr["rank"] = rr.groupby(["archetype", "horizon"]).score.rank(ascending=False).astype(int)
        loo.append({"left_out": e, "tau": kendalltau(base, rr.set_index(["archetype", "horizon", "alternative"])["rank"].reindex(base.index)).statistic})
    loo = pd.DataFrame(loo)
    cons = consensus_index(df) if df is not None else pd.Series(dtype=float)
    R.to_csv(RES / f"C_local_scores_{label}.csv", index=False); G.to_csv(RES / f"C_global_scores_{label}.csv", index=False)
    sens.to_csv(RES / f"C_sensitivity_{label}.csv", index=False); loo.to_csv(RES / f"C_loo_{label}.csv", index=False)
    cons.to_csv(RES / f"C_consensus_{label}.csv")
    summary = {"label": label, "n_experts": int(n_exp), "A_t": A_T, "group_weights": GROUP_W, "cost_scale": COST_SCALE,
               "sens_tau_min": float(sens.tau.min()), "sens_tau_mean": float(sens.tau.mean()), "top1_agree_mean": float(sens.top1_agree.mean()),
               "topsis_tau": float(kendalltau(R["rank"], R["topsis_rank"]).statistic),
               "pooled_vs_dfss_tau": float(kendalltau(G["rank"], G["pooled_rank"]).statistic),
               "loo_tau_min": float(loo.tau.min()) if len(loo) else None, "mean_consensus_mad": float(cons.mean()) if len(cons) else None}
    json.dump(summary, open(RES / f"C_summary_{label}.json", "w"), indent=1)
    return R, G, summary


def make_placeholder():
    """Structured placeholder ratings (single pseudo-expert), clearly labelled. Replace with Delphi data."""
    # (C1, C2, C3, C4) by archetype and horizon, per alternative
    P = {
        "L": {"H1": {"a1": "HMHH", "a2": "MMMH", "a3": "MLMM", "a4": "HHHH", "a5": "MLMH", "a6": "HHHH", "a7": "MHML"},
              "H2": {"a1": "HMHH", "a2": "HMHH", "a3": "MMLM", "a4": "HHHH", "a5": "HMHH", "a6": "HHHH", "a7": "LMLVL"},
              "H3": {"a1": "MMMM", "a2": "MMMM", "a3": "LMLL", "a4": "HHHM", "a5": "HHHH", "a6": "HHHH", "a7": "VLLVLVL"}},
        "EW": {"H1": {"a1": "MLMH", "a2": "MLLM", "a3": "MLMM", "a4": "MMMM", "a5": "LVLLM", "a6": "MLLM", "a7": "MMHM"},
               "H2": {"a1": "MMMH", "a2": "MMMM", "a3": "MLLM", "a4": "HMMH", "a5": "MLMM", "a6": "HMMH", "a7": "LLML"},
               "H3": {"a1": "MMMM", "a2": "MMMM", "a3": "LLLL", "a4": "HMHM", "a5": "HMMH", "a6": "HHHH", "a7": "VLLLVL"}},
        "LW": {"H1": {"a1": "MLLM", "a2": "LLLM", "a3": "MLMM", "a4": "MLLM", "a5": "LVLVLM", "a6": "MLLM", "a7": "MMHM"},
               "H2": {"a1": "MMMM", "a2": "MLMM", "a3": "MLLM", "a4": "MMMM", "a5": "MLLM", "a6": "HMMH", "a7": "LMML"},
               "H3": {"a1": "MMMM", "a2": "MMMM", "a3": "LLLL", "a4": "HMMM", "a5": "HMMH", "a6": "HHHH", "a7": "VLLLVL"}},
    }
    import re
    rows = []
    for g, hs in P.items():
        for h, alts in hs.items():
            for a, code in alts.items():
                toks = re.findall(r"VL|VH|L|M|H", code)
                assert len(toks) == 4, (g, h, a, code)
                for c, r in zip(["C1", "C2", "C3", "C4"], toks):
                    rows.append({"expert_id": "PLACEHOLDER", "horizon": h, "archetype": g, "alternative": a, "criterion": c, "rating": r})
    pd.DataFrame(rows).to_csv(DATA / "expert_ratings_PLACEHOLDER.csv", index=False)
    pd.DataFrame(columns=["expert_id", "horizon", "archetype", "alternative", "criterion", "rating"]).to_csv(DATA / "expert_ratings_TEMPLATE.csv", index=False)


if __name__ == "__main__":
    make_placeholder()
    # primary: institutional criteria from public-data proxies (Track A); Delphi, if responses exist, as validation
    R, G, s = run(None, "proxy")
    f = DATA / "expert_ratings.csv"
    if f.exists():
        Rd, Gd, sd = run(f, "delphi")
        from scipy.stats import kendalltau as kt
        agree = kt(R["rank"], Rd["rank"].reindex(R.index)).statistic
        json.dump({"proxy_vs_delphi_tau": float(agree), "delphi": sd}, open(RES / "C_delphi_validation.json", "w"), indent=1)
        print("Delphi validation: tau(proxy, delphi) =", round(agree, 3))
    print(json.dumps(s, indent=1))
    for g in ARCH:
        print(f"\n== {ARCH_LAB[g]}")
        piv = R[R.archetype == g].pivot(index="alternative", columns="horizon", values="rank")
        sc = R[R.archetype == g].pivot(index="alternative", columns="horizon", values="score").round(3)
        piv.columns = [f"rank_{c}" for c in piv.columns]
        print(pd.concat([piv, sc, G[G.archetype == g].set_index("alternative")[["rank", "pooled_rank"]]], axis=1).to_string())
