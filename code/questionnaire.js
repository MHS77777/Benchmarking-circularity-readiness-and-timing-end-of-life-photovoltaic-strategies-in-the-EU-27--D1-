const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, BorderStyle, ShadingType, LevelFormat, PageBreak, PageOrientation, VerticalAlign,
} = require("docx");

const NAVY = "1F4E79";
const font = "Calibri";
const P = (text, opts = {}) => new Paragraph({
  spacing: { after: 120, ...(opts.spacing || {}) }, alignment: opts.align,
  children: [new TextRun({ text, font, size: opts.size || 21, bold: opts.bold, italics: opts.italics, color: opts.color })],
});
const H = (text, level = HeadingLevel.HEADING_1) => new Paragraph({ heading: level, spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, font, bold: true, color: NAVY, size: level === HeadingLevel.HEADING_1 ? 28 : 24 })] });
const bullet = (text) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 },
  children: [new TextRun({ text, font, size: 21 })] });
const cell = (text, w, opts = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
  shading: opts.shade ? { type: ShadingType.CLEAR, fill: opts.shade, color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 80, right: 80 },
  children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font, size: opts.size || 18, bold: opts.bold, color: opts.color })] })],
});

const ALTS = [
  ["A1", "Repair and refurbishment for domestic reuse", "R4 Repair / R5 Refurbish", "Tested, cleaned and re-certified modules re-deployed in the same or similar applications within the country."],
  ["A2", "Cascaded second use (repowering with down-cycling of modules)", "R7 Repurpose", "Modules removed during repowering are re-used in lower-demand applications (e.g. off-grid, agrivoltaic, small C&I)."],
  ["A3", "Export for second-life use outside the EU", "R7 Repurpose (external)", "Functional used modules exported under the WEEE/Basel used-equipment rules for reuse in third countries."],
  ["A4", "Bulk mechanical recycling (glass, aluminium, copper)", "R8 Recycle (low value)", "Frame removal, shredding and separation; recovers bulk fractions, downcycled glass; silicon/silver largely lost."],
  ["A5", "High-value recycling (delamination; silicon, silver and glass recovery)", "R8 Recycle (high value)", "Thermal/chemical delamination or advanced separation to recover solar-grade glass, silicon and silver."],
  ["A6", "Formalised collection through SMEs and installer take-back networks", "R8/R9 enabling", "Producer-financed take-back at installer/distributor level with certified collection and pre-treatment."],
  ["A7", "Landfill / incineration with energy recovery (baseline)", "R9 Recover / disposal", "Reference pathway: modules enter mixed WEEE or construction waste streams."],
];
const CRIT = [
  ["C1", "Regulatory readiness", "Extent to which current EU/national rules (WEEE Directive, EPR schemes, product standards, waste-shipment rules) enable the pathway without new legislation."],
  ["C2", "Enforcement and compliance feasibility", "Practicality of monitoring, certification and preventing leakage (e.g. illegal export, informal dismantling)."],
  ["C3", "Actor and market readiness", "Availability of the actors, capacity and business cases needed (installers, recyclers, refurbishers, secondary-material buyers)."],
  ["C4", "Social acceptance and public support", "Acceptability to consumers, installers and local communities; willingness to hand over or purchase used/recycled modules."],
];
const HORIZONS = [["H1", "2026–2030", "early wave: first decommissioning of 2008–2013 installations"],
  ["H2", "2031–2040", "peak wave: bulk of the feed-in-tariff cohort reaches end of life"],
  ["H3", "2041–2050", "mature phase: steady-state flows, second-generation modules"]];
const SCALE = [["VL", "Very low", "(0, 0, 0.25)"], ["L", "Low", "(0, 0.25, 0.50)"], ["M", "Medium", "(0.25, 0.50, 0.75)"],
  ["H", "High", "(0.50, 0.75, 1)"], ["VH", "Very high", "(0.75, 1, 1)"]];

function ratingTable(hz) {
  const w = [560, 3200, 1400, 1400, 1400, 1400]; const tot = w.reduce((a, b) => a + b);
  const head = new TableRow({ tableHeader: true, children: [
    cell("", w[0], { shade: "D9E2F3", bold: true }), cell("Alternative", w[1], { shade: "D9E2F3", bold: true }),
    ...CRIT.map(c => cell(`${c[0]} ${c[1]}`, w[2], { shade: "D9E2F3", bold: true, align: AlignmentType.CENTER, size: 16 }))] });
  const rows = ALTS.map(a => new TableRow({ children: [
    cell(a[0], w[0], { bold: true }), cell(a[1], w[1], { size: 17 }),
    ...CRIT.map(() => cell("VL  L  M  H  VH", w[2], { align: AlignmentType.CENTER, color: "808080", size: 16 }))] }));
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: w, rows: [head, ...rows] });
}

function contextTable() {
  const w = [560, 4000, 2400, 2400]; const tot = w.reduce((a, b) => a + b);
  const head = new TableRow({ tableHeader: true, children: [
    cell("", w[0], { shade: "D9E2F3", bold: true }), cell("Alternative", w[1], { shade: "D9E2F3", bold: true }),
    cell("Consolidated-leader member states", w[2], { shade: "D9E2F3", bold: true, align: AlignmentType.CENTER, size: 16 }),
    cell("Converging member states", w[3], { shade: "D9E2F3", bold: true, align: AlignmentType.CENTER, size: 16 })] });
  const rows = ALTS.map(a => new TableRow({ children: [cell(a[0], w[0], { bold: true }), cell(a[1], w[1], { size: 17 }),
    cell("VL  L  M  H  VH", w[2], { align: AlignmentType.CENTER, color: "808080", size: 16 }),
    cell("VL  L  M  H  VH", w[3], { align: AlignmentType.CENTER, color: "808080", size: 16 })] }));
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: w, rows: [head, ...rows] });
}

function weightTable() {
  const items = [...CRIT.map(c => [c[0], c[1]]), ["C5", "Net cost per tonne treated (literature-derived)"],
    ["C6", "Material recovery rate and quality (literature-derived)"], ["C7", "Avoided greenhouse-gas emissions (literature-derived)"],
    ["C8", "Critical raw material recovery: silicon, silver (literature-derived)"], ["C9", "Employment and regional value added (literature-derived)"]];
  const w = [700, 5400, 3200]; const tot = w.reduce((a, b) => a + b);
  const head = new TableRow({ tableHeader: true, children: [cell("", w[0], { shade: "D9E2F3", bold: true }),
    cell("Criterion", w[1], { shade: "D9E2F3", bold: true }), cell("Importance 1 (negligible) – 9 (decisive)", w[2], { shade: "D9E2F3", bold: true, align: AlignmentType.CENTER, size: 16 })] });
  const rows = items.map(i => new TableRow({ children: [cell(i[0], w[0], { bold: true }), cell(i[1], w[1], { size: 17 }),
    cell("1  2  3  4  5  6  7  8  9", w[2], { align: AlignmentType.CENTER, color: "808080", size: 16 })] }));
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: w, rows: [head, ...rows] });
}

function simpleTable(rows, widths, header) {
  const tot = widths.reduce((a, b) => a + b);
  const head = new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], { shade: "D9E2F3", bold: true })) });
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: widths,
    rows: [head, ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i], { size: 17 })) }))] });
}

const children = [];
children.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 60 },
  children: [new TextRun({ text: "Expert survey — Round 1 of 2", font, size: 22, color: "808080" })] }));
children.push(new Paragraph({ spacing: { after: 200 },
  children: [new TextRun({ text: "Circular pathways for end-of-life photovoltaic modules in the European Union", font, size: 34, bold: true, color: NAVY })] }));
children.push(P("Institutional feasibility of end-of-life strategies across three time horizons", { size: 24, italics: true, color: "404040" }));
children.push(H("1. Purpose and how your answers will be used"));
children.push(P("This survey supports a research article prepared for the special issue “Embedding Circular Practices into Renewable and Sustainable Energy Production and Management” of Renewable and Sustainable Energy Reviews. The study projects the wave of end-of-life photovoltaic (PV) modules that EU member states will face between now and 2050 and asks which circular strategies should be activated, and when, in member states with different levels of circular-economy readiness."));
children.push(P("Quantifiable aspects of each strategy (treatment cost, material recovery rates, avoided emissions, critical-raw-material recovery, employment) are taken from published life-cycle and techno-economic studies. Your judgement is needed only for the institutional aspects that no dataset captures: regulatory readiness, enforcement feasibility, actor and market readiness, and social acceptance."));
children.push(P("The survey takes 20–30 minutes. Responses are anonymous; only an aggregate profile of the panel (roles, sectors, years of experience) is reported. Ratings are combined using a fuzzy consensus procedure; in Round 2 you will see the panel’s aggregated distribution for each item and may revise your rating. No individual response is identifiable in any output."));
children.push(H("2. About you (no name required)"));
children.push(simpleTable([
  ["Primary role", "☐ Policy / regulator   ☐ Producer-responsibility organisation   ☐ PV installer / EPC   ☐ Recycler / waste operator   ☐ Researcher   ☐ Other: ________"],
  ["Sector focus", "☐ PV manufacturing   ☐ PV deployment / O&M   ☐ Waste & recycling   ☐ Circular-economy policy   ☐ Other: ________"],
  ["Years of professional experience with PV or WEEE", "☐ < 3   ☐ 3–7   ☐ 8–15   ☐ > 15"],
  ["Member states you know best (up to three)", "________   ________   ________"],
  ["Self-assessed familiarity with PV end-of-life issues", "☐ Basic   ☐ Working knowledge   ☐ Expert"],
], [3600, 5700], ["Item", "Response"]));
children.push(H("3. Definitions used in this survey"));
children.push(H("3.1 End-of-life strategies (alternatives)", HeadingLevel.HEADING_2));
children.push(P("Each alternative is a distinct circular practice, mapped to the R-strategy ladder (R0 refuse … R9 recover). Please rate each alternative as a system-level pathway that a member state could prioritise, not as an individual project."));
children.push(simpleTable(ALTS.map(a => [a[0], a[1], a[2], a[3]]), [600, 2900, 1700, 4100], ["", "Alternative", "R-strategy", "Description"]));
children.push(H("3.2 Institutional criteria", HeadingLevel.HEADING_2));
children.push(simpleTable(CRIT.map(c => [c[0], c[1], c[2]]), [600, 2800, 5900], ["", "Criterion", "What to consider"]));
children.push(H("3.3 Time horizons", HeadingLevel.HEADING_2));
children.push(simpleTable(HORIZONS.map(h => [h[0], h[1], h[2]]), [700, 1800, 6800], ["", "Horizon", "Context"]));
children.push(H("3.4 Rating scale", HeadingLevel.HEADING_2));
children.push(P("Please circle or mark one level per cell. The scale is deliberately coarse; use VL/VH only where you are confident. For analysis, each level is converted to a triangular fuzzy number (shown for transparency; you do not need to use the numbers)."));
children.push(simpleTable(SCALE, [900, 2400, 3000], ["Code", "Meaning", "Fuzzy number (l, m, u)"]));
children.push(new Paragraph({ children: [new PageBreak()] }));

children.push(H("4. Ratings by horizon"));
children.push(P("For each horizon, rate how far each alternative satisfies each institutional criterion in a typical EU member state, assuming currently announced policy (e.g. the WEEE Directive revision, Ecodesign requirements for PV, the Critical Raw Materials Act) is implemented as planned. Section 5 then asks how these ratings differ between member-state groups."));
HORIZONS.forEach((h, i) => {
  if (i === 2) children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(H(`4.${h[0].slice(1)} Horizon ${h[0]}: ${h[1]} — ${h[2]}`, HeadingLevel.HEADING_2));
  children.push(ratingTable(h));
  children.push(P("Optional comment for this horizon: ________________________________________________________________", { size: 18, color: "606060", spacing: { before: 80, after: 200 } }));
});
children.push(new Paragraph({ children: [new PageBreak()] }));

children.push(H("5. Member-state context"));
children.push(P("Our benchmarking of Eurostat circular-economy indicators (2012–2023) distinguishes two groups of member states: consolidated leaders, which have ranked consistently in the upper tier on the EU monitoring framework (e.g. the Netherlands, Belgium, Luxembourg, France, Italy, Austria, Germany, Estonia), and converging member states, which have lower or more volatile readiness (the remaining nineteen). For the peak-wave horizon (2031–2040), how would you rate the overall institutional feasibility of each alternative in each group?"));
children.push(contextTable());
children.push(P("Which single factor most limits the converging group? ________________________________________________", { size: 18, color: "606060", spacing: { before: 80 } }));

children.push(H("6. Relative importance of criteria"));
children.push(P("When a member state chooses which end-of-life pathway to prioritise, how important is each criterion? Institutional criteria C1–C4 are those you rated above; C5–C9 are quantified from the literature and are listed so that you can weigh all criteria on the same scale."));
children.push(weightTable());

children.push(H("7. Open questions"));
[
  "Which policy instrument would most accelerate high-value recycling (A5) before 2035?",
  "Is export for second-life use (A3) a legitimate circular pathway or a leakage risk? Under what conditions?",
  "Are there alternatives or criteria missing from this survey that you consider essential?",
].forEach((q, i) => { children.push(P(`7.${i + 1} ${q}`, { bold: true, spacing: { before: 120, after: 60 } })); children.push(P("______________________________________________________________________________________________", { color: "808080" })); children.push(P("______________________________________________________________________________________________", { color: "808080" })); });

children.push(H("8. Round 2"));
children.push(P("Within three weeks you will receive a short Round-2 form showing, for each item, the panel’s aggregated rating and your own Round-1 rating. You may keep or revise your rating. Items reaching a consensus threshold in Round 1 will not be re-asked."));
children.push(P("Thank you for your contribution.", { bold: true, spacing: { before: 200 } }));

const doc = new Document({
  styles: { default: { document: { run: { font, size: 21 } } } },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{ properties: { page: { margin: { top: 1000, bottom: 1000, left: 1100, right: 1100 } } }, children }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(process.argv[2], buf); console.log("written", process.argv[2]); });
