"""Generate all manuscript figures for the Oman 2025 National Energy Balance paper.

Every number below is taken from the 2025 National Energy Balance report or is
derived from it with the arithmetic shown inline. Run:  python make_figures.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- style
plt.rcParams.update({
    "font.family": "Liberation Sans",
    "font.size": 8.5,
    "axes.titlesize": 9,
    "axes.titleweight": "bold",
    "axes.labelsize": 8.5,
    "axes.edgecolor": "#52514e",
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#e4e3df",
    "grid.linewidth": 0.5,
    "xtick.color": "#52514e",
    "ytick.color": "#52514e",
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "legend.frameon": False,
    "legend.fontsize": 7.5,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "figure.dpi": 150,
})
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"

# Fixed entity -> colour mapping (validated categorical order, reference palette)
C = {
    "gas": "#2a78d6", "oil": "#eb6834", "products": "#eda100", "lng": "#6250d6",
    "coal": "#e87ba4", "re": "#1baf7a", "elec": "#008300", "grey": "#a3a29b",
    "gap": "#c9c8c2", "red": "#e34948",
}
SEC = {  # sectors
    "Industrial": "#2a78d6", "Transport": "#eb6834", "Residential": "#1baf7a",
    "Commercial": "#eda100", "Government": "#e87ba4", "Other / unallocated": "#a3a29b",
    "Power generation": "#6250d6",
}


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"))
    plt.close(fig)


def panel(ax, letter):
    ax.text(-0.02, 1.04, f"({letter})", transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", va="bottom", ha="right", color=INK)


def bar_labels(ax, bars, fmt="{:,.0f}", horizontal=False, pad=3, size=7.2):
    for b in bars:
        v = b.get_width() if horizontal else b.get_height()
        if horizontal:
            ax.annotate(fmt.format(v), (b.get_x() + v, b.get_y() + b.get_height() / 2),
                        xytext=(pad if v >= 0 else -pad, 0), textcoords="offset points",
                        ha="left" if v >= 0 else "right", va="center", fontsize=size, color=INK2)
        else:
            ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v),
                        xytext=(0, pad if v >= 0 else -pad - 7), textcoords="offset points",
                        ha="center", va="bottom", fontsize=size, color=INK2)


# ================================================================ core data
KTOE = dict(crude=0.136, prod=0.145, gas=0.02549, lng=1090, coal=0.00065, elec=0.086)
crude_prod_kbbl, crude_exp_kbbl, crude_imp_kbbl = 365_754.4, 307_960.9, 71_094.8
refinery_out_kbbl = 210_833.1
gas_mmscf = 2_018_799.2
lng_feed_mmscf = 599_187
gen_gwh, cons_gwh, re_gwh = 50_973.5, 45_033.1, 4_509.0

crude_prod = crude_prod_kbbl * KTOE["crude"]            # 49,742.6
crude_exp = crude_exp_kbbl * KTOE["crude"]              # 41,882.7
crude_imp = crude_imp_kbbl * KTOE["crude"]              # 9,668.9
ref_out = refinery_out_kbbl * KTOE["prod"]              # 30,570.8
gas_prod = 51_459.2
lng_feed = lng_feed_mmscf * KTOE["gas"]                 # 15,273.3
lng_out = 12_317.0
gas_power, gas_ind, gas_own = 13_974.0, 10_331.0, 11_880.0
re_ktoe = re_gwh * KTOE["elec"]                         # 387.8
elec_gen = gen_gwh * KTOE["elec"]                       # 4,383.7
elec_tfc = cons_gwh * KTOE["elec"]                      # 3,872.8
elec_loss = elec_gen - elec_tfc                         # 510.9
coal_imp = (246_603.5 + 18_153.2) * KTOE["coal"]        # 172.1
coal_exp = 5_143.9 * KTOE["coal"]                       # 3.3
coal_net = coal_imp - coal_exp                          # 168.7
prod_exp = 19_008.0                                     # refined product exports (ktoe)
bunkers = 453.8                                         # closes the as-compiled TPES identity
crude_to_ref = crude_prod - crude_exp + crude_imp       # 17,528.8
ref_gap = ref_out - crude_to_ref                        # 13,042.0 (unreconciled)

prod_compiled, tpes_compiled, tfc = 105_585.5, 41_761.7, 25_481.7
prod_ires = prod_compiled - elec_gen + re_ktoe          # 101,589.6
tpes_ires = tpes_compiled - elec_gen + re_ktoe          # 37,765.8

sectors = ["Industrial", "Other / unallocated", "Transport", "Residential", "Commercial", "Government"]
tfc_sec = [12_150.1, 5_541.3, 4_435.5, 1_918.6, 1_045.9, 390.3]
elec_sec_gwh = {"Residential": 18_624.9, "Commercial": 12_161.8, "Industrial": 8_136.6,
                "Government": 4_538.7, "Other / unallocated": 1_571.1}

# =========================================================== Fig 1 framework
def box(ax, x, y, w, h, text, fc, ec=INK2, size=7.5, bold=False, tc=INK):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
                       fc=fc, ec=ec, lw=0.7)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            fontweight="bold" if bold else "normal", color=tc, wrap=True, linespacing=1.25)


def arrow(ax, x0, y0, x1, y1, color=INK2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=0.8, color=color, mutation_scale=9))


def fig1():
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    cols = [0.005, 0.255, 0.505, 0.755]
    w = 0.225
    heads = ["1  Primary data", "2  Harmonisation", "3  IRES balance", "4  Analysis & policy"]
    for x, h in zip(cols, heads):
        box(ax, x, 0.90, w, 0.075, h, "#2a78d6", ec="#2a78d6", size=8, bold=True, tc="white")
    d1 = ["NCSI Statistical Year Book\n(oil, gas, electricity, GDP)",
          "Ministry of Energy & Minerals\n(refinery, gas by sector)",
          "Renewable Energy Bulletin\n(plant-level generation)",
          "OQ8 Duqm refinery data;\nCustoms (HS 2701/2704);\nbunkering records"]
    d2 = ["Physical units → ktoe\n(kbbl, MMscf, t, GWh)",
          "Mix-weighted product factor;\nNCV basis (1 toe = 41.868 GJ)",
          "Sector allocation of\npetroleum retail sales",
          "Stock change = 0;\nflagged input gaps"]
    d3 = ["Supply: Prod + Imp − Exp\n− Bunkers ± ΔStock = TPES",
          "Transformation: refining,\npower, LNG liquefaction",
          "Corrections: LNG feedstock,\nDuqm flows, primary electricity",
          "Closure tests: statistical\ndifference, process efficiency"]
    d4 = ["IPCC 2006 Tier 1 CO₂\n(sector × fuel)",
          "Counterfactual avoided\nemissions & gas displacement",
          "Indicators: SSR, intensity,\nRE share, per-capita TPES",
          "Policy instruments:\nsupply, demand, enabling"]
    fills = ["#f3f2ef", "#f3f2ef", "#eaf2fb", "#e8f6f0"]
    for x, items, fc in zip(cols, [d1, d2, d3, d4], fills):
        for i, t in enumerate(items):
            box(ax, x, 0.69 - i * 0.205, w, 0.17, t, fc, size=6.8)
    for x in cols[:-1]:
        for i in range(4):
            yy = 0.69 - i * 0.205 + 0.085
            arrow(ax, x + w + 0.003, yy, x + 0.25 - 0.003, yy)
    ax.text(0.5, 0.0, "Feedback: diagnostics (stage 3) trigger re-harmonisation of source data (stage 2)",
            ha="center", va="bottom", fontsize=7, color=MUTED, style="italic")
    save(fig, "Fig01_framework")


# =============================================================== Fig 2 Sankey
def sankey_ribbon(ax, x0, y0a, y0b, x1, y1a, y1b, color, alpha=0.45, hatch=None):
    xm = (x0 + x1) / 2
    verts = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a), (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), fc=color, ec="none", alpha=alpha, hatch=hatch))


def _declutter(items, min_gap):
    """items: list of [y, ...] sorted top->bottom; push labels apart vertically."""
    items.sort(key=lambda t: -t[0])
    for i in range(1, len(items)):
        if items[i - 1][0] - items[i][0] < min_gap:
            items[i][0] = items[i - 1][0] - min_gap
    return items


def fig2():
    plt.rcParams["hatch.linewidth"] = 0.35
    layers_x = [0.14, 0.40, 0.64, 0.86]
    nodes = {
        "Crude oil production": (0, C["oil"]), "Crude oil imports (Duqm)": (0, C["oil"]),
        "Unreconciled refinery feed": (0, C["gap"]), "Natural gas production": (0, C["gas"]),
        "Solar & wind": (0, C["re"]), "Coal & lignite (net imports)": (0, C["coal"]),
        "Refineries": (1, C["products"]), "LNG trains": (1, C["lng"]), "Power plants": (1, C["elec"]),
        "Energy-sector own use": (1, C["grey"]), "Gas (direct use)": (1, C["gas"]),
        "Coal (direct use)": (1, C["coal"]),
        "Refined products": (2, C["products"]), "LNG": (2, C["lng"]), "Electricity": (2, C["elec"]),
        "Exports & bunkers": (3, MUTED), "Conversion losses": (3, C["gap"]),
        "Own use & T&D losses": (3, C["gap"]), "Industrial": (3, SEC["Industrial"]),
        "Transport": (3, SEC["Transport"]), "Residential": (3, SEC["Residential"]),
        "Commercial": (3, SEC["Commercial"]), "Government": (3, SEC["Government"]),
        "Other / unallocated": (3, SEC["Other / unallocated"]),
    }
    flows = [
        ("Crude oil production", "Exports & bunkers", crude_exp, C["oil"]),
        ("Crude oil production", "Refineries", crude_prod - crude_exp, C["oil"]),
        ("Crude oil imports (Duqm)", "Refineries", crude_imp, C["oil"]),
        ("Unreconciled refinery feed", "Refineries", ref_gap, C["gap"]),
        ("Natural gas production", "LNG trains", lng_feed, C["gas"]),
        ("Natural gas production", "Power plants", gas_power, C["gas"]),
        ("Natural gas production", "Energy-sector own use", gas_own, C["gas"]),
        ("Natural gas production", "Gas (direct use)", gas_ind, C["gas"]),
        ("Coal & lignite (net imports)", "Coal (direct use)", coal_net, C["coal"]),
        ("Solar & wind", "Power plants", re_ktoe, C["re"]),
        ("Refineries", "Refined products", ref_out, C["products"]),
        ("LNG trains", "LNG", lng_out, C["lng"]),
        ("LNG trains", "Conversion losses", lng_feed - lng_out, C["gap"]),
        ("Power plants", "Electricity", elec_gen, C["elec"]),
        ("Power plants", "Conversion losses", gas_power + re_ktoe - elec_gen, C["gap"]),
        ("Energy-sector own use", "Own use & T&D losses", gas_own, C["grey"]),
        ("Gas (direct use)", "Industrial", gas_ind, C["gas"]),
        ("Coal (direct use)", "Industrial", coal_net, C["coal"]),
        ("Refined products", "Exports & bunkers", prod_exp + bunkers, C["products"]),
        ("Refined products", "Industrial", 950.7, C["products"]),
        ("Refined products", "Transport", 4_435.5, C["products"]),
        ("Refined products", "Residential", 316.9, C["products"]),
        ("Refined products", "Other / unallocated", 5_406.2, C["products"]),
        ("LNG", "Exports & bunkers", lng_out, C["lng"]),
        ("Electricity", "Own use & T&D losses", elec_loss, C["elec"]),
        ("Electricity", "Industrial", elec_sec_gwh["Industrial"] * 0.086, C["elec"]),
        ("Electricity", "Residential", elec_sec_gwh["Residential"] * 0.086, C["elec"]),
        ("Electricity", "Commercial", elec_sec_gwh["Commercial"] * 0.086, C["elec"]),
        ("Electricity", "Government", elec_sec_gwh["Government"] * 0.086, C["elec"]),
        ("Electricity", "Other / unallocated", elec_sec_gwh["Other / unallocated"] * 0.086, C["elec"]),
    ]
    inflow = {n: 0.0 for n in nodes}; outflow = {n: 0.0 for n in nodes}
    for s, t, v, _ in flows:
        outflow[s] += v; inflow[t] += v
    size = {n: max(inflow[n], outflow[n]) for n in nodes}
    scale = 0.80 / sum(size[n] for n in nodes if nodes[n][0] == 0)
    gaps = [0.014, 0.022, 0.03, 0.016]
    pos = {}
    for L in range(4):
        names = [n for n in nodes if nodes[n][0] == L]
        tot = sum(size[n] for n in names) * scale + gaps[L] * (len(names) - 1)
        y = 0.49 + tot / 2
        for n in names:
            h = max(size[n] * scale, 0.003)
            pos[n] = [y - h, y]
            y -= h + gaps[L]
    centre = {n: sum(p) / 2 for n, p in pos.items()}
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    ax.set_xlim(0, 1.06); ax.set_ylim(-0.02, 1.0); ax.axis("off"); ax.grid(False)
    nw = 0.014
    # order ribbons by the vertical position of the opposite node to minimise crossings
    out_order = sorted(flows, key=lambda f: -centre[f[1]])
    in_order = sorted(flows, key=lambda f: -centre[f[0]])
    out_cursor = {n: pos[n][1] for n in nodes}; in_cursor = {n: pos[n][1] for n in nodes}
    ys = {}
    for f in out_order:
        s, t, v, _ = f; h = v * scale
        ys.setdefault(id(f), {})["src"] = (out_cursor[s], out_cursor[s] - h); out_cursor[s] -= h
    for f in in_order:
        s, t, v, _ = f; h = v * scale
        ys[id(f)]["dst"] = (in_cursor[t], in_cursor[t] - h); in_cursor[t] -= h
    for f in flows:
        s, t, v, col = f
        (y0b, y0a), (y1b, y1a) = ys[id(f)]["src"], ys[id(f)]["dst"]
        x0 = layers_x[nodes[s][0]] + nw; x1 = layers_x[nodes[t][0]]
        gapflow = s == "Unreconciled refinery feed"
        sankey_ribbon(ax, x0, y0b, y0a, x1, y1b, y1a, col, alpha=0.38 if not gapflow else 0.5,
                      hatch="//////" if gapflow else None)
    for n, (L, col) in nodes.items():
        y0, y1 = pos[n]
        ax.add_patch(Rectangle((layers_x[L], y0), nw, y1 - y0, fc=col, ec="none",
                               hatch="//////" if n == "Unreconciled refinery feed" else None))
    # labels
    for L in range(4):
        names = [n for n in nodes if nodes[n][0] == L]
        if L in (0, 3):
            items = _declutter([[centre[n], n] for n in names], 0.034 if L == 3 else 0.03)
            for yl, n in items:
                if L == 0:
                    ax.text(layers_x[0] - 0.006, yl, f"{n}\n{size[n]:,.0f}" if size[n] > 1000 else f"{n}  {size[n]:,.0f}", ha="right", va="center",
                            fontsize=6.3, color=INK, linespacing=1.1)
                else:
                    ax.text(layers_x[3] + nw + 0.006, yl, f"{n}  {size[n]:,.0f}", ha="left", va="center",
                            fontsize=6.3, color=INK)
                if abs(yl - centre[n]) > 0.004:
                    x_n = layers_x[0] if L == 0 else layers_x[3] + nw
                    ax.plot([x_n, x_n + (-0.005 if L == 0 else 0.005)], [centre[n], yl], color=MUTED, lw=0.4)
        else:
            for n in names:
                y0, y1 = pos[n]
                ax.text(layers_x[L] + nw / 2, y1 + 0.004, f"{n} {size[n]:,.0f}", ha="center", va="bottom",
                        fontsize=6.0, color=INK,
                        bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.6))
    for L, t in enumerate(["Primary supply", "Transformation", "Secondary carriers", "Disposition & final use"]):
        ax.text(layers_x[L] + nw / 2, 0.985, t, ha="center", fontsize=7.4, fontweight="bold", color=INK2)
    ax.text(0.0, -0.015, "All flows in ktoe, IRES-restated balance. Hatched ribbon: refinery output not matched by "
            "recorded crude input (Section 2.6).", fontsize=6.4, color=MUTED, style="italic")
    save(fig, "Fig02_sankey")


# ===================================================== Fig 3 reconciliation
def fig3():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax = axes[0]
    steps = [("TPES\nas compiled", tpes_compiled, "total"),
             ("Remove total\ngeneration counted\nas primary", -elec_gen, "delta"),
             ("Add primary\nsolar & wind\nelectricity", re_ktoe, "delta"),
             ("TPES\nIRES-restated", tpes_ires, "total")]
    run = 0
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "total":
            b = ax.bar(i, v, color=C["gas"], width=0.6); run = v
            ax.text(i, v + 600, f"{v:,.1f}", ha="center", va="bottom", fontsize=7.2, color=INK2)
        else:
            base = run if v > 0 else run + v
            ax.bar(i, abs(v), bottom=base, color=C["re"] if v > 0 else C["red"], width=0.6)
            ax.text(i, run + max(v, 0) + 600, f"{v:+,.1f}", ha="center", va="bottom", fontsize=7.2, color=INK2)
            run += v
    ax.set_xticks(range(4)); ax.set_xticklabels([s[0] for s in steps], fontsize=7)
    ax.set_ylabel("ktoe"); ax.set_ylim(0, 47_000); ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_title("TPES under the IRES primary-electricity convention", loc="left"); panel(ax, "a")

    ax = axes[1]
    ssr_compiled = prod_compiled / tpes_compiled * 100
    ssr_ires = prod_ires / tpes_ires * 100
    ssr_lo = prod_ires / (tpes_ires + ref_gap) * 100
    ssr_hi_prod = (prod_ires + ref_gap) / (tpes_ires + ref_gap) * 100
    labels = ["As compiled", "IRES-restated", "Restated + refinery\nclosure (gap =\nunder-recorded\nproduction)",
              "Restated + refinery\nclosure (gap =\nover-recorded\nexports)"]
    vals = [ssr_compiled, ssr_ires, ssr_hi_prod, ssr_lo]
    cols = [C["grey"], C["gas"], "#7fb0e8", "#7fb0e8"]
    bars = ax.barh(range(4)[::-1], vals, color=cols, height=0.6)
    bar_labels(ax, bars, "{:.1f}%", horizontal=True)
    ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(labels, fontsize=6.8)
    ax.axvline(100, color=MUTED, lw=0.6, ls="--")
    ax.set_xlim(0, 320); ax.set_xlabel("Self-sufficiency ratio (production ÷ TPES, %)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Sensitivity of the self-sufficiency ratio", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2.5)
    save(fig, "Fig03_reconciliation")
    return ssr_compiled, ssr_ires, ssr_hi_prod, ssr_lo


# ====================================================== Fig 4 headline supply
def fig4():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw=dict(width_ratios=[1, 1.25, 0.9]))
    ax = axes[0]
    labs = ["Natural\ngas", "Crude\noil", "Solar &\nwind"]
    vals = [gas_prod, crude_prod, re_ktoe]
    bars = ax.bar(labs, vals, color=[C["gas"], C["oil"], C["re"]], width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 900, f"{v:,.0f}\n({v / prod_ires * 100:.1f}%)",
                ha="center", va="bottom", fontsize=6.8, color=INK2)
    ax.set_ylim(0, 62_000); ax.set_ylabel("ktoe"); ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.tick_params(axis="x", labelsize=7)
    ax.set_title(f"Indigenous production\n{prod_ires:,.1f} ktoe", loc="left"); panel(ax, "a")

    ax = axes[1]
    labs = ["Natural gas", "Crude oil", "Solar & wind", "Coal & lignite", "LNG", "Refined products"]
    vals = [gas_prod, crude_to_ref, re_ktoe, coal_net, -lng_out, -(prod_exp + bunkers)]
    cols = [C["gas"], C["oil"], C["re"], C["coal"], C["lng"], C["products"]]
    y = np.arange(len(labs))[::-1]
    bars = ax.barh(y, vals, color=cols, height=0.62)
    bar_labels(ax, bars, "{:,.0f}", horizontal=True, size=6.6)
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=7)
    ax.axvline(0, color=INK2, lw=0.6); ax.set_xlim(-42_000, 70_000)
    ax.set_xticks([-25_000, 0, 25_000, 50_000]); ax.tick_params(axis="y", length=0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("ktoe (negative = net export of secondary product)"); ax.grid(axis="y", visible=False)
    ax.set_title(f"TPES contribution by commodity\nTotal {tpes_ires:,.1f} ktoe", loc="left"); panel(ax, "b")

    ax = axes[2]
    conv = (lng_feed - lng_out) + (gas_power + re_ktoe - elec_gen)
    own = gas_own + elec_loss
    ax.bar(0, tpes_ires, color=C["gas"], width=0.6)
    ax.bar(0, ref_gap, bottom=tpes_ires, color="white", edgecolor=C["red"], hatch="////", width=0.6, lw=0.7)
    ax.text(0, tpes_ires / 2, f"TPES\n{tpes_ires:,.0f}", ha="center", va="center", fontsize=6.5, color="white")
    ax.text(0, tpes_ires + ref_gap / 2, f"Refinery\ngain\n{ref_gap:,.0f}", ha="center", va="center",
            fontsize=6.2, color=C["red"])
    bottom = 0
    for lab, v, col in [("TFC", tfc, C["elec"]), ("Conversion\nlosses", conv, C["grey"]),
                        ("Own use &\nT&D losses", own, "#c9c8c2")]:
        ax.bar(1, v, bottom=bottom, color=col, width=0.6, edgecolor="white", lw=1)
        ax.text(1, bottom + v / 2, f"{lab}\n{v:,.0f}", ha="center", va="center", fontsize=6.2,
                color="white" if col == C["elec"] else INK)
        bottom += v
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Sources", "Uses"], fontsize=7)
    ax.set_xlim(-0.55, 1.55); ax.set_ylim(0, 56_000); ax.grid(axis="x", visible=False)
    ax.set_ylabel("ktoe"); ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_title("Sources and uses of TPES", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.8)
    save(fig, "Fig04_supply_aggregates")
    return conv, own


# ================================================================ Fig 5 oil
def fig5():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.1, 1]))
    ax = axes[0]
    labs = ["Production", "Exports", "Retained for\nrefining", "Imports\n(Duqm feed)", "Recorded\nrefinery\ninput", "Refinery\noutput\n(all products)"]
    vals = [crude_prod_kbbl, crude_exp_kbbl, crude_prod_kbbl - crude_exp_kbbl, crude_imp_kbbl,
            crude_prod_kbbl - crude_exp_kbbl + crude_imp_kbbl, refinery_out_kbbl]
    cols = [C["oil"], MUTED, C["oil"], C["oil"], C["oil"], C["products"]]
    bars = ax.bar(range(6), np.array(vals) / 1000, color=cols, width=0.62)
    bar_labels(ax, bars, "{:,.1f}", size=6.8)
    ax.set_xticks(range(6)); ax.set_xticklabels(labs, fontsize=6.6)
    ax.set_ylabel("Million barrels"); ax.grid(axis="x", visible=False); ax.set_ylim(0, 410)
    ax.set_title("Crude oil disposition and refinery throughput", loc="left"); panel(ax, "a")

    ax = axes[1]
    prods = ["Diesel / gas oil", "Naphtha / other", "Gasoline 91", "Gasoline 95", "Jet / kerosene", "LPG", "Fuel oil"]
    pv = [35_254, 28_111, 16_540, 14_887, 11_712, 8_112, 524]
    tot = sum(pv)
    y = np.arange(len(prods))[::-1]
    bars = ax.barh(y, pv, color=C["products"], height=0.62)
    for b, v in zip(bars, pv):
        ax.text(v + 400, b.get_y() + b.get_height() / 2, f"{v:,}  ({v / tot * 100:.1f}%)", va="center",
                fontsize=6.6, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(prods, fontsize=7); ax.set_xlim(0, 48_000)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("Thousand barrels"); ax.grid(axis="y", visible=False)
    ax.set_title(f"Product-resolved refinery slate ({tot:,} kbbl)", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig05_oil")
    return tot


# ======================================================== Fig 6 gas & coal
def fig6():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axes[0]
    labs = ["LNG liquefaction\nfeedstock", "Power\ngeneration", "Oil-field\nown use", "Industrial final\nconsumption"]
    vals = [lng_feed, gas_power, gas_own, gas_ind]
    cols = [C["lng"], C["elec"], C["grey"], C["gas"]]
    bars = ax.bar(labs, vals, color=cols, width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 250, f"{v:,.0f}\n({v / gas_prod * 100:.1f}%)", ha="center",
                va="bottom", fontsize=6.8, color=INK2)
    ax.set_ylim(0, 20_500); ax.set_ylabel("ktoe"); ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.tick_params(axis="x", labelsize=7)
    ax.annotate(f"LNG output {lng_out:,.0f} ktoe\n(11.3 Mt; efficiency {lng_out / lng_feed * 100:.1f}%)",
                xy=(0, lng_feed), xytext=(1.05, 18_300), fontsize=6.6, color=C["lng"],
                arrowprops=dict(arrowstyle="-", color=C["lng"], lw=0.6))
    ax.set_title(f"Natural gas allocation (production {gas_prod:,.1f} ktoe)", loc="left"); panel(ax, "a")

    ax = axes[1]
    labs = ["Coal\n(HS 2701)", "Lignite\n(HS 2704)", "Coal\nre-exports"]
    vals = [246_603.5, 18_153.2, -5_143.9]
    bars = ax.bar(labs, np.array(vals) / 1000, color=[C["coal"], C["coal"], MUTED], width=0.55)
    bar_labels(ax, bars, "{:,.1f}", size=6.8)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_ylabel("Thousand tonnes"); ax.set_ylim(-30, 290); ax.grid(axis="x", visible=False)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_title(f"Coal & lignite trade (net {coal_net:,.1f} ktoe)", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig06_gas_coal")


# ========================================================= Fig 7 electricity
def fig7():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw=dict(width_ratios=[0.85, 1.2, 1.1]))
    ax = axes[0]
    ax.bar(0, gen_gwh - re_gwh, color=C["gas"], width=0.6, label="Gas-fired thermal")
    ax.bar(0, re_gwh, bottom=gen_gwh - re_gwh, color=C["re"], width=0.6, label="Solar & wind")
    ax.bar(1, cons_gwh, color=C["elec"], width=0.6)
    ax.bar(2, gen_gwh - cons_gwh, color=C["grey"], width=0.6)
    for x, v in [(0, gen_gwh), (1, cons_gwh), (2, gen_gwh - cons_gwh)]:
        ax.text(x, v + 700, f"{v:,.0f}", ha="center", fontsize=6.8, color=INK2)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Gener-\nation", "Consum-\nption", "Losses &\nown use"], fontsize=6.6)
    ax.set_ylabel("GWh"); ax.set_ylim(0, 72_000); ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.legend(loc="upper center", fontsize=6.2, handlelength=1, ncol=1)
    ax.set_title("Electricity balance", loc="left"); panel(ax, "a")

    ax = axes[1]
    plants = ["Ibri II Solar IPP", "Manah/Sembcorp\nJinko Shine (PV)", "Wadi Noor Solar", "Dhofar I Wind IPP",
              "OPWP purchases", "Al Mazyonah"]
    plants[1] = "Sembcorp Jinko\nShine (PV)"
    pv = [1_585.4, 1_420.6, 1_375.5, 124.0, 3.0, 0.5]
    cols = [C["re"]] * 3 + [C["gas"]] + [C["grey"]] * 2
    y = np.arange(len(plants))[::-1]
    bars = ax.barh(y, pv, color=cols, height=0.62)
    for b, v in zip(bars, pv):
        ax.text(v + 25, b.get_y() + b.get_height() / 2, f"{v:,.1f} ({v / re_gwh * 100:.1f}%)", va="center",
                fontsize=6.4, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(plants, fontsize=6.8); ax.set_xlim(0, 2_250)
    ax.set_xlabel("GWh"); ax.grid(axis="y", visible=False)
    ax.set_title("RE generation by plant", loc="left"); panel(ax, "b")

    ax = axes[2]
    yrs = [2024, 2025]; act = [4.89, 8.85]
    ax.plot(yrs, act, "-o", color=C["re"], lw=2, ms=6, label="Observed", zorder=3)
    ax.plot([2025, 2030], [8.85, 30], "--", color=C["re"], lw=1.4, label="OPWP 30% target path")
    ax.plot([2025, 2030], [8.85, 20], ":", color=C["gas"], lw=1.4, label="20% target (IEA, 2023)")
    ax.plot(2030, 30, "D", color=C["re"], ms=6); ax.plot(2030, 20, "D", color=C["gas"], ms=5)
    for x, v in zip(yrs, act):
        ax.text(x - 0.15, v + 1.2, f"{v:.2f}%", ha="right", fontsize=6.6, color=INK2)
    ax.text(2030, 31.3, "30%", ha="center", fontsize=6.8, color=INK2)
    ax.text(2030, 21.3, "20%", ha="center", fontsize=6.8, color=INK2)
    ax.text(2027.4, 11, "required: +4.2 pp yr$^{-1}$\n(observed 2024–25: +3.96 pp)", fontsize=6.3, color=INK2)
    ax.set_xlim(2023.0, 2030.8); ax.set_ylim(0, 36); ax.set_ylabel("Share of generation (%)")
    ax.legend(loc="upper left", fontsize=6.0, handlelength=1.6)
    ax.set_title("RE share trajectory", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.6)
    save(fig, "Fig08_electricity")


# ========================================================== Fig 8 sectoral
def fig8():
    fig = plt.figure(figsize=(7.4, 5.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1.25, 1], hspace=0.75, wspace=0.45)
    # (a) TFC by sector stacked by carrier
    ax = fig.add_subplot(gs[0, :])
    order = ["Industrial", "Other / unallocated", "Transport", "Residential", "Commercial", "Government"]
    carriers = {
        "Natural gas": ([10_331, 0, 0, 0, 0, 0], C["gas"]),
        "Petroleum products": ([950.7, 5_406.2, 4_435.5, 316.9, 0, 0], C["products"]),
        "Electricity": ([699.7, 135.1, 0, 1_601.7, 1_045.9, 390.3], C["elec"]),
        "Coal & lignite": ([168.7, 0, 0, 0, 0, 0], C["coal"]),
    }
    y = np.arange(len(order))[::-1]; left = np.zeros(len(order))
    for name, (v, col) in carriers.items():
        ax.barh(y, v, left=left, color=col, height=0.62, label=name, edgecolor="white", linewidth=0.8)
        left += np.array(v)
    for yi, tot in zip(y, tfc_sec):
        ax.text(tot + 120, yi, f"{tot:,.1f} ktoe ({tot / tfc * 100:.1f}%)", va="center", fontsize=6.8, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(order, fontsize=7.2); ax.set_xlim(0, 15_500)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("ktoe"); ax.grid(axis="y", visible=False)
    ax.legend(ncol=4, loc="upper center", fontsize=6.8, bbox_to_anchor=(0.5, -0.28))
    ax.set_title(f"Total final consumption by sector and carrier ({tfc:,.1f} ktoe)", loc="left"); panel(ax, "a")

    # (b) electricity by sector
    ax = fig.add_subplot(gs[1, 0])
    names = list(elec_sec_gwh.keys()); vals = list(elec_sec_gwh.values())
    y = np.arange(len(names))[::-1]
    bars = ax.barh(y, vals, color=[SEC[n] for n in names], height=0.62)
    for b, v in zip(bars, vals):
        ax.text(v + 250, b.get_y() + b.get_height() / 2, f"{v:,.0f} ({v / cons_gwh * 100:.1f}%)", va="center",
                fontsize=6.6, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(["Residential", "Commercial", "Industrial", "Government", "Other"], fontsize=7)
    ax.set_xlim(0, 25_500); ax.set_xlabel("GWh"); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_title("Electricity consumption by sector", loc="left"); panel(ax, "b")

    # (c) petroleum allocation sensitivity
    ax = fig.add_subplot(gs[1, 1])
    secs = ["Transport", "Industrial", "Residential", "Other"]
    bal = [4_435.5, 950.7, 316.9, 633.7]
    prod_spec = [40_642.1 * 0.145, 2_253.8 * 0.145, 804.0 * 0.145, 0.0]
    x = np.arange(len(secs)); w = 0.38
    b1 = ax.bar(x - w / 2, bal, w, color=C["products"], label="Uniform 70/15/5/10 split (balance)")
    b2 = ax.bar(x + w / 2, prod_spec, w, color=C["oil"], label="Product-specific split")
    for bars in (b1, b2):
        bar_labels(ax, bars, "{:,.0f}", size=6.2)
    ax.set_xticks(x); ax.set_xticklabels(secs, fontsize=7); ax.set_ylabel("ktoe")
    ax.set_ylim(0, 7_600); ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.legend(loc="upper right", fontsize=6.2)
    ax.set_title("Retail petroleum allocation sensitivity", loc="left"); panel(ax, "c")
    save(fig, "Fig07_sectoral")


# ========================================================== Fig 9 emissions
EM_DIRECT = {"Power generation": 32.82, "Industrial": 27.81, "Other / unallocated": 16.60,
             "Transport": 13.29, "Residential": 0.95}
EM_TOTAL = 91.48


def end_use_emissions():
    share = {k: v / cons_gwh for k, v in elec_sec_gwh.items()}
    out = {"Industrial": 27.81, "Other / unallocated": 16.60, "Transport": 13.29, "Residential": 0.95,
           "Commercial": 0.0, "Government": 0.0}
    for k, s in share.items():
        out[k] += 32.82 * s
    return out


def fig9():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.0), gridspec_kw=dict(width_ratios=[1.35, 0.85, 1.25]))
    ax = axes[0]
    order = ["Industrial", "Residential", "Other / unallocated", "Transport", "Commercial", "Government"]
    eu = end_use_emissions()
    direct = [EM_DIRECT.get(k, 0) for k in order]
    indirect = [eu[k] - EM_DIRECT.get(k, 0) for k in order]
    y = np.arange(len(order))[::-1]
    ax.barh(y, direct, color=[SEC[k] for k in order], height=0.62, label="Direct combustion")
    ax.barh(y, indirect, left=direct, color="white", edgecolor=[SEC[k] for k in order], hatch="////",
            height=0.62, linewidth=0.7, label="Allocated power-sector CO₂")
    for yi, d, i in zip(y, direct, indirect):
        ax.text(d + i + 0.5, yi, f"{d + i:.1f}", va="center", fontsize=6.6, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(["Industrial", "Residential", "Other / unalloc.", "Transport",
                                          "Commercial", "Government"], fontsize=7)
    ax.set_xlim(0, 41); ax.set_xlabel("MtCO₂"); ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=6.2)
    ax.set_title("End-use attribution of CO₂", loc="left"); panel(ax, "a")

    ax = axes[1]
    fuels = ["Natural\ngas", "Petro-\nleum", "Coal &\nlignite"]
    fv = [57.09, 33.69, 0.70]
    bars = ax.bar(fuels, fv, color=[C["gas"], C["products"], C["coal"]], width=0.6)
    for b, v in zip(bars, fv):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.2f}\n({v / EM_TOTAL * 100:.1f}%)", ha="center",
                fontsize=6.6, color=INK2)
    ax.set_ylim(0, 72); ax.set_ylabel("MtCO₂"); ax.grid(axis="x", visible=False); ax.tick_params(axis="x", labelsize=6.8)
    ax.set_title("By fuel", loc="left"); panel(ax, "b")

    ax = axes[2]
    rows = ["Power gen.", "Industrial", "Transport", "Other / unalloc.", "Residential"]
    colsn = ["Gas", "Petroleum", "Coal"]
    M = np.array([[32.82, 0, 0], [24.27, 2.84, 0.70], [0, 13.29, 0], [0, 16.60, 0], [0, 0.95, 0]])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#f4f8fd", "#2a78d6", "#0d3b73"])
    ax.imshow(M, cmap=cmap, aspect="auto", vmin=0, vmax=34)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, "—" if v == 0 else f"{v:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if v > 17 else INK)
    ax.set_xticks(range(3)); ax.set_xticklabels(colsn, fontsize=7); ax.set_yticks(range(5))
    ax.set_yticklabels(rows, fontsize=7); ax.grid(False)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Sector × fuel matrix (MtCO₂)", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.4)
    save(fig, "Fig09_emissions")
    return eu


# ===================================================== Fig 10 avoided CO2
EF_AVG = 32.82e6 / ((gen_gwh - re_gwh) * 1e3)  # tCO2/MWh = 0.7064
EF_CCGT = 56.1 * 3.6 / 0.55 / 1000             # 0.367
EF_OCGT = 56.1 * 3.6 / 0.35 / 1000             # 0.577


def fig10():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax = axes[0]
    shares = np.array([8.85, 10, 20, 30, 40, 50])
    for ef, col, lab, ls in [(EF_AVG, C["re"], f"Fleet-average EF ({EF_AVG:.3f} t/MWh)", "-"),
                             (EF_OCGT, C["gas"], f"OCGT margin ({EF_OCGT:.3f} t/MWh)", "--"),
                             (EF_CCGT, C["lng"], f"CCGT margin ({EF_CCGT:.3f} t/MWh)", ":")]:
        av = shares / 100 * gen_gwh * ef / 1000
        ax.plot(shares, av, ls, color=col, lw=1.8, marker="o", ms=4, label=lab)
    for s in [8.85, 30]:
        v = s / 100 * gen_gwh * EF_AVG / 1000
        ax.annotate(f"{v:.2f}", (s, v), xytext=(5, -11), textcoords="offset points", fontsize=6.8, color=INK2)
    ax.axvline(30, color=MUTED, lw=0.6, ls="--"); ax.text(30.6, 1, "OPWP 2030\ntarget", fontsize=6.4, color=MUTED)
    ax.set_xlabel("Renewable share of generation (%; 2025 generation held constant)")
    ax.set_ylabel("Avoided CO₂ (MtCO₂ yr$^{-1}$)"); ax.set_xlim(5, 52); ax.set_ylim(0, 20)
    ax.legend(loc="upper left", fontsize=6.3)
    ax.set_title("Avoided CO₂ by RE share and displaced EF", loc="left"); panel(ax, "a")

    ax = axes[1]
    cases = ["2025 actual\n(8.85%)", "30% target"]
    x = np.arange(2); w = 0.25
    for k, (ef, col, lab) in enumerate([(EF_CCGT, C["lng"], "CCGT"), (EF_OCGT, C["gas"], "OCGT"),
                                        (EF_AVG, C["re"], "Fleet avg.")]):
        v = [re_gwh * ef / 1000, 0.30 * gen_gwh * ef / 1000]
        bars = ax.bar(x + (k - 1) * w, v, w, color=col, label=lab)
        bar_labels(ax, bars, "{:.2f}", size=6.2)
    ax.set_xticks(x); ax.set_xticklabels(cases, fontsize=7); ax.set_ylabel("MtCO₂ yr$^{-1}$")
    ax.set_ylim(0, 12.5); ax.grid(axis="x", visible=False); ax.legend(fontsize=6.4, loc="upper left")
    ax.set_title("Range of avoided-emission estimates", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig10_avoided_emissions")


# ===================================================== Fig 11 dual dividend
HEAT = gas_power / (gen_gwh - re_gwh)      # ktoe gas per GWh thermal (0.3007)
MMBTU_PER_TOE = 39.683


def fig11():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1, 1.15]))
    ax = axes[0]
    shares = np.linspace(5, 50, 46)
    for heat, col, lab, ls in [(HEAT, C["gas"], f"Fleet-average heat rate ({HEAT * 41.868:.1f} GJ/MWh)", "-"),
                               (HEAT * EF_CCGT / EF_AVG, C["lng"], "CCGT heat rate (6.5 GJ/MWh)", ":")]:
        gas_ktoe = shares / 100 * gen_gwh * heat
        bcm = gas_ktoe / KTOE["gas"] * 28_316.8 / 1e9  # MMscf -> m3 -> bcm
        ax.plot(shares, bcm, ls, color=col, lw=1.8, label=lab)
    v25 = re_gwh * HEAT / KTOE["gas"] * 28_316.8 / 1e9
    ax.plot(8.85, v25, "o", color=C["gas"], ms=5)
    ax.annotate(f"2025: {v25:.2f} bcm\n({re_gwh * HEAT:,.0f} ktoe)", (8.85, v25), xytext=(28, -14),
                textcoords="offset points", fontsize=6.6, color=INK2,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED))
    ax.set_xlabel("Renewable share of generation (%)"); ax.set_ylabel("Gas freed from power (bcm yr$^{-1}$)")
    ax.set_xlim(5, 50); ax.set_ylim(0, 9.5); ax.legend(loc="upper left", fontsize=6.3)
    ax.set_title("Gas displaced from power generation", loc="left"); panel(ax, "a")

    ax = axes[1]
    sh = np.array([8.85, 15, 20, 30, 40, 50]); price = np.array([6, 8, 10, 12, 14])
    lng_eff = lng_out / lng_feed
    V = np.array([[s / 100 * gen_gwh * HEAT * lng_eff * 1e3 * MMBTU_PER_TOE * p / 1e9 for s in sh] for p in price])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("g", ["#f1faf6", "#1baf7a", "#0b5a3d"])
    ax.imshow(V, cmap=cmap, aspect="auto", origin="lower")
    for i in range(len(price)):
        for j in range(len(sh)):
            ax.text(j, i, f"{V[i, j]:.2f}", ha="center", va="center", fontsize=6.6,
                    color="white" if V[i, j] > V.max() * 0.55 else INK)
    ax.set_xticks(range(len(sh))); ax.set_xticklabels([f"{s:g}%" for s in sh], fontsize=7)
    ax.set_yticks(range(len(price))); ax.set_yticklabels([f"${p}" for p in price], fontsize=7)
    ax.set_xlabel("Renewable share of generation"); ax.set_ylabel("LNG price (USD/MMBtu)")
    ax.grid(False); [s.set_visible(False) for s in ax.spines.values()]; ax.tick_params(length=0)
    ax.set_title("Gross LNG value of freed gas (USD bn yr$^{-1}$)", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig11_dual_dividend")
    return re_gwh * HEAT, v25, V


# =================================================== Fig 12 capacity needs
def fig12():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.1, 1]))
    ax = axes[0]
    growth = np.array([0.0, 0.02, 0.03, 0.04, 0.05])
    cf = [0.25, 0.30, 0.35]
    for c, col, ls in zip(cf, [C["oil"], C["re"], C["gas"]], [":", "-", "--"]):
        add = (0.30 * gen_gwh * (1 + growth) ** 5 - re_gwh) / (8.76 * c) / 1000
        ax.plot(growth * 100, add, ls, marker="o", ms=4, color=col, lw=1.6, label=f"Capacity factor {c:.2f}")
    ax.set_xlabel("Electricity demand growth 2025–2030 (% yr$^{-1}$)")
    ax.set_ylabel("Additional VRE capacity by 2030 (GW)")
    ax.set_ylim(0, 9); ax.legend(fontsize=6.4, loc="upper left")
    ax.set_title("Grid capacity to reach 30% by 2030", loc="left"); panel(ax, "a")

    ax = axes[1]
    base = re_gwh / (8.76 * 0.30) / 1000
    grid_add = (0.30 * gen_gwh * 1.03 ** 5 - re_gwh) / (8.76 * 0.30) / 1000
    labs = ["Implied 2025\nVRE fleet", "Grid target\nadditions (3%\ngrowth, CF 0.30)", "Hydrogen 2030\n(1.0–1.25 Mt H₂)"]
    lo = [base, grid_add, 16]; hi = [base, grid_add, 20]
    bars = ax.bar(range(3), lo, color=[C["re"], C["re"], C["lng"]], width=0.58)
    ax.bar(2, hi[2] - lo[2], bottom=lo[2], color="white", edgecolor=C["lng"], hatch="////", width=0.58, lw=0.7)
    for i, (a, b) in enumerate(zip(lo, hi)):
        ax.text(i, b + 0.4, f"{a:.1f}" if a == b else f"{a:.0f}–{b:.0f}", ha="center", fontsize=7, color=INK2)
    ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=6.6); ax.set_ylabel("GW")
    ax.set_ylim(0, 23); ax.grid(axis="x", visible=False)
    ax.set_title("Scale of the hydrogen build-out", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig12_capacity")
    return base, grid_add


# ===================================================== Fig 13 policy schema
def fig13():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.04, 0.86, 0.92, 0.11, "Evidence layer: IRES-consistent National Energy Balance\n"
        "TPES · TFC by sector × carrier · CO₂ by sector × fuel · RE share · gas displacement",
        "#2a78d6", ec="#2a78d6", size=7.6, bold=True, tc="white")
    pillars = [
        ("Supply-side decarbonisation", "#e8f6f0",
         "• Utility-scale PV & wind (30% by 2030)\n• Storage: PHES / CAES\n• Hydrogen: 16–20 GW dedicated VRE\n"
         "• Gas freed → LNG / petrochemicals"),
        ("Demand-side efficiency", "#fdf3e1",
         "• Electricity & fuel subsidy reform\n• Building codes; IoT-based HVAC\n• Industrial benchmarking (TFEE)\n"
         "• Industrial fuel switching"),
        ("Enabling institutions", "#efedfb",
         "• Unified green taxonomy & ESG\n• Value-chain localisation (Sohar PV)\n• Transition minerals (Cu, Li)\n"
         "• Annual balance + NDC reporting"),
    ]
    xs = [0.02, 0.35, 0.68]
    for x, (h, fc, body) in zip(xs, pillars):
        box(ax, x, 0.62, 0.30, 0.075, h, fc, size=8, bold=True)
        box(ax, x, 0.30, 0.30, 0.30, body, fc, size=7.2)
        arrow(ax, 0.5, 0.86, x + 0.15, 0.70)
        arrow(ax, x + 0.15, 0.30, 0.5, 0.17)
    box(ax, 0.17, 0.04, 0.66, 0.12, "Outcomes: dual dividend (CO₂ avoided + export rent preserved) · "
        "decoupling of growth from\ndomestic fossil use · credible NDC tracking toward net zero 2050",
        "#f3f2ef", size=7.6, bold=True)
    save(fig, "Fig13_policy_framework")


if __name__ == "__main__":
    fig1(); fig2()
    ssr = fig3(); conv, own = fig4(); slate = fig5(); fig6(); fig7(); fig8()
    eu = fig9(); fig10(); gas_freed, bcm25, V = fig11(); base, grid_add = fig12(); fig13()
    print("prod_ires", round(prod_ires, 1), "tpes_ires", round(tpes_ires, 1))
    print("SSR compiled/ires/hi/lo", [round(s, 1) for s in ssr])
    print("conversion losses", round(conv, 1), "own use+T&D", round(own, 1), "ref gap", round(ref_gap, 1))
    print("slate", slate, "end-use CO2", {k: round(v, 2) for k, v in eu.items()})
    print("EF avg/ccgt/ocgt", round(EF_AVG, 4), round(EF_CCGT, 3), round(EF_OCGT, 3))
    print("gas freed ktoe", round(gas_freed, 1), "bcm", round(bcm25, 3), "value 2025 @6..14", V[:, 0].round(3))
    print("VRE base GW", round(base, 2), "grid add GW", round(grid_add, 2))
    print("intensity", round(tpes_ires * 1000 / 40_130, 1), "per cap kgoe", round(tpes_ires * 1e6 / 5_359_557, 1),
          "RE share TPES", round(re_ktoe / tpes_ires * 100, 2))
