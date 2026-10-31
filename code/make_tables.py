"""Write LaTeX tables (booktabs) from results into manuscript/tables/."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES, DATA = ROOT / "results", ROOT / "data"
# tables go to the manuscript source: final_src/ in the authors' working tree, manuscript/ in the public repository
TAB = (ROOT / "final_src" / "tables") if (ROOT / "final_src").exists() else (ROOT / "manuscript" / "tables")
TAB.mkdir(parents=True, exist_ok=True)
T = [2012, 2016, 2020, 2023]


def w(name, s):
    """Write in the CAS (cas-sc.cls) style used by the submission source: [pos=t] floats and
    tabulars wrapped in adjustbox so wide tables fit the text width."""
    s = s.replace("\\begin{table*}[t]", "\\begin{table*}[pos=t]").replace("\\begin{table}[t]", "\\begin{table}[pos=t]")
    s = s.replace("\\begin{tabular}", "\\begin{adjustbox}{max width=\\linewidth}\\begin{tabular}", 1)
    s = s.replace("\\end{tabular}", "\\end{tabular}\\end{adjustbox}", 1)
    (TAB / f"{name}.tex").write_text(s)


def esc(s):
    return str(s).replace("%", r"\%").replace("&", r"\&").replace("_", r"\_")


# Table (indicators), direction, availability, active sets
meta = pd.read_csv(DATA / "indicators.csv"); av = pd.read_csv(DATA / "availability.csv", index_col=0)
S2 = {int(k): v for k, v in json.load(open(DATA / "active_sets_S2.json")).items()}
DIMN = {"PC": "Production \\& consumption", "WM": "Waste management", "SRM": "Secondary raw materials", "CIE": "Competitiveness \\& innovation", "GSR": "Global sustainability \\& resilience"}
rows = []
last = None
for _, r in meta.iterrows():
    d = DIMN[r.dim] if r.dim != last else ""; last = r.dim
    act = "".join("\\checkmark" if r.ind in S2[t] else "--" for t in T)
    act = " & ".join("\\checkmark" if r.ind in S2[t] else "--" for t in T)
    cov = " & ".join(str(int(av.loc[r.ind, str(t)])) for t in T)
    rows.append(f"{d} & {r.ind} & {esc(r['name'])} & {r.direction[0].upper()} & {cov} & {act} \\\\")
w("tab1_indicators", r"""\begin{table*}[t]\centering\scriptsize
\caption{Indicator panel drawn from the Eurostat circular economy monitoring framework (2023 revision), benefit (B)/cost (C) direction, number of EU-27 member states reporting in each window, and membership of the framework-faithful active parameter sets $A_t$ (Scenario S2). Windows: 2011--2013, 2015--2017, 2019--2021, 2022--2024.}
\label{tab:indicators}
\begin{tabular}{@{}p{2.6cm}lp{5.2cm}lcccccccc@{}}\toprule
 & & & & \multicolumn{4}{c}{Reporting (of 27)} & \multicolumn{4}{c}{$e\in A_t$} \\ \cmidrule(lr){5-8}\cmidrule(lr){9-12}
Dimension & Code & Indicator & Dir. & 2012 & 2016 & 2020 & 2023 & 2012 & 2016 & 2020 & 2023 \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 2: DFSS scores and ranks (S2)
D = pd.read_csv(RES / "S2_dfss_scores.csv", index_col=0); LR = pd.read_csv(RES / "S2_local_ranks.csv", index_col=0)
cl = pd.read_csv(RES / "S2_clusters.csv", index_col=0); st = pd.read_csv(RES / "S2_rank_stability.csv", index_col=0)
rows = []
for g, r in D.sort_values("rank").iterrows():
    rows.append(f"{int(r['rank'])} & {g} & " + " & ".join(f"{r[str(t)]:.3f} ({int(LR.loc[g, str(t)])})" for t in T) + f" & {r['global']:.3f} & {int(st.loc[g,'min'])}--{int(st.loc[g,'max'])} & {int(cl.loc[g,'cluster'])} \\\\")
w("tab2_dfss", r"""\begin{table*}[t]\centering\footnotesize
\caption{DFSS circularity scores of EU-27 under the framework in force (Scenario S2, dimension-balanced weights): local scores $P_t(u)$ with period rank in parentheses, global score $P(u)$, rank range across the 36 alternative specifications of the sensitivity grid (Fig.~S1), and trajectory cluster (0 = consolidated leaders). MS: member state (ISO 3166 code).}
\label{tab:dfss}
\begin{tabular}{@{}rlccccccc@{}}\toprule
Rank & MS & $P_{2012}$ & $P_{2016}$ & $P_{2020}$ & $P_{2023}$ & $P(u)$ & Range & Cluster \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 3: agreement with baselines
s = json.load(open(RES / "S2_summary.json")); s1 = json.load(open(RES / "S1_summary.json"))
names = {"B1_pooled": "B1 Pooled composite (all $(t,e)$ pairs)", "B2_imputed": "B2 Full-set composite with cross-period imputation", "B3_listwise": "B3 Listwise composite (9 common indicators)", "B4_topsis": "B4 Fuzzy TOPSIS per period"}
rows = []
for k, n in names.items():
    a, b = s["baseline_agreement"][k], s1["baseline_agreement"][k]
    rows.append(f"{n} & {a['kendall_tau']:.3f} & {a['spearman']:.3f} & {a['max_abs_shift']} & {a['n_shift_ge3']} & {b['kendall_tau']:.3f} & {b['max_abs_shift']} \\\\")
pp = s["per_period"]
rows.append(r"\midrule \multicolumn{7}{l}{\emph{Per-period agreement with the DFSS local ranking (S2), Kendall $\tau_b$}} \\")
rows.append(r" & 2012 & 2016 & 2020 & 2023 & & \\ \cmidrule(lr){2-5}")
rows.append("B3 Listwise & " + " & ".join(f"{pp[str(t)]['listwise']['kendall_tau']:.2f}" for t in T) + " & & \\\\")
rows.append("B4 Fuzzy TOPSIS & " + " & ".join(f"{pp[str(t)]['topsis']['kendall_tau']:.2f}" for t in T) + " & & \\\\")
w("tab3_baselines", r"""\begin{table*}[t]\centering\footnotesize
\caption{Agreement between the DFSS global ranking and conventional aggregation baselines. Left block: Scenario S2 (framework-faithful); right block: Scenario S1 (availability-driven). Lower block: agreement per period, with the window years as column headers.}
\label{tab:baselines}
\begin{tabular}{@{}lcccccc@{}}\toprule
 & \multicolumn{4}{c}{S2} & \multicolumn{2}{c}{S1} \\ \cmidrule(lr){2-5}\cmidrule(lr){6-7}
Baseline & $\tau_b$ & $r_s$ & Max shift & $n(|\Delta|\ge3)$ & $\tau_b$ & Max shift \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 4: decomposition 2020->2023 (top movers)
d = pd.read_csv(RES / "S2_activation_decomposition.csv"); x = d[d["to"] == 2023].sort_values("structural_effect")
sel = pd.concat([x.head(7), x.tail(7)])
rows = [f"{r.geo} & {r.P_t0:.3f} & {r.P_t1:.3f} & {r.value_effect:+.3f} & {r.structural_effect:+.3f} & {r.rank_t0} & {r.rank_cf} & {r.rank_t1} \\\\" for _, r in sel.iterrows()]
share = x.structural_effect.abs().sum() / (x.structural_effect.abs() + x.value_effect.abs()).sum()
w("tab4_decomposition", r"""\begin{table*}[t]\centering\footnotesize
\caption{Decomposition of the change in local score between the 2020 and 2023 windows into a value effect (performance change evaluated on the counterfactual set $A_{2020}\cap\{e:\ e \text{ observed in } 2023\}$, which omits PAT, discontinued in 2021) and a structural effect (indicators entering $A_{2023}$: MF, RP, WG, PW, PPW, CF, GHG, MID). Seven largest negative and positive structural effects; rank$_{cf}$ is the 2023 rank that would have obtained under the counterfactual set. MS: member state. Across all 27 member states, """ + f"{share*100:.0f}\\,\\%" + r""" of total absolute change is structural.}
\label{tab:decomp}
\begin{tabular}{@{}lccrrccc@{}}\toprule
MS & $P_{2020}$ & $P_{2023}$ & Value & Structural & rank$_{2020}$ & rank$_{cf}$ & rank$_{2023}$ \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 5: PV wave summary
B = pd.read_csv(RES / "B_country_summary.csv", index_col=0).sort_values("cum_eol_2050_kt", ascending=False)
rows = [f"{g} & {r.installed_2024_MW/1e3:.1f} & {r.stock_mass_2024_kt:.0f} & {r.cum_eol_2030_kt:.0f} & {r.cum_eol_2040_kt:.0f} & {r.cum_eol_2050_kt:.0f} & {r.cum2050_p10_kt:.0f}--{r.cum2050_p90_kt:.0f} & {r.cum_eol_2040_kg_cap:.1f} & {int(r.onset_10pct)} & {int(r.mid_50pct)} \\\\" for g, r in B.iterrows()]
_mc = json.load(open(RES / "B_summary.json"))["EU27_MC_band"]
rows.append(r"\midrule EU-27 & " + f"{B.installed_2024_MW.sum()/1e3:.0f} & {B.stock_mass_2024_kt.sum():.0f} & {B.cum_eol_2030_kt.sum():.0f} & {B.cum_eol_2040_kt.sum():.0f} & {B.cum_eol_2050_kt.sum():.0f} & {_mc['cum2050_p10_kt']:.0f}--{_mc['cum2050_p90_kt']:.0f} & & & \\\\")
w("tab5_wave", r"""\begin{table*}[t]\centering\scriptsize
\caption{Projected end-of-life photovoltaic module mass by member state (central scenario, continued deployment at the 2022--2024 rate): installed capacity 2024, mass of the 2024 stock, cumulative arisings by 2030/2040/2050 (kt) with Monte Carlo p10--p90 range for 2050 (EU-27 row: quantiles of the EU-total draws), cumulative mass per capita by 2040 (Eurostat population on 1 January 2024 as retrieved on 20 October 2026), and wave timing of the stock installed by 2024 (onset = year in which that stock's cumulative arisings reach 10\,\% of its cumulative-to-2050 arisings; midpoint = 50\,\%). MS: member state.}
\label{tab:wave}
\begin{tabular}{@{}lrrrrrrrcc@{}}\toprule
MS & GW$_{2024}$ & Stock (kt) & 2030 & 2040 & 2050 & p10--p90 & kg/cap$_{2040}$ & Onset & Mid \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 6: readiness gap
G = pd.read_csv(RES / "B_readiness_gap.csv", index_col=0).sort_values("gap_rank")
rows = [f"{int(r.gap_rank)} & {g} & {r.urgency:.2f} & {r.readiness_norm:.2f} & {r.gap:.3f} & {r.gap_lo:.2f}--{r.gap_hi:.2f} & {int(r.rank_min)}--{int(r.rank_max)} & {r.archetype.split(':')[0]} \\\\" for g, r in G.iterrows()]
w("tab6_gap", r"""\begin{table*}[t]\centering\footnotesize
\caption{Readiness gap $G(u)=\mathrm{urg}(u)\,[1-\mathrm{rdy}(u)]$ of EU-27 member states, with urgency (cumulative arisings per capita by 2040 and onset earliness, ratio-normalised), readiness (DFSS global score, min--max normalised), Monte Carlo p10--p90 band of the gap, the range of ranks attained across the 600 joint draws (parameters are common to all member states within a draw, so bands can overlap while ranks are stable), and archetype (L consolidated leaders; EW converging, early wave; LW converging, late wave). MS: member state.}
\label{tab:gap}
\begin{tabular}{@{}rlcccccc@{}}\toprule
Rank & MS & Urgency & Readiness & Gap & p10--p90 & Rank range & Archetype \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 7: Layer C activation
import sys; sys.path.insert(0, str(ROOT / "code"))
from layer_c import ALTS, ALT_NAMES, HOR, ARCH, ARCH_LAB
def alab(a):
    return f"$a_{a[1]}$"
C = pd.read_csv(RES / "C_local_scores_proxy.csv"); Gc = pd.read_csv(RES / "C_global_scores_proxy.csv")
rows = []
for a in ALTS:
    cells = []
    for g in ARCH:
        for h in HOR:
            r = C[(C.archetype == g) & (C.horizon == h) & (C.alternative == a)].iloc[0]
            cells.append(f"{int(r['rank'])} ({r.score:.2f})")
        cells.append(str(int(Gc[(Gc.archetype == g) & (Gc.alternative == a)]["rank"].iloc[0])))
    rows.append(f"{alab(a)} {esc(ALT_NAMES[a])} & " + " & ".join(cells) + " \\\\")
w("tab7_activation", r"""\begin{table*}[t]\centering\scriptsize
\caption{Strategy-activation results per archetype: DFSS local rank (graded-mean score in parentheses) for horizons H1 2026--2030, H2 2031--2040, H3 2041--2050, and global Phase-3 rank $\Sigma$ (ranks are computed on unrounded scores). Institutional criteria C1--C4 are derived from public-data proxies (Table~\ref{tab:proxies}).}
\label{tab:activation}
\begin{tabular}{@{}lcccc@{\hspace{18pt}}cccc@{\hspace{18pt}}cccc@{}}\toprule
 & \multicolumn{4}{c}{L: consolidated leaders} & \multicolumn{4}{c}{EW: converging, early wave} & \multicolumn{4}{c}{LW: converging, late wave} \\ \cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}
Alternative & H1 & H2 & H3 & $\Sigma$ & H1 & H2 & H3 & $\Sigma$ & H1 & H2 & H3 & $\Sigma$ \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

# Table 8: synthesis
Sy = pd.read_csv(RES / "synthesis_table.csv")
import re as _re
def am(x):
    return _re.sub(r"a([1-7])", r"$a_\1$", str(x))
rows = [f"{esc(r.archetype)} & {r.n} & {esc(r['member_states (by gap)'])} & {r.onset_range} & {r.cum_EoL_2050_Mt:.1f} & {r.mean_readiness:.2f} & {r.mean_gap:.2f} & {am(r.top2_H1)} & {am(r.top2_H2)} & {am(r.top2_H3)} \\\\" for _, r in Sy.iterrows()]
w("tab8_synthesis", r"""\begin{table*}[t]\centering\scriptsize
\caption{Synthesis across layers: archetype membership (ordered by readiness gap), onset range, cumulative arisings by 2050, mean readiness and gap, and the two highest-ranked strategies per horizon.}
\label{tab:synthesis}
\begin{tabular}{@{}lcp{4.2cm}ccccccc@{}}\toprule
Archetype & $n$ & Member states & Onset & Mt$_{2050}$ & Rdy & Gap & H1 & H2 & H3 \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")
print("tables written:", sorted(p.name for p in TAB.glob("*.tex")))

# ---------------- Table 9: treatment bill by horizon and pathway; Table 10: comparison with IRENA
import sys
sys.path.insert(0, str(ROOT / "code"))
from layer_c import LIT, COST_SCALE, scale_cost
long = pd.read_csv(RES / "B_eol_flows_long.csv"); gap = pd.read_csv(RES / "B_readiness_gap.csv", index_col=0)
cen = long[(long.future == "flat") & (long.scenario == "central")]
HZ = {"H1": (2026, 2030), "H2": (2031, 2040), "H3": (2041, 2050)}
arch = gap.archetype.str.split(":").str[0]
rows = []
for code, name in [("L", "Leaders ($\\times$0.90)"), ("EW", "Converging, early ($\\times$1.00)"), ("LW", "Converging, late ($\\times$1.15)"), ("EU", "EU-27 (unscaled)")]:
    ms = list(arch[arch == code].index) if code != "EU" else list(arch.index)
    for j, (h, (a, b)) in enumerate(HZ.items()):
        kt = cen[(cen.geo.isin(ms)) & (cen.year >= a) & (cen.year <= b)].eol_t.sum() / 1e3
        cells = [name if j == 0 else "", f"{h} {a}--{b}", f"{kt:,.0f}"]
        for alt in ["a4", "a5", "a7"]:
            # archetype multiplier applied exactly as in layer_c.decision_matrix (EU-27 row: 1.00)
            sc = COST_SCALE.get(code, 1.0)
            l, m, u = scale_cost(LIT["C5"][h][alt], sc); gm = (l + 4 * m + u) / 6
            cells.append(f"{kt*gm/1e6:,.2f} [{kt*l/1e6:,.2f}; {kt*u/1e6:,.2f}]")
        rows.append(" & ".join(cells) + " \\\\")
    rows.append("\\addlinespace")
w("tab9_cost", r"""\begin{table*}[t]\centering\footnotesize
\caption{Indicative net treatment bill (EUR billion) by archetype and horizon under three pathways: central-scenario arisings (kt) times the literature-derived net cost per tonne (graded mean, with [lower; upper] bounds of the triangular fuzzy number; negative values are net revenue), with the archetype cost factor used in the decision matrix (0.90, 1.00, 1.15) applied to positive net costs and its reciprocal to net revenues; the EU-27 row is unscaled. Bulk = mechanical recycling ($a_4$); HV = high-value recycling ($a_5$); Landfill = disposal ($a_7$) with rising gate fees. Net costs exclude collection logistics, which \citet{markert2020} find to dominate private end-of-life cost.}
\label{tab:cost}
\begin{tabular}{@{}llrlll@{}}\toprule
Archetype & Horizon & kt & Bulk & HV & Landfill \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")

B = pd.read_csv(RES / "B_country_summary.csv", index_col=0)
IR = {"DE": (4.3, 4.3, 0.4, 1.0), "IT": (2.1, 2.2, 0.14, 0.5), "FR": (1.5, 1.8, 0.045, 0.2), "DK": (0.125, 0.13, 0.004, 0.022)}
cap = pd.read_csv(DATA / "pv_capacity_mw.csv", index_col=0)
rows = []
for g, (r50, e50, r30, e30) in IR.items():
    capi = cap[g].astype(float).replace(0.0, float("nan")).interpolate(limit_area="inside")   # interior reporting gaps (e.g. DK 2014--2017) interpolated as in Layer B
    c15 = capi.loc[2015]
    rng50 = f"{r50}--{e50}" if r50 != e50 else f"{r50}"; rng30 = f"{r30}--{e30}" if r30 != e30 else f"{r30}"
    rows.append(f"{g} & {c15/1e3:.1f} & {cap.loc[2024, g]/1e3:.1f} & {rng30} & {B.loc[g,'cum_eol_2030_kt']/1e3:.2f} & {rng50} & {B.loc[g,'cum_eol_2050_kt']/1e3:.2f} & {B.loc[g,'cum2050_p10_kt']/1e3:.2f}--{B.loc[g,'cum2050_p90_kt']/1e3:.2f} \\\\")
w("tab10_compare", r"""\begin{table}[t]\centering\footnotesize
\caption{Cumulative end-of-life PV mass (Mt): projections of \citet{irena2016} (regular--early loss, based on 2015 capacity and the IRENA/IEA deployment trajectory) versus this study (central scenario, Monte Carlo p10--p90 for 2050). Installed capacity in 2015 and 2024 (GW) from Eurostat, with interior reporting gaps interpolated (Denmark 2014--2017).}
\label{tab:compare}
\begin{tabular}{@{}lcccccc c@{}}\toprule
 & \multicolumn{2}{c}{GW} & \multicolumn{2}{c}{2030} & \multicolumn{3}{c}{2050} \\ \cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-8}
MS & 2015 & 2024 & IRENA & This study & IRENA & This study & p10--p90 \\ \midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}\end{table}
""")
print("tab9/tab10 written")


# ---------------- Table 11: institutional proxies, archetype capacities and requirement matrix
import json as _json
from layer_c_proxies import PROXIES, PROXY_DESC, RHO, CRIT as PCRIT
meta = _json.load(open(RES / "C_proxies_meta.json"))
A = pd.read_csv(RES / "C_archetype_capacity.csv", index_col=0)
cn = {"C1": "Regulatory readiness", "C2": "Enforcement \\& compliance", "C3": "Actor \\& market readiness", "C4": "Social acceptance"}
rows = []
for c in PCRIT:
    first = True
    for px in PROXIES[c]:
        rows.append((f"{c} {cn[c]}" if first else "") + f" & {esc(PROXY_DESC[px])} & " + (f"{A.loc['L',c]:.2f} & {A.loc['EW',c]:.2f} & {A.loc['LW',c]:.2f}" if first else " & & ") + " \\\\")
        first = False
    rows.append("\\addlinespace")
def rs(v):
    return (f"inv\\,{float(v[3:]):.2f}") if isinstance(v, str) else f"{v:.2f}"
rho_rows = []
for a in ALTS:
    cells = []
    for c in PCRIT:
        v1, v3 = RHO["H1"][a][c], RHO["H3"][a][c]
        cells.append(rs(v1) if v1 == v3 else f"{rs(v1)}$\\to${rs(v3)}")
    rho_rows.append(f"{alab(a)} {esc(ALT_NAMES[a])} & " + " & ".join(cells) + " \\\\")
w("tab11_proxies", r"""\begin{table*}[t]\centering\scriptsize
\caption{Institutional criteria from public data. Upper block: proxy indicators per criterion (2021--2024 means; WGI 2021--2023, ratio-normalised across EU-27 and averaged within the criterion) and the resulting archetype capacities $\kappa_{g,c}$. Lower block: requirement matrix $\rho(a,c)$ (1.00 pathway hinges on the capacity; 0.75 strongly depends; 0.50 moderately; 0.25 weakly; ``inv'' = strong institutions reduce feasibility), with H1$\to$H3 changes where the requirement evolves. Feasibility $f=1-\rho(1-\kappa)$, or $1-\rho\kappa$ for inverse entries; archetype spread gives the fuzzy support.}
\label{tab:proxies}
\begin{tabular}{@{}p{3.1cm}p{8.6cm}ccc@{}}\toprule
Criterion & Proxy indicator (source) & $\kappa_L$ & $\kappa_{EW}$ & $\kappa_{LW}$ \\ \midrule
""" + "\n".join(rows) + r"""
\midrule
Requirement $\rho(a,c)$ by alternative & C1 Regulatory readiness & C2 Enforcement & C3 Actors \& market & C4 Acceptance \\ \midrule
""" + "\n".join(r.replace(" & ", " & ", 1) for r in rho_rows) + r"""
\bottomrule\end{tabular}\end{table*}
""")
print("tab11 written")
