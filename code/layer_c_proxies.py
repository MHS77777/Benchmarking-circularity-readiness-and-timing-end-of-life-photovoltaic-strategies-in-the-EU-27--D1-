"""Institutional criteria C1-C4 for Layer C from public data (Track A).

For each member state, a capacity index on each institutional criterion is built from
public indicators (Eurostat WEEE statistics, Eurostat CE monitoring framework, World Bank
Worldwide Governance Indicators), ratio-normalised across EU-27 as in Layer A, and averaged
within the criterion. Archetype capacities are the mean (and spread) over members.
Feasibility of alternative a on criterion c in archetype g is obtained by matching the
archetype capacity against the alternative's literature-based requirement rho(a, c, h):

    f = 1 - rho * (1 - kappa)            (requirement-weighted capacity)
    f = 1 - rho * kappa                  (for the disposal baseline, where strong institutions
                                          reduce feasibility: 'inverse' entries)

Spread across archetype members gives the triangular fuzzy number (f(kappa-s), f(kappa), f(kappa+s)).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA, RES = ROOT / "data", ROOT / "results"
EU27 = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL", "HU", "IE", "IT",
        "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
ISO3 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP", "CZ": "CZE", "DK": "DNK", "EE": "EST", "FI": "FIN",
        "FR": "FRA", "DE": "DEU", "EL": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA", "LV": "LVA", "LT": "LTU", "LU": "LUX",
        "MT": "MLT", "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN", "ES": "ESP", "SE": "SWE"}
WINDOW = (2021, 2024)
ALTS = ["a1", "a2", "a3", "a4", "a5", "a6", "a7"]
CRIT = ["C1", "C2", "C3", "C4"]
HOR = ["H1", "H2", "H3"]

# ---------------------------------------------------------------- proxy definitions
PROXIES = {
    "C1": ["WEEE_COLRATE", "WGI_RQ"],                   # regulatory readiness
    "C2": ["WGI_RL", "PV_CAPTURE"],                     # enforcement and compliance
    "C3": ["CE_EMP", "CE_INV", "WEEE_RCYRATE"],         # actor and market readiness
    "C4": ["WEEE_HH_KGCAP", "MW_RECYCLING"],            # social acceptance (revealed participation)
}
PROXY_DESC = {
    "WEEE_COLRATE": "WEEE collection rate: tonnes collected / 3-year mean tonnes put on market (Eurostat env_waseleeos, EE6)",
    "WGI_RQ": "Regulatory Quality estimate (World Bank WGI)",
    "WGI_RL": "Rule of Law estimate (World Bank WGI)",
    "PV_CAPTURE": "PV panels collected / modelled central arisings, capped at 1 (Eurostat EE_LE_PVP vs Layer B)",
    "CE_EMP": "Employment in circular-economy sectors, % of total (Eurostat cei_cie011)",
    "CE_INV": "Private investment in circular-economy sectors, % GDP (Eurostat cei_cie012)",
    "WEEE_RCYRATE": "WEEE recycled and prepared for reuse / WEEE collected (Eurostat env_waseleeos, EE6)",
    "WEEE_HH_KGCAP": "WEEE collected from households, kg per inhabitant (Eurostat env_waseleeos, EE6)",
    "MW_RECYCLING": "Recycling rate of municipal waste, % (Eurostat cei_wm011)",
}

# ---------------------------------------------------------------- requirement matrix rho(a, c) by horizon
# 1.00 = pathway hinges on this institutional capacity; 0.75 strongly depends; 0.50 moderately; 0.25 weakly.
# 'inv' marks the disposal baseline, for which strong institutions reduce feasibility.
RHO = {
    "H1": {"a1": {"C1": .75, "C2": .50, "C3": .75, "C4": .75}, "a2": {"C1": .75, "C2": .50, "C3": .50, "C4": .50},
           "a3": {"C1": 1.0, "C2": 1.0, "C3": .25, "C4": .50}, "a4": {"C1": .50, "C2": .50, "C3": .75, "C4": .25},
           "a5": {"C1": .75, "C2": .50, "C3": 1.0, "C4": .25}, "a6": {"C1": .75, "C2": .75, "C3": .75, "C4": .75},
           "a7": {"C1": "inv1.0", "C2": "inv1.0", "C3": .25, "C4": "inv.75"}},
}
RHO["H2"] = {a: dict(v) for a, v in RHO["H1"].items()}
RHO["H2"]["a5"]["C3"] = .75          # high-value recycling commercialising
RHO["H3"] = {a: dict(v) for a, v in RHO["H2"].items()}
RHO["H3"]["a5"]["C3"] = .50          # mature technology, less dependent on first movers
RHO["H3"]["a6"]["C3"] = .50          # take-back networks established
RHO["H3"]["a1"]["C4"] = 1.0          # old vintages: reuse depends more on buyer acceptance
RHO["H3"]["a2"]["C4"] = .75
RHO_NOTES = {
    "a1": "Reuse needs preparing-for-reuse standards and re-certification rules (C1), refurbishers and a used-module market (C3), and buyer acceptance of used modules (C4); acceptance becomes decisive for old vintages in H3 (Tsanakas et al. 2020).",
    "a2": "Cascading through repowering is enabled by repowering rules and warranty transfer (C1) and by second-use demand (C3, C4).",
    "a3": "Export hinges on the used-equipment/waste boundary and shipment rules (C1) and on their enforcement (C2); it needs only traders (C3).",
    "a4": "Bulk recycling is already mandated by the WEEE Directive (C1 moderate) and needs treatment capacity (C3).",
    "a5": "High-value recycling needs recovery targets or CRM crediting (C1) and, above all, recyclers and secondary-material buyers (C3), a dependence that falls as the technology matures (Heath et al. 2020; Deng et al. 2019).",
    "a6": "Formalised take-back needs EPR scheme design (C1), certified collection and leakage control (C2), installer and PRO actors (C3), and willingness of owners to hand over modules (C4).",
    "a7": "Disposal is the default where regulation, enforcement and public participation are weak; strong institutions reduce its feasibility (inverse).",
}


def feas(kappa, rho):
    if isinstance(rho, str) and rho.startswith("inv"):
        return 1 - float(rho[3:]) * kappa
    return 1 - rho * (1 - kappa)


def fetch_wgi(code):
    cache = DATA / "raw" / f"wgi_{code}_{WINDOW[0]}_{WINDOW[1]}.json"
    if cache.exists():
        js = json.loads(cache.read_text())
    else:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?source=3&format=json&date={WINDOW[0]}:{WINDOW[1]}&per_page=800"
        js = requests.get(url, timeout=60).json()
        cache.parent.mkdir(exist_ok=True); cache.write_text(json.dumps(js))
    rows = [(x["countryiso3code"], int(x["date"]), x["value"]) for x in js[1] if x["value"] is not None]
    d = pd.DataFrame(rows, columns=["iso3", "year", "value"])
    inv = {v: k for k, v in ISO3.items()}
    d["geo"] = d.iso3.map(inv)
    return d.dropna(subset=["geo"]).groupby("geo").value.mean()


def build_country_proxies():
    import sys
    sys.path.insert(0, str(ROOT / "code"))
    from eurostat import get
    y0, y1 = WINDOW
    w = get("env_waseleeos")
    e6 = w[(w.waste == "EE6") & (w.geo.isin(EU27)) & (w.unit == "T")]
    piv = e6.pivot_table(index=["geo", "time"], columns="wst_oper", values="value")
    mkt = piv["MKT"].unstack("geo")
    mkt3 = mkt.rolling(3).mean().shift(1)           # mean of three preceding years
    col = piv["COL"].unstack("geo")
    colrate = (col / mkt3).loc[y0:y1].mean()
    rcyrate = (piv["RCY_PRP_REU"] / piv["COL"]).unstack("geo").loc[y0:y1].mean().clip(upper=1)
    hh = w[(w.waste == "EE6") & (w.geo.isin(EU27)) & (w.unit == "KG_HAB") & (w.wst_oper == "COL_HH")]
    hh_kg = hh.pivot(index="time", columns="geo", values="value").loc[y0:y1].mean()
    # PV capture: observed PV collected vs modelled central arisings
    pvc = pd.read_csv(DATA / "weee_pv_all.csv"); pvc = pvc[(pvc.time >= y0) & (pvc.time <= y1)].groupby("geo").value.sum()
    long = pd.read_csv(RES / "B_eol_flows_long.csv")
    cen = long[(long.future == "flat") & (long.scenario == "central") & (long.year >= y0) & (long.year <= y1)].groupby("geo").eol_t.sum()
    pv_years = pd.read_csv(DATA / "weee_pv_all.csv"); pv_years = pv_years[(pv_years.time >= y0) & (pv_years.time <= y1)].groupby("geo").time.nunique()
    capture = (pvc / cen).clip(upper=1.0)
    capture = capture.where(pv_years.reindex(capture.index).fillna(0) >= 2)   # need at least two reported years
    ann = pd.read_csv(DATA / "panel_annual.csv")
    def ce(ind):
        d = ann[(ann.ind == ind) & (ann.time >= y0) & (ann.time <= y1)]
        return d.groupby("geo").value.mean()
    P = pd.DataFrame({"WEEE_COLRATE": colrate, "WGI_RQ": fetch_wgi("GOV_WGI_RQ.EST"), "WGI_RL": fetch_wgi("GOV_WGI_RL.EST"),
                      "PV_CAPTURE": capture, "CE_EMP": ce("EMP"), "CE_INV": ce("INV"), "WEEE_RCYRATE": rcyrate,
                      "WEEE_HH_KGCAP": hh_kg, "MW_RECYCLING": ce("RRMW")}).reindex(EU27)
    return P


def normalise(P):
    N = pd.DataFrame(index=P.index)
    for c in P.columns:
        x = P[c].astype(float)
        if c.startswith("WGI"):
            x = x - x.min() + 0.1 * (x.max() - x.min())   # shift WGI estimates (can be negative) before ratio scaling
        N[c] = (x / x.max()).clip(0, 1)
    return N


def main():
    P = build_country_proxies(); P.to_csv(RES / "C_proxies_raw.csv")
    N = normalise(P); N.to_csv(RES / "C_proxies_norm.csv")
    K = pd.DataFrame({c: N[PROXIES[c]].mean(axis=1, skipna=True) for c in CRIT})     # country capacity per criterion
    cov = pd.DataFrame({c: N[PROXIES[c]].notna().sum(axis=1) for c in CRIT})
    K.to_csv(RES / "C_country_capacity.csv")
    gap = pd.read_csv(RES / "B_readiness_gap.csv", index_col=0)
    arch = gap.archetype.str.split(":").str[0]
    rows = []
    for g in ["L", "EW", "LW"]:
        members = arch[arch == g].index
        for c in CRIT:
            k = K.loc[members, c]; m, s = k.mean(), k.std(ddof=0)
            for h in HOR:
                for a in ALTS:
                    rho = RHO[h][a][c]
                    l, mm, u = sorted([feas(np.clip(m - s, 0, 1), rho), feas(m, rho), feas(np.clip(m + s, 0, 1), rho)])
                    rows.append({"horizon": h, "archetype": g, "alternative": a, "criterion": c, "kappa": m, "kappa_sd": s,
                                 "rho": rho, "l": l, "m": mm, "u": u})
    T = pd.DataFrame(rows); T.to_csv(RES / "C_institutional_proxy.csv", index=False)
    # archetype capacity table
    A = pd.DataFrame({g: K.loc[arch[arch == g].index].mean() for g in ["L", "EW", "LW"]}).T
    A.to_csv(RES / "C_archetype_capacity.csv")
    meta = {"window": WINDOW, "proxies": PROXIES, "descriptions": PROXY_DESC, "rho_notes": RHO_NOTES,
            "coverage_min": int(cov.min().min()), "missing_cells": int(P.isna().sum().sum())}
    json.dump(meta, open(RES / "C_proxies_meta.json", "w"), indent=1)
    print("Raw proxies:\n", P.round(3).to_string())
    print("\nCountry capacity per criterion:\n", K.round(3).to_string())
    print("\nArchetype capacity:\n", A.round(3).to_string())
    print("\nMissing raw cells:", int(P.isna().sum().sum()))


if __name__ == "__main__":
    main()
