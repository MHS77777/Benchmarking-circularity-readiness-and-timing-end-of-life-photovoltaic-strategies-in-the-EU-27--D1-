"""Build the EU-27 circular-economy indicator panel from Eurostat CE monitoring
framework tables and derive the indicator-availability table that defines the
active parameter set A_t for each period.

Periods are 3-year windows centred on the nominal years T = {2012, 2016, 2020,
2023}; a country's period value is the mean of available annual values in the
window, and its confidence weight reflects Eurostat quality flags and the
number of years available.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from eurostat import EU27, get

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"

# code, short name, dimension, direction, dataset, filter dict
INDICATORS = [
    ("MF",    "Material footprint (t/cap)",                      "PC",  "cost",    "cei_pc020", {}),
    ("RP",    "Resource productivity (PPS/kg)",                  "PC",  "benefit", "cei_pc030", {"unit": "PPS_KG"}),
    ("WG",    "Total waste generation (kg/cap)",                 "PC",  "cost",    "cei_pc034", {}),
    ("WGDP",  "Waste excl. major mineral per GDP (kg/kEUR)",     "PC",  "cost",    "cei_pc032", {}),
    ("MW",    "Municipal waste generation (kg/cap)",             "PC",  "cost",    "cei_pc031", {}),
    ("FW",    "Food waste (kg/cap)",                             "PC",  "cost",    "cei_pc035", {}),
    ("PW",    "Packaging waste generation (kg/cap)",             "PC",  "cost",    "cei_pc040", {}),
    ("PPW",   "Plastic packaging waste generation (kg/cap)",     "PC",  "cost",    "cei_pc050", {}),
    ("RRMW",  "Recycling rate of municipal waste (%)",           "WM",  "benefit", "cei_wm011", {}),
    ("RRAW",  "Recycling rate of all waste excl. mineral (%)",   "WM",  "benefit", "cei_wm010", {}),
    ("RRPW",  "Recycling rate of packaging waste (%)",           "WM",  "benefit", "cei_wm020", {"waste": "W1501"}),
    ("RRWEEE","Recycling rate of WEEE separately collected (%)", "WM",  "benefit", "cei_wm060", {}),
    ("CMU",   "Circular material use rate (%)",                  "SRM", "benefit", "cei_srm030", {}),
    ("INV",   "Private investment in CE sectors (% GDP)",        "CIE", "benefit", "cei_cie012", {"indic_env": "INV", "unit": "PC_GDP"}),
    ("GVA",   "Gross value added of CE sectors (% GDP)",         "CIE", "benefit", "cei_cie012", {"indic_env": "GVA", "unit": "PC_GDP"}),
    ("EMP",   "Employment in CE sectors (% total, FTE)",         "CIE", "benefit", "cei_cie011", {"unit": "PC_EMP_FTE"}),
    ("PAT",   "Recycling/SRM patents (per million inh.)",        "CIE", "benefit", "cei_cie020", {"unit": "P_MHAB"}),
    ("CF",    "Consumption footprint (score/inh.)",              "GSR", "cost",    "cei_gsr010", {"cons_fp": "SWS", "unit": "P_HAB"}),
    ("GHG",   "GHG emissions from production (kg/cap)",          "GSR", "cost",    "cei_gsr011", {}),
    ("MID",   "Material import dependency (%)",                  "GSR", "cost",    "cei_gsr030", {}),
]

DIM_NAMES = {"PC": "Production and consumption", "WM": "Waste management",
             "SRM": "Secondary raw materials", "CIE": "Competitiveness and innovation",
             "GSR": "Global sustainability and resilience"}

PERIODS = {2012: (2011, 2013), 2016: (2015, 2017), 2020: (2019, 2021), 2023: (2022, 2024)}

# Flag-based confidence: Eurostat observation status codes
FLAG_CONF = {"": 1.0, "b": 0.9, "p": 0.85, "e": 0.75, "d": 0.75, "s": 0.75, "u": 0.5, "c": 0.5, "z": 0.0, "n": 0.0}


def flag_conf(flag: str) -> float:
    if not flag:
        return 1.0
    return min(FLAG_CONF.get(ch, 0.8) for ch in flag)


def load_annual() -> pd.DataFrame:
    frames = []
    for code, name, dim, direction, ds, filt in INDICATORS:
        df = get(ds)
        for k, v in filt.items():
            df = df[df[k] == v]
        df = df[df.geo.isin(EU27)][["geo", "time", "value", "flag"]].copy()
        df["ind"] = code
        frames.append(df)
    annual = pd.concat(frames, ignore_index=True)
    annual["conf"] = annual.flag.map(flag_conf)
    return annual


def to_periods(annual: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (ind, geo), g in annual.groupby(["ind", "geo"]):
        for t, (a, b) in PERIODS.items():
            w = g[(g.time >= a) & (g.time <= b)]
            if len(w) == 0:
                continue
            # confidence: mean flag confidence, discounted if only 1 of 3 years
            conf = w.conf.mean() * (1.0 if len(w) >= 2 else 0.9)
            rows.append({"ind": ind, "geo": geo, "t": t, "value": w.value.mean(),
                         "n_years": len(w), "conf": conf,
                         "flags": "".join(sorted(set("".join(w.flag))))})
    return pd.DataFrame(rows)


def main():
    annual = load_annual()
    annual.to_csv(OUT / "panel_annual.csv", index=False)
    per = to_periods(annual)
    per.to_csv(OUT / "panel_periods.csv", index=False)

    meta = pd.DataFrame(INDICATORS, columns=["ind", "name", "dim", "direction", "dataset", "filter"])
    meta["filter"] = meta["filter"].apply(json.dumps)
    meta.to_csv(OUT / "indicators.csv", index=False)

    # availability: number of EU-27 countries with a value in each period
    avail = per.pivot_table(index="ind", columns="t", values="geo", aggfunc="count").reindex(meta.ind).fillna(0).astype(int)
    first_year = annual.groupby("ind").time.min().reindex(meta.ind)
    last_year = annual.groupby("ind").time.max().reindex(meta.ind)
    avail_tab = avail.copy()
    avail_tab.insert(0, "dimension", meta.set_index("ind").dim)
    avail_tab.insert(1, "direction", meta.set_index("ind").direction)
    avail_tab["first_year"] = first_year
    avail_tab["last_year"] = last_year
    avail_tab.to_csv(OUT / "availability.csv")
    print(avail_tab.to_string())

    # active parameter sets: coverage >= 80 % of EU-27 (22 countries)
    THRESH = 22
    A = {t: [i for i in meta.ind if avail.loc[i, t] >= THRESH] for t in PERIODS}
    json.dump(A, open(OUT / "active_sets_S1.json", "w"), indent=1)
    # Scenario S2: framework-faithful A_t. 2018 framework indicators (retro-applied
    # to 2012/2016), food waste enters 2020 (framework 2018 item, data from 2020),
    # 2023 revision adds MF, RP, WG, PW, PPW, CF, GHG, MID.
    FW2018 = ["WGDP", "MW", "RRMW", "RRAW", "RRPW", "RRWEEE", "CMU", "INV", "GVA", "EMP", "PAT"]
    S2 = {2012: FW2018, 2016: FW2018, 2020: FW2018 + ["FW"],
          2023: [i for i in meta.ind if avail.loc[i, 2023] >= THRESH]}
    S2 = {t: [i for i in s if avail.loc[i, t] >= THRESH] for t, s in S2.items()}
    json.dump(S2, open(OUT / "active_sets_S2.json", "w"), indent=1)
    print("\nScenario S2 (framework-faithful):")
    for t, s in S2.items():
        print(f"  A_{t} ({len(s)}): {', '.join(s)}")
    print("\nActive parameter sets A_t (coverage >= %d/27):" % THRESH)
    for t, s in A.items():
        print(f"  A_{t} ({len(s)}): {', '.join(s)}")

    # flag summary
    fl = per.groupby("t").apply(lambda g: pd.Series({"obs": len(g), "flagged": (g["flags"] != "").sum(),
                                                       "mean_conf": g.conf.mean()}))
    print("\nFlag summary by period:\n", fl)


if __name__ == "__main__":
    main()
