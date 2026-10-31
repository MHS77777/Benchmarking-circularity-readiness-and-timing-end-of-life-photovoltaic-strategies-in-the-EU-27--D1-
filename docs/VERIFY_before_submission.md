# Verification status (Session 8, finalized source) — what has been verified, what remains

## Verified against primary sources in this session (web-fetched or search-confirmed)
- IRENA/IEA-PVPS (2016) *End-of-Life Management: Solar Photovoltaic Panels* (report T12-06:2016): Weibull form F(t)=1−exp[−(t/T)^α] with T = 30-yr average lifetime; α = 2.4928 (early) / 5.3759 (regular); 80–100 t/MW for the 2016 stock; c-Si composition 76/10/8/5/1/<0.1 % (glass/polymer/Al/Si/Cu/Ag); Table 6 national totals (DE 4.3 Mt, IT 2.1–2.2, FR 1.5–1.8, DK 0.125–0.13 by 2050).
- Kostakis & Tsagarakis (2022) J. Clean. Prod. 348:131267, DOI 10.1016/j.jclepro.2022.131267.
- Chen & Hsieh (1999) J. Chinese Fuzzy Systems 5(2):1–7.
- Fujita & Smarandache (2026) *A Dynamic Survey of Soft Set Theory and Its Extensions*, NSIA book, ISBN 978-1-59973-859-8, arXiv:2602.21268 (entry changed to @book).
- Alcantud et al. (2024) Neural Comput. Appl., DOI 10.1007/s00521-024-09552-x.
- Heath et al. (2020) Nature Energy 5(7):502–510, DOI 10.1038/s41560-020-0645-2 (full author list).
- Tsanakas et al. (2020) Prog. Photovolt. 28(6):454–464, DOI 10.1002/pip.3193.
- Markert, Celik & Apul (2020) Energies 13(14):3650, DOI 10.3390/en13143650 — and, via its reference list: Latunussa et al. (2016) DOI 10.1016/j.solmat.2016.03.020; Deng et al. (2019) DOI 10.1016/j.rser.2019.04.020; Cucchiella et al. (2015) DOI 10.1016/j.rser.2015.03.076; D'Adamo et al. (2017) DOI 10.1155/2017/4184676; Fiandra et al. (2019) Waste Manag. 84:91–101; Tao & Yu (2015) SEMSC 141:108–124; Faircloth et al. (2019) RCR 143:260–272; Fthenakis (2000) Energy Policy 28:1051–1058; Choi & Fthenakis (2010) ES&T 44:8678–8683; Lunardi et al. (2018) DOI 10.5772/intechopen.74390.
- Policy: CJEU Case C-181/20; WEEE amending directive adopted 2024 with review clause (assessment by 31 Dec 2026) and Parliament's call for a PV-panels category and lifetime-based collection targets; Commission WEEE evaluation SWD(2025) 184 (2 July 2025); ESPR Regulation (EU) 2024/1781 and working plan COM(2025) 187 (16 April 2025).
- Nguyen et al. (2024) Energies 17(20):5179; Nunes et al. (2023) Energies 16(1):485; Fortea et al. (2026) CSR-EM DOI 10.1002/csr.70406; Preet & Smith (2024) JCP 448:141661.

## Flagged references — all eight resolved against Crossref on 20 Oct 2026
neri2027 → RSER 243:117363 (2027), Neri, Trivella, Butturi & Yazan; hosseini2026 → RSER 241:117237; ghasemi2026 → Ghasemi & Sadeghkhani, IJER 2026(1):5096351; maani2020 confirmed; huang2017 DOI confirmed; komoto2018 author list confirmed (OSTI DOI 10.2172/1561523 added); islam2020 DOI corrected to 10.1177/0734242X20962837 (online 2020, issue 2021); fortea2026 → Fortea, Antohi, Hassan, Andrei & Erokhin, CSR-EM 33(4):4688–4724. No VERIFY notes remain in refs.bib. Still worth a glance: the WEEE amending directive number (cited as 2024/884) and the WSR number (2024/1157).

## Numerical assumptions — now sourced
Mass per MW anchors and composition → IRENA/IEA-PVPS (2016) (verified above); recent-module mass (~50 t/MW) from current data sheets — cite one manufacturer data sheet or ITRPV. Layer-C C5/C6/C8 anchors → Markert et al. (2020), D'Adamo et al. (2017), Latunussa et al. (2016), Heath et al. (2020). C7 (avoided GHG) remains a relative range (Latunussa 2016; Maani 2020) — state as such (done in Supplement S2.4). C9 employment indicative (IRENA 2016 qualitative) — consider dropping or sourcing a jobs-per-tonne figure.

## Text items still to complete in main.tex
1. Corresponding e-mail (`\ead{[corresponding e-mail]}`). 2. Generative-AI declaration (`\rev{[To be completed according to journal policy.]}`). 3. Reviewer suggestions in cover_letter.md. 4. Zenodo DOI in the Data availability statement.

## Finalized source (received 20 Oct 2026)
Converted to the Elsevier CAS single-column template (cas-sc.cls); content, figures and numbers identical to the audited Session-7 build; DOIs added to 38 references and author lists completed (see reference_corrections_log.txt); compiles cleanly, 29 pages, 92 references, no undefined citations.
(The Section 2.4 database search is now documented on OpenAlex, 20 Oct 2026; an optional Scopus cross-check would strengthen it but is not required.)

## Done in Session 7 (items 5–8)
- Journal format: abstract 241 words; five highlights ≤ 83 characters; six keywords.
- Clean-room reproduction from live APIs (20 Oct 2026) and, separately, from the frozen cache with the network blocked: identical outputs. Eurostat had revised 84 panel cells since 4 Sep; results refreshed and the retrieval date updated throughout.
- Audit found and corrected stale statistics in Section 4.1 (listwise 2023 agreement 0.41 → 0.71; B2 2012 example; sensitivity ranges), all now generated from the current files.
- Submission package in submission/ (manuscript.pdf, supplementary_material.pdf, figures/, highlights.txt, cover_letter.md with reviewer slots to fill); Zenodo-ready repository in zenodo/ (code, frozen raw data, results, figures, README, LICENSE, requirements).
- 92 references; all VERIFY notes cleared.

## New in Session 6 (Track A)
- Layer-C institutional criteria now come from public data (Eurostat env_waseleeos, CE framework, World Bank WGI). The requirement matrix rho(a,c) is an author construction documented in Supplement S3.1 — review the values and rationale; they are the one judgement-based input left in the paper.
- The Delphi is now a protocol (Supplement S3.2). If responses arrive, run ingest_forms.py → layer_c.py; the pipeline reports tau(proxy, delphi) in results/C_delphi_validation.json, which can be added as a validation sentence.
- Correction: the earlier claim that PV-specific WEEE statistics ended in 2018 was wrong; the open-scope dataset reports PV panels (EE_LE_PVP) 2019–2024. Manuscript corrected; calibration now uses 2016–2024.
- Bulgaria's WEEE collection rate (~100 %) is a known reporting anomaly — stated in Limitations; consider a sentence in Section 3.6 if a reviewer is likely to ask.

## Superseded numbers
Session 2–5 reports quote earlier Layer-B figures (16.8 Mt / π = 0.24; then 20.6 Mt / π = 0.13). The manuscript and all files in this bundle use the IRENA scale convention calibrated on 2016–2024 (20.9 Mt by 2050, π = 0.18). Treat the manuscript as authoritative.

## Length
Main text ≈ 9,300 words (excl. tables/references), 92 references. Remaining expansion candidates if the editors ask: CE–RE integration review (+600 words), technology-mix sensitivity in Layer B (+400).
