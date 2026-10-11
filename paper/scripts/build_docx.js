// Build the submission manuscript (.docx) from content.js. Run: node build_docx.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, BorderStyle, ShadingType, PageBreak, Footer, PageNumber, LineNumberRestartFormat,
  VerticalAlign, LevelFormat, TabStopType,
} = require("docx");
const C = require("./content.js");

const FIG = path.join(__dirname, "..", "figures");
const FONT = "Times New Roman";
const SIZE = 24; // 12 pt
const DOUBLE = { line: 480 };
const TABLE_W = 9360; // 6.5 in

// ---- inline markup: **bold**, *italic*, ~subscript~
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|~[^~]+~)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else if (t.startsWith("*")) out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), subScript: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

const P = (text, opts = {}) =>
  new Paragraph({
    children: runs(text, opts.run || {}),
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { ...DOUBLE, after: opts.after ?? 0, before: opts.before ?? 0 },
    indent: opts.noIndent ? undefined : { firstLine: 360 },
    keepNext: opts.keepNext,
    style: opts.style,
  });

const H = (text, level) =>
  new Paragraph({
    heading: level,
    children: [new TextRun({ text, font: FONT, bold: true, italics: level === HeadingLevel.HEADING_3,
      size: level === HeadingLevel.HEADING_1 ? 26 : 24 })],
    spacing: { line: 480, before: level === HeadingLevel.HEADING_1 ? 240 : 120, after: 0 },
    keepNext: true,
  });

const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };

function makeTable(t) {
  const sum = t.widths.reduce((a, b) => a + b, 0);
  const widths = t.widths.map((w) => Math.round((w * TABLE_W) / sum));
  widths[widths.length - 1] += TABLE_W - widths.reduce((a, b) => a + b, 0);
  const cell = (text, i, isHead, isLastRow, isTotal) =>
    new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      margins: { top: 50, bottom: 50, left: 80, right: 80 },
      verticalAlign: VerticalAlign.CENTER,
      borders: {
        top: isHead ? border : none,
        bottom: isHead || isLastRow ? border : none,
        left: none, right: none,
      },
      shading: isHead ? { fill: "F2F2F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
      children: [new Paragraph({
        alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
        spacing: { line: 240 },
        children: runs(String(text), { font: FONT, size: t.fontSize || 18, bold: isHead || isTotal }),
      })],
    });
  const rows = [new TableRow({ tableHeader: true, children: t.header.map((h, i) => cell(h, i, true, false)) })];
  t.rows.forEach((r, ri) => {
    const last = ri === t.rows.length - 1;
    const total = /^Total|^TPES|^TFC$|^Total Final/.test(r[0]) && t.bold !== false;
    rows.push(new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, i, false, last, total)) }));
  });
  return new Table({ width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: widths, rows });
}

function caption(label, text) {
  return new Paragraph({
    keepNext: true,
    spacing: { before: 240, after: 80, line: 276 },
    children: [new TextRun({ text: label + " ", bold: true, font: FONT, size: 20 }), ...runs(text, { font: FONT, size: 20 })],
  });
}
function note(text) {
  return new Paragraph({ spacing: { before: 60, after: 240, line: 240 }, children: runs(text, { font: FONT, size: 18, italics: false }) });
}

// ---- IRES balance matrix (Table 4)
function balanceTable() {
  const header = ["Flow (ktoe)", "Crude oil", "Refined products", "Natural gas", "LNG", "Coal & lignite", "Solar & wind", "Electricity", "Total"];
  const d = "–";
  const rows = [
    ["Indigenous production", "49,742.6", d, "51,459.2", d, d, "387.8", d, "101,589.6"],
    ["Imports", "9,668.9", d, d, d, "172.1", d, d, "9,841.0"],
    ["Exports", "−41,882.7", "−19,008.0", d, "−12,317.0", "−3.3", d, d, "−73,211.0"],
    ["International marine bunkers", d, "−453.8", d, d, d, d, d, "−453.8"],
    ["Stock change", "0.0", "0.0", "0.0", "0.0", "0.0", d, d, "0.0"],
    ["TPES", "17,528.8", "−19,461.8", "51,459.2", "−12,317.0", "168.7", "387.8", d, "37,765.8"],
    ["Oil refineries", "−17,528.8", "30,570.8", d, d, d, d, d, "13,042.0*"],
    ["Power plants", d, d, "−13,974.0", d, d, "−387.8", "4,383.7", "−9,978.1"],
    ["LNG liquefaction", d, d, "−15,273.3", "12,317.0", d, d, d, "−2,956.3"],
    ["Energy-industry own use", d, d, "−11,880.0", d, d, d, d, "−11,880.0"],
    ["Losses and plant own use", d, d, d, d, d, d, "−510.9", "−510.9"],
    ["Statistical difference", "0.0", "0.0", "0.9", "0.0", "0.0", "0.0", "0.0", "0.9"],
    ["TFC", d, "11,109.0", "10,331.0", d, "168.7", d, "3,872.8", "25,481.7"],
    ["  Industrial", d, "950.7", "10,331.0", d, "168.7", d, "699.7", "12,150.1"],
    ["  Transport", d, "4,435.5", d, d, d, d, d, "4,435.5"],
    ["  Residential", d, "316.9", d, d, d, d, "1,601.7", "1,918.6"],
    ["  Commercial", d, d, d, d, d, d, "1,045.9", "1,045.9"],
    ["  Government", d, d, d, d, d, d, "390.3", "390.3"],
    ["  Other / unallocated", d, "5,406.2", d, d, d, d, "135.1", "5,541.3"],
  ];
  return makeTable({ widths: [2050, 1000, 1000, 1000, 1000, 900, 850, 1050, 1100], header, rows, fontSize: 16 });
}

// ---- assemble
const children = [];
// Title page
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240, line: 360 },
  children: [new TextRun({ text: C.meta.title, bold: true, font: FONT, size: 32 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
  children: [new TextRun({ text: C.meta.authors, font: FONT, size: SIZE })] }));
C.meta.affiliations.forEach((a) => children.push(new Paragraph({ alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: a, italics: true, font: FONT, size: 20 })] })));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 360 },
  children: [new TextRun({ text: C.meta.corresponding, font: FONT, size: 20 })] }));
children.push(new Paragraph({ children: [new TextRun({ text: "Target journals: ", bold: true, font: FONT, size: 20 }),
  new TextRun({ text: "Energy Policy; Renewable and Sustainable Energy Reviews; Applied Energy", font: FONT, size: 20 })] }));
children.push(new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: "Running title: ", bold: true, font: FONT, size: 20 }),
  new TextRun({ text: C.meta.runningTitle, font: FONT, size: 20 })] }));

// Highlights
children.push(H("Highlights", HeadingLevel.HEADING_1));
C.meta.highlights.forEach((h) => children.push(new Paragraph({ numbering: { reference: "bul", level: 0 },
  spacing: { line: 360 }, children: runs(h, { font: FONT, size: SIZE }) })));

// Graphical abstract
children.push(H("Graphical abstract", HeadingLevel.HEADING_1));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png",
  data: fs.readFileSync(path.join(FIG, "Fig02_sankey.png")), transformation: { width: 600, height: Math.round(600 * 2714 / 4004) },
  altText: { title: "Graphical abstract", description: "Sankey diagram of Oman's 2025 energy balance", name: "ga" } })] }));
children.push(new Paragraph({ children: [new PageBreak()] }));

// Abstract & keywords
children.push(H("Abstract", HeadingLevel.HEADING_1));
children.push(P(C.meta.abstract, { noIndent: true }));
children.push(new Paragraph({ spacing: { ...DOUBLE, before: 120 }, children: [new TextRun({ text: "Keywords: ", bold: true, font: FONT, size: SIZE }),
  new TextRun({ text: C.meta.keywords.join("; "), font: FONT, size: SIZE })] }));

// Abbreviations
children.push(H("Abbreviations", HeadingLevel.HEADING_1));
children.push(makeTable({ widths: [1600, 7760], header: ["Abbreviation", "Definition"], rows: C.abbreviations, bold: false }));
children.push(new Paragraph({ children: [new PageBreak()] }));

// Body
const levelOf = { h1: HeadingLevel.HEADING_1, h2: HeadingLevel.HEADING_2, h3: HeadingLevel.HEADING_3 };
for (const b of C.body) {
  if (levelOf[b.type]) children.push(H(b.text, levelOf[b.type]));
  else if (b.type === "p") children.push(P(b.text));
  else if (b.type === "eq") {
    children.push(new Paragraph({
      tabStops: [{ type: TabStopType.CENTER, position: 4680 }, { type: TabStopType.RIGHT, position: 9360 }],
      spacing: { ...DOUBLE, before: 60, after: 60 },
      children: [new TextRun({ text: "\t", font: FONT, size: SIZE }), ...runs(b.text, { font: FONT, size: SIZE, italics: true }),
        new TextRun({ text: `\t(${b.n})`, font: FONT, size: SIZE })],
    }));
  } else if (b.type === "table") {
    children.push(caption(`Table ${b.n}.`, b.caption));
    children.push(makeTable(b));
    children.push(note(b.note || " "));
  } else if (b.type === "balance") {
    children.push(caption("Table 4.", "IRES-consistent National Energy Balance of Oman, 2025 (ktoe)."));
    children.push(balanceTable());
    children.push(note("*Refinery output exceeds the recorded crude input; the 13,042.0 ktoe apparent gain is the unreconciled feedstock gap discussed in Section 2.3.5. Negative transformation entries are inputs, positive entries outputs. Totals may not sum exactly owing to rounding."));
  } else if (b.type === "fig") {
    const w = 610; const h = Math.round((w * b.h) / b.w);
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 240 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(FIG, b.file)),
        transformation: { width: w, height: h },
        altText: { title: `Fig. ${b.n}`, description: b.caption, name: `fig${b.n}` } })] }));
    children.push(new Paragraph({ spacing: { before: 80, after: 240, line: 276 }, alignment: AlignmentType.JUSTIFIED,
      children: [new TextRun({ text: `Fig. ${b.n}. `, bold: true, font: FONT, size: 20 }), ...runs(b.caption, { font: FONT, size: 20 })] }));
  }
}
for (const b of C.backMatter) {
  if (b.type === "h1") children.push(H(b.text, HeadingLevel.HEADING_2));
  else children.push(P(b.text, { noIndent: true }));
}

// References
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(H("References", HeadingLevel.HEADING_1));
C.references.forEach((r) => children.push(new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { line: 360, after: 80 }, indent: { left: 360, hanging: 360 },
  children: runs(r, { font: FONT, size: 22 }) })));

// Appendices
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(H("Appendix A. Emission factors", HeadingLevel.HEADING_1));
children.push(caption("", C.appendixA.caption));
children.push(makeTable({ ...C.appendixA, bold: false }));
children.push(note(C.appendixA.note));
children.push(H("Appendix B. Priority indicator set", HeadingLevel.HEADING_1));
children.push(caption("", C.appendixB.caption));
children.push(makeTable({ ...C.appendixB, bold: false }));
children.push(note("Values refer to the IRES-restated balance; ranges in parentheses reflect the refinery-closure and displaced-plant sensitivities."));

const doc = new Document({
  creator: "Authors",
  title: C.meta.title,
  styles: {
    default: { document: { run: { font: FONT, size: SIZE } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 24, bold: true }, paragraph: { outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 24, bold: true, italics: true }, paragraph: { outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1273, bottom: 1273, left: 1273, right: 1273 } },
      lineNumbers: { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS, distance: 300 },
    },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children,
  }],
});

const out = path.join(__dirname, "..", "Oman_NEB_2025_Q1_Manuscript.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out); });
