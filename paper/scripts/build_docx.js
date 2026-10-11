// Build the anonymised manuscript and the separate title page (.docx) from content.js.
// Run: python model.py && python make_figures.py && node build_docx.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, BorderStyle, ShadingType, PageBreak, Footer, PageNumber, LineNumberRestartFormat,
  VerticalAlign, LevelFormat, TabStopType,
} = require("docx");
const C = require("./content.js");

const ROOT = path.join(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const FONT = "Times New Roman";
const SIZE = 24;
const DOUBLE = { line: 480 };
const TABLE_W = 9360;

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

// inline markup: **bold**, *italic*, ~subscript~, ^superscript^
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|~[^~]+~|\^[^^]+\^)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else if (t.startsWith("*")) out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    else if (t.startsWith("~")) out.push(new TextRun({ text: t.slice(1, -1), subScript: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), superScript: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

const P = (text, opts = {}) => new Paragraph({
  children: runs(text, opts.run || {}), alignment: opts.align || AlignmentType.JUSTIFIED,
  spacing: { ...DOUBLE, after: 0, before: 0 }, indent: opts.noIndent ? undefined : { firstLine: 360 },
});
const H = (text, level) => new Paragraph({
  heading: level,
  children: [new TextRun({ text, font: FONT, bold: true, italics: level === HeadingLevel.HEADING_3,
    size: level === HeadingLevel.HEADING_1 ? 26 : 24 })],
  spacing: { line: 480, before: level === HeadingLevel.HEADING_1 ? 240 : 120, after: 0 }, keepNext: true,
});

const line = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function makeTable(t) {
  const sum = t.widths.reduce((a, b) => a + b, 0);
  const widths = t.widths.map((w) => Math.round((w * TABLE_W) / sum));
  widths[widths.length - 1] += TABLE_W - widths.reduce((a, b) => a + b, 0);
  const cell = (text, i, head, last, bold) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA }, margins: { top: 50, bottom: 50, left: 80, right: 80 },
    verticalAlign: VerticalAlign.CENTER,
    borders: { top: head ? line : none, bottom: head || last ? line : none, left: none, right: none },
    shading: head ? { fill: "F2F2F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
    children: [new Paragraph({ alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { line: 240 },
      children: runs(String(text), { font: FONT, size: t.fontSize || 18, bold: head || bold }) })],
  });
  const rows = [new TableRow({ tableHeader: true, children: t.header.map((h, i) => cell(h, i, true, false)) })];
  t.rows.forEach((r, ri) => {
    const bold = t.boldRows !== false && /^(Total|TPES|TFC)$/.test(r[0]);
    rows.push(new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, i, false, ri === t.rows.length - 1, bold)) }));
  });
  return new Table({ width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: widths, rows });
}
const caption = (label, text) => new Paragraph({ keepNext: true, spacing: { before: 240, after: 80, line: 276 },
  children: [new TextRun({ text: label + " ", bold: true, font: FONT, size: 20 }), ...runs(text, { font: FONT, size: 20 })] });
const note = (text) => new Paragraph({ spacing: { before: 60, after: 240, line: 240 }, children: runs(text, { font: FONT, size: 18 }) });

function figure(file, n, cap, width = 610) {
  const { w, h } = pngSize(path.join(FIG, file));
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 240 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(FIG, file)),
        transformation: { width, height: Math.round((width * h) / w) },
        altText: { title: `Fig. ${n}`, description: cap, name: `fig${n}` } })] }),
    new Paragraph({ spacing: { before: 80, after: 240, line: 276 }, alignment: AlignmentType.JUSTIFIED,
      children: [new TextRun({ text: `Fig. ${n}. `, bold: true, font: FONT, size: 20 }), ...runs(cap, { font: FONT, size: 20 })] }),
  ];
}

const docStyles = {
  default: { document: { run: { font: FONT, size: SIZE } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true }, paragraph: { outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true }, paragraph: { outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, italics: true }, paragraph: { outlineLevel: 2 } },
  ],
};
const numbering = { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
  alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] };
const page = { size: { width: 11906, height: 16838 }, margin: { top: 1273, bottom: 1273, left: 1273, right: 1273 } };
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
  children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] });

// ================================================================ manuscript (anonymised)
const ch = [];
ch.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360, line: 360 },
  children: [new TextRun({ text: C.meta.title, bold: true, font: FONT, size: 32 })] }));
ch.push(H("Highlights", HeadingLevel.HEADING_1));
C.meta.highlights.forEach((h) => ch.push(new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { line: 360 },
  children: runs(h, { font: FONT, size: SIZE }) })));
ch.push(H("Graphical abstract", HeadingLevel.HEADING_1));
{
  const { w, h } = pngSize(path.join(FIG, "Fig02_sankey.png"));
  ch.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png",
    data: fs.readFileSync(path.join(FIG, "Fig02_sankey.png")), transformation: { width: 600, height: Math.round((600 * h) / w) },
    altText: { title: "Graphical abstract", description: "Sankey diagram of Oman's reconciled 2025 energy balance", name: "ga" } })] }));
}
ch.push(new Paragraph({ children: [new PageBreak()] }));
ch.push(H("Abstract", HeadingLevel.HEADING_1));
ch.push(P(C.meta.abstract, { noIndent: true }));
ch.push(new Paragraph({ spacing: { ...DOUBLE, before: 120 }, children: [new TextRun({ text: "Keywords: ", bold: true, font: FONT, size: SIZE }),
  new TextRun({ text: C.meta.keywords.join("; "), font: FONT, size: SIZE })] }));
ch.push(H("Abbreviations", HeadingLevel.HEADING_1));
ch.push(makeTable({ widths: [1600, 7760], header: ["Abbreviation", "Definition"], rows: C.abbreviations, boldRows: false }));
ch.push(new Paragraph({ children: [new PageBreak()] }));

const lvl = { h1: HeadingLevel.HEADING_1, h2: HeadingLevel.HEADING_2, h3: HeadingLevel.HEADING_3 };
for (const b of C.body) {
  if (lvl[b.type]) ch.push(H(b.text, lvl[b.type]));
  else if (b.type === "p") ch.push(P(b.text));
  else if (b.type === "eq") ch.push(new Paragraph({
    tabStops: [{ type: TabStopType.CENTER, position: 4680 }, { type: TabStopType.RIGHT, position: 9360 }],
    spacing: { ...DOUBLE, before: 60, after: 60 },
    children: [new TextRun({ text: "\t", font: FONT, size: SIZE }), ...runs(b.text, { font: FONT, size: 22, italics: true }),
      new TextRun({ text: `\t(${b.n})`, font: FONT, size: SIZE })] }));
  else if (b.type === "table") { ch.push(caption(`Table ${b.n}.`, b.caption)); ch.push(makeTable(b)); ch.push(note(b.note || " ")); }
  else if (b.type === "balance") {
    ch.push(caption("Table 5.", "Reconciled energy balance of Oman, 2025 (ktoe; central case H1)."));
    ch.push(makeTable({ widths: [2050, 1000, 1000, 1000, 1000, 900, 850, 1050, 1100], fontSize: 16,
      header: ["Flow (ktoe)", "Crude oil", "Refined products", "Natural gas", "LNG", "Coal & lignite", "Solar & wind", "Electricity", "Total"],
      rows: C.balanceRows }));
    ch.push(note("Negative transformation entries are inputs and positive entries outputs. Crude oil exports are reconciled to refinery intake (Section 2.4.1); natural gas production excludes reinjection. Totals may not sum exactly owing to rounding."));
  } else if (b.type === "fig") ch.push(...figure(b.file, b.n, b.caption));
}
for (const b of C.backMatter) ch.push(b.type === "h1" ? H(b.text, HeadingLevel.HEADING_2) : P(b.text, { noIndent: true }));
ch.push(new Paragraph({ children: [new PageBreak()] }));
ch.push(H("References", HeadingLevel.HEADING_1));
C.references.forEach((r) => ch.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 360, after: 80 },
  indent: { left: 360, hanging: 360 }, children: runs(r, { font: FONT, size: 22 }) })));
ch.push(new Paragraph({ children: [new PageBreak()] }));
ch.push(H("Appendix A. Emission factors", HeadingLevel.HEADING_1));
ch.push(caption("", C.appendixA.caption)); ch.push(makeTable({ ...C.appendixA, boldRows: false })); ch.push(note(C.appendixA.note));
ch.push(H("Appendix B. Product-specific conversion factors", HeadingLevel.HEADING_1));
ch.push(caption("", C.appendixB.caption)); ch.push(makeTable({ ...C.appendixB, boldRows: false })); ch.push(note(C.appendixB.note));

const manuscript = new Document({ creator: "", title: C.meta.title, styles: docStyles, numbering,
  sections: [{ properties: { page, lineNumbers: { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS, distance: 300 } },
    footers: { default: footer }, children: ch }] });

// ================================================================ title page (not anonymised)
const tp = [];
const t = (text, o = {}) => new Paragraph({ alignment: o.align || AlignmentType.LEFT, spacing: { after: o.after ?? 120, line: 360 },
  children: runs(text, { font: FONT, size: o.size || SIZE, bold: o.bold, italics: o.italics }) });
tp.push(t(C.meta.title, { align: AlignmentType.CENTER, size: 30, bold: true, after: 300 }));
tp.push(t("Author One^a,*^, Author Two^b^, Author Three^a^", { align: AlignmentType.CENTER }));
tp.push(t("^a^ Department, Institution, City, Postal code, Sultanate of Oman", { align: AlignmentType.CENTER, italics: true, size: 20, after: 40 }));
tp.push(t("^b^ Department, Institution, City, Postal code, Country", { align: AlignmentType.CENTER, italics: true, size: 20 }));
tp.push(t("* Corresponding author. E-mail: name@institution.om; ORCID: 0000-0000-0000-0000", { align: AlignmentType.CENTER, size: 20, after: 300 }));
tp.push(t("Running title: " + C.meta.runningTitle, { size: 20, after: 240 }));
const sec = (h, body) => { tp.push(H(h, HeadingLevel.HEADING_2)); tp.push(t(body)); };
sec("CRediT authorship contribution statement", "Author One: Conceptualization, Methodology, Data curation, Formal analysis, Software, Writing – original draft. Author Two: Validation, Visualization, Writing – review & editing. Author Three: Supervision, Writing – review & editing.");
sec("Declaration of competing interest", "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.");
sec("Funding", "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.");
sec("Data permission", "National energy statistics were used with the written permission of the Ministry of Energy and Minerals of the Sultanate of Oman (letter reference and date).");
sec("Acknowledgements", "The authors thank the Ministry of Energy and Minerals and the National Centre for Statistics and Information for providing data and for comments on the reconciliation procedures.");
const titlePage = new Document({ creator: "", title: "Title page", styles: docStyles, numbering,
  sections: [{ properties: { page }, footers: { default: footer }, children: tp }] });

Promise.all([
  Packer.toBuffer(manuscript).then((b) => fs.writeFileSync(path.join(ROOT, "Manuscript_anonymised.docx"), b)),
  Packer.toBuffer(titlePage).then((b) => fs.writeFileSync(path.join(ROOT, "Title_page.docx"), b)),
]).then(() => console.log("wrote Manuscript_anonymised.docx and Title_page.docx"));
