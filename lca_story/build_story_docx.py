"""
Builds the narrative Word edition of the Jordan transport LCA paper.

Run lca_matrix_model.py first (it writes output/results.json and the figures),
then:  python build_story_docx.py   -> output/The_Price_of_Clean_LCA_Story.docx
"""

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Cm

HERE = Path(__file__).parent
OUT = HERE / "output"
R = json.loads((OUT / "results.json").read_text())
DET = R["deterministic"]

NAVY = RGBColor(0x12, 0x2B, 0x4A)
TEAL = RGBColor(0x0E, 0x7C, 0x66)
GREY = RGBColor(0x52, 0x51, 0x4E)
RED = RGBColor(0xB8, 0x32, 0x32)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)  # A4
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Inches(1.0))
sec.top_margin = sec.bottom_margin = Inches(0.9)

st = doc.styles
st["Normal"].font.name = "Georgia"
st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), "Georgia")
st["Normal"].font.size = Pt(11)
st["Normal"].paragraph_format.space_after = Pt(8)
st["Normal"].paragraph_format.line_spacing = 1.2
for name, size, color in [("Heading 1", 20, NAVY), ("Heading 2", 14, TEAL), ("Heading 3", 12, NAVY)]:
    s = st[name]
    s.font.name = "Calibri"
    s.element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    s.element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = color
    s.paragraph_format.space_before = Pt(18 if name == "Heading 1" else 12)
    s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.keep_with_next = True


# ---------------------------------------------------------------- helpers
def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def cell_borders(cell, color="FFFFFF", left=None):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for edge in ("top", "bottom", "right", "left"):
        e = OxmlElement(f"w:{edge}")
        if edge == "left" and left:
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "36")
            e.set(qn("w:color"), left)
        else:
            e.set(qn("w:val"), "nil")
        b.append(e)
    tcPr.append(b)


def rich(par, text, size=None, color=None, italic=False):
    """Add text with **bold** spans."""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        r = par.add_run(part)
        r.bold = i % 2 == 1
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
    return par


def p(text, italic=False, align=None, size=None, color=None, after=None):
    par = doc.add_paragraph()
    rich(par, text, size=size, color=color, italic=italic)
    if align:
        par.alignment = align
    if after is not None:
        par.paragraph_format.space_after = Pt(after)
    return par


def h(text, level=1):
    return doc.add_heading(text, level=level)


def bullets(items):
    for it in items:
        par = doc.add_paragraph(style="List Bullet")
        rich(par, it)
        par.paragraph_format.space_after = Pt(4)


def callout(title, body, accent="0E7C66", fill="EAF5F1"):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]
    fix_widths(t, [6.27])
    no_split(t)
    shade(c, fill)
    cell_borders(c, left=accent)
    c.paragraphs[0].paragraph_format.space_after = Pt(2)
    r = c.paragraphs[0].add_run(title.upper())
    r.bold = True
    r.font.size = Pt(9)
    r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string(accent)
    par = c.add_paragraph()
    rich(par, body, size=11)
    par.paragraph_format.space_after = Pt(4)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def quote(text):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(10)
    par.paragraph_format.space_after = Pt(14)
    par.paragraph_format.left_indent = Inches(0.6)
    par.paragraph_format.right_indent = Inches(0.6)
    r = par.add_run(f"“{text}”")
    r.italic = True
    r.font.size = Pt(14)
    r.font.color.rgb = TEAL


def figure(path, caption, width=6.2):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = GREY


def code(text):
    t = doc.add_table(rows=1, cols=1)
    c = t.rows[0].cells[0]
    fix_widths(t, [6.27])
    shade(c, "F3F2EE")
    cell_borders(c, left="122B4A")
    c.paragraphs[0].text = ""
    for i, line in enumerate(text.strip("\n").split("\n")):
        par = c.paragraphs[0] if i == 0 else c.add_paragraph()
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.0
        r = par.add_run(line if line else " ")
        r.font.name = "Consolas"
        r.element.rPr.rFonts.set(qn("w:hAnsi"), "Consolas")
        r.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def fix_widths(t, widths):
    t.autofit = False
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w * 1440)))
    for row in t.rows:
        for c, w in zip(row.cells, widths):
            c.width = Inches(w)


def no_split(t):
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        el = OxmlElement("w:cantSplit")
        trPr.append(el)


def table(header, rows, widths, font=9.5, header_fill="122B4A", zebra="F5F4F0", bold_last=False, numeric=True):
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for i, txt in enumerate(header):
        c = t.rows[0].cells[i]
        shade(c, header_fill)
        c.paragraphs[0].text = ""
        r = c.paragraphs[0].add_run(txt)
        r.bold = True
        r.font.size = Pt(font)
        r.font.name = "Calibri"
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for ri, row in enumerate(rows, start=1):
        for ci, txt in enumerate(row):
            c = t.rows[ri].cells[ci]
            if ri % 2 == 0:
                shade(c, zebra)
            c.paragraphs[0].text = ""
            r = c.paragraphs[0].add_run(str(txt))
            r.font.size = Pt(font)
            r.font.name = "Calibri"
            r.bold = bold_last and ri == len(rows)
            if ci > 0 and numeric:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fix_widths(t, widths)
    no_split(t)
    for row in t.rows:
        for c in row.cells:
            for par in c.paragraphs:
                par.paragraph_format.space_after = Pt(1)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_page_number(section):
    par = section.footer.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run()
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = txt
        run._r.append(el)
    run.font.size = Pt(9)
    run.font.color.rgb = GREY


add_page_number(sec)

# Numbers used in the narrative (all from the Python model / paper)
bd = R["baseline_breakdown"]
up_total = DET["Baseline"]["upstream_gg"]
base_model = DET["Baseline"]["model_gwp_gg"]
s1 = DET["S1"]
s1_avoided = 0.2 * bd["Gasoline vehicles"]["tailpipe"] + 0.2 * bd["Gasoline vehicles"]["upstream"]
s1_grid_cal = s1["grid_gg"] - DET["Baseline"]["grid_gg"]
s1_grid_phys = s1["physics_gwp_gg"] - (base_model - s1_avoided)
mm = R["micro_medians"]
thr = R["swap_thresholds"]
pb = R["p_below_2400"]
gq, dq = R["macro_gwp_q"], R["macro_daly_q"]
sw = R["sweep"]
f0 = lambda x: f"{x:,.0f}"

# ================================================================= COVER
for _ in range(5):
    doc.add_paragraph()
p("A STORY TOLD IN MATRICES", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, color=TEAL, after=6)
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("The Price of Clean")
r.bold = True
r.font.size = Pt(36)
r.font.name = "Calibri"
r.font.color.rgb = NAVY
p("How Jordan’s roads revealed the Grid Penalty, the Pollution Swap — and a way out for the developing world",
  align=WD_ALIGN_PARAGRAPH.CENTER, size=15, color=GREY, italic=True, after=30)
p("A narrative edition of the Well-to-Wheel Life Cycle Assessment of the Jordanian transport fleet (2022), "
  "re-computed in Python with matrix algebra and 10,000-run Monte Carlo simulation",
  align=WD_ALIGN_PARAGRAPH.CENTER, size=11, after=40)
p("Based on the research of A. O. H. Ghawanmeh", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, color=NAVY)
p("Jordan University of Science and Technology", align=WD_ALIGN_PARAGRAPH.CENTER, size=10, color=GREY)
page_break()

# ================================================================= ABSTRACT
h("The story in one page", 1)
p("Every country that wants cleaner air and a cooler planet is told the same simple story: buy electric cars, "
  "build more buses, tighten engine standards. This study asks what happens when that story meets a real "
  "developing economy — one that imports almost all of its energy and still burns fossil fuel to make most of "
  "its electricity.")
p("Using Jordan’s entire 2022 fleet of about **1.85 million vehicles** as a living laboratory, we followed every "
  "kilogram of emissions from the oil well and the power station all the way to the wheel. The accounting is "
  "done with matrices: a technology matrix **A** that describes how fuels, electricity and vehicles depend on "
  "each other, solved as **s = A⁻¹f**, and characterization factors that turn emissions into climate damage and "
  "lost years of healthy life. A Python model reproduces the SimaPro results of the original study and then "
  "stress-tests them 10,000 times.")
callout("What we found",
        "**1. The grid penalty.** An electric car in Jordan is cleaner than any petrol or diesel car "
        f"(≈{mm['Battery EV (JO grid)']:.0f} vs ≈{mm['Gasoline car']:.0f} g CO₂-eq per km) — but part of its gain is "
        "moved, not removed: it travels from millions of exhaust pipes to a few power-station chimneys.\n"
        "**2. The pollution swap.** A diesel bus carrying fewer than about "
        f"{thr['Conventional diesel bus']:.0f} passengers puts more fine particles into the street, per passenger, "
        "than the cars it replaces.\n"
        "**3. The incremental trap.** 20% EVs, diesel buses and Euro 6 engines each cut only 9–11% of emissions; "
        "none can push the sector below ≈2,400 Gg CO₂-eq.\n"
        "**4. The way out.** Full electrification cuts emissions by about 84% (to 448 Gg) and health damage from "
        "2,790 to 449 DALYs — and on a solar-and-wind grid, the same fleet would fall to about "
        f"{f0(sw['S4_calibrated@30'])} Gg, close to the floor set by aviation.")
quote("The question is not whether to electrify. It is whether we clean the grid at the same speed.")
page_break()

# ================================================================= PROLOGUE
h("Prologue: Two chimneys", 1)
p("It is seven in the morning in Amman. The traffic on the main roads is already thick, and the air carries "
  "the familiar smell of exhaust. Each car is a small chimney on wheels. Together, in 2022, Jordan’s vehicles "
  "and domestic flights released about **2,800 thousand tonnes of CO₂-equivalent** — and the fine particles "
  "from their engines settled into the lungs of the people who walk beside them.")
p("Now imagine every one of those cars replaced, overnight, by an electric car. The streets go quiet. "
  "The air at the bus stop clears. It looks like the end of the story.")
p("But follow the charging cable. It runs through the wall, down the street, along the high-voltage lines, "
  "and ends at a power station burning imported natural gas or domestic oil shale. The chimney has not "
  "disappeared. It has moved.")
p("This is the story of what happens to pollution when we try to make it go away — and of the one path, "
  "found in the numbers, that truly works.")

# ================================================================= CH 1
h("Chapter 1 — A question the world forgot to ask", 1)
p("Transport moves the world’s economies and connects people to work, school and care. It is also one of the "
  "fastest-growing sources of greenhouse gases (UNFCCC, 2022), and the IPCC warns that efficiency gains alone "
  "will not be enough: every mode needs a deep, structural change (IPCC, 2022). The global playbook is "
  "summarised as **Avoid–Shift–Improve** (Jarre et al., 2024): avoid unnecessary trips, shift people into "
  "high-capacity public transport, and improve vehicles — mostly by electrifying them (IEA, 2024).")
p("That playbook was written in countries whose power grids are already fairly clean. Its hidden assumption "
  "is that the electricity charging an EV is low-carbon. In much of the developing world, including the Middle "
  "East and North Africa, that assumption has never been tested (Evensen et al., 2025; Al-Alawi and Al-Alawi, "
  "2022).")
p("**Jordan is the perfect place to test it.** It has almost no domestic oil and imports most of its fuel "
  "(MEMR, 2022). Transport causes about 16% of national greenhouse gas emissions and 49% of final energy use "
  "(MoEnv, 2022; Jelti et al., 2021). Solar and wind reached about 27% of grid capacity in 2022 (NEPCO, 2022), "
  "yet the electricity that actually flows remains mostly fossil, at roughly **391 g CO₂-eq per kWh** "
  "(Low Carbon Power, 2022). Jordan has also promised a 31% cut in greenhouse gases by 2030 (Ministry of "
  "Environment, 2021). The question is therefore urgent and practical:")
quote("If a fossil-powered country follows the global clean-transport playbook, does it actually get cleaner?")
p("To answer it we must look further than the exhaust pipe. Traditional inventories count only "
  "**Tank-to-Wheel** emissions — what leaves the tailpipe. They ignore the **Well-to-Tank** chain: drilling, "
  "shipping crude to Aqaba, refining it, trucking fuel across the country, and generating electricity. "
  "Burdens that are not counted are not eliminated; they are moved somewhere else or turned into a different "
  "kind of harm (Requia et al., 2018). We gave these hidden movements two names:")
bullets([
    "**The grid penalty** — emissions that leave the city streets with the EV, but reappear at the power station "
    "(Qiao et al., 2019; Buberger et al., 2022).",
    "**The pollution swap** — a change that lowers global CO₂ but raises local toxic pollution, as when "
    "half-empty diesel buses replace cars (Brewer, 2019; Grutter, 2014).",
])

# ================================================================= CH 2
h("Chapter 2 — The language of matrices", 1)
p("A country’s transport system is a web. Cars need petrol; petrol needs a refinery; the refinery needs "
  "electricity and crude oil; electric cars need the grid; the grid needs gas and oil shale. Life Cycle "
  "Assessment untangles this web with linear algebra, following ISO 14040/14044 (ISO, 2006a; ISO, 2006b).")
h("2.1  The technology matrix A", 2)
p("Each column of the **technology matrix A** is one process — for example, “Jordan’s gasoline car fleet for "
  "one year” or “one GWh from the Jordanian grid”. Each row is one product. A positive 1 on the diagonal is "
  "what the process makes; negative numbers are what it consumes. The final demand vector **f** says what "
  "society wants: one year of transport for every fleet. The amount each process must run is then:")
p("s = A⁻¹ f          (1)", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, color=NAVY)
p("Each process also releases emissions, recorded in the intervention matrix **B**, so the total flows are "
  "**g = B s**. Finally, the characterization matrix **Q** translates flows into impacts:")
p("hᵢ = Σⱼ Qᵢⱼ × gⱼ          (2)", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, color=NAVY)
p("The original study solved this system in SimaPro with the Ecoinvent 3 database and the ReCiPe 2016 "
  "Endpoint (H) method (Huijbregts et al., 2017; Weidema et al., 2013), reporting 18 midpoint categories and "
  "three damage areas: human health (DALYs), ecosystems (species·yr) and resources (USD). For this narrative "
  "edition we rebuilt the core of that system in **Python (NumPy)** — a 12 × 12 technology matrix with "
  "five fuel and energy supply chains and seven fleets — so that every step of the story can be inspected, "
  "re-run and challenged. The heart of the model is three lines:")
code("""
A, B = build_system(params)        # technology matrix and emissions matrix
s = np.linalg.solve(A, f)          # Eq. (1): how much each process must run
g = B @ s                          # flows: [tailpipe CO2-eq, upstream CO2-eq]
""")
figure(HERE / "system_boundary.png",
       "Figure 1. Well-to-Wheel boundary: the fuel and electricity chains (Well-to-Tank) and vehicle operation "
       "(Tank-to-Wheel). Source: original study.", width=5.6)

h("2.2  What the matrix looks like", 2)
p("Table 1 shows the baseline 2022 technology matrix as built in Python. Read down a column to see what a "
  "process needs: Jordan’s gasoline car fleet, for example, draws about 14,900 TJ of gasoline per year. "
  "The fuel quantities are implied by calibrating the matrix to the SimaPro baseline (Figure 3 of the "
  "original paper) with IPCC default combustion factors and a ≈20% upstream share.")
A = R["A_baseline"]
names = R["short"]
idx = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]  # omit 'Other fuels' column (no matrix inputs)
hdr = ["Product ↓ / Process →"] + [names[j] for j in idx]


def fmt(v):
    if abs(v) < 1e-9:
        return "·"
    if abs(v - 1) < 1e-9:
        return "1"
    return f"{v:,.0f}" if abs(v) >= 10 else f"{v:,.2f}"


rows = [[names[i]] + [fmt(A[i][j]) for j in idx] for i in range(5)]
table(hdr, rows, [0.99] + [0.48] * len(idx), font=6.5)
p("Table 1. Upper block of the technology matrix A (supply rows; units TJ or GWh). Diagonal entries of the "
  "fleet rows equal 1 and are omitted for space. Negative entries are inputs.", italic=True, size=9, color=GREY)

h("2.3  Four roads forward", 2)
p("Following the Avoid–Shift–Improve framework and Jordan’s climate policy (MoEnv, 2022), four futures were "
  "written into the matrix by changing **f** and the columns of **A**:")
table(["Scenario", "What changes in the matrix", "The question it asks"], [
    ["Baseline 2022", "Fleet and grid as they were in 2022", "Where do we stand?"],
    ["S1  Promoting EVs", "20% of gasoline-car demand moves to an EV column fed by the JO grid",
     "How big is the grid penalty?"],
    ["S2  Public transport", "30% of gasoline-car demand moves to a diesel-bus column",
     "Is there a pollution swap?"],
    ["S3  Euro 6 standards", "Engines more efficient; half of gasoline becomes premium low-sulphur fuel",
     "Can cleaner combustion be enough?"],
    ["S4  Full transformation", "All road fleets become electric; aviation stays fossil",
     "What is the upper limit?"],
], [1.45, 2.9, 1.92], font=9, numeric=False)
p("Three scenarios (S2, S3, S4) each have one parameter tuned so that the Python matrix matches the SimaPro "
  "result. **S1 is not tuned**: it is predicted from the EV energy ratio learned on S4 — a fair test of whether "
  "the matrix has learned the system. It lands within 0.3% of SimaPro "
  f"({f0(s1['model_gwp_gg'])} vs 2,550 Gg).", size=10.5)

h("2.4  Ten thousand possible Jordans", 2)
p("Real roads are not averages. Traffic jams, hot summers that push air-conditioning loads up by 20–50% "
  "(Alarrouqi et al., 2024), changing grid intensity and buses that are full in the morning and empty at noon "
  "all move the result. Following Henriksson et al. (2015), every uncertain input was given a probability "
  "distribution and the whole matrix was re-solved **10,000 times** for every scenario — 50,000 national "
  "inventories in all. Three questions were asked: how does one vehicle behave (micro, grid penalty), how does "
  "one bus behave (micro, pollution swap), and how does the whole sector behave (macro, incremental trap)?")
page_break()

# ================================================================= CH 3
h("Chapter 3 — Counting the cost of 2022", 1)
p(f"The matrix gives the baseline footprint as **≈2,800 Gg CO₂-eq** per year. Gasoline vehicles alone emit "
  f"1,270 Gg — almost half — in line with their ≈60% share of the fleet. Diesel vehicles add 1,080 Gg, domestic "
  f"aviation 257 Gg and hybrids 183 Gg. Electric vehicles, still rare in 2022, emit just 0.08 Gg.")
figure(OUT / "fig1_baseline_breakdown.png",
       "Figure 2. Baseline 2022 Well-to-Wheel footprint by fleet, split by the matrix into tailpipe (TTW) and "
       "upstream (WTT) emissions. Python model calibrated to SimaPro.")
p(f"The orange part of every bar is what a tailpipe-only inventory would never see: about **{f0(up_total)} Gg "
  f"({up_total / base_model:.0%})** of the sector’s emissions happen before fuel ever reaches the tank — in "
  "oil fields, tankers, the refinery and fuel trucks.")
p("The damage is not only to the climate. The SimaPro endpoint results put the human-health burden at "
  "**2,790 DALYs** — 2,790 years of healthy life lost every year. Diesel carries a disproportionate share of "
  "local harm: 497 DALYs through carcinogenic toxicity and 55.4 DALYs through non-carcinogenic toxicity, the "
  "fingerprint of heavy-duty diesel engines and their black carbon (Brewer, 2019). Fuel combustion also "
  "acidifies soils (2.05 species·yr) and damages ecosystems through ozone (1.23 species·yr).")
callout("The bill for importing fossil energy",
        "Fossil resource scarcity alone is valued at about **US$1.62 billion** for 2022 — US$703 million from "
        "gasoline vehicles and US$658 million from diesel vehicles. Every kilometre driven on imported fuel is "
        "a payment that leaves the country.", accent="B83232", fill="FBEDEC")

# ================================================================= CH 4
h("Chapter 4 — Four roads forward", 1)
p("We then let the matrix travel down each of the four roads. Figure 3 shows the result, with the SimaPro "
  "values from the original study as black diamonds.")
figure(OUT / "fig2_scenarios.png",
       "Figure 3. Sector GWP for each scenario. Bars: Python matrix model (blue = fuel chain, yellow = electricity "
       "for EV charging). Diamonds: SimaPro results of the original study.")
table(["Scenario", "Python matrix (Gg CO₂-eq)", "SimaPro (Gg CO₂-eq)", "Change vs 2022", "Health (DALYs)*"], [
    [SCENARIO, f0(DET[k]["model_gwp_gg"]), f0(DET[k]["simapro_gwp_gg"]),
     "—" if k == "Baseline" else f"{(DET[k]['simapro_gwp_gg'] / 2800 - 1):+.0%}", f0(DET[k]["simapro_daly"])]
    for k, SCENARIO in [("Baseline", "Baseline 2022"), ("S1", "S1  20% EVs"), ("S2", "S2  Diesel buses"),
                        ("S3", "S3  Euro 6"), ("S4", "S4  Full electrification")]
], [1.77, 1.25, 1.15, 1.05, 1.05], font=9.5, bold_last=True)
p("*Human-health endpoint from SimaPro / ReCiPe 2016 (H). The Python baseline (2,793 Gg) equals the sum of the "
  "fleet results in the original Figure 3; the headline 2,800 Gg is its rounded value.", italic=True, size=9,
  color=GREY)
p("The first three roads end in almost the same place: between 2,490 and 2,550 Gg, a cut of only 9–11%. "
  "Health damage barely moves — Euro 6 leaves it at 2,760 DALYs, practically identical to today, because the "
  "premium low-sulphur fuel it needs still has to be extracted, shipped and intensively refined. Only the fourth "
  "road breaks away: complete electrification brings the sector to **448 Gg (−84%)** and the health burden to "
  "**449 DALYs (−84%)**. What remains is mostly aviation, which was not electrified, and the electricity used "
  "to charge the fleet.")
p("The single-score view of the original study tells the same story: Baseline, S1, S2 and S3 sit together "
  "around 110–125 MPt, while S4 drops to about 20 MPt. Partial measures do not remove damage — they move it "
  "between categories. S1 trades climate damage for mineral scarcity (lithium, cobalt); S2 trades climate "
  "damage for local health damage.")

# ================================================================= CH 5
h("Chapter 5 — The grid penalty", 1)
p("Why does putting one in five gasoline cars on electricity cut so little? Because the energy has to come "
  "from somewhere. In the matrix, the EV column pulls on the electricity row, and the electricity row pulls "
  "on gas and oil shale. Emissions leave the street and reappear at the power plant.")
p(f"In S1 the matrix removes about {f0(s1_avoided)} Gg of gasoline emissions and adds back about "
  f"{f0(s1_grid_cal)} Gg at the power stations under the original study’s EV energy assumption. Under a stricter, "
  f"physics-based assumption (an EV using about 30% of the energy of the petrol car it replaces), the grid "
  f"takes back about **{f0(s1_grid_phys)} Gg — roughly {s1_grid_phys / s1_avoided:.0%} of the gain**. Either way, "
  f"the penalty is paid in the place where it is hardest to see.")
figure(OUT / "fig3_micro_density.png",
       "Figure 4. Monte Carlo (10,000 runs) of Well-to-Wheel emissions per kilometre. EV electricity drawn from "
       "the Jordanian grid (370–450 g/kWh) with air-conditioning loads of +0–50%.")
p(f"And yet — this is the hopeful half of the chapter — the EV still wins. Even with summer air-conditioning "
  f"and a fossil-heavy grid, its median footprint is **≈{mm['Battery EV (JO grid)']:.0f} g CO₂-eq/km**, against "
  f"≈{mm['Gasoline car']:.0f} for a gasoline car, ≈{mm['Euro 6 gasoline car']:.0f} for a Euro 6 car and "
  f"≈{mm['Modern diesel car']:.0f} for a modern diesel. In {R['micro_p_ev_below_all']:.2%} of the 10,000 runs the "
  "EV was cleaner than every combustion option. The curves barely touch. Euro 6 and modern diesel, in "
  "contrast, overlap almost completely with the baseline: cleaner combustion is a small step, not a leap. "
  "Short domestic flights sit at the level of a modern diesel car per passenger-kilometre.")
quote("The grid penalty does not mean EVs are wrong. It means the grid is part of the car.")

# ================================================================= CH 6
h("Chapter 6 — The pollution swap", 1)
p("Climate change is global: a tonne of CO₂ warms the planet equally wherever it is released. Fine particles "
  "are local: they are breathed by the people standing next to the exhaust. PM2.5 penetrates deep into the "
  "lungs and the blood, raising the risk of heart disease, stroke and lung cancer (Haines et al., 2009; "
  "WHO, 2023), and diesel engines produce about 90% of transport’s black carbon (Brewer, 2019).")
p("So we asked the matrix a very human question: **how full does a bus need to be before it is cleaner, for "
  "the people on the pavement, than the cars it replaces?**")
figure(OUT / "fig4_pollution_swap.png",
       "Figure 5. Local PM2.5 per passenger-kilometre versus bus occupancy (10,000 runs; occupancy 10–60 riders). "
       "Emission factors are illustrative and set to reproduce the 25–30 rider threshold of the original study.")
p(f"Below about **{thr['Conventional diesel bus']:.0f} passengers**, a conventional diesel bus releases more "
  f"fine particles for every passenger-kilometre than a private gasoline car. With realistic occupancy that "
  f"varies through the day, that happened in **{R['p_bus_dirtier_than_car']:.0%}** of simulated trips. A Euro VI "
  f"diesel bus lowers the break-even to about {thr['Euro VI diesel bus']:.0f} riders — better, but still exposed "
  "in off-peak hours. An electric bus, whose only particles come from brakes and tyres, is cleaner than the car "
  "with almost anyone on board.")
p("This is the pollution swap. Measured by national CO₂, a diesel-bus programme looks like success. Measured "
  "at the bus stop, in the narrow street canyons of Amman where exhaust is trapped (Morales Betancourt et al., "
  "2017; Fantke et al., 2017), it can make the air worse for exactly the people it was meant to help.")
callout("A rule for planners",
        "Never judge a public-transport project by CO₂ alone. Check the occupancy it can guarantee and the local "
        "PM2.5 it will produce. Good policy cannot trade global climate benefits for local health damage.")

# ================================================================= CH 7
h("Chapter 7 — The incremental trap", 1)
p("Finally the matrix was scaled up to the whole country and re-solved 10,000 times for each scenario, with "
  "traffic, grid intensity, air-conditioning, bus fuel use and real-world Euro 6 performance all allowed to vary.")
figure(OUT / "fig5_macro_boxplots.png",
       "Figure 6. Sector-level Monte Carlo (10,000 runs per scenario). Left: GWP from the Python matrix. Right: "
       "SimaPro health damage scaled with each run; S2 carries a wider, right-skewed occupancy uncertainty.",
       width=6.4)
p(f"The three incremental options form one tight cluster. Across all runs the sector stayed above 2,400 Gg "
  f"in {1 - pb['S1']:.1%} of cases for S1, {1 - pb['S2']:.1%} for S2 and {1 - pb['S3']:.1%} for S3. Their "
  "boxes overlap so much that, statistically, it hardly matters which of them a government chooses — this is "
  "the **incremental trap**.")
p(f"The health panel adds a warning. Under S2 the middle half of outcomes spans "
  f"{f0(dq['S2'][1])}–{f0(dq['S2'][3])} DALYs, more than twice as wide as the baseline "
  f"({f0(dq['Baseline'][1])}–{f0(dq['Baseline'][3])}), and its upper tail reaches {f0(dq['S2'][4])} DALYs — above "
  "anything seen in the baseline. A diesel-bus expansion that cannot guarantee full buses carries a real risk "
  "of making national health worse.")
p(f"Scenario 4 stands completely apart. Its 95% range is {f0(gq['S4'][0])}–{f0(gq['S4'][4])} Gg and "
  f"{f0(dq['S4'][0])}–{f0(dq['S4'][4])} DALYs — not one of the 10,000 runs comes anywhere near the incremental "
  "cluster. (The median sits slightly above the deterministic 448 Gg because the simulation deliberately adds "
  "extra summer air-conditioning load.) Only a structural change, not a better version of the old system, "
  "escapes the trap.")

# ================================================================= CH 8
h("Chapter 8 — The leapfrog", 1)
p("If the grid is part of the car, then cleaning the grid cleans every car at once. Because the model is a "
  "matrix, we can turn one dial — the carbon intensity of electricity — and watch the whole sector respond.")
figure(OUT / "fig6_grid_sweep.png",
       "Figure 7. Sector GWP as the grid becomes cleaner. Solid: EV energy as calibrated to the original study. "
       "Dotted: stricter physics-based EV energy use (sensitivity check).")
p(f"With today’s grid, full electrification gives 448 Gg. On a grid powered by solar and wind (about 30 g/kWh "
  f"over the life cycle) the same fleet would emit about **{f0(sw['S4_calibrated@30'])} Gg — a 90% cut from 2022**, "
  "and almost everything left would be aviation. Even under the stricter physics check, which gives a larger "
  f"grid penalty today ({f0(sw['S4_physics@391'])} Gg), a clean grid brings the sector down to about "
  f"{f0(sw['S4_physics@30'])} Gg. The conclusion does not depend on the assumption: **the cleaner the grid, the "
  "more every electric kilometre is worth.**")
p("Notice the flat blue line. Twenty percent EVs on any grid leaves the sector near 2,550 Gg. Cleaning the grid "
  "without electrifying the fleet does little; electrifying the fleet without cleaning the grid leaves value on "
  "the table. The two must move together.")
quote("Developing countries do not have to repeat the long, dirty road that others took. They can leapfrog it.")

# ================================================================= CH 9
h("Chapter 9 — What Jordan can teach the world", 1)
p("The numbers point to four practical actions for Jordan and for every fossil-dependent economy that is "
  "planning its clean-transport future:")
bullets([
    "**Couple the EV target to the grid target.** National EV goals should be tied, number for number, to the "
    "retirement of fossil power plants and the connection of new renewables (Al-Shetwi et al., 2020). EV policy "
    "and energy policy must stop living in separate offices.",
    "**Build “Solar-to-EV” islands now.** Require new charging depots for buses, taxis and government fleets to "
    "run on local solar microgrids. These zero-emission islands let EVs escape the grid penalty from day one "
    "(Evensen et al., 2025).",
    "**Charge with the sun.** Encourage daytime charging that soaks up solar output instead of adding to evening "
    "peaks, turning EVs from a burden on hot-climate distribution networks into flexible storage (Al-Owaifeer "
    "et al., 2020; Al-Shetwi et al., 2022).",
    "**Skip the “transition” diesel.** New bus investment should go straight to battery-electric or hydrogen "
    "fuel-cell buses rather than CNG or Euro 5/6 diesel, which lock cities into decades of fossil fuel and "
    "PM2.5 (Grutter, 2014; Jelti et al., 2021; Ahmadi et al., 2022). Feasibility studies should count the "
    "avoided health costs that justify the higher upfront price.",
    "**Plan for the minerals.** Electrification swaps dependence on imported oil for dependence on battery "
    "minerals (IEA, 2021a; Lai et al., 2022). Battery reuse and mandatory recycling keep that new dependence "
    "small (Harper et al., 2019; Ahmadi et al., 2017).",
])
p("These lessons travel. Similar fossil-based grids exist across the Gulf, North Africa and much of Asia, "
  "where comparative studies find that an EV’s climate value mirrors the national electricity mix almost "
  "exactly (Aryan et al., 2025; Alghamdi, 2026). Jordan’s matrix is, in that sense, a map for many countries.")

# ================================================================= EPILOGUE
h("Epilogue: The same morning, ten years later", 1)
p("It is seven in the morning in Amman again. The bus that stops at the corner is electric and full; it "
  "charged overnight and at noon from solar panels on the depot roof. The cars that pass are quiet, and the "
  "energy in their batteries came from the desert sun and wind of the south. The air at the bus stop is "
  "clearer, and fewer children wake up with asthma.")
p("None of this needs a miracle. It needs the two halves of the system — the vehicles and the grid — to be "
  "planned as one. The mathematics is simple: when the right column of the matrix changes together with the "
  "right row, the footprint falls by nine-tenths. The lesson is simpler still:")
quote("Do not just move the chimney. Close it — with the sun.")

# ================================================================= APPENDIX
page_break()
h("Appendix A — How the Python model works", 1)
p("All code is in two scripts: **lca_matrix_model.py** (model, Monte Carlo and figures) and "
  "**build_story_docx.py** (this document). Running the first writes every figure and a results.json file; "
  "every number quoted in the story is read from that file.")
h("A.1  Structure", 2)
bullets([
    "**Products (rows) and processes (columns), 12 × 12:** gasoline, diesel, jet fuel, premium low-sulphur "
    "gasoline, electricity [JO]; and the fleets: gasoline cars, diesel vehicles, aviation, hybrids, other "
    "fuels, EVs, diesel buses.",
    "**Emissions matrix B (2 rows):** tailpipe CO₂-eq (TTW) and upstream CO₂-eq (WTT and power plants). "
    "TTW factors: 70 / 75 / 72 t CO₂-eq per TJ for gasoline / diesel / jet fuel (IPCC 2006 defaults incl. "
    "CH₄ and N₂O); WTT: 15 / 15 / 13 / 17 t per TJ (premium fuel needs more refining); electricity "
    "391 t per GWh.",
    "**Calibration:** baseline fuel use is solved from the SimaPro fleet totals. One parameter each is fitted "
    f"for S2 (bus energy = {R['calibration']['bus_ratio']:.3f} × shifted car energy), S3 (Euro 6 fuel saving = "
    f"{R['calibration']['euro6_gain']:.1%}) and S4 (EV electricity = {R['calibration']['ev_ratio']:.3f} × displaced "
    "fuel energy). S1 is predicted, not fitted.",
])
h("A.2  Monte Carlo distributions (10,000 iterations)", 2)
table(["Parameter", "Distribution", "Used in"], [
    ["Grid intensity (g CO₂-eq/kWh)", "Triangular 370 / 391 / 450", "Micro EV, macro"],
    ["EV consumption (kWh/km)", "Triangular 0.15 / 0.17 / 0.20", "Micro EV"],
    ["Air-conditioning load factor", "Triangular 1.0 / 1.2 / 1.5 (micro); 1.0 / 1.15 / 1.35 (macro)", "EVs"],
    ["ICE WTW (g/km)", "Normal: gasoline 215±25, Euro 6 200±22, diesel 190±20, flight 190±30", "Micro"],
    ["Traffic / driving cycle", "Normal 1.00 ± 0.04 on fuel use", "Macro"],
    ["Bus fuel use", "Triangular 0.90 / 1.00 / 1.25", "S2"],
    ["Real-world Euro 6 gain", "Triangular 0.5 / 1.0 / 1.1 × calibrated", "S3"],
    ["Bus occupancy (riders)", "Triangular 10 / 30 / 60 (Grutter, 2014)", "Pollution swap"],
    ["Bus PM2.5 (g/km)", "Diesel 0.18–0.26; Euro VI 0.05–0.10; electric 0.010–0.020", "Pollution swap"],
], [1.9, 3.12, 1.25], font=9, numeric=False)
h("A.3  Honest limits", 2)
bullets([
    "The Python model is a transparent reduced-form reconstruction of the SimaPro/Ecoinvent system, focused on "
    "climate; health, ecosystem and resource endpoints are taken from the SimaPro results of the original study.",
    "PM2.5 emission factors in Chapter 6 are illustrative values chosen to reproduce the study’s 25–30 rider "
    "threshold; they are not measured Jordanian factors.",
    "The EV electricity implied by the original S4 result (≈0.5 TWh/yr) is low compared with a physics-based "
    "estimate (≈2.4 TWh/yr). The dotted line in Figure 7 shows that the main conclusions hold under both.",
    "As in the original study, vehicle and battery manufacturing and end-of-life are outside the boundary.",
])
h("A.4  Reproduce it", 2)
code("""
pip install numpy matplotlib python-docx
python lca_matrix_model.py      # matrix LCA + 50,000 Monte Carlo solves + figures
python build_story_docx.py      # writes output/The_Price_of_Clean_LCA_Story.docx
""")

# ================================================================= REFERENCES
h("References", 1)
for line in (HERE / "references.txt").read_text().splitlines():
    if line.strip():
        par = doc.add_paragraph(line.strip())
        par.paragraph_format.left_indent = Inches(0.3)
        par.paragraph_format.first_line_indent = Inches(-0.3)
        par.paragraph_format.space_after = Pt(4)
        for r in par.runs:
            r.font.size = Pt(9)

out = OUT / "The_Price_of_Clean_LCA_Story.docx"
doc.save(out)
print("saved", out)
