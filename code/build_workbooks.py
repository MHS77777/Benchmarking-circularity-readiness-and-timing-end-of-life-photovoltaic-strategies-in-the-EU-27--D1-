"""Rebuild the three results workbooks (LayerA/B/C_results.xlsx) from results/ and data/.
Sheet names follow the numbering used in the analysis record (ANALYSIS.md)."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES, DATA = ROOT / "results", ROOT / "data"


def rd(name, **kw):
    return pd.read_csv(RES / name, **kw)


def layer_a():
    meta = pd.read_csv(DATA / "indicators.csv")
    av = pd.read_csv(DATA / "availability.csv", index_col=0)
    S2 = {int(k): v for k, v in json.load(open(DATA / "active_sets_S2.json")).items()}
    S1 = {int(k): v for k, v in json.load(open(DATA / "active_sets_S1.json")).items()}
    t1 = meta.merge(av.reset_index().rename(columns={"index": "ind"}), on="ind", how="left")
    for t in S2:
        t1[f"S2_{t}"] = t1.ind.isin(S2[t]).astype(int); t1[f"S1_{t}"] = t1.ind.isin(S1[t]).astype(int)
    sheets = {"T1_indicators_availability": t1}
    for sc in ["S2", "S1"]:
        D = rd(f"{sc}_dfss_scores.csv", index_col=0); LR = rd(f"{sc}_local_ranks.csv", index_col=0)
        T2 = D.rename(columns={c: f"P_{c}" for c in ["2012", "2016", "2020", "2023"]})
        for c in LR.columns:
            T2[f"rank_{c}"] = LR[c]
        sheets[f"T2_{sc}_DFSS_scores_ranks"] = T2.reset_index()
        sheets[f"T3_{sc}_method_ranks"] = rd(f"{sc}_ranks.csv")
        sheets[f"T4_{sc}_decomposition"] = rd(f"{sc}_activation_decomposition.csv")
        sheets[f"T5_{sc}_clusters"] = rd(f"{sc}_clusters.csv")
        sheets[f"T6_{sc}_sensitivity"] = rd(f"{sc}_sensitivity.csv")
    sheets["T7_S2_rank_stability"] = rd("S2_rank_stability.csv")
    sheets["D1_panel_periods"] = pd.read_csv(DATA / "panel_periods.csv")
    write(ROOT / "LayerA_results.xlsx", sheets)


def layer_b():
    sheets = {"T8_country_wave_summary": rd("B_country_summary.csv"),
              "T9_readiness_gap_archetypes": rd("B_readiness_gap.csv"),
              "T10_validation_WEEE": rd("B_validation_weee.csv"),
              "T10b_mass_check": rd("B_mass_check.csv")}
    long = rd("B_eol_flows_long.csv"); cen = long[(long.future == "flat") & (long.scenario == "central")]
    sheets["D2_annual_eol_t_central"] = cen.pivot_table(index="year", columns="geo", values="eol_t").reset_index()
    flat = long[long.future == "flat"].groupby(["year", "scenario"]).eol_t.sum().unstack().reset_index()
    sheets["D3_EU27_annual_by_scenario"] = flat[["year", "central", "early", "regular"]]
    write(ROOT / "LayerB_results.xlsx", sheets)


def layer_c():
    import sys; sys.path.insert(0, str(ROOT / "code"))
    from layer_c import LIT
    sheets = {"T11_synthesis": rd("synthesis_table.csv"),
              "T12_local_scores": rd("C_local_scores_proxy.csv"),
              "T13_global_vs_pooled": rd("C_global_scores_proxy.csv"),
              "T14_sensitivity": rd("C_sensitivity_proxy.csv"),
              "D5_proxies_raw": rd("C_proxies_raw.csv"),
              "D5b_country_capacity": rd("C_country_capacity.csv"),
              "D5c_institutional_TFNs": rd("C_institutional_proxy.csv")}
    rows = []
    for c, by_h in LIT.items():
        for h, by_a in by_h.items():
            for a, (l, m, u) in by_a.items():
                rows.append({"criterion": c, "horizon": h, "alternative": a, "l": l, "m": m, "u": u})
    sheets["D6_literature_TFNs"] = pd.DataFrame(rows)
    write(ROOT / "LayerC_results.xlsx", sheets)


def write(path, sheets):
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    print("wrote", path.name, len(sheets), "sheets")


if __name__ == "__main__":
    layer_a(); layer_b(); layer_c()
