"""Cross-layer synthesis table."""
import pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "results"
gap = pd.read_csv(R / "B_readiness_gap.csv", index_col=0); s = pd.read_csv(R / "B_country_summary.csv", index_col=0)
lab = "proxy"
C = pd.read_csv(R / f"C_local_scores_{lab}.csv")
rows = []
for code, name in [("L", "L: consolidated leaders"), ("EW", "EW: converging, early wave"), ("LW", "LW: converging, late wave")]:
    g = gap[gap.archetype == name].sort_values("gap_rank")
    top = {h: ", ".join(C[(C.archetype == code) & (C.horizon == h)].sort_values("rank").alternative[:2]) for h in ["H1", "H2", "H3"]}
    rows.append({"archetype": name, "n": len(g), "member_states (by gap)": ", ".join(g.index),
                 "onset_range": f"{int(s.loc[g.index,'onset_10pct'].min())}–{int(s.loc[g.index,'onset_10pct'].max())}",
                 "cum_EoL_2050_Mt": round(s.loc[g.index, "cum_eol_2050_kt"].sum() / 1e3, 2),
                 "mean_readiness": round(g.readiness_norm.mean(), 2), "mean_gap": round(g.gap.mean(), 2),
                 "top2_H1": top["H1"], "top2_H2": top["H2"], "top2_H3": top["H3"]})
T = pd.DataFrame(rows); T.to_csv(R / "synthesis_table.csv", index=False); print(T.to_string())
