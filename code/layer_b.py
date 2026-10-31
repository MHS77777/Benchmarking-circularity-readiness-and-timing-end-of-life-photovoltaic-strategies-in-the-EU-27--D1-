"""Layer B - EU-27 photovoltaic end-of-life waste wave and readiness gap.

Model (IRENA/IEA-PVPS 2016 convention): modules installed in year y with
mass M_y reach end of life according to a Weibull distribution with shape
alpha and Weibull scale (characteristic life) ETA; early-loss alpha = 2.4928, regular-loss alpha =
5.3759. A central scenario mixes both with a weight pi calibrated on the
Eurostat PV-panel WEEE collection series (2016-2018).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, RES = ROOT / "data", ROOT / "results"
EU27 = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL", "HU", "IE", "IT",
        "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
Y0, Y1, YEND = 1991, 2024, 2050
YEARS = np.arange(Y0, YEND + 1)
ALPHA = {"early": 2.4928, "regular": 5.3759}
ETA = 30.0  # IRENA/IEA-PVPS (2016): 30-year average lifetime used as the Weibull scale parameter
# module mass per MW by vintage (t/MW): IRENA/IEA-PVPS (2016) exponential fit (80-100 t/MW for the
# 2016 stock; Sander et al. 2007 used 100 t/MW); current modules ~550-600 Wp at 28-30 kg (~50 t/MW)
MASS_ANCHORS = {1990: 140.0, 2000: 120.0, 2010: 100.0, 2016: 85.0, 2020: 65.0, 2024: 55.0, 2050: 42.0}
# c-Si module composition by mass, IRENA/IEA-PVPS (2016), Sander et al. (2007), Wambach & Schlenker (2006):
# ~76 % glass, 10 % polymer, 8 % aluminium, 5 % silicon, 1 % copper, <0.1 % silver and other metals
COMPOSITION = {"glass": 0.755, "aluminium": 0.08, "polymer": 0.10, "silicon": 0.05, "copper": 0.010,
               "silver": 0.0005, "other": 0.0045}
FUTURE = {"flat": 1.0, "stock_only": 0.0, "growth3": None}  # multiplier of 2022-24 mean additions


def mass_factor(years):
    xs = np.array(sorted(MASS_ANCHORS)); ys = np.array([MASS_ANCHORS[x] for x in xs])
    return np.interp(years, xs, ys)


def weibull_cdf(a, alpha, eta=ETA):
    """IRENA/IEA-PVPS convention: F(t) = 1 - exp(-(t/T)^alpha) with T = 30-year average lifetime (scale)."""
    return 1 - np.exp(-(np.maximum(a, 0) / eta) ** alpha)


def additions():
    W = pd.read_csv(DATA / "pv_capacity_mw.csv", index_col=0).reindex(YEARS[: Y1 - Y0 + 1])
    # interior reporting gaps (zero or missing between positive values: DK 2014-17, 2019; LU 2018-20;
    # LV 2017; RO 2023) are linearly interpolated; leading gaps are zero
    for g in W.columns:
        s = W[g].copy(); pos = s[s > 0]
        if len(pos):
            lo, hi = pos.index.min(), pos.index.max()
            seg = s.loc[lo:hi].replace(0.0, np.nan).interpolate()
            s.loc[lo:hi] = seg
        W[g] = s.fillna(0.0)
    add = W.diff().clip(lower=0).fillna(0.0)
    add.loc[Y0] = W.loc[Y0]
    return add[EU27]


def cohort_masses(add, future="flat", growth=0.03):
    """Mass installed per year (t), 1991-2050, per country."""
    A = add.reindex(YEARS).copy()
    base = add.loc[2022:2024].mean()
    for y in range(Y1 + 1, YEND + 1):
        if future == "flat":
            A.loc[y] = base
        elif future == "stock_only":
            A.loc[y] = 0.0
        else:
            A.loc[y] = base * (1 + growth) ** (y - Y1)
    return A.mul(mass_factor(YEARS), axis=0)


def eol_flows(M, alpha, eta=ETA):
    """Annual end-of-life mass (t) per year and country from cohort masses M."""
    n = len(YEARS); out = np.zeros((n, M.shape[1]))
    ages = np.arange(n)
    dF = weibull_cdf(ages + 0.5, alpha, eta) - weibull_cdf(ages - 0.5, alpha, eta)
    dF[0] = weibull_cdf(0.5, alpha, eta)
    Mv = M.values
    for i in range(n):  # cohort i
        out[i:, :] += np.outer(dF[: n - i], Mv[i, :])
    return pd.DataFrame(out, index=YEARS, columns=M.columns)


def calibrate_pi(add, years=(2016, 2024)):
    """Fit mixture weight pi (early share) on Eurostat PV-panel WEEE collected: old-scope category
    EE_CPV_PVP (2016-2018) and open-scope category EE_LE_PVP (2019-2024), pooled."""
    col = pd.read_csv(DATA / "weee_pv_all.csv")
    col = col[(col.time >= years[0]) & (col.time <= years[1])]
    M = cohort_masses(add, "stock_only")
    E, R = eol_flows(M, ALPHA["early"]), eol_flows(M, ALPHA["regular"])
    rows = []
    for _, r in col.iterrows():
        if pd.notna(r.value) and r.value > 0 and r.geo in E.columns:
            rows.append({"geo": r.geo, "year": int(r.time), "scope": r.scope, "collected_t": r.value,
                         "early_t": E.loc[r.time, r.geo], "regular_t": R.loc[r.time, r.geo]})
    v = pd.DataFrame(rows)
    # pooled least squares in log space on country-years with >100 t collected; HU-2018 (reporting outlier) excluded
    big = v[(v.collected_t > 100) & ~((v.geo == "HU") & (v.year == 2018))]
    grid = np.linspace(0, 1, 201)
    def sse(p, d):
        return ((np.log(d.collected_t) - np.log(p * d.early_t + (1 - p) * d.regular_t)) ** 2).sum()
    err = [sse(p, big) for p in grid]
    pi = float(grid[int(np.argmin(err))])
    # per-country implied share (countries with >= 3 qualifying years)
    cc = {}
    for g, d in big.groupby("geo"):
        if len(d) >= 3:
            cc[g] = float(grid[int(np.argmin([sse(p, d) for p in grid]))])
    v["central_t"] = pi * v.early_t + (1 - pi) * v.regular_t
    v["ratio_col_central"] = v.collected_t / v.central_t
    v.attrs["country_pi"] = cc; v.attrs["n_fit"] = int(len(big))
    return pi, v


def mass_check(add):
    """Compare Eurostat PV modules put on market (t, open scope) with capacity additions x mass factor."""
    raw = pd.read_csv(DATA / "weee_pv_mkt.csv") if (DATA / "weee_pv_mkt.csv").exists() else None
    if raw is None:
        return None
    M = add.mul(mass_factor(add.index), axis=0)
    rows = []
    for _, r in raw.iterrows():
        if pd.notna(r.value) and r.value > 1000 and r.time in M.index:
            rows.append({"geo": r.geo, "year": int(r.time), "mkt_t": r.value, "model_t": M.loc[r.time, r.geo],
                         "add_MW": add.loc[r.time, r.geo]})
    d = pd.DataFrame(rows); d["ratio"] = d.mkt_t / d.model_t
    return d


def monte_carlo(add, n=1000, seed=1, pi=0.5):
    """Uncertainty bands: alpha ~ U(early, regular) weighted toward pi, ETA ~ Tri(25,30,35), mass x Tri(0.85,1,1.15)."""
    rng = np.random.default_rng(seed)
    M0 = cohort_masses(add, "flat")
    cum40, cum50, peak, onset = [], [], [], []
    for _ in range(n):
        alpha = ALPHA["early"] if rng.random() < pi else ALPHA["regular"]
        eta = rng.triangular(25, 30, 35); mf = rng.triangular(0.85, 1.0, 1.15)
        F = eol_flows(M0 * mf, alpha, eta)
        cum40.append(F.loc[:2040].sum()); cum50.append(F.loc[:2050].sum())
    return pd.DataFrame(cum40), pd.DataFrame(cum50)


def wave_timing(F_stock):
    """Onset (10 % of 2050 cumulative), midpoint (50 %), peak year — from existing stock only."""
    cum = F_stock.cumsum(); tot = cum.loc[YEND]
    rows = {}
    for g in F_stock.columns:
        c = cum[g] / tot[g]
        rows[g] = {"onset_10pct": int(c.index[c >= 0.10][0]), "mid_50pct": int(c.index[c >= 0.50][0]),
                   "peak_year": int(F_stock[g].loc[2025:].idxmax())}
    return pd.DataFrame(rows).T


def main():
    add = additions()
    pi, val = calibrate_pi(add)
    print(f"Calibrated early-loss share pi = {pi:.2f} on {val.attrs['n_fit']} country-years (of {len(val)}); country pi: {val.attrs['country_pi']}")
    val.to_csv(RES / "B_validation_weee.csv", index=False)
    mc = mass_check(add)
    if mc is not None:
        mc.to_csv(RES / "B_mass_check.csv", index=False)
        print("Mass check (Eurostat PV put-on-market t vs capacity additions x mass factor): median ratio",
              round(mc.ratio.median(), 2), "IQR", mc.ratio.quantile([.25, .75]).round(2).tolist(), "n", len(mc))

    scen = {}
    for fut in ["flat", "stock_only", "growth3"]:
        M = cohort_masses(add, fut)
        for name, a in ALPHA.items():
            scen[(fut, name)] = eol_flows(M, a)
        scen[(fut, "central")] = pi * scen[(fut, "early")] + (1 - pi) * scen[(fut, "regular")]
    # save long table
    long = []
    for (fut, s), F in scen.items():
        d = F.loc[2010:].stack().reset_index(); d.columns = ["year", "geo", "eol_t"]; d["future"] = fut; d["scenario"] = s
        long.append(d)
    long = pd.concat(long); long.to_csv(RES / "B_eol_flows_long.csv", index=False)

    pop = pd.read_csv(DATA / "population.csv", index_col=0).loc[2024, EU27]
    C = scen[("flat", "central")]
    summ = pd.DataFrame({
        "installed_2024_MW": pd.read_csv(DATA / "pv_capacity_mw.csv", index_col=0).loc[2024, EU27],
        "stock_mass_2024_kt": cohort_masses(add, "stock_only").sum() / 1e3,
        "cum_eol_2030_kt": C.loc[:2030].sum() / 1e3, "cum_eol_2040_kt": C.loc[:2040].sum() / 1e3,
        "cum_eol_2050_kt": C.loc[:2050].sum() / 1e3,
        "cum_eol_2040_kg_cap": C.loc[:2040].sum() / pop * 1e3,
        "cum_eol_2050_early_kt": scen[("flat", "early")].loc[:2050].sum() / 1e3,
        "cum_eol_2050_regular_kt": scen[("flat", "regular")].loc[:2050].sum() / 1e3,
        "peak_annual_kt_2025_50": C.loc[2025:].max() / 1e3,
    })
    tm = wave_timing(pi * scen[("stock_only", "early")] + (1 - pi) * scen[("stock_only", "regular")])
    summ = summ.join(tm)
    c40, c50 = monte_carlo(add, n=600, pi=pi)
    summ["cum2040_p10_kt"] = c40.quantile(0.10) / 1e3; summ["cum2040_p90_kt"] = c40.quantile(0.90) / 1e3
    summ["cum2050_p10_kt"] = c50.quantile(0.10) / 1e3; summ["cum2050_p90_kt"] = c50.quantile(0.90) / 1e3
    # material streams by 2050 (central)
    for m, f in COMPOSITION.items():
        summ[f"{m}_2050_kt"] = summ.cum_eol_2050_kt * f
    summ = summ.round(2); summ.to_csv(RES / "B_country_summary.csv")

    # ---------------- readiness gap and archetypes
    A = pd.read_csv(RES / "S2_dfss_scores.csv", index_col=0)
    clus = pd.read_csv(RES / "S2_clusters.csv", index_col=0)
    urg_mass = summ.cum_eol_2040_kg_cap / summ.cum_eol_2040_kg_cap.max()
    earl = (YEND - summ.onset_10pct) / (YEND - 2026)
    urg_time = earl / earl.max()
    urgency = 0.5 * (urg_mass + urg_time)
    # MC urgency band
    u10 = 0.5 * ((c40.quantile(0.10) / pop * 1e3) / summ.cum_eol_2040_kg_cap.max() + urg_time)
    u90 = 0.5 * ((c40.quantile(0.90) / pop * 1e3) / summ.cum_eol_2040_kg_cap.max() + urg_time)
    r = A["global"]; r_norm = (r - r.min()) / (r.max() - r.min())
    r23 = A["2023"]; r23_norm = (r23 - r23.min()) / (r23.max() - r23.min())
    gap = pd.DataFrame({"urgency": urgency, "urgency_p10": u10, "urgency_p90": u90,
                        "readiness_global": r, "readiness_norm": r_norm, "readiness_2023_norm": r23_norm,
                        "gap": urgency * (1 - r_norm), "gap_2023": urgency * (1 - r23_norm),
                        "cluster": clus.cluster, "onset_10pct": summ.onset_10pct})
    gap["gap_lo"] = u10 * (1 - r_norm); gap["gap_hi"] = u90 * (1 - r_norm)
    gap["gap_rank"] = gap.gap.rank(ascending=False).astype(int)
    # Rank probabilities from the joint Monte Carlo draws (parameters are common to all
    # countries within a draw, so marginal bands may overlap while ranks are stable).
    kg_d = c40[EU27] / pop[EU27] * 1e3
    gap_d = 0.5 * (kg_d / summ.cum_eol_2040_kg_cap.max() + urg_time[EU27]) * (1 - r_norm[EU27])
    rk = gap_d.rank(axis=1, ascending=False)
    gap["p_rank1"] = (rk == 1).mean(); gap["p_top3"] = (rk <= 3).mean(); gap["p_top4"] = (rk <= 4).mean()
    gap["rank_min"] = rk.min().astype(int); gap["rank_max"] = rk.max().astype(int)
    gap["rank_median"] = rk.median()
    rk.to_csv(RES / "B_gap_rank_draws.csv", index=False)
    med_onset = gap.loc[gap.cluster == 1, "onset_10pct"].median()
    gap["archetype"] = np.where(gap.cluster == 0, "L: consolidated leaders",
                       np.where(gap.onset_10pct <= med_onset, "EW: converging, early wave", "LW: converging, late wave"))
    gap = gap.round(3).sort_values("gap", ascending=False); gap.to_csv(RES / "B_readiness_gap.csv")

    eu = {s: {y: float(scen[("flat", s)].loc[:y].sum().sum() / 1e6) for y in [2030, 2040, 2050]} for s in ["early", "central", "regular"]}
    eu_stock = {s: float(scen[("stock_only", s)].loc[:2050].sum().sum() / 1e6) for s in ["early", "central", "regular"]}
    eu_tot40, eu_tot50 = c40[EU27].sum(axis=1) / 1e3, c50[EU27].sum(axis=1) / 1e3   # EU-level quantiles from the EU-total draws
    eu_band = {"cum2040_p10_kt": float(eu_tot40.quantile(0.10)), "cum2040_p90_kt": float(eu_tot40.quantile(0.90)),
               "cum2050_p10_kt": float(eu_tot50.quantile(0.10)), "cum2050_p90_kt": float(eu_tot50.quantile(0.90)),
               "sum_of_country_p10_2050_kt": float(summ.cum2050_p10_kt.sum()), "sum_of_country_p90_2050_kt": float(summ.cum2050_p90_kt.sum())}
    info = {"pi_early_share": pi, "country_pi": val.attrs["country_pi"], "n_fit": val.attrs["n_fit"], "ETA": ETA, "alpha": ALPHA, "mass_anchors_t_per_MW": MASS_ANCHORS,
            "composition": COMPOSITION, "EU27_cumulative_Mt_flat": eu, "EU27_cumulative_2050_Mt_stock_only": eu_stock, "EU27_MC_band": eu_band,
            "EU27_peak_year_central_flat": int(scen[("flat", "central")].sum(axis=1).loc[2025:].idxmax()),
            "EU27_peak_annual_kt_central_flat": float(scen[("flat", "central")].sum(axis=1).loc[2025:].max() / 1e3),
            "archetype_counts": gap.archetype.value_counts().to_dict(), "median_onset_converging": float(med_onset)}
    json.dump(info, open(RES / "B_summary.json", "w"), indent=1)
    print(json.dumps(info, indent=1))
    print(summ[["installed_2024_MW", "stock_mass_2024_kt", "cum_eol_2040_kt", "cum_eol_2050_kt", "cum_eol_2040_kg_cap", "onset_10pct", "mid_50pct", "peak_year"]].sort_values("cum_eol_2040_kg_cap", ascending=False).to_string())
    print(gap[["urgency", "readiness_norm", "gap", "gap_lo", "gap_hi", "gap_rank", "archetype"]].to_string())


if __name__ == "__main__":
    main()
