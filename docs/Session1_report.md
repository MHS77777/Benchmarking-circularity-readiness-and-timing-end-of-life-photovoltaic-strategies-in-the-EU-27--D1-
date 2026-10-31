# Session 1 report — Layer A: DFSS circularity benchmarking of EU-27

**Paper (working title):** From benchmark to pathway: a dynamic fuzzy soft set framework for circularity readiness and end-of-life photovoltaic strategy selection in the European Union
**Target:** RSER special issue *Embedding Circular Practices into Renewable and Sustainable Energy Production and Management* (deadline 31 Oct 2026)
**Status:** Layer A complete (data, model, baselines, decomposition, clustering, sensitivity, figures). Delphi Round-1 questionnaire drafted.

---

## 1. Decisions taken this session (and why)

| Decision | Choice | Rationale |
|---|---|---|
| Time index T | 3-year windows centred on 2012, 2016, 2020, 2023 (2011–13, 2015–17, 2019–21, 2022–24); period value = mean of available years | Absorbs single-year reporting gaps; windows straddle the 2018 and 2023 framework revisions |
| Universe U | EU-27 | Cleanest longitudinal panel |
| Indicator set E | 20 country-level indicators of the Eurostat CE monitoring framework (2023 revision); EOL-RIR, EU self-sufficiency (EU-level only) and trade in recyclables (no direction) excluded | All indicators must have a defensible benefit/cost direction |
| Active set A_t — **primary (S2, framework-faithful)** | 2012, 2016: 2018-framework indicators (11); 2020: +food waste (12, but RRAW drops on coverage → 11); 2023: 2023-revision set (18) | The yardstick the EU itself applied; produces the policy-relevant structural break |
| Active set A_t — **sensitivity (S1, availability-driven)** | indicator active if ≥ 22/27 countries report in the window (19, 19, 19, 18) | What the data allow, irrespective of framework membership |
| Fuzzification | reference normalisation: benefit μ = x/max, cost μ = min/x (as Saeed et al. 2026, extended to cost criteria); min-max as sensitivity | Consistent with the DFSS paper; μ = 1 for the best EU performer |
| Missing values inside A_t | EU-27 median, confidence 0.25 | Never silently imputed: low confidence weight |
| Data-quality flags | Eurostat status codes → confidence c ∈ [0,1] (e/d/s 0.75, p 0.85, b 0.90, u/c 0.50); confidence-weighted local aggregation | Bookkeeping, not a lever: rankings change by τ < 0.01 when switched off |
| Criterion weights (**primary**) | dimension-balanced: equal weight per framework dimension, equal within | JRC/OECD composite-indicator practice; most stable specification (mean τ 0.89 vs alternatives) |
| Period weights | equal (DFSS Phase 3); recency and entropy as sensitivity | Structural fairness principle of the DFSS paper |
| Baselines | B1 pooled composite, B2 imputed full-set composite, B3 listwise common-set composite, B4 fuzzy TOPSIS per period | Answers "why not a composite index?" empirically |

Change from the plan: the Pakistan case is replaced by a pan-EU PV waste-wave layer (Session 2), so Layer C will select strategies per *readiness archetype* and compute a country-level readiness gap.

## 2. Data

Source: Eurostat dissemination API (JSON-stat), retrieved 4 Sep 2026. Datasets: cei_pc020/030/031/032/034/035/040/050, cei_wm010/011/020/060, cei_srm030, cei_cie011/012/020, cei_gsr010/011/030. Raw JSON cached in `data/raw/`; annual panel in `data/panel_annual.csv` (with flags); period panel in `data/panel_periods.csv`.

Availability by window (countries reporting, of 27) — see Fig. 1 and `data/availability.csv`. Structural facts that define A_t:
- Food waste (FW): no data before 2020 → activates in A_2020.
- Recycling rate of all waste excl. mineral (RRAW): 25, 24, 21, 0 → deactivates after 2016 (coverage rule) and is discontinued after 2020.
- Patents (PAT): series ends 2021 → inactive in A_2023.
- WEEE recycling rate: 25/27 in 2023.
- Flagged observations: 8 % (2012) → 23 % (2023); mean confidence 0.972 → 0.962.

## 3. Method as implemented (for the Methods section)

Notation follows Saeed (2025) and Saeed et al. (2026). For each t ∈ T, e ∈ A_t, u ∈ U:

- **Phase 1 (fuzzification).** μ_{t,e}(u) = x_{t,e}(u)/max_v x_{t,e}(v) for benefit criteria; μ_{t,e}(u) = min_v x_{t,e}(v)/x_{t,e}(u) for cost criteria.
- **Phase 2 (local, confidence-weighted).** P_t(u) = Σ_{e∈A_t} w_{t,e} c_{t,e}(u) μ_{t,e}(u) / Σ_{e∈A_t} w_{t,e} c_{t,e}(u), with w dimension-balanced and c from quality flags. Reduces to the DFSS paper's Phase 2 when w is uniform and c ≡ 1.
- **Phase 3 (global).** P(u) = (1/|T|) Σ_t P_t(u).
- **Activation decomposition.** For consecutive periods t0 → t1: ΔP = [P_{t1}^{A_{t0}}(u) − P_{t0}(u)] (value effect) + [P_{t1}(u) − P_{t1}^{A_{t0}}(u)] (structural effect), where P_{t1}^{A_{t0}} evaluates period-t1 data with the period-t0 active set.
- **Clustering.** Features (P_2012, P_2016, P_2020, P_2023, OLS slope), standardised; k-means (k by silhouette, k = 2..6), 200 bootstrap re-fits (Jaccard co-membership), Ward agreement (ARI), PCA for display.
- **Sensitivity grid.** 2 normalisations × 3 weightings × 2 confidence settings × 3 period weightings = 36 specifications + S1; rank stability per country (Fig. 6, `results/S2_rank_stability.csv`); coverage threshold 18–26.
- Complexity O(|T|·|A_max|·|U|), consistent with the DFSS paper.

## 4. Results (Scenario S2, primary)

**Global DFSS ranking.** NL 0.682 (1), BE 0.616, LU 0.608, FR 0.575, IT 0.563, AT 0.561, DE 0.546, EE 0.538, CZ 0.510, SI 0.498, ES 0.488, SE 0.479, DK 0.476, PL 0.475, SK 0.474, LV 0.469, HR 0.460, FI 0.454, LT 0.452, IE 0.446, HU 0.439, MT 0.438, PT 0.411, BG 0.393, CY 0.391, RO 0.383, EL 0.336 (27).

**Period ranks (Fig. 2).** LU: 1, 3, 3, 10. NL: 2, 1, 1, 1. EE: 6, 17, 6, 2. DK: 11, 8, 15, 22. HR: 19, 18, 17, 12. SK: 18, 21, 12, 8.

**Structural break at the 2023 revision (Fig. 3, headline).** 65 % of the total absolute change in local scores between the 2020 and 2023 windows is attributable to the eight indicators entering A_2023 (MF, RP, WG, PW, PPW, CF, GHG, MID), not to performance change. Largest structural effects: LU −0.112 (value effect −0.004; rank 1 → 14 in the period ranking), EE −0.099, DE −0.065, AT −0.061, DK −0.057, IE −0.057; positive: RO +0.112, EL +0.107, HR +0.069 (value effect 0.000; period rank 15 → 2), BG +0.056. Interpretation: the 2023 revision shifted the meaning of "circular" from waste-management and CE-economy performance toward consumption-side footprints and import dependency, which favour low-consumption economies. The 2016→2020 activation of food waste has a mean absolute structural effect of only 0.015.

**Baseline agreement with DFSS (global rank, Kendall τ_b).** B1 pooled 0.989 (max shift 1); B2 imputed full set 0.692 (13 countries shift ≥ 3; max 10); B3 listwise common set (9 indicators) 0.863 (7 shift ≥ 3; max 9); B4 fuzzy TOPSIS 0.801 (max 13). Per period, listwise agreement collapses in 2023 (τ 0.41) — the common set cannot see the revised framework at all. B2 is the "invented data" case: applying the 2023 set retroactively to 2012 ranks HR 1st and EE 27th.

**Clusters (Fig. 5).** k = 2 (silhouette 0.45; bootstrap Jaccard 0.84). Cluster 0 "consolidated leaders": AT, BE, DE, EE, FR, IT, LU, NL. Cluster 1 "converging": the other 19. Ward agreement is moderate (ARI 0.57), so k = 2 should be presented as a coarse typology; Layer C will split cluster 1 by waste-wave timing to obtain three archetypes.

**Sensitivity (Fig. 6).** Across 37 specifications: NL 1–3, BE 2–5, EL 27 always, RO 21–26, BG 19–26; most volatile FI (2–22), DK (8–24), EE (5–20), SK (6–21), IE (9–25). Volatility concentrates in countries whose profile is polarised across dimensions (FI: strong CE economy and recycling, weak footprints). S1 vs S2 τ = 0.744; shifts ≥ 5 positions: DK, HR, SK, BG, IE, RO.

## 5. Draft findings for the paper (one sentence each)

1. National circularity rankings on the EU monitoring framework are not comparable across the 2023 revision without a model that treats the criteria set as time-varying; two-thirds of the apparent 2020→2023 movement is structural.
2. The revision re-weighted the concept of circularity toward consumption footprints and resilience, moving Luxembourg, Austria, Germany, Estonia and Ireland down and Croatia, Slovakia, Latvia, Romania and Greece up — with essentially no change in underlying performance.
3. Conventional remedies fail in opposite directions: imputing the new indicators backward invents history (τ 0.69), while restricting to the common set discards the revision (τ 0.41 in 2023).
4. Under a framework-faithful, dimension-balanced DFSS, a stable core of eight consolidated leaders emerges (bootstrap Jaccard 0.84), and it is this group's readiness that Layer C will contrast with the timing of the PV waste wave.
5. Data-quality weighting is necessary for honesty but immaterial for rankings (τ > 0.99), which reviewers should find reassuring.

## 6. Open points for you

1. **Primary scenario.** I recommend S2 (framework-faithful) as primary and S1 as robustness. Confirm.
2. **Cluster count.** k = 2 is statistically preferred; for Layer C I propose three archetypes = leaders / converging-early-wave / converging-late-wave (defined once Layer B gives wave timing). Confirm.
3. **Cost-criterion normalisation.** min/x is consistent with the DFSS paper's ratio form but non-linear; min-max is reported as sensitivity (τ 0.74–0.80 between the two). If you prefer min-max as primary, results shift moderately (Fig. 6 shows the ranges).
4. **Questionnaire.** Review alternatives A1–A7 and criteria C1–C4; the two member-state groups in Section 5 use the cluster labels above. Suggested panel: 8–12 respondents across regulator/PRO, installer/EPC, recycler, researcher.

## 7. Next session (Layer B)

- Extract Eurostat `nrg_inf_epcrw` (solar PV net capacity, 2000–2024) for EU-27; cross-check three countries against IRENA published figures.
- Annual additions → Weibull early-loss (α = 2.4928) and regular-loss (α = 5.3759) scenarios (IRENA/IEA-PVPS 2016), 30-year mean life; mass factors by vintage; material streams (glass, Al, Si, Ag, Cu).
- Validation against Eurostat `env_waselee` category EE_CPV_PVP (PV panels collected/treated, 2012–2022).
- Outputs: annual and cumulative EoL mass per country to 2050; wave-timing indicators (year of 10 %, peak, 50 % cumulative); fuzzy bands via Monte Carlo over lifetime and mass-factor uncertainty.
- Readiness gap = urgency(u) ⊗ (1 − readiness(u)); urgency–readiness map; three archetypes.

## 8. File index (all in `session1/`)

- `figs/fig1_availability_active_sets.png` … `fig6_sensitivity_S2.png` — journal-ready (300 dpi)
- `LayerA_results.xlsx` — all tables (T1 indicators/availability; T2 scores & period ranks; T3 method ranks; T4 decomposition; T5 clusters; T6 sensitivity grid; T7 rank stability; D1 panel)
- `results/*.csv|json` — machine-readable results, both scenarios
- `data/` — annual and period panels, availability table, active sets (S1/S2 JSON), raw JSON cache
- `code/eurostat.py`, `build_panel.py`, `layer_a.py`, `figures_a.py`, `questionnaire.js` — re-run with `python3 build_panel.py && python3 layer_a.py && python3 figures_a.py`
- `Delphi_Round1_PV_EoL_questionnaire.docx` — ready to circulate

Please re-upload the `session1` folder (or at least `data/` and `results/`) at the start of Session 2 so I can continue from the same state.
