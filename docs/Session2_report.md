# Session 2 report — Layer B: EU-27 PV waste wave, validation, readiness gap and archetypes

**Status:** Layer B complete. Decisions from Session 1 applied: S2 primary, ratio normalisation, three archetypes.

---

## 1. Model as implemented (for the Methods section)

- **Installed capacity.** Eurostat `nrg_inf_epcrw`, solar PV net electrical capacity (MW), EU-27, 1991–2024, complete for all 27 states in 2024 (25 missing cells in early years for small states, set to 0). Annual additions = positive year-on-year differences.
- **Cohort mass.** Module mass per MW by vintage, interpolated between anchors 115 t/MW (1990), 110 (2000), 85 (2010), 62 (2020), 58 (2024), 48 (2050) — consistent with IRENA/IEA-PVPS (2016) and subsequent efficiency trends. *To be cited/verified in writing; ±15 % in Monte Carlo.*
- **Future deployment (2025–2050).** Primary: continued deployment at the 2022–2024 mean annual addition (flat). Sensitivities: existing 2024 stock only; +3 %/yr growth.
- **Failure model.** Weibull with median life T50 = 30 yr; early-loss α = 2.4928, regular-loss α = 5.3759 (IRENA/IEA-PVPS 2016). **Central scenario** = π·early + (1−π)·regular with π = 0.24 calibrated by pooled log-least-squares on Eurostat `env_waselee` PV-panel collection (category EE_CPV_PVP, 2016–2018, country-years with > 100 t; HU-2018 excluded as a reporting outlier).
- **Monte Carlo (600 draws).** Shape drawn as early with probability π else regular; T50 ~ Tri(25, 30, 35); mass factor × Tri(0.85, 1, 1.15). Bands reported as p10–p90.
- **Wave timing (existing stock, central).** Onset = year in which 10 % of the 2024 stock's cumulative-to-2050 arisings have occurred; midpoint = 50 %; peak = year of maximum annual arisings 2025–2050.
- **Material streams.** c-Si mass composition: glass 74 %, aluminium 10 %, polymers 10 %, silicon 3.5 %, copper 1 %, silver 0.05 %, other 1.45 %. *To be cited (IRENA 2016; Deng et al. 2019).*
- **Urgency.** u(g) = ½ [ mass_2040/cap ÷ max ] + ½ [ (2050 − onset) ÷ max ], i.e. ratio-normalised as in Layer A.
- **Readiness.** r(g) = DFSS global score (Scenario S2), min–max normalised; r_2023 as sensitivity.
- **Readiness gap.** G(g) = u(g) · (1 − r(g)); bands from the urgency p10–p90.
- **Archetypes.** L = consolidated leaders (Layer A cluster 0, n = 8); CE = converging with onset ≤ 2035 (median of cluster 1; n = 10); CL = converging with onset > 2035 (n = 9).

## 2. Validation (Fig. 9, Table T10)

Germany: collected 2.0 / 3.6 / 7.9 kt (2016–18) vs central 4.8 / 6.1 / 7.8 kt; early-loss 16.9 / 21.0 / 25.4 kt; regular-loss 1.0 / 1.6 / 2.4 kt. Italy 2018: 1.35 kt collected vs 2.7 kt central. France 2017–18: 1.9 / 1.6 kt collected vs 0.6 / 0.8 kt central (France's PV Cycle scheme collected above modelled arisings, plausibly including pre-consumer/damaged stock). Small markets collect well below modelled arisings — expected given immature take-back and <100 % collection rates — so π = 0.24 should be read as a lower bound on the true early-loss share of *arisings*, and the early-loss scenario as the upper envelope. This is the honest framing for the paper.

## 3. Results (central scenario, continued deployment)

**EU-27 totals.** Cumulative end-of-life PV mass: 0.94 Mt by 2030, 5.2 Mt by 2040, 16.8 Mt by 2050 (early-loss 2.1 / 7.9 / 20.2; regular-loss 0.6 / 4.4 / 15.7). The 2024 stock alone yields 12.2 Mt by 2050. Annual arisings rise monotonically to ≈ 1.6 Mt/yr in 2050; there is no pre-2050 peak at EU level because deployment kept growing — the "wave" is a rising tide whose *onset* differs across member states.

**Country waves (Fig. 8, Table T8).** Onset 2030: DE, CZ. 2031: IT, SK. 2032: BE, LU, ES. 2033: EL, BG, FR. 2034: SI, MT. 2035: NL, DK, AT, CY, PT. 2036: HU, SE, HR, FI. 2037: LT, EE, PL, RO, IE. 2038: LV. Midpoints 2041 (DE, CZ, IT, SK) to 2046 (LT, PL, RO, IE, LV).
Cumulative mass by 2050: DE 5.35 Mt, IT 2.21, ES 1.87, FR 1.33, NL 1.10, PL 1.00, BE 0.53, EL 0.47. Per capita by 2040: DE 25.3 kg, BE 14.6, IT 14.6, NL 13.2, LU 13.2, EL 12.9, ES 10.2, DK 10.2, AT 10.1, CZ 9.8 … IE 1.9.
Material streams 2025–2050 (EU-27, central): glass ≈ 12.4 Mt, aluminium ≈ 1.7 Mt, polymers ≈ 1.7 Mt, silicon ≈ 0.59 Mt, copper ≈ 0.17 Mt, silver ≈ 8.4 kt.

**Readiness gap (Fig. 10–11, Table T9).** Top ten: EL 0.68 [0.57–0.85], BG 0.51, CY 0.45, DE 0.39, MT 0.37, PT 0.37, ES 0.37, CZ 0.34, DK 0.34, SK 0.34. Bottom: NL 0.00, BE 0.14, LU 0.15, FR 0.17, EE 0.18, AT 0.20. Germany is the only leader in the top ten: highest urgency in the Union (u = 1.00) against readiness 0.61. The p10–p90 bands do not overlap between EL and any country ranked below fourth, so the priority position of Greece is robust to lifetime and mass uncertainty.

**Archetypes.** L: AT, BE, DE, EE, FR, IT, LU, NL. CE (early wave): BG, CY, CZ, DK, EL, ES, MT, PT, SI, SK. CL (late wave): FI, HR, HU, IE, LT, LV, PL, RO, SE.

## 4. Draft findings for the paper

1. The EU's PV waste wave is front-loaded in the feed-in-tariff cohorts: ten member states reach onset by 2033, all by 2038; cumulative arisings roughly triple each decade (0.9 → 5.2 → 16.8 Mt).
2. Calibration on the only PV-specific collection series Eurostat has ever published (2016–18) places the EU on a trajectory much closer to IRENA's regular-loss than early-loss curve for the next decade (π ≈ 0.24), while confirming that regular-loss alone under-predicts observed collection three-fold.
3. Urgency and readiness are only weakly aligned: the earliest and heaviest waves fall on a mix of leaders (DE, IT, BE) and converging states (EL, CZ, BG, ES, SK); the readiness gap isolates Greece, Bulgaria and Cyprus as the priority group and flags Germany as a high-readiness state that nevertheless faces the largest absolute task (5.4 Mt by 2050, onset 2030).
4. Three archetypes with distinct policy clocks emerge: leaders (infrastructure and EPR in place; the question is high-value recovery), converging-early (onset ≤ 2035 with weak readiness; the question is collection and enforcement before 2032), converging-late (onset > 2035; time to build capacity but risk of complacency).

## 5. Points to verify when writing (flagged, not blocking)

- Cite sources for mass-per-MW anchors and composition (IRENA/IEA-PVPS 2016; more recent module bill-of-materials studies); cross-check the German 2050 figure against IRENA's 4.3 Mt regular-loss projection (ours is higher because 2016–2024 additions are included).
- Eurostat PV-panel WEEE category ends 2018 (category reform); state this explicitly as the reason for the short validation window.
- Population = Eurostat tps00001, 1 Jan 2024.

## 6. Next session (Layer C)

Strategy pathway selection per archetype and horizon with DFSS: seven alternatives (A1–A7), nine criteria (C1–C4 expert; C5–C9 literature), three horizons (H1 2026–30, H2 2031–40, H3 2041–50), time-varying A_t (e.g. EPR-compliance and high-value recycling maturity criteria inactive in H1; refurbishment demand fades in H3). Literature-derived criterion values with fuzzy ranges; institutional criteria as clearly labelled placeholders until Round-1 responses arrive; strategy-activation timeline per archetype; comparison with fuzzy TOPSIS/VIKOR; leave-one-expert-out sensitivity harness ready for the real data.

## 7. Files (in `session2/`)

- `figs/fig7_eu_wave.png`, `fig8_country_waves.png`, `fig9_validation.png`, `fig10_urgency_readiness_map.png`, `fig11_gap_materials.png`
- `LayerB_results.xlsx` — T8 country wave summary; T9 readiness gap & archetypes; T10 validation; D2 annual EoL by country (central); D3 EU-27 annual by scenario; D4 capacity series
- `results/B_*.csv|json`, `code/layer_b.py`, `figures_b.py`; Session 1 artefacts retained unchanged.
