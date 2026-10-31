"""Layer A - Dynamic fuzzy soft set (DFSS) circularity benchmarking of EU-27.

Implements the three-phase DFSS algorithm of Saeed et al. (2026):
  Phase 1  fuzzification by reference normalisation within each (t, e)
  Phase 2  local aggregation over the active parameter set A_t
  Phase 3  global temporal aggregation over T
extended with (i) cost-type criteria, (ii) confidence-weighted local
aggregation using Eurostat quality flags, (iii) optional entropy weights.

Baselines: static pooled composite (B1), imputed full-set composite (B2),
listwise common-set composite (B3), fuzzy TOPSIS per period (B4).
"""
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA, RES = ROOT / "data", ROOT / "results"
RES.mkdir(exist_ok=True)

EU27 = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL", "HU", "IE", "IT",
        "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
T = [2012, 2016, 2020, 2023]

per = pd.read_csv(DATA / "panel_periods.csv")
meta = pd.read_csv(DATA / "indicators.csv").set_index("ind")
DIRECTION = meta.direction.to_dict()
ALL_IND = list(meta.index)


def matrices(t: int, inds: list[str], impute_conf: float = 0.25):
    """Return (X, C) DataFrames [country x indicator] of raw values and confidence
    for period t. Missing values are imputed with the EU-27 median and given
    low confidence."""
    sub = per[(per.t == t) & (per.ind.isin(inds))]
    X = sub.pivot(index="geo", columns="ind", values="value").reindex(index=EU27, columns=inds)
    C = sub.pivot(index="geo", columns="ind", values="conf").reindex(index=EU27, columns=inds)
    med = X.median()
    C = C.where(~X.isna(), impute_conf).fillna(impute_conf)
    X = X.fillna(med)
    return X, C


def fuzzify(X: pd.DataFrame, method: str = "ref") -> pd.DataFrame:
    """Phase 1. 'ref' = reference (best-performer) normalisation: benefit x/max,
    cost min/x, as in Saeed et al. (2026) extended to cost criteria.
    'minmax' = classical min-max scaling (sensitivity)."""
    M = pd.DataFrame(index=X.index, columns=X.columns, dtype=float)
    for e in X.columns:
        x = X[e].astype(float)
        if method == "ref":
            M[e] = x / x.max() if DIRECTION[e] == "benefit" else x.min() / x
        else:
            rng = x.max() - x.min()
            M[e] = (x - x.min()) / rng if DIRECTION[e] == "benefit" else (x.max() - x) / rng
    return M.clip(0, 1)


def entropy_weights(M: pd.DataFrame) -> pd.Series:
    P = M / M.sum()
    k = 1.0 / np.log(len(M))
    E = -k * (P * np.log(P.replace(0, np.nan))).sum(skipna=True)
    d = 1 - E
    return d / d.sum()


def local_scores(t, A_t, norm="ref", weights="dimension", use_conf=True):
    """Phase 2: P_t(u) = sum_e w_e c_e(u) mu_{t,e}(u) / sum_e w_e c_e(u).

    Default weighting is dimension-balanced, identical to dfss(), so that every
    derived quantity (decomposition, worked example, tables) is computed from the
    same run as the headline scores."""
    X, C = matrices(t, A_t)
    M = fuzzify(X, norm)
    if weights == "entropy":
        w = entropy_weights(M)
    elif weights == "dimension":  # equal weight per framework dimension, equal within
        dims = meta.loc[A_t, "dim"]
        nd = dims.nunique()
        w = pd.Series({e: 1.0 / (nd * (dims == dims[e]).sum()) for e in A_t})
    else:
        w = pd.Series(1.0 / len(A_t), index=A_t)
    Cw = C if use_conf else pd.DataFrame(1.0, index=C.index, columns=C.columns)
    num = (M * Cw * w).sum(axis=1)
    den = (Cw * w).sum(axis=1)
    return num / den, M, C, w


def dfss(A: dict, norm="ref", weights="dimension", use_conf=True, period_weights="equal"):
    P = pd.DataFrame({t: local_scores(t, A[t], norm, weights, use_conf)[0] for t in T})
    if period_weights == "equal":
        pw = pd.Series(1.0 / len(T), index=T)
    elif period_weights == "recency":
        pw = pd.Series([1, 2, 3, 4], index=T, dtype=float); pw /= pw.sum()
    else:  # entropy over periods
        pw = entropy_weights(P)
    P["global"] = (P[T] * pw).sum(axis=1)
    P["rank"] = P["global"].rank(ascending=False).astype(int)
    return P


# ---------------------------------------------------------------- baselines
def dim_w(inds):
    dims = meta.loc[inds, "dim"]; nd = dims.nunique()
    return pd.Series({e: 1.0 / (nd * (dims == dims[e]).sum()) for e in inds})


def b1_pooled(A):
    """Static pooled composite: average of all (t,e) memberships, e in A_t.
    Periods with more active parameters receive proportionally more weight."""
    cols = []
    for t in T:
        M = fuzzify(matrices(t, A[t])[0])
        M.columns = [f"{t}_{e}" for e in M.columns]
        cols.append(M)
    big = pd.concat(cols, axis=1)
    w = pd.concat([dim_w(A[t]).rename(lambda e, t=t: f"{t}_{e}") for t in T])
    s = (big * w).sum(axis=1) / w.sum()
    return pd.DataFrame({"global": s, "rank": s.rank(ascending=False).astype(int)})


def b2_imputed():
    """Full-set composite with cross-period imputation: every indicator is used in
    every period; values missing in a period are carried from the nearest period
    with data (invents observations)."""
    wide = per.pivot_table(index=["geo", "ind"], columns="t", values="value").reindex(columns=T)
    wide = wide.ffill(axis=1).bfill(axis=1)
    P = {}
    for t in T:
        X = wide[t].unstack("ind").reindex(index=EU27, columns=ALL_IND)
        X = X.fillna(X.median())
        P[t] = (fuzzify(X) * dim_w(ALL_IND)).sum(axis=1)
    P = pd.DataFrame(P); P["global"] = P[T].mean(axis=1)
    P["rank"] = P["global"].rank(ascending=False).astype(int)
    return P


def b3_listwise(A):
    """Common-set composite: only indicators active in every period."""
    common = [e for e in ALL_IND if all(e in A[t] for t in T)]
    P = pd.DataFrame({t: (fuzzify(matrices(t, common)[0]) * dim_w(common)).sum(axis=1) for t in T})
    P["global"] = P[T].mean(axis=1); P["rank"] = P["global"].rank(ascending=False).astype(int)
    P.attrs["common"] = common
    return P


def topsis(M: pd.DataFrame, w=None):
    """TOPSIS on a benefit-oriented membership matrix (all columns already oriented)."""
    w = pd.Series(1.0 / M.shape[1], index=M.columns) if w is None else w
    R = M / np.sqrt((M ** 2).sum())
    V = R * w
    pis, nis = V.max(), V.min()
    dp = np.sqrt(((V - pis) ** 2).sum(axis=1)); dn = np.sqrt(((V - nis) ** 2).sum(axis=1))
    return dn / (dp + dn)


def b4_topsis(A):
    P = pd.DataFrame({t: topsis(fuzzify(matrices(t, A[t])[0]), dim_w(A[t])) for t in T})
    P["global"] = P[T].mean(axis=1); P["rank"] = P["global"].rank(ascending=False).astype(int)
    return P


# ------------------------------------------------------------- diagnostics
def compare(r1: pd.Series, r2: pd.Series):
    tau = kendalltau(r1, r2).statistic; rho = spearmanr(r1, r2).statistic
    d = (r1 - r2)
    return {"kendall_tau": round(float(tau), 3), "spearman": round(float(rho), 3),
            "max_abs_shift": int(d.abs().max()), "n_shift_ge3": int((d.abs() >= 3).sum())}


def activation_decomposition(A, norm="ref", weights="dimension", use_conf=True):
    """For consecutive periods, split the change in local score into a
    structural component (A_t changes, values held at t) and a value component.
    Uses the same weighting/confidence settings as dfss() by default."""
    rows = []
    for t0, t1 in zip(T[:-1], T[1:]):
        P0 = local_scores(t0, A[t0], norm, weights, use_conf)[0]
        P1 = local_scores(t1, A[t1], norm, weights, use_conf)[0]
        # counterfactual: period t1 data evaluated with A_{t0} (restricted to what exists at t1)
        A_cf = [e for e in A[t0] if e in set(per[per.t == t1].ind)]
        Pcf = local_scores(t1, A_cf, norm, weights, use_conf)[0]
        entering = sorted(set(A[t1]) - set(A[t0])); leaving = sorted(set(A[t0]) - set(A[t1]))
        for u in EU27:
            rows.append({"from": t0, "to": t1, "geo": u, "P_t0": P0[u], "P_t1": P1[u],
                         "value_effect": Pcf[u] - P0[u], "structural_effect": P1[u] - Pcf[u],
                         "rank_t0": int(P0.rank(ascending=False)[u]), "rank_t1": int(P1.rank(ascending=False)[u]),
                         "rank_cf": int(Pcf.rank(ascending=False)[u]),
                         "entering": ",".join(entering), "leaving": ",".join(leaving)})
    return pd.DataFrame(rows)


def cluster_trajectories(P: pd.DataFrame, seed=0):
    F = P[T].copy()
    F["slope"] = np.polyfit(np.arange(len(T)), P[T].T.values, 1)[0]
    Z = StandardScaler().fit_transform(F.values)
    sil = {}
    for k in range(2, 7):
        lab = KMeans(k, n_init=50, random_state=seed).fit_predict(Z)
        sil[k] = silhouette_score(Z, lab)
    k = max(sil, key=sil.get)
    km = KMeans(k, n_init=50, random_state=seed).fit(Z)
    lab = km.labels_
    # order clusters by mean global score (0 = leaders)
    order = pd.Series(P["global"].values).groupby(lab).mean().sort_values(ascending=False).index
    remap = {old: new for new, old in enumerate(order)}
    lab = np.array([remap[l] for l in lab])
    # bootstrap stability (Jaccard of co-membership)
    rng = np.random.default_rng(seed); jac = []
    for _ in range(200):
        idx = rng.choice(len(Z), len(Z), replace=True)
        lb = KMeans(k, n_init=10, random_state=int(rng.integers(1e6))).fit(Z[idx]).predict(Z)
        a = lab[:, None] == lab[None, :]; b = lb[:, None] == lb[None, :]
        jac.append((a & b).sum() / (a | b).sum())
    hier = AgglomerativeClustering(k, linkage="ward").fit_predict(Z)
    from sklearn.metrics import adjusted_rand_score
    pca = PCA(2).fit(Z); coords = pca.transform(Z)
    out = pd.DataFrame({"geo": P.index, "cluster": lab, "pc1": coords[:, 0], "pc2": coords[:, 1],
                        "slope": F["slope"].values}).set_index("geo")
    info = {"k": int(k), "silhouette": {int(a): round(float(b), 3) for a, b in sil.items()},
            "bootstrap_jaccard_mean": round(float(np.mean(jac)), 3),
            "ari_kmeans_vs_ward": round(float(adjusted_rand_score(lab, hier)), 3),
            "pca_explained": [round(float(x), 3) for x in pca.explained_variance_ratio_]}
    return out, info


def run(scenario: str):
    A = {int(k): v for k, v in json.load(open(DATA / f"active_sets_{scenario}.json")).items()}
    out = {}
    D = dfss(A); out["dfss"] = D
    B = {"B1_pooled": b1_pooled(A), "B2_imputed": b2_imputed(), "B3_listwise": b3_listwise(A), "B4_topsis": b4_topsis(A)}
    comp = {k: compare(D["rank"], v["rank"]) for k, v in B.items()}
    # per-period agreement DFSS vs TOPSIS and vs listwise
    per_t = {t: {"topsis": compare(D[t].rank(ascending=False), B["B4_topsis"][t].rank(ascending=False)),
                 "listwise": compare(D[t].rank(ascending=False), B["B3_listwise"][t].rank(ascending=False))} for t in T}
    ranks = pd.DataFrame({"DFSS": D["rank"], **{k: v["rank"] for k, v in B.items()}})
    scores = pd.DataFrame({"DFSS": D["global"], **{k: v["global"] for k, v in B.items()}})
    dec = activation_decomposition(A)
    # Consistency guard: the decomposition's period scores must equal the DFSS
    # period scores (same run, same weights); a mismatch would mix two runs.
    for t0, t1 in zip(T[:-1], T[1:]):
        d = dec[(dec["from"] == t0) & (dec["to"] == t1)].set_index("geo")
        assert np.allclose(d["P_t0"].reindex(EU27), D[t0].reindex(EU27)), f"decomposition/dfss mismatch at {t0}"
        assert np.allclose(d["P_t1"].reindex(EU27), D[t1].reindex(EU27)), f"decomposition/dfss mismatch at {t1}"
    clus, cinfo = cluster_trajectories(D)

    # sensitivity grid
    sens = []
    base = D["rank"]
    for norm, w, conf, pw in itertools.product(["ref", "minmax"], ["dimension", "equal", "entropy"], [True, False], ["equal", "recency", "entropy"]):
        R = dfss(A, norm, w, conf, pw)["rank"]
        sens.append({"norm": norm, "weights": w, "conf": conf, "period_w": pw, **compare(base, R),
                     "top5": ",".join(R.sort_values().index[:5])})
    sens = pd.DataFrame(sens)
    # coverage threshold sensitivity (S1 only meaningful)
    thr_rows = []
    avail = pd.read_csv(DATA / "availability.csv", index_col=0)
    for thr in [18, 20, 22, 24, 26]:
        A2 = {t: [e for e in ALL_IND if avail.loc[e, str(t)] >= thr] for t in T} if scenario == "S1" else \
             {t: [e for e in A[t] if avail.loc[e, str(t)] >= thr] for t in T}
        thr_rows.append({"threshold": thr, "sizes": [len(A2[t]) for t in T], **compare(base, dfss(A2)["rank"])})

    D.to_csv(RES / f"{scenario}_dfss_scores.csv"); ranks.to_csv(RES / f"{scenario}_ranks.csv"); scores.to_csv(RES / f"{scenario}_scores.csv")
    dec.to_csv(RES / f"{scenario}_activation_decomposition.csv", index=False)
    clus.to_csv(RES / f"{scenario}_clusters.csv"); sens.to_csv(RES / f"{scenario}_sensitivity.csv", index=False)
    for k, v in B.items():
        v.to_csv(RES / f"{scenario}_{k}.csv")
    # local rankings per period
    LR = pd.DataFrame({t: D[t].rank(ascending=False).astype(int) for t in T}); LR.to_csv(RES / f"{scenario}_local_ranks.csv")
    summary = {"scenario": scenario, "A": A, "sizes": {t: len(A[t]) for t in T}, "baseline_agreement": comp,
               "per_period": per_t, "clusters": cinfo, "listwise_common": B["B3_listwise"].attrs["common"],
               "threshold_sensitivity": thr_rows,
               "sens_tau_min": float(sens.kendall_tau.min()), "sens_tau_median": float(sens.kendall_tau.median())}
    json.dump(summary, open(RES / f"{scenario}_summary.json", "w"), indent=1, default=str)
    return D, ranks, dec, clus, summary


if __name__ == "__main__":
    for sc in ["S1", "S2"]:
        D, ranks, dec, clus, summ = run(sc)
        print(f"\n================ Scenario {sc}: sizes {summ['sizes']}")
        print(ranks.sort_values("DFSS").to_string())
        print("Agreement with DFSS:", json.dumps(summ["baseline_agreement"]))
        print("Clusters:", json.dumps(summ["clusters"]))
        print(clus.groupby("cluster").apply(lambda g: ",".join(g.index)).to_string())
        big = dec[dec.structural_effect.abs() > 0.02].sort_values("structural_effect")
        print("Largest structural (activation) effects:\n", big[["from", "to", "geo", "value_effect", "structural_effect", "rank_t0", "rank_cf", "rank_t1"]].head(10).to_string())
        print("Sensitivity tau min/median:", summ["sens_tau_min"], summ["sens_tau_median"])
        print("Threshold sens:", summ["threshold_sensitivity"])
