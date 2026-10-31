# Session 3 report — Layer C: strategy pathways per archetype and horizon

**Status:** Layer C pipeline complete and validated on placeholder institutional ratings. All outputs carrying institutional information are labelled PLACEHOLDER and will be regenerated automatically when `data/expert_ratings.csv` (Delphi responses, template provided) is present.

---

## 1. Model as implemented

- **Universe** U = {A1 repair & refurbish, A2 cascaded second use, A3 export for second life, A4 bulk mechanical recycling, A5 high-value recycling, A6 formalised take-back, A7 landfill/incineration}.
- **Criteria** E = {C1 regulatory readiness, C2 enforcement feasibility, C3 actor/market readiness, C4 social acceptance (expert, benefit); C5 net treatment cost (literature, cost); C6 quality-weighted recovery, C7 avoided GHG, C8 CRM recovery Si/Ag (literature, benefit); C9 employment (literature, benefit)}.
- **Time index** T = {H1 2026–30, H2 2031–40, H3 2041–50}. **Active sets:** A_H1 = E \ {C8} (CRM recovery not yet a binding criterion before the CRMA 2030 benchmarks and PV Ecodesign requirements); A_H2 = E; A_H3 = E \ {C1} (regulatory readiness no longer discriminates once the revised WEEE/Ecodesign framework is assumed harmonised). |A_t| = 8, 9, 8.
- **Contexts** = the three archetypes from Layer B (L, CE, CL). Institutional ratings are archetype-specific; net cost carries a scale multiplier (L 0.90, CE 1.00, CL 1.15).
- **Fuzzy arithmetic.** All values are triangular fuzzy numbers. Linguistic ratings map to TFNs as in the questionnaire (VL (0,0,.25) … VH (.75,1,1)); experts are combined by fuzzy averaging. Ratio normalisation per (t, e): benefit (l/u*, m/u*, u/u*); cost (l*/u, l*/m, l*/l) after a positive shift. Local score = weighted fuzzy sum; ranking by graded mean (l + 4m + u)/6; the support (l, u) is reported (Fig. 13).
- **Weights** (placeholder until Delphi Section 6): institutional 0.40, economic 0.15, environmental 0.30, social 0.15, equal within group; renormalised over A_t.
- **Baselines.** Fuzzy TOPSIS (Chen 2000) per horizon; static pooled aggregation over all (t, e) pairs vs DFSS Phase 3.
- **Diagnostics.** Weight schemes (group / equal / institution-heavy), defuzzification (graded mean vs mode), 30 runs of ±20 % uniform perturbation of every literature TFN, fuzzy consensus index (mean absolute deviation of graded means across experts per item), leave-one-expert-out Kendall τ.

## 2. Literature-informed values (PROVISIONAL — Table D6 in `LayerC_results.xlsx`)

Net cost (EUR/t): reuse pathways net-negative to slightly positive (−300…+300); bulk mechanical 100–450 falling to 60–330; high-value 400–1,100 (H1) falling to 100–600 (H3); landfill 50–250 rising to 150–500 with landfill restrictions. Quality-weighted recovery: high-value 75–97 %; bulk 45–75 %; reuse 45–95 % declining over horizons as module vintages age. Avoided GHG (kg CO2e/t): reuse 1,000–7,000 declining; high-value 800–3,000 rising; bulk 300–1,000. CRM recovery: high-value 60–97 %; reuse retains 35–90 %; export and landfill ≈ 0. Employment (FTE/kt): refurbishment 5–25; recycling 3–14.
**Sources to cite/verify in writing:** IRENA/IEA-PVPS (2016); Latunussa et al. (2016) FRELP LCA; Deng et al. (2019) RSER review of PV recycling; Ansanelli et al. (2021); Lunardi et al. (2018); Farrell et al. (2020); Tsanakas et al. (2020) on reuse/second life; PV Cycle / SOREN cost data. I have entered ranges consistent with these works, but each cell must be checked against the cited source before submission.

## 3. Results (placeholder institutional ratings — structure, not final values)

**Activation timeline (Fig. 12).** All archetypes: A1 reuse ranks 1st in H1 and H2; A5 high-value recycling ranks 1st in H3 and 2nd (L) / 3rd (CE) / 4th (CL) in H2; A6 formalised take-back reaches 2nd in H3 everywhere and already 2nd in H2 for late-wave states; A7 last throughout. Distinctive: A3 export ranks 2nd (CL) and 3rd (CE) in H1 — attractive on cost and short-run acceptance before enforcement and CRM criteria bite — then falls to 6th, identifying 2026–2030 as a leakage window for converging states. Global (Phase 3) ranks: L: A1, A5, A6, A2; CE: A1, A5, A2, A6; CL: A1, A6, A5, A2.

**Diagnostics.** Sensitivity τ ≥ 0.90 (mean 0.95) across weight schemes, defuzzification and ±20 % literature perturbation; top-1 agreement 98 %. Fuzzy TOPSIS τ = 0.95 vs DFSS. Pooled vs DFSS global ranks identical here because |A_t| varies only 8–9–8; the cardinality-bias argument therefore rests on Layer A (11→18), which is where it should sit. Consensus and leave-one-out will populate with real panel data.

**Synthesis (Table T11).** L (DE, IT, AT, EE, FR, LU, BE, NL): onset 2030–37, 11.0 Mt by 2050, readiness 0.72, gap 0.19 → the leaders' question is high-value recovery (A5 by H2). CE (EL, BG, CY, MT, PT, ES, CZ, DK, SK, SI): onset 2030–35, 3.6 Mt, readiness 0.30, gap 0.41 → collection and enforcement before 2032, close the export window. CL (HU, RO, LT, FI, SE, HR, PL, IE, LV): onset 2036–38, 2.2 Mt, readiness 0.33, gap 0.27 → build take-back (A6) in H2 ahead of the wave.

## 4. What changes when the Delphi data arrive

Place responses in `data/expert_ratings.csv` (columns: expert_id, horizon, archetype, alternative, criterion, rating ∈ {VL, L, M, H, VH}; template provided). Re-run `python3 layer_c.py && python3 figures_c.py`. Outputs switch to label `delphi`, the PLACEHOLDER tag disappears from figures, and consensus/leave-one-out tables populate. If Section 6 weights are returned, replace `GROUP_W` with the panel means (normalised).

## 5. Next session (Session 4): manuscript

Full elsarticle draft (~12,000 words) with: literature review incl. comparative table of national PV-waste studies; methods (Layers A–C, one DFSS definition in the main text, operators and proofs in Supplement S1); results (Figs 1–13, Tables 1–8); discussion organised around the special issue's cost / environmental impact / resilience themes; policy implications by archetype; limitations. Plus Supplement S2 (data and code description, Zenodo-ready), CRediT/declarations placeholders, and a reference list with the items flagged above marked for verification.

## 6. Files (in `session3/`, superset of sessions 1–2)

`figs/fig12_activation_timeline.png`, `fig13_fuzzy_scores.png`; `LayerC_results.xlsx` (T11 synthesis; T12 local scores; T13 global vs pooled; T14 sensitivity; D5 placeholder ratings; D6 literature TFNs); `results/C_*`, `results/synthesis_table.csv`; `data/expert_ratings_TEMPLATE.csv`, `expert_ratings_PLACEHOLDER.csv`; `code/layer_c.py`, `figures_c.py`.
