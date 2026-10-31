# Session 8 report — revision in response to reviewer-style comments (21 October 2026)

## What was wrong and what was done

| # | Comment | Diagnosis | Fix |
|---|---------|-----------|-----|
| 1 | Tables 4 and 5 (scores vs decomposition) disagree; "65 %", Luxembourg 0.649 / rank 1, Croatia 2nd, Slovakia/Latvia top five | `layer_a.local_scores()` defaulted to equal weights, `dfss()` to dimension-balanced weights; the decomposition and the worked example were computed with the former, the score table with the latter | Unified default (dimension-balanced); `activation_decomposition()` takes weights explicitly; `run()` asserts that decomposition and DFSS period scores are identical. Structural share unchanged at 64.7 % ("two-thirds"); Luxembourg 0.596→0.534, rank 3→10; Croatia 17→13; Slovakia 12→8; Latvia 20→11. Worked example, Table 5, Fig. 3, Section 4.1, Discussion 5.1 and graphical abstract rewritten |
| 2 | Gap bands claimed non-overlapping | Only Greece's band is separated | Text now states Greece robustly first; BG/CY next on the central estimate with overlapping bands (abstract, 4.3, 5.2, conclusion, cover letter) |
| 3 | 7.25 Mt rounds to 7.2 | — | 7.2 Mt everywhere (abstract, highlights, 4.2, conclusion, cover letter, graphical abstract) |
| 4 | Export "competitive only in 2026–2030" contradicted by rank 4 (LW, H2; global) | — | "Mid-table throughout, strongest before 2030, never dominant"; LW policy paragraph notes the H2 fourth place |
| 5 | Onset defined inconsistently | — | Unified definition in Methods, Table 7 caption, Fig. 8 caption and figure title |
| 6 | Germany "within 25 % through 2021" false (2021 +32 %); WEEE scope labels; Fig. 6 shows 127 points | — | "Within 11 % in 2019–2020, +32 % 2021, +60 % 2022"; Annex I (2016–18) / Annex III open scope (2019–24); Fig. 6 shows all 128 (HU 2018 hollow, excluded) and states 71 in the fit |
| 7 | Table 9 ignores archetype cost multipliers | `make_tables` used raw literature TFNs | Multipliers 0.90/1.00/1.15 applied; EU row labelled unscaled; table made full width |
| 8 | Table 8 rank order; dangling cross-reference; abbreviations | Rows 17/18 swapped (float tie); "Table S3" never existed | Sorted by rank; reference now to Supplement S2.4; WEEE, IRENA/IEA-PVPS, TOPSIS, CRM, WGI defined at first use |
| 9 | Symbol collisions | A_t vs A1–A7; T scale vs T index; ρ Spearman vs ρ requirement; CE archetype vs circular economy | a_1…a_7; η; r_s; L / EW / LW — in code, data files, tables, figures, text and supplement |
| 10 | Missing literature; "first calibration" claim | Kastanaki 2025/2026, Pitacco 2026, Nagarajan 2026, D'Adamo 2023/2024, Martínez Moreno 2023 | All seven verified (Crossref) and added (99 references); claims withdrawn; Table 1 extended with four EU-wide studies; contribution reframed as the integration; new comparison paragraph in 5.6 (Pitacco 2035 figures agree within 10 % for DE/IT/ES; Nagarajan 3.6–6.9 Mt net c-Si vs 7.2 Mt gross) |

## Rebuilt
All Layer A/B/C results, 13 figures, 11 tables, main.pdf (30 pp, 0 errors), supplement.pdf, graphical abstract (PPTX + PNG), cover letter, highlights, workbooks (`code/build_workbooks.py`), ANALYSIS.md (§8 revision log), submission / Zenodo / repository packages.

## Verified after rebuild
- `python3 code/layer_a.py` passes the new decomposition/DFSS consistency assertion for S1 and S2.
- PDF text audit: no "7.3 Mt", "1st → 14th", "−0.108", "0.649", "within 25", "Table S3", "$A_1$" remain; 7.2 Mt appears 5×, 20.9 Mt 4×; all seven new references cited.
- Highlights ≤ 83 characters; abstract unchanged in length class (≤ 250 words).
