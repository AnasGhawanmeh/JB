"""
Builds the Word edition of the Jordan transport LCA paper.

Run lca_matrix_model.py first (it writes output/results.json and the figures),
then:  python build_story_docx.py   -> output/Jordan_Transport_LCA_Story.docx
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
    for ri, row in enumerate(t.rows):
        for c in row.cells:
            for par in c.paragraphs:
                par.paragraph_format.space_after = Pt(1)
                par.paragraph_format.keep_with_next = ri < len(t.rows) - 1
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
for _ in range(6):
    doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Where Does the Pollution Go?")
r.bold = True
r.font.size = Pt(30)
r.font.name = "Calibri"
r.font.color.rgb = NAVY
p("The grid penalty and the pollution swap in Jordan’s transport sector",
  align=WD_ALIGN_PARAGRAPH.CENTER, size=15, color=GREY, italic=True, after=30)
p("A Well-to-Wheel Life Cycle Assessment of the 2022 Jordanian fleet, with the matrix calculations and the "
  "Monte Carlo simulation carried out in Python",
  align=WD_ALIGN_PARAGRAPH.CENTER, size=11, after=40)
p("A. O. H. Ghawanmeh", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, color=NAVY)
p("Jordan University of Science and Technology", align=WD_ALIGN_PARAGRAPH.CENTER, size=10, color=GREY)
page_break()

# ================================================================= SUMMARY
h("Summary", 1)
p("Most countries that want to decarbonize transport follow the same plan: more electric vehicles, more "
  "public buses and stricter engine standards. This plan was developed in countries where electricity is "
  "already fairly clean. Jordan is different. It imports most of its energy, and most of its electricity "
  "still comes from natural gas and oil shale. This study asks whether the usual plan still works under "
  "these conditions.")
p("The whole 2022 fleet (about 1.85 million vehicles) was assessed from the well to the wheel. The "
  "calculation is a matrix problem: a technology matrix A links fuels, electricity and vehicles, the system "
  "is solved as s = A⁻¹f, and characterization factors convert the emissions into climate and health "
  "damage. The original assessment was done in SimaPro. Here the same structure was rebuilt in Python, "
  "checked against the SimaPro results, and then tested with 10,000 Monte Carlo runs.")
p("The main findings are:")
bullets([
    "**Grid penalty.** An electric car on the Jordanian grid emits about "
    f"{mm['Battery EV (JO grid)']:.0f} g CO₂-eq per km, compared with about {mm['Gasoline car']:.0f} g for a "
    "gasoline car. It is clearly better, but part of the saving does not disappear. It moves from the exhaust "
    "pipe to the power station.",
    f"**Pollution swap.** A conventional diesel bus with fewer than about {thr['Conventional diesel bus']:.0f} "
    "passengers releases more fine particles per passenger than the private cars it replaces.",
    "**Incremental trap.** 20% EVs, diesel buses and Euro 6 standards each reduce emissions by only 9 to 11%. "
    "None of them brings the sector below about 2,400 Gg CO₂-eq.",
    "**Full electrification.** Converting the whole road fleet reduces emissions by about 84% (to 448 Gg) and "
    "health damage from 2,790 to 449 DALYs. With a solar and wind grid, the same fleet would emit about "
    f"{f0(sw['S4_calibrated@30'])} Gg, and most of what remains would come from aviation.",
])
p("The practical message for Jordan and similar countries is that electric transport and renewable "
  "electricity have to be planned together.")
page_break()

# ================================================================= OPENING
h("1. A morning in Amman", 1)
p("At seven in the morning the main roads of Amman are already busy. Every car on these roads burns fuel, "
  "and together, in 2022, Jordan’s vehicles and domestic flights released about 2,800 thousand tonnes of "
  "CO₂-equivalent. The fine particles from their engines are breathed by the people who walk and wait "
  "beside the road.")
p("If all of these cars were replaced by electric cars, the street would become quieter and the air at the "
  "bus stop would improve. However, the electricity for these cars has to be generated somewhere. In Jordan "
  "it comes mostly from power stations that burn imported natural gas or domestic oil shale. Part of the "
  "pollution would therefore move from the street to the power station instead of disappearing.")
p("This document follows that pollution through the whole system, using the numbers from the life cycle "
  "assessment, to find out which options really reduce it.")

# ================================================================= CH 1
h("2. Background and research question", 1)
p("Transport supports economic activity and gives people access to work, education and health care. It is "
  "also one of the fastest growing sources of greenhouse gas emissions (UNFCCC, 2022). According to the IPCC, "
  "efficiency improvements alone are not enough, and every transport mode needs a structural change "
  "(IPCC, 2022). The common international approach is the Avoid-Shift-Improve framework (Jarre et al., "
  "2024): avoid unnecessary trips, shift passengers to public transport, and improve vehicles, mainly through "
  "electrification (IEA, 2024).")
p("This approach assumes that the electricity used by EVs is low-carbon. That is true in many high-income "
  "countries, but in the Middle East and North Africa it has rarely been checked (Evensen et al., 2025; "
  "Al-Alawi and Al-Alawi, 2022).")
p("Jordan is a good case for checking it. The country has almost no domestic oil and imports most of its "
  "fuel (MEMR, 2022). Transport is responsible for about 16% of national greenhouse gas emissions and 49% of "
  "final energy consumption (MoEnv, 2022; Jelti et al., 2021). Solar and wind made up about 27% of grid "
  "capacity in 2022 (NEPCO, 2022), but the electricity actually supplied is still mostly fossil, at about "
  "391 g CO₂-eq per kWh (Low Carbon Power, 2022). Jordan has also committed to a 31% reduction in greenhouse "
  "gas emissions by 2030 (Ministry of Environment, 2021).")
p("The research question is therefore: **if a fossil-dependent country follows the usual clean transport "
  "plan, do its emissions and health impacts actually fall?**")
p("To answer it, the assessment must go beyond the exhaust pipe. Conventional inventories count only "
  "Tank-to-Wheel emissions. They leave out the Well-to-Tank chain: crude extraction, shipping to Aqaba, "
  "refining, distribution by tanker trucks, and electricity generation. Emissions that are not counted are "
  "not removed; they are moved to another place or turned into another type of damage (Requia et al., 2018). "
  "This study uses two terms for these effects:")
bullets([
    "**Grid penalty:** emissions that leave the street with the EV but appear again at the power station "
    "(Qiao et al., 2019; Buberger et al., 2022).",
    "**Pollution swap:** a measure that lowers total CO₂ but raises local toxic pollution, for example when "
    "buses with low occupancy replace cars (Brewer, 2019; Grutter, 2014).",
])

# ================================================================= CH 2
h("3. Method: the matrix model", 1)
p("The transport system is a network. Cars need gasoline, gasoline needs a refinery, the refinery needs "
  "crude oil and electricity, and electric cars need the grid. Life Cycle Assessment describes this network "
  "with linear algebra, following ISO 14040 and 14044 (ISO, 2006a; ISO, 2006b).")
h("3.1  The technology matrix A", 2)
p("Each column of the technology matrix A is one process, for example the gasoline car fleet for one year or "
  "one GWh of Jordanian electricity. Each row is one product. The value 1 on the diagonal is the output of "
  "the process, and negative values are its inputs. The final demand vector f contains the annual transport "
  "of each fleet. The scaling vector s, which gives how much each process must operate, is:")
p("s = A⁻¹ f          (1)", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, color=NAVY)
p("The emissions of each process are stored in the intervention matrix B, so the total emissions are "
  "g = B s. The characterization factors Q then convert the emissions into impact indicators:")
p("hᵢ = Σⱼ Qᵢⱼ × gⱼ          (2)", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, color=NAVY)
p("In the original study this system was solved in SimaPro with the Ecoinvent 3 database and the ReCiPe 2016 "
  "Endpoint (H) method (Huijbregts et al., 2017; Weidema et al., 2013). For this document the main part of "
  "the system was rebuilt in Python with NumPy as a 12 × 12 technology matrix, with five fuel and electricity "
  "supply processes and seven fleets. The core calculation is:")
code("""
A, B = build_system(params)        # technology matrix and emissions matrix
s = np.linalg.solve(A, f)          # Eq. (1): how much each process must run
g = B @ s                          # flows: [tailpipe CO2-eq, upstream CO2-eq]
""")
figure(HERE / "system_boundary.png",
       "Figure 1. Well-to-Wheel system boundary: fuel and electricity supply (Well-to-Tank) and vehicle "
       "operation (Tank-to-Wheel).", width=5.6)

h("3.2  The baseline matrix", 2)
p("Table 1 shows the supply rows of the baseline 2022 matrix. Each column shows what a process uses; for "
  "example, the gasoline car fleet uses about 14,900 TJ of gasoline per year. The fuel quantities were "
  "obtained by calibrating the matrix to the SimaPro baseline, using IPCC default combustion factors and an "
  "upstream share of about 20%.")
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
p("Table 1. Supply rows of the technology matrix A (units TJ or GWh). The diagonal entries of the fleet rows "
  "are 1 and are not shown. Negative entries are inputs.", italic=True, size=9, color=GREY)

h("3.3  Scenarios", 2)
p("Four scenarios were defined based on the Avoid-Shift-Improve framework and Jordan’s climate policy "
  "(MoEnv, 2022). Each one changes the vector f or the columns of A:")
table(["Scenario", "Change in the matrix", "Question"], [
    ["Baseline 2022", "Fleet and grid as in 2022", "Reference case"],
    ["S1  Promoting EVs", "20% of gasoline car demand moved to an EV column supplied by the JO grid",
     "How large is the grid penalty?"],
    ["S2  Public transport", "30% of gasoline car demand moved to a diesel bus column",
     "Is there a pollution swap?"],
    ["S3  Euro 6 standards", "More efficient engines; half of the gasoline replaced by premium low-sulphur fuel",
     "Is cleaner combustion enough?"],
    ["S4  Full transformation", "All road fleets electric; aviation unchanged",
     "What is the maximum reduction?"],
], [1.45, 2.9, 1.92], font=9, numeric=False)
p("For S2, S3 and S4, one parameter each was adjusted so that the Python result matches SimaPro. S1 was not "
  "adjusted. It was calculated with the EV energy ratio taken from S4, which makes it a check on the model. "
  f"The Python result for S1 is {f0(s1['model_gwp_gg'])} Gg, compared with 2,550 Gg in SimaPro (a difference "
  "of 0.3%).", size=10.5)

h("3.4  Monte Carlo simulation", 2)
p("Real conditions differ from average values. Traffic congestion, air-conditioning in summer (which can "
  "raise EV consumption by 20 to 50%; Alarrouqi et al., 2024), changes in grid intensity and changes in bus "
  "occupancy all affect the results. Following Henriksson et al. (2015), a probability distribution was "
  "assigned to each uncertain input, and the matrix was solved 10,000 times for each scenario. The analysis "
  "was done at three levels: single vehicles (grid penalty), single buses (pollution swap) and the whole "
  "sector (incremental trap).")
page_break()

# ================================================================= CH 3
h("4. The baseline in 2022", 1)
p("The baseline carbon footprint of the sector is about 2,800 Gg CO₂-eq per year. Gasoline vehicles emit "
  "1,270 Gg, almost half of the total, which matches their share of about 60% of the fleet. Diesel vehicles "
  "emit 1,080 Gg, domestic aviation 257 Gg and hybrids 183 Gg. Electric vehicles, which were still few in "
  "2022, emit only 0.08 Gg.")
figure(OUT / "fig1_baseline_breakdown.png",
       "Figure 2. Baseline 2022 Well-to-Wheel emissions by fleet, split into tailpipe (TTW) and upstream (WTT) "
       "emissions.")
p(f"The orange part of each bar is not visible in a tailpipe-only inventory. About {f0(up_total)} Gg "
  f"({up_total / base_model:.0%}) of the sector’s emissions occur before the fuel reaches the vehicle, during "
  "extraction, shipping, refining and distribution.")
p("The impacts are not limited to climate change. The SimaPro endpoint results give a human health burden "
  "of 2,790 DALYs, meaning 2,790 years of healthy life lost each year. Diesel causes a large part of the "
  "local damage: 497 DALYs through carcinogenic toxicity and 55.4 DALYs through non-carcinogenic toxicity, "
  "which reflects the black carbon and particles from heavy-duty diesel engines (Brewer, 2019). Fuel "
  "combustion also causes terrestrial acidification (2.05 species·yr) and ozone damage to ecosystems "
  "(1.23 species·yr).")
p("Fossil resource scarcity for the base year is valued at about US$1.62 billion, of which US$703 million "
  "comes from gasoline vehicles and US$658 million from diesel vehicles. This is a large cost for a country "
  "that imports most of its fuel.")

# ================================================================= CH 4
h("5. Comparing the scenarios", 1)
p("Figure 3 shows the results of the four scenarios. The bars are the Python model and the black diamonds "
  "are the SimaPro results.")
figure(OUT / "fig2_scenarios.png",
       "Figure 3. Sector GWP for each scenario. Bars: Python model (blue = fuel chain, yellow = electricity for "
       "EV charging). Diamonds: SimaPro results.")
table(["Scenario", "Python (Gg CO₂-eq)", "SimaPro (Gg CO₂-eq)", "Change vs 2022", "Health (DALYs)*"], [
    [SCENARIO, f0(DET[k]["model_gwp_gg"]), f0(DET[k]["simapro_gwp_gg"]),
     "-" if k == "Baseline" else f"{(DET[k]['simapro_gwp_gg'] / 2800 - 1):+.0%}", f0(DET[k]["simapro_daly"])]
    for k, SCENARIO in [("Baseline", "Baseline 2022"), ("S1", "S1  20% EVs"), ("S2", "S2  Diesel buses"),
                        ("S3", "S3  Euro 6"), ("S4", "S4  Full electrification")]
], [1.77, 1.25, 1.15, 1.05, 1.05], font=9.5, bold_last=True)
p("*Human health endpoint from SimaPro (ReCiPe 2016 H). The Python baseline (2,793 Gg) is the sum of the "
  "fleet results; 2,800 Gg is the rounded value.", italic=True, size=9, color=GREY)
p("The first three scenarios give almost the same result, between 2,490 and 2,550 Gg, which is a reduction of "
  "only 9 to 11%. Health damage changes very little. Under Euro 6 it stays at 2,760 DALYs, close to the "
  "baseline, because the premium low-sulphur fuel still has to be extracted, shipped and refined. Only "
  "full electrification gives a large change: emissions fall to 448 Gg (-84%) and health damage to 449 DALYs "
  "(-84%). The remaining emissions come mainly from aviation, which was not electrified, and from the "
  "electricity used to charge the fleet.")
p("The single score results of the original study show the same pattern. The baseline, S1, S2 and S3 are all "
  "between about 110 and 125 MPt, while S4 is about 20 MPt. The partial measures mostly move the damage from "
  "one category to another. S1 replaces part of the climate damage with mineral resource scarcity (lithium "
  "and cobalt), and S2 replaces part of it with local health damage.")

# ================================================================= CH 5
h("6. The grid penalty", 1)
p("The reason S1 gives only a small reduction is that the electricity for the EVs is mostly generated from "
  "fossil fuels. In the matrix, the EV column uses the electricity row, and the electricity row is linked to "
  "gas and oil shale.")
p(f"In S1 the model removes about {f0(s1_avoided)} Gg of gasoline emissions and adds about {f0(s1_grid_cal)} Gg "
  "at the power stations, using the EV energy assumption of the original study. With a stricter assumption "
  "based on vehicle physics (an EV using about 30% of the energy of the gasoline car it replaces), the power "
  f"stations add about {f0(s1_grid_phys)} Gg, which is about {s1_grid_phys / s1_avoided:.0%} of the saving. In "
  "both cases part of the benefit is lost at the power station.")
figure(OUT / "fig3_micro_density.png",
       "Figure 4. Monte Carlo results (10,000 runs) for Well-to-Wheel emissions per km. EV electricity from the "
       "Jordanian grid (370 to 450 g/kWh) with an air-conditioning load of 0 to 50%.")
p(f"Even so, the EV remains the best option per kilometre. With air-conditioning and the current grid, its "
  f"median value is about {mm['Battery EV (JO grid)']:.0f} g CO₂-eq/km, compared with about "
  f"{mm['Gasoline car']:.0f} for a gasoline car, {mm['Euro 6 gasoline car']:.0f} for a Euro 6 car and "
  f"{mm['Modern diesel car']:.0f} for a modern diesel car. The EV was lower than all combustion options in "
  f"{R['micro_p_ev_below_all']:.2%} of the runs. The Euro 6 and modern diesel curves overlap strongly with the "
  "gasoline car, so better combustion gives only a small improvement. Short domestic flights are at about the "
  "same level as a modern diesel car per passenger-km.")
p("The grid penalty therefore does not mean that EVs should be avoided. It means that the benefit of an EV "
  "depends on the electricity grid that charges it.")

# ================================================================= CH 6
h("7. The pollution swap", 1)
p("CO₂ has the same effect on the climate wherever it is emitted, but fine particles affect mainly the people "
  "close to the source. PM2.5 reaches deep into the lungs and the blood and increases the risk of heart "
  "disease, stroke and lung cancer (Haines et al., 2009; WHO, 2023). Diesel engines produce about 90% of the "
  "black carbon from transport (Brewer, 2019).")
p("The question here is how many passengers a bus needs before it releases less local PM2.5 per passenger "
  "than the cars it replaces.")
figure(OUT / "fig4_pollution_swap.png",
       "Figure 5. Local PM2.5 per passenger-km against bus occupancy (10,000 runs, 10 to 60 passengers). The "
       "emission factors are illustrative values set to match the 25 to 30 passenger threshold of the original "
       "study.")
p(f"Below about {thr['Conventional diesel bus']:.0f} passengers, a conventional diesel bus releases more PM2.5 "
  "per passenger-km than a private gasoline car. With occupancy varying during the day, this was the case in "
  f"{R['p_bus_dirtier_than_car']:.0%} of the simulated trips. A Euro VI diesel bus lowers the threshold to about "
  f"{thr['Euro VI diesel bus']:.0f} passengers, which is better but can still be exceeded in off-peak hours. An "
  "electric bus, whose only particles come from brakes and tyres, is cleaner than the car at almost any "
  "occupancy.")
p("This is the pollution swap. At the national level a diesel bus programme lowers CO₂, but at street level, "
  "especially in the narrow streets of Amman where exhaust is trapped (Morales Betancourt et al., 2017; "
  "Fantke et al., 2017), it can make the air worse for the people it is meant to serve. Public transport "
  "projects should therefore be assessed on occupancy and local PM2.5, and not on CO₂ alone.")

# ================================================================= CH 7
h("8. The incremental trap", 1)
p("At the sector level, the matrix was solved 10,000 times for each scenario, with traffic, grid intensity, "
  "air-conditioning, bus fuel use and the real-world performance of Euro 6 allowed to vary.")
figure(OUT / "fig5_macro_boxplots.png",
       "Figure 6. Sector-level Monte Carlo results (10,000 runs per scenario). Left: GWP from the Python model. "
       "Right: SimaPro health damage scaled in each run; S2 includes a wider occupancy uncertainty.",
       width=6.4)
p(f"The three incremental scenarios form one group. The sector stayed above 2,400 Gg in {1 - pb['S1']:.1%} of "
  f"the runs for S1, {1 - pb['S2']:.1%} for S2 and {1 - pb['S3']:.1%} for S3. Their ranges overlap so much that "
  "there is little statistical difference between them. This study calls this the incremental trap.")
p(f"The health results show a further risk. Under S2 the middle 50% of the results lies between "
  f"{f0(dq['S2'][1])} and {f0(dq['S2'][3])} DALYs, more than twice the width of the baseline range "
  f"({f0(dq['Baseline'][1])} to {f0(dq['Baseline'][3])}), and the upper end reaches {f0(dq['S2'][4])} DALYs, "
  "which is higher than any baseline result. Expanding diesel buses without making sure they are well "
  "occupied could increase the national health burden.")
p(f"Scenario 4 is clearly separate. Its 95% range is {f0(gq['S4'][0])} to {f0(gq['S4'][4])} Gg and "
  f"{f0(dq['S4'][0])} to {f0(dq['S4'][4])} DALYs, far below the other scenarios in every run. (The median is "
  "slightly above the deterministic value of 448 Gg because extra air-conditioning load was added in the "
  "simulation.) Only a structural change of the fleet gets out of the incremental trap.")

# ================================================================= CH 8
h("9. Cleaning the grid", 1)
p("Since the benefit of EVs depends on the grid, a cleaner grid improves every EV at the same time. In the "
  "matrix model this can be tested by changing one value, the carbon intensity of the electricity.")
figure(OUT / "fig6_grid_sweep.png",
       "Figure 7. Sector GWP against grid carbon intensity. Solid line: EV energy as calibrated to the original "
       "study. Dotted line: stricter physics-based EV energy use.")
p("With the current grid, full electrification gives 448 Gg. With a solar and wind grid (about 30 g/kWh over "
  f"the life cycle), the same fleet would emit about {f0(sw['S4_calibrated@30'])} Gg, about 90% less than in "
  "2022, and almost all of the remaining emissions would come from aviation. With the stricter physics-based "
  f"assumption the current value is higher ({f0(sw['S4_physics@391'])} Gg), but a clean grid still brings it "
  f"down to about {f0(sw['S4_physics@30'])} Gg. The conclusion is the same under both assumptions.")
p("The S1 line stays almost flat at about 2,550 Gg for any grid. A cleaner grid has little effect if only a "
  "small part of the fleet is electric, and a fully electric fleet gives only part of its benefit if the grid "
  "stays fossil-based. The two changes need to happen together.")

# ================================================================= CH 9
h("10. Recommendations", 1)
p("Based on these results, the following actions are recommended for Jordan and for other countries with "
  "fossil-based electricity:")
bullets([
    "**Link EV targets to grid targets.** National EV targets should be tied to the retirement of fossil "
    "power plants and the addition of new renewable capacity (Al-Shetwi et al., 2020).",
    "**Solar charging depots.** New charging depots for buses, taxis and government fleets should be "
    "supplied by local solar microgrids, so that these vehicles avoid the grid penalty from the start "
    "(Evensen et al., 2025).",
    "**Daytime charging.** Charging during the day can use solar output instead of adding to the evening "
    "peak, which reduces the stress on distribution networks in hot climates (Al-Owaifeer et al., 2020; "
    "Al-Shetwi et al., 2022).",
    "**Avoid diesel as a transition technology.** New bus investment should go directly to battery electric "
    "or hydrogen fuel cell buses instead of CNG or Euro 5/6 diesel, which would keep cities dependent on "
    "fossil fuel and PM2.5 for decades (Grutter, 2014; Jelti et al., 2021; Ahmadi et al., 2022). Feasibility "
    "studies should include the avoided health costs.",
    "**Plan for battery minerals.** Electrification replaces dependence on imported oil with dependence on "
    "battery minerals (IEA, 2021a; Lai et al., 2022). Battery reuse and recycling should be required to keep "
    "this dependence low (Harper et al., 2019; Ahmadi et al., 2017).",
])
p("These results are also relevant outside Jordan. Many countries in the Gulf, North Africa and Asia have "
  "similar fossil-based grids, and comparative studies show that the climate benefit of EVs follows the "
  "national electricity mix closely (Aryan et al., 2025; Alghamdi, 2026).")

# ================================================================= CONCLUSION
h("11. Conclusion", 1)
p("Partial measures such as 20% EVs, diesel buses or Euro 6 standards reduce emissions by about 10% and "
  "mostly move the damage to the power station, to mineral supply chains or to the street. Full "
  "electrification reduces both emissions and health damage by more than 80%, and combined with a renewable "
  "grid it could reduce sector emissions by about 90%.")
p("If Jordan plans its vehicles and its electricity grid together, a morning in Amman could look very "
  "different in ten years: electric buses charged from solar depots, quieter streets and cleaner air at the "
  "bus stops. The results of this study show that this is technically achievable, provided the transport "
  "and energy sectors are developed as one system.")

# ================================================================= APPENDIX
page_break()
h("Appendix A. The Python model", 1)
p("The code consists of two scripts: lca_matrix_model.py (model, Monte Carlo simulation and figures) and "
  "build_story_docx.py (this document). The first script writes all figures and a results.json file, and "
  "every number in the text is read from that file.")
h("A.1  Structure", 2)
bullets([
    "**Products and processes (12 × 12):** gasoline, diesel, jet fuel, premium low-sulphur gasoline and "
    "electricity [JO]; and the fleets: gasoline cars, diesel vehicles, aviation, hybrids, other fuels, EVs and "
    "diesel buses.",
    "**Emissions matrix B (2 rows):** tailpipe CO₂-eq (TTW) and upstream CO₂-eq (WTT and power plants). "
    "TTW factors: 70, 75 and 72 t CO₂-eq per TJ for gasoline, diesel and jet fuel (IPCC 2006 defaults "
    "including CH₄ and N₂O). WTT factors: 15, 15, 13 and 17 t per TJ (premium fuel needs more refining). "
    "Electricity: 391 t per GWh.",
    "**Calibration:** baseline fuel use is calculated from the SimaPro fleet totals. One parameter is fitted "
    f"for each of S2 (bus energy = {R['calibration']['bus_ratio']:.3f} × shifted car energy), S3 (Euro 6 fuel "
    f"saving = {R['calibration']['euro6_gain']:.1%}) and S4 (EV electricity = {R['calibration']['ev_ratio']:.3f} × "
    "displaced fuel energy). S1 is calculated, not fitted.",
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
    ["Bus PM2.5 (g/km)", "Diesel 0.18-0.26; Euro VI 0.05-0.10; electric 0.010-0.020", "Pollution swap"],
], [1.9, 3.12, 1.25], font=9, numeric=False)
h("A.3  Limitations", 2)
bullets([
    "The Python model is a simplified reconstruction of the SimaPro/Ecoinvent system and covers climate "
    "impacts. Health, ecosystem and resource endpoints are taken from the SimaPro results.",
    "The PM2.5 emission factors in Section 7 are illustrative values chosen to match the 25 to 30 passenger "
    "threshold of the original study. They are not measured Jordanian values.",
    "The EV electricity implied by the original S4 result (about 0.5 TWh per year) is low compared with a "
    "physics-based estimate (about 2.4 TWh per year). Figure 7 shows that the main conclusions hold in both "
    "cases.",
    "As in the original study, vehicle and battery manufacturing and end-of-life are outside the system "
    "boundary.",
])
h("A.4  Running the code", 2)
code("""
pip install numpy matplotlib python-docx
python lca_matrix_model.py      # matrix LCA + 50,000 Monte Carlo solves + figures
python build_story_docx.py      # writes output/Jordan_Transport_LCA_Story.docx
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

out = OUT / "Jordan_Transport_LCA_Story.docx"
doc.save(out)
print("saved", out)
