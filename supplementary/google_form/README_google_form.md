# Delphi Round 1 in Google Forms — setup and data flow

## A. Build the form (once, ~2 minutes)
1. Open https://script.google.com and click **New project**.
2. Delete the default code, paste the contents of `build_form.gs`, and save.
3. In the toolbar choose the function `buildDelphiForm` and click **Run**. Approve the permission request (Forms, Sheets, Drive — your account only).
4. Open **Executions** (or View → Logs). It prints three links: the EDIT link (yours), the SHARE link (for experts) and the response spreadsheet.
5. Open the edit link once to review; the form has 6 pages, 14 rating grids (12 for horizons × criteria, 2 for member-state context), the criterion-importance grid, profile and open questions — identical in content to the Word version.

Settings applied by the script: no e-mail collection, no sign-in required (anonymous), progress bar on, respondents may edit their answers, confirmation message announces Round 2. Change any of these in the form's Settings if your ethics process requires otherwise.

## B. Share
Send the SHARE link (or a QR code from the form's Send menu) with the invitation e-mail. Responses appear live in the linked spreadsheet.

## C. Convert responses for the analysis
1. In the response spreadsheet: File → Download → **CSV** (current sheet).
2. Run `python3 ingest_forms.py responses.csv --out ../data` (from the `code/` folder of the project bundle; `ingest_forms.py` is also copied there).
   It writes `data/expert_ratings.csv` (the file `layer_c.py` reads), `expert_weights.csv` and `expert_weights_normalised.csv`, `expert_profile.csv`, `expert_comments.csv`, and prints the panel's group weights to paste into `GROUP_W` in `layer_c.py`.
3. Run `python3 layer_c.py && python3 figures_c.py && python3 synthesis.py && python3 make_tables.py`. Outputs switch from PLACEHOLDER to `delphi`; the consensus index and leave-one-expert-out checks populate; figures lose the provisional tag.

## D. Round 2 (later)
The same response sheet gives, for every item, the panel's distribution. I will generate the Round-2 form (each item shown with the panel's aggregated rating and a field to keep or revise) from the Round-1 sheet when it is ready.

## Notes
- Question titles start with tokens (`H1|C1 …`, `CONTEXT|L …`, `WEIGHTS …`, `PROFILE|role …`) that the converter relies on. Rename questions freely *after* the token if you wish, but keep the token and the row labels' leading codes (A1–A7, C1–C9).
- Section 4 (member-state context) is asked for two groups; the converter maps "converging" to both converging archetypes (early and late wave), as agreed.
- The optional Round-2 e-mail field is stored in the same sheet; delete that column before sharing the sheet with anyone else.
