/**
 * Delphi Round 1 — Circular pathways for end-of-life PV modules in the EU
 * Builds the complete Google Form and links it to a response spreadsheet.
 *
 * HOW TO RUN (about 2 minutes):
 *   1. Go to https://script.google.com  →  New project.
 *   2. Delete the default code, paste this whole file, save (name it e.g. "Delphi form builder").
 *   3. Select the function  buildDelphiForm  in the toolbar and click Run.
 *      Grant the permissions it asks for (Forms + Sheets + Drive, your own account only).
 *   4. Open View → Logs (or Executions). It prints the EDIT link, the SHARE link and the response sheet.
 *   5. Open the edit link once to check the look, then share the SHARE link with experts.
 *
 * Question titles contain machine-readable tokens (e.g. "H1|C1 …", rows "A1 …") so that the
 * response spreadsheet can be converted automatically by ingest_forms.py.
 */

function buildDelphiForm() {
  const form = FormApp.create('Expert survey (Round 1): Circular pathways for end-of-life photovoltaic modules in the EU');

  form.setDescription(
    'This survey supports a research article for the special issue "Embedding Circular Practices into Renewable ' +
    'and Sustainable Energy Production and Management" of Renewable and Sustainable Energy Reviews. The study projects ' +
    'the wave of end-of-life photovoltaic (PV) modules that EU member states will face between now and 2050 and asks ' +
    'which circular strategies should be activated, and when, in member states with different levels of circular-economy readiness.\n\n' +
    'Quantifiable aspects of each strategy (treatment cost, material recovery, avoided emissions, critical-raw-material ' +
    'recovery, employment) are taken from published studies. Your judgement is needed only for the institutional aspects ' +
    'that no dataset captures: regulatory readiness, enforcement feasibility, actor and market readiness, and social acceptance.\n\n' +
    'Time: 20–30 minutes. Responses are anonymous; only an aggregate profile of the panel is reported. This is Round 1 of 2: ' +
    'in about three weeks you will receive a short follow-up showing the panel\'s aggregated ratings alongside your own.'
  );
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);   // keeps it anonymous (no Google sign-in required)
  form.setProgressBar(true);
  form.setShuffleQuestions(false);
  form.setAllowResponseEdits(true);
  form.setConfirmationMessage('Thank you. Your ratings have been recorded. You will receive the Round-2 form in about three weeks.');

  const SCALE = ['VL – Very low', 'L – Low', 'M – Medium', 'H – High', 'VH – Very high'];

  const ALTS = [
    'A1 Repair and refurbishment for domestic reuse (R4/R5)',
    'A2 Cascaded second use – repowering with down-cycling of modules (R7)',
    'A3 Export for second-life use outside the EU (R7, external)',
    'A4 Bulk mechanical recycling – glass, aluminium, copper (R8, low value)',
    'A5 High-value recycling – delamination; silicon, silver and glass recovery (R8, high value)',
    'A6 Formalised collection through SMEs and installer take-back networks (R8/R9 enabling)',
    'A7 Landfill / incineration with energy recovery (baseline)'
  ];

  const CRIT = [
    ['C1', 'Regulatory readiness',
      'Extent to which current EU/national rules (WEEE Directive, EPR schemes, product standards, waste-shipment rules) enable the pathway without new legislation.'],
    ['C2', 'Enforcement and compliance feasibility',
      'Practicality of monitoring, certification and preventing leakage (e.g. illegal export, informal dismantling).'],
    ['C3', 'Actor and market readiness',
      'Availability of the actors, capacity and business cases needed (installers, recyclers, refurbishers, secondary-material buyers).'],
    ['C4', 'Social acceptance and public support',
      'Acceptability to consumers, installers and local communities; willingness to hand over or purchase used/recycled modules.']
  ];

  const HORIZONS = [
    ['H1', '2026–2030', 'early wave: first decommissioning of 2008–2013 installations'],
    ['H2', '2031–2040', 'peak wave: the bulk of the feed-in-tariff cohort reaches end of life'],
    ['H3', '2041–2050', 'mature phase: steady-state flows, second-generation modules']
  ];

  // ---------------------------------------------------------------- Section 1: profile
  form.addSectionHeaderItem().setTitle('1. About you (no name required)');

  form.addMultipleChoiceItem().setTitle('PROFILE|role Primary role').setRequired(true)
    .setChoiceValues(['Policy / regulator', 'Producer-responsibility organisation', 'PV installer / EPC',
                      'Recycler / waste operator', 'Researcher']).showOtherOption(true);
  form.addCheckboxItem().setTitle('PROFILE|sector Sector focus (tick all that apply)').setRequired(true)
    .setChoiceValues(['PV manufacturing', 'PV deployment / O&M', 'Waste & recycling', 'Circular-economy policy']).showOtherOption(true);
  form.addMultipleChoiceItem().setTitle('PROFILE|years Years of professional experience with PV or WEEE').setRequired(true)
    .setChoiceValues(['< 3', '3–7', '8–15', '> 15']);
  form.addTextItem().setTitle('PROFILE|countries Member states you know best (up to three, e.g. "DE, IT, EL")').setRequired(false);
  form.addMultipleChoiceItem().setTitle('PROFILE|familiarity Self-assessed familiarity with PV end-of-life issues').setRequired(true)
    .setChoiceValues(['Basic', 'Working knowledge', 'Expert']);

  // ---------------------------------------------------------------- Section 2: definitions
  form.addPageBreakItem().setTitle('2. Definitions used in this survey');
  form.addSectionHeaderItem().setTitle('2.1 End-of-life strategies (the alternatives you will rate)').setHelpText(
    'Each alternative is a system-level pathway a member state could prioritise, mapped to the R-ladder (R0 refuse … R9 recover).\n\n' +
    'A1 Repair and refurbishment for domestic reuse — tested, cleaned and re-certified modules re-deployed in the same or similar applications within the country.\n' +
    'A2 Cascaded second use — modules removed during repowering are re-used in lower-demand applications (off-grid, agrivoltaic, small C&I).\n' +
    'A3 Export for second-life use — functional used modules exported under the WEEE/Basel used-equipment rules for reuse in third countries.\n' +
    'A4 Bulk mechanical recycling — frame removal, shredding and separation; recovers bulk fractions, downcycled glass; silicon/silver largely lost.\n' +
    'A5 High-value recycling — thermal/chemical delamination or advanced separation to recover solar-grade glass, silicon and silver.\n' +
    'A6 Formalised collection through SMEs and installer take-back — producer-financed take-back at installer/distributor level with certified collection and pre-treatment.\n' +
    'A7 Landfill / incineration with energy recovery — reference pathway: modules enter mixed WEEE or construction waste streams.');
  form.addSectionHeaderItem().setTitle('2.2 Institutional criteria').setHelpText(
    CRIT.map(c => c[0] + ' ' + c[1] + ' — ' + c[2]).join('\n'));
  form.addSectionHeaderItem().setTitle('2.3 Time horizons').setHelpText(
    HORIZONS.map(h => h[0] + ' ' + h[1] + ' — ' + h[2]).join('\n'));
  form.addSectionHeaderItem().setTitle('2.4 Rating scale').setHelpText(
    'One level per cell. The scale is deliberately coarse; use VL/VH only where you are confident. For analysis each level is ' +
    'converted to a triangular fuzzy number: VL (0, 0, 0.25); L (0, 0.25, 0.50); M (0.25, 0.50, 0.75); H (0.50, 0.75, 1); VH (0.75, 1, 1).\n\n' +
    'In Section 3, rate each alternative for a TYPICAL EU member state, assuming currently announced policy (WEEE Directive review, ' +
    'Ecodesign requirements for PV, Critical Raw Materials Act) is implemented as planned. Section 4 then asks how ratings differ between member-state groups.');

  // ---------------------------------------------------------------- Section 3: ratings by horizon (12 grids)
  HORIZONS.forEach(h => {
    form.addPageBreakItem().setTitle('3. Ratings — Horizon ' + h[0] + ' (' + h[1] + ')').setHelpText(h[2]);
    CRIT.forEach(c => {
      form.addGridItem()
        .setTitle(h[0] + '|' + c[0] + ' ' + c[1] + ' — ' + h[0] + ' ' + h[1])
        .setHelpText(c[2])
        .setRows(ALTS).setColumns(SCALE).setRequired(true);
    });
    form.addParagraphTextItem().setTitle('COMMENT|' + h[0] + ' Optional comment for horizon ' + h[0]).setRequired(false);
  });

  // ---------------------------------------------------------------- Section 4: member-state context (H2)
  form.addPageBreakItem().setTitle('4. Member-state context (peak-wave horizon 2031–2040)').setHelpText(
    'Our benchmarking of Eurostat circular-economy indicators (2012–2023) distinguishes two groups of member states: ' +
    'CONSOLIDATED LEADERS, which have ranked consistently in the upper tier on the EU monitoring framework ' +
    '(Netherlands, Belgium, Luxembourg, France, Italy, Austria, Germany, Estonia), and CONVERGING member states, with lower or ' +
    'more volatile readiness (the remaining nineteen). For the peak-wave horizon, rate the OVERALL institutional feasibility ' +
    'of each alternative in each group.');
  form.addGridItem().setTitle('CONTEXT|L Overall institutional feasibility in CONSOLIDATED-LEADER member states (2031–2040)')
    .setRows(ALTS).setColumns(SCALE).setRequired(true);
  form.addGridItem().setTitle('CONTEXT|CONV Overall institutional feasibility in CONVERGING member states (2031–2040)')
    .setRows(ALTS).setColumns(SCALE).setRequired(true);
  form.addParagraphTextItem().setTitle('COMMENT|CONTEXT Which single factor most limits the converging group?').setRequired(false);

  // ---------------------------------------------------------------- Section 5: criterion weights
  form.addPageBreakItem().setTitle('5. Relative importance of criteria').setHelpText(
    'When a member state chooses which end-of-life pathway to prioritise, how important is each criterion? ' +
    'C1–C4 are the institutional criteria you rated above; C5–C9 are quantified from the literature and are listed so that ' +
    'all criteria are weighed on the same scale. 1 = negligible … 9 = decisive.');
  form.addGridItem().setTitle('WEIGHTS Importance of each criterion (1 = negligible, 9 = decisive)')
    .setRows([
      'C1 Regulatory readiness', 'C2 Enforcement and compliance feasibility', 'C3 Actor and market readiness',
      'C4 Social acceptance and public support', 'C5 Net cost per tonne treated', 'C6 Material recovery rate and quality',
      'C7 Avoided greenhouse-gas emissions', 'C8 Critical raw material recovery (silicon, silver)', 'C9 Employment and regional value added'])
    .setColumns(['1', '2', '3', '4', '5', '6', '7', '8', '9']).setRequired(true);

  // ---------------------------------------------------------------- Section 6: open questions
  form.addPageBreakItem().setTitle('6. Open questions (optional)');
  form.addParagraphTextItem().setTitle('OPEN|Q1 Which policy instrument would most accelerate high-value recycling (A5) before 2035?');
  form.addParagraphTextItem().setTitle('OPEN|Q2 Is export for second-life use (A3) a legitimate circular pathway or a leakage risk? Under what conditions?');
  form.addParagraphTextItem().setTitle('OPEN|Q3 Are there alternatives or criteria missing from this survey that you consider essential?');
  form.addTextItem().setTitle('OPEN|R2 If you are willing to take part in Round 2, enter an e-mail address (optional; stored separately from your ratings).');

  // ---------------------------------------------------------------- response spreadsheet
  const ss = SpreadsheetApp.create('Delphi Round 1 – responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('EDIT link (for you):   ' + form.getEditUrl());
  Logger.log('SHARE link (experts):  ' + form.getPublishedUrl());
  Logger.log('Response sheet:        ' + ss.getUrl());
  Logger.log('Items created: ' + form.getItems().length);
}
