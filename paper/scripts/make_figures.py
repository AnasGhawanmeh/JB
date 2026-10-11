"""Generate all manuscript figures from ../data/results.json (produced by model.py).

Run:  python model.py && python make_figures.py
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(HERE, "..", "data", "results.json")))
c = R["central"]
MC = np.load(os.path.join(HERE, "..", "data", "mc_draws.npz"))

plt.rcParams.update({
    "font.family": "Liberation Sans", "font.size": 8.5, "axes.titlesize": 9, "axes.titleweight": "bold",
    "axes.labelsize": 8.5, "axes.edgecolor": "#52514e", "axes.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True, "grid.color": "#e4e3df",
    "grid.linewidth": 0.5, "xtick.color": "#52514e", "ytick.color": "#52514e", "xtick.major.width": 0.5,
    "ytick.major.width": 0.5, "legend.frameon": False, "legend.fontsize": 7.5, "savefig.dpi": 600,
    "savefig.bbox": "tight", "figure.dpi": 150, "hatch.linewidth": 0.35,
})
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
C = {"gas": "#2a78d6", "oil": "#eb6834", "products": "#eda100", "lng": "#6250d6", "coal": "#e87ba4",
     "re": "#1baf7a", "elec": "#008300", "grey": "#a3a29b", "gap": "#c9c8c2", "red": "#e34948"}
SEC = {"Industrial": "#2a78d6", "Transport": "#eb6834", "Residential": "#1baf7a", "Commercial": "#eda100",
       "Government": "#e87ba4", "Agriculture & other": "#8a8984", "Non-energy use": "#6250d6"}
FMT = matplotlib.ticker.StrMethodFormatter("{x:,.0f}")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"))
    plt.close(fig)


def panel(ax, letter):
    ax.text(-0.02, 1.04, f"({letter})", transform=ax.transAxes, fontsize=9.5, fontweight="bold",
            va="bottom", ha="right", color=INK)


def hbar_labels(ax, bars, vals, fmt, size=6.6, pad=3):
    for b, v in zip(bars, vals):
        ax.annotate(fmt(v), (b.get_x() + b.get_width(), b.get_y() + b.get_height() / 2),
                    xytext=(pad if b.get_width() >= 0 else -pad, 0), textcoords="offset points",
                    ha="left" if b.get_width() >= 0 else "right", va="center", fontsize=size, color=INK2)


def vbar_labels(ax, bars, vals, fmt, size=6.6, pad=2):
    for b, v in zip(bars, vals):
        h = b.get_height()
        ax.annotate(fmt(v), (b.get_x() + b.get_width() / 2, b.get_y() + h if h >= 0 else b.get_y()),
                    xytext=(0, pad if h >= 0 else -pad - 7), textcoords="offset points", ha="center",
                    va="bottom", fontsize=size, color=INK2)


def box(ax, x, y, w, h, text, fc, ec=INK2, size=7.2, bold=False, tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012", fc=fc, ec=ec, lw=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            fontweight="bold" if bold else "normal", color=tc, linespacing=1.25)


def arrow(ax, x0, y0, x1, y1, color=INK2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=color,
                                                                  mutation_scale=9))


# ===================================================================== Fig 1
def fig1():
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    cols, w = [0.005, 0.255, 0.505, 0.755], 0.225
    heads = ["1  Activity data", "2  Harmonisation", "3  Closure & calibration", "4  Analysis"]
    items = [
        ["National statistics: oil,\ngas, electricity, trade", "Plant-level refinery,\nLNG & renewable data",
         "Customs (HS 2701/2704);\nport bunker records", "External series: EI,\nGCP, Ember (2015–2025)"],
        ["NCV basis throughout\n(gas NCV = 0.9 × GCV)", "Product-specific NCV &\ndensity (IPCC 2006)",
         "Reinjection, feedstock &\nbunkers separated", "Retail sales allocated\nby product"],
        ["T1 column closure\n(statistical difference)", "T2 process closure:\nrefinery, LNG, power",
         "Calibration: oil-field\ngas vs EI gas use", "Validation on data not\nused in calibration"],
        ["Reconciled balance &\nIPCC Tier 1 inventory", "Monte Carlo (10,000)\n& LMDI 2015–2024",
         "Avoided CO₂, gas freed\n& rent preserved", "Rent incidence &\npolicy instruments"],
    ]
    fills = ["#f3f2ef", "#f3f2ef", "#eaf2fb", "#e8f6f0"]
    for x, h in zip(cols, heads):
        box(ax, x, 0.90, w, 0.075, h, "#2a78d6", ec="#2a78d6", size=8, bold=True, tc="white")
    for x, its, fc in zip(cols, items, fills):
        for i, t in enumerate(its):
            box(ax, x, 0.69 - i * 0.205, w, 0.17, t, fc, size=6.8)
    for x in cols[:-1]:
        for i in range(4):
            yy = 0.69 - i * 0.205 + 0.085
            arrow(ax, x + w + 0.003, yy, x + 0.25 - 0.003, yy)
    ax.text(0.5, 0.0, "Failed closure tests (stage 3) trigger re-harmonisation (stage 2); residual gaps are reported, not imputed",
            ha="center", fontsize=6.8, color=MUTED, style="italic")
    save(fig, "Fig01_framework")

# ===================================================================== Fig 2 Sankey
def ribbon(ax, x0, y0a, y0b, x1, y1a, y1b, color, alpha=0.4, hatch=None):
    xm = (x0 + x1) / 2
    v = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a), (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
    cd = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4,
          Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(v, cd), fc=color, ec="none", alpha=alpha, hatch=hatch))


def declutter(items, gap):
    items.sort(key=lambda t: -t[0])
    for i in range(1, len(items)):
        if items[i - 1][0] - items[i][0] < gap:
            items[i][0] = items[i - 1][0] - gap
    return items


def fig2():
    s = c["sectors"]; es = c["elec_sec"]
    nodes = {
        "Crude oil production": (0, C["oil"]), "Crude oil imports": (0, C["oil"]),
        "Crude statistical difference": (0, C["gap"]),
        "Natural gas (marketable)": (0, C["gas"]), "Solar & wind": (0, C["re"]), "Coal & lignite": (0, C["coal"]),
        "Refineries": (1, C["products"]), "LNG trains": (1, C["lng"]), "Power & water plants": (1, C["elec"]),
        "Upstream own use": (1, C["grey"]), "Gas (direct use)": (1, C["gas"]), "Coal (direct use)": (1, C["coal"]),
        "Refined products": (2, C["products"]), "LNG": (2, C["lng"]), "Electricity": (2, C["elec"]),
        "Exports & bunkers": (3, MUTED), "Conversion & own use": (3, C["gap"]),
        "Industrial": (3, SEC["Industrial"]), "Transport": (3, SEC["Transport"]),
        "Residential": (3, SEC["Residential"]), "Commercial & government": (3, SEC["Commercial"]),
        "Non-energy use": (3, SEC["Non-energy use"]), "Agriculture & other": (3, SEC["Agriculture & other"]),
    }
    crude_dom = c["crude_prod"] - c["crude_exp"]
    pw_loss = c["gas_power"] + c["re"] - c["gen"]
    ind_pet = c["sectors"]["Industrial"] - c["ind_fuel"] - c["coal"] - es["Industrial"]
    flows = [
        ("Crude oil production", "Exports & bunkers", c["crude_exp"], C["oil"]),
        ("Crude oil production", "Refineries", crude_dom, C["oil"]),
        ("Crude oil imports", "Refineries", c["crude_imp"], C["oil"]),
        ("Crude statistical difference", "Refineries", -c["sd_crude"], C["gap"]),
        ("Natural gas (marketable)", "LNG trains", c["lng_feed"], C["gas"]),
        ("Natural gas (marketable)", "Power & water plants", c["gas_power"], C["gas"]),
        ("Natural gas (marketable)", "Upstream own use", c["own"], C["gas"]),
        ("Natural gas (marketable)", "Gas (direct use)", c["gas_industry"], C["gas"]),
        ("Coal & lignite", "Coal (direct use)", c["coal"], C["coal"]),
        ("Solar & wind", "Power & water plants", c["re"], C["re"]),
        ("Refineries", "Refined products", c["ref_out"], C["products"]),
        ("Refineries", "Conversion & own use", c["ref_loss"], C["gap"]),
        ("LNG trains", "LNG", c["lng_out"], C["lng"]),
        ("LNG trains", "Conversion & own use", c["lng_loss"], C["gap"]),
        ("Power & water plants", "Electricity", c["gen"], C["elec"]),
        ("Power & water plants", "Conversion & own use", pw_loss, C["gap"]),
        ("Upstream own use", "Conversion & own use", c["own"], C["grey"]),
        ("Gas (direct use)", "Industrial", c["ind_fuel"], C["gas"]),
        ("Gas (direct use)", "Non-energy use", c["chem"], C["gas"]),
        ("Coal (direct use)", "Industrial", c["coal"], C["coal"]),
        ("Refined products", "Exports & bunkers", c["prod_exp"] + c["bunk_total"], C["products"]),
        ("Refined products", "Industrial", ind_pet, C["products"]),
        ("Refined products", "Transport", s["Transport"], C["products"]),
        ("Refined products", "Residential", s["Residential"] - es["Residential"], C["products"]),
        ("Refined products", "Non-energy use", c["ne_oil"], C["products"]),
        ("LNG", "Exports & bunkers", c["lng_out"], C["lng"]),
        ("Electricity", "Conversion & own use", c["elec_loss"], C["elec"]),
        ("Electricity", "Industrial", es["Industrial"], C["elec"]),
        ("Electricity", "Residential", es["Residential"], C["elec"]),
        ("Electricity", "Commercial & government", es["Commercial"] + es["Government"], C["elec"]),
        ("Electricity", "Agriculture & other", es["Agriculture & other"], C["elec"]),
    ]
    inflow = {n: 0.0 for n in nodes}; outflow = {n: 0.0 for n in nodes}
    for a, b, v, _ in flows:
        outflow[a] += v; inflow[b] += v
    size = {n: max(inflow[n], outflow[n]) for n in nodes}
    lx = [0.15, 0.41, 0.65, 0.86]
    scale = 0.80 / sum(size[n] for n in nodes if nodes[n][0] == 0)
    gaps = [0.016, 0.022, 0.03, 0.016]
    pos = {}
    for L in range(4):
        names = [n for n in nodes if nodes[n][0] == L]
        tot = sum(size[n] for n in names) * scale + gaps[L] * (len(names) - 1)
        y = 0.49 + tot / 2
        for n in names:
            h = max(size[n] * scale, 0.003); pos[n] = [y - h, y]; y -= h + gaps[L]
    cen = {n: sum(p) / 2 for n, p in pos.items()}
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    ax.set_xlim(0, 1.07); ax.set_ylim(-0.02, 1.0); ax.axis("off")
    nw = 0.014
    oc = {n: pos[n][1] for n in nodes}; ic = {n: pos[n][1] for n in nodes}; ys = {}
    for f in sorted(flows, key=lambda f: -cen[f[1]]):
        h = f[2] * scale; ys.setdefault(id(f), {})["s"] = (oc[f[0]], oc[f[0]] - h); oc[f[0]] -= h
    for f in sorted(flows, key=lambda f: -cen[f[0]]):
        h = f[2] * scale; ys[id(f)]["d"] = (ic[f[1]], ic[f[1]] - h); ic[f[1]] -= h
    for f in flows:
        (a0, a1), (b0, b1) = ys[id(f)]["s"], ys[id(f)]["d"]
        ribbon(ax, lx[nodes[f[0]][0]] + nw, a0, a1, lx[nodes[f[1]][0]], b0, b1, f[3])
    for n, (L, col) in nodes.items():
        ax.add_patch(Rectangle((lx[L], pos[n][0]), nw, pos[n][1] - pos[n][0], fc=col, ec="none"))
    for L in range(4):
        names = [n for n in nodes if nodes[n][0] == L]
        if L in (0, 3):
            for yl, n in declutter([[cen[n], n] for n in names], 0.034 if L == 3 else 0.032):
                lab = f"{n}\n{size[n]:,.0f}" if (L == 0 and size[n] > 1000) else f"{n}  {size[n]:,.0f}"
                xx = lx[0] - 0.006 if L == 0 else lx[3] + nw + 0.006
                ax.text(xx, yl, lab, ha="right" if L == 0 else "left", va="center", fontsize=6.3, color=INK,
                        linespacing=1.1)
                if abs(yl - cen[n]) > 0.004:
                    x_n = lx[0] if L == 0 else lx[3] + nw
                    ax.plot([x_n, x_n + (-0.005 if L == 0 else 0.005)], [cen[n], yl], color=MUTED, lw=0.4)
        else:
            for n in names:
                ax.text(lx[L] + nw / 2, pos[n][1] + 0.004, f"{n} {size[n]:,.0f}", ha="center", va="bottom",
                        fontsize=6.0, color=INK, bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.6))
    for L, t in enumerate(["Primary supply", "Transformation", "Secondary carriers", "Disposition & final use"]):
        ax.text(lx[L] + nw / 2, 0.985, t, ha="center", fontsize=7.4, fontweight="bold", color=INK2)
    ax.text(0.0, -0.015, "Reconciled 2025 balance, ktoe (NCV). Grey source ribbon: crude statistical difference "
            "(Section 2.4.1); reinjected gas excluded from production.", fontsize=6.4, color=MUTED, style="italic")
    save(fig, "Fig02_sankey")


# ===================================================================== Fig 3 diagnostics
def fig3():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.2), gridspec_kw=dict(width_ratios=[1.0, 1.45, 1.15]))
    ax = axes[0]
    v = R["valid"]["refinery"]
    x = np.arange(len(v)); w = 0.36
    b1 = ax.bar(x - w / 2, [g["cap_kbd"] for g in v], w, color=C["grey"], label="Nameplate")
    b2 = ax.bar(x + w / 2, [g["out_kbd"] for g in v], w, color=C["products"], label="Reported output")
    vbar_labels(ax, b1, [g["cap_kbd"] for g in v], lambda t: f"{t:.0f}", size=6.4)
    vbar_labels(ax, b2, [g["out_kbd"] for g in v], lambda t: f"{t:.0f}", size=6.4)
    ax.set_xticks(x); ax.set_xticklabels(["Sohar +\nMina Al Fahal", "Duqm"], fontsize=6.8)
    ax.axhline(R["valid"]["crude_supply_kbd"], color=C["red"], lw=0.8, ls="--")
    ax.text(-0.45, R["valid"]["crude_supply_kbd"] + 6, f"recorded crude supply to all refineries: {R['valid']['crude_supply_kbd']:.0f} kb/d",
            fontsize=5.6, color=C["red"], ha="left", va="bottom")
    ax.set_ylabel("kb/d"); ax.set_ylim(0, 500); ax.legend(fontsize=6.0, loc="upper right", ncol=2); ax.grid(axis="x", visible=False)
    ax.set_title(f"Refinery output vs capacity\n(implied intake {R['valid']['intake_kbd']:.0f} kb/d)", loc="left"); panel(ax, "a")

    ax = axes[1]
    steps = R["steps"]
    labs = ["As compiled", "Primary elec. = solar & wind", "Gas on NCV basis", "Reinjection excluded",
            "LNG 1.177 toe/t", "Product factors", "Aviation bunkers", "Crude statistical difference", "Reconciled (use side)"]
    run = 0
    for i, (lab, val) in enumerate(steps):
        if i in (0, len(steps) - 1):
            ax.bar(i, val, color=C["gas"], width=0.62); run = val
            ax.text(i, val / 2, f"{val:,.0f}", ha="center", va="center", rotation=90, fontsize=6.2, color="white")
        else:
            base = run if val > 0 else run + val
            ax.bar(i, abs(val), bottom=base, color=C["re"] if val > 0 else C["red"], width=0.62,
                   hatch="////" if "statistical" in lab else None, edgecolor="white" if "statistical" in lab else None)
            ax.text(i, max(run, run + val) + 700, f"{val:+,.0f}", ha="center", va="bottom", fontsize=5.8, color=INK2,
                    rotation=90 if abs(val) < 4000 else 0)
            run += val
    ax.set_xticks(range(len(steps))); ax.set_xticklabels(labs, fontsize=6.0, rotation=40, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, 50_000); ax.yaxis.set_major_formatter(FMT); ax.set_ylabel("TPES, ktoe"); ax.grid(axis="x", visible=False)
    ax.set_title("From as-compiled to reconciled TPES", loc="left"); panel(ax, "b")

    ax = axes[2]
    cal, val = R["calib"], R["valid"]
    rows = [
        ("V  Crude + condensate\nproduction (kb/d ÷ 10)", val["production_kbd"] / 10, val["ext_production_kbd"] / 10, None),
        ("V  Oil consumption\n(Mtoe)", val["oil_ours"] / 1e3, val["oil_ei25"][0] / 1e3, val["oil_ei25"]),
        ("V  Generation (TWh)", val["gen_ours"] / 1e3, val["gen_ember25"] / 1e3, None),
        ("C  Gas consumption\n(Mtoe, NCV)", c["gas_cons_ei_def"] / 1e3, cal["ei_gas25_ncv"][0] / 1e3, None),
    ]
    y = np.arange(len(rows))[::-1]; h = 0.36
    b1 = ax.barh(y + h / 2, [r[1] for r in rows], h, color=C["gas"], label="This study, 2025")
    b2 = ax.barh(y - h / 2, [r[2] for r in rows], h, color=C["grey"], label="External, 2025*")
    hbar_labels(ax, b1, [r[1] for r in rows], lambda t: f"{t:.1f}", size=6.0)
    hbar_labels(ax, b2, [r[2] for r in rows], lambda t: f"{t:.1f}", size=6.0)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=6.2); ax.set_xlim(0, 135)
    ax.legend(loc="upper center", bbox_to_anchor=(0.4, -0.13), fontsize=6.0); ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.set_title("Validation (V) and calibration (C)", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.0)
    save(fig, "Fig03_diagnostics")

# ===================================================================== Fig 4 supply
def fig4():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw=dict(width_ratios=[1, 1.25, 0.95]))
    ax = axes[0]
    labs = ["Natural\ngas", "Crude\noil", "Solar &\nwind"]
    vals = [c["gas_marketable"], c["crude_prod"], c["re"]]
    b = ax.bar(labs, vals, color=[C["gas"], C["oil"], C["re"]], width=0.6)
    for bb, v in zip(b, vals):
        ax.text(bb.get_x() + bb.get_width() / 2, v / 2 if v > 5000 else v + 900,
                f"{v:,.0f}\n({v / c['production'] * 100:.1f}%)", ha="center", va="center" if v > 5000 else "bottom",
                fontsize=6.4, color="white" if v > 5000 else INK2)
    ax.bar(0, c["reinj"], bottom=c["gas_marketable"], color="white", edgecolor=C["gas"], hatch="////", width=0.6, lw=0.6)
    ax.text(0, c["gas_marketable"] + c["reinj"] + 600, "reinjected (excluded)", fontsize=5.8, color=C["gas"], ha="center")
    ax.set_ylim(0, 60_000); ax.set_ylabel("ktoe (NCV)"); ax.yaxis.set_major_formatter(FMT); ax.grid(axis="x", visible=False)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_title(f"Indigenous production\n{c['production']:,.0f} ktoe", loc="left"); panel(ax, "a")

    ax = axes[1]
    labs = ["Natural gas", "Crude oil (recorded)", "Crude stat. difference", "Solar & wind", "Coal & lignite", "LNG",
            "Refined products"]
    vals = [c["gas_marketable"], c["crude_supply"], -c["sd_crude"], c["re"], c["coal"], -c["lng_out"],
            -(c["prod_exp"] + c["bunk_total"])]
    cols = [C["gas"], C["oil"], "#f4b08f", C["re"], C["coal"], C["lng"], C["products"]]
    y = np.arange(len(labs))[::-1]
    b = ax.barh(y, vals, color=cols, height=0.62)
    b[2].set_hatch("////"); b[2].set_edgecolor("white")
    hbar_labels(ax, b, vals, lambda v: f"{v:,.0f}")
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=6.8); ax.tick_params(axis="y", length=0)
    ax.axvline(0, color=INK2, lw=0.6); ax.set_xlim(-46_000, 62_000); ax.set_xticks([-25_000, 0, 25_000, 50_000])
    ax.xaxis.set_major_formatter(FMT); ax.set_xlabel("ktoe (negative = net export / bunkers)"); ax.grid(axis="y", visible=False)
    ax.set_title(f"TPES by commodity (use side)\nTotal {c['tpes']:,.0f} ktoe", loc="left"); panel(ax, "b")

    ax = axes[2]
    conv = c["lng_loss"] + (c["gas_power"] + c["re"] - c["gen"]) + c["ref_loss"]
    own = c["own"] + c["elec_loss"]
    bottom = 0
    for lab, v, col in [("TFC", c["tfc"], C["elec"]), ("Conversion\nlosses", conv, C["grey"]),
                        ("Own use &\nT&D losses", own, "#c9c8c2")]:
        ax.bar(0, v, bottom=bottom, color=col, width=0.55, edgecolor="white", lw=1)
        ax.text(0.36, bottom + v / 2, f"{lab}\n{v:,.0f} ({v / c['tpes'] * 100:.0f}%)", va="center", fontsize=6.4)
        bottom += v
    ax.set_xlim(-0.5, 1.5); ax.set_xticks([]); ax.set_ylim(0, 42_000); ax.yaxis.set_major_formatter(FMT)
    ax.grid(axis="x", visible=False); ax.set_ylabel("ktoe")
    ax.set_title("Uses of TPES", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.6)
    save(fig, "Fig04_supply")

# ===================================================================== Fig 5 oil
def fig5():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.1, 1]))
    ax = axes[0]
    labs = ["Production", "Exports", "Imports\n(Duqm)", "Recorded\nsupply to\nrefineries", "Intake\nimplied by\noutput",
            "Output:\nSohar+MAF", "Output:\nDuqm"]
    vals = [c["crude_prod"], c["crude_exp"], c["crude_imp"], c["crude_supply"], c["ref_intake"], c["out_sm"], c["out_dq"]]
    cols = [C["oil"], MUTED, C["oil"], C["oil"], "#f4b08f", C["products"], C["products"]]
    b = ax.bar(range(7), vals, color=cols, width=0.62)
    vbar_labels(ax, b, vals, lambda v: f"{v:,.0f}", size=6.0)
    ax.annotate("", xy=(4, c["ref_intake"]), xytext=(3, c["crude_supply"]),
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=0.8))
    ax.text(3.5, c["ref_intake"] + 3500, f"SD {c['sd_crude']:,.0f}", color=C["red"], fontsize=6.4, ha="center")
    ax.set_xticks(range(7)); ax.set_xticklabels(labs, fontsize=5.5); ax.set_ylabel("ktoe")
    ax.yaxis.set_major_formatter(FMT); ax.set_ylim(0, 56_000); ax.grid(axis="x", visible=False)
    ax.set_title("Crude oil account", loc="left"); panel(ax, "a")

    ax = axes[1]
    sl = R["slate_ktoe"]; fp = R["f_prod"]
    names = sorted(sl, key=lambda k: -sl[k])
    y = np.arange(len(names))[::-1]
    b = ax.barh(y, [sl[k] for k in names], color=C["products"], height=0.62)
    tot = sum(sl.values())
    for bb, k in zip(b, names):
        ax.text(sl[k] + 60, bb.get_y() + bb.get_height() / 2, f"{sl[k]:,.0f} ({sl[k] / tot * 100:.0f}%; {fp[k]:.3f})",
                va="center", fontsize=6.3, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=7); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 7_200); ax.xaxis.set_major_formatter(FMT); ax.set_xlabel("ktoe (factor, ktoe/kbbl)")
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Sohar + Mina Al Fahal slate, {tot:,.0f} ktoe", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig05_oil")

# ===================================================================== Fig 6 gas
def fig6():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axes[0]
    labs = ["LNG\nfeed gas", "Power &\nwater plants", "Industry:\nfuel", "Industry:\nfeedstock",
            "Oil fields:\ncombusted", "Oil fields:\nreinjected"]
    vals = [c["lng_feed"], c["gas_power"], c["ind_fuel"], c["chem"], c["own"], c["reinj"]]
    cols = [C["lng"], C["elec"], C["gas"], SEC["Non-energy use"], C["grey"], "#c9c8c2"]
    b = ax.bar(range(6), vals, color=cols, width=0.62)
    for bb, v in zip(b, vals):
        ax.text(bb.get_x() + bb.get_width() / 2, v + 250, f"{v:,.0f}\n({v / c['gas_gross'] * 100:.1f}%)",
                ha="center", fontsize=6.2, color=INK2)
    ax.bar(1, c["gas_pw_other"], bottom=c["gas_grid"], color="white", edgecolor=C["elec"], hatch="////", width=0.62, lw=0.6)
    ax.text(1, c["gas_grid"] + c["gas_pw_other"] / 2, "desal. &\nunattrib.", fontsize=5.6, color=C["elec"], va="center",
            ha="center", bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xticks(range(6)); ax.set_xticklabels(labs, fontsize=6.4); ax.set_ylabel("ktoe (NCV)"); ax.set_ylim(0, 18_500)
    ax.yaxis.set_major_formatter(FMT); ax.grid(axis="x", visible=False)
    ax.set_title(f"Gross gas production {c['gas_gross']:,.0f} ktoe (NCV) by use", loc="left"); panel(ax, "a")

    ax = axes[1]
    labs = ["Feed gas:\nreported", "Feed gas:\nreconciled", "LNG\noutput"]
    vals = [c["lng_feed_reported"], c["lng_feed"], c["lng_out"]]
    b = ax.bar(range(3), vals, color=["#c9c8c2", C["gas"], C["lng"]], width=0.58)
    vbar_labels(ax, b, vals, lambda v: f"{v:,.0f}")
    ax.text(0, vals[0] / 2, f"η = {c['eta_lng_reported'] * 100:.1f}%\n(implausible)", ha="center", fontsize=6.0, color=INK)
    ax.text(1, vals[1] / 2, f"η = {c['eta_lng'] * 100:.1f}%", ha="center", fontsize=6.6, color="white", fontweight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=6.6); ax.set_ylabel("ktoe (NCV)"); ax.set_ylim(0, 17_500)
    ax.yaxis.set_major_formatter(FMT); ax.grid(axis="x", visible=False)
    ax.set_title("LNG (11.3 Mt) on a consistent NCV basis", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig06_gas")

# ===================================================================== Fig 7 sectoral
def fig7():
    s = c["sectors"]; es = c["elec_sec"]
    fig = plt.figure(figsize=(7.4, 5.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1], hspace=0.75, wspace=0.45)
    ax = fig.add_subplot(gs[0, :])
    order = ["Industrial", "Transport", "Non-energy use", "Residential", "Commercial", "Government", "Agriculture & other"]
    pet = {"Industrial": s["Industrial"] - c["ind_fuel"] - c["coal"] - es["Industrial"], "Transport": s["Transport"],
           "Residential": s["Residential"] - es["Residential"], "Non-energy use": c["ne_oil"]}
    carriers = [("Natural gas", {"Industrial": c["ind_fuel"], "Non-energy use": c["chem"]}, C["gas"]),
                ("Petroleum products", pet, C["products"]),
                ("Electricity", {k: es.get(k, 0) for k in order}, C["elec"]),
                ("Coal & lignite", {"Industrial": c["coal"]}, C["coal"])]
    y = np.arange(len(order))[::-1]; left = np.zeros(len(order))
    for name, d, col in carriers:
        v = np.array([d.get(k, 0.0) for k in order])
        ax.barh(y, v, left=left, color=col, height=0.62, label=name, edgecolor="white", lw=0.8); left += v
    for yi, k in zip(y, order):
        ax.text(s[k] + 120, yi, f"{s[k]:,.0f} ({s[k] / c['tfc'] * 100:.1f}%)", va="center", fontsize=6.7, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(order, fontsize=7.2); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 11_000); ax.xaxis.set_major_formatter(FMT); ax.set_xlabel("ktoe (NCV)"); ax.grid(axis="y", visible=False)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.27), fontsize=6.8)
    ax.set_title(f"TFC by sector and carrier ({c['tfc']:,.0f} ktoe)", loc="left"); panel(ax, "a")

    ax = fig.add_subplot(gs[1, 0])
    names = list(es.keys()); gwh = [es[k] / 0.086 for k in names]
    y = np.arange(len(names))[::-1]
    b = ax.barh(y, gwh, color=[SEC[k] for k in names], height=0.62)
    tot = sum(gwh)
    hbar_labels(ax, b, gwh, lambda v: f"{v:,.0f} ({v / tot * 100:.1f}%)")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=7); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 26_000); ax.set_xlabel("GWh"); ax.xaxis.set_major_formatter(FMT); ax.grid(axis="y", visible=False)
    ax.set_title("Electricity consumption by sector", loc="left"); panel(ax, "b")

    ax = fig.add_subplot(gs[1, 1])
    labs = ["Retail:\nroad & air", "Retail:\nother", "Residual:\nnon-energy", "Residual:\nLPG", "Residual:\nnaphtha\nenergy",
            "Aviation\nbunkers"]
    vals = [c["transport"], c["ind_retail"] + c["res_retail"], c["ne_oil"], c["lpg_res"] + c["lpg_ind"],
            c["naph_ind"] + c["res_rfo"], c["jet_intl"]]
    cols = [SEC["Transport"], C["products"], SEC["Non-energy use"], SEC["Residential"], SEC["Industrial"], MUTED]
    b = ax.bar(range(6), vals, color=cols, width=0.62)
    vbar_labels(ax, b, vals, lambda v: f"{v:,.0f}", size=6.0)
    ax.set_xticks(range(6)); ax.set_xticklabels(labs, fontsize=5.8); ax.set_ylabel("ktoe"); ax.set_ylim(0, 5_400)
    ax.yaxis.set_major_formatter(FMT); ax.grid(axis="x", visible=False)
    ax.set_title(f"Domestic products ({c['domestic_prod']:,.0f} ktoe)", loc="left"); panel(ax, "c")
    save(fig, "Fig07_sectoral")

# ===================================================================== Fig 8 electricity
def fig8():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw=dict(width_ratios=[0.8, 1.2, 1.15]))
    ax = axes[0]
    gen, cons, re = 50_973.5, 45_033.1, 4_509.0
    ax.bar(0, gen - re, color=C["gas"], width=0.6, label="Gas-fired")
    ax.bar(0, re, bottom=gen - re, color=C["re"], width=0.6, label="Solar & wind")
    ax.bar(1, cons, color=C["elec"], width=0.6); ax.bar(2, gen - cons, color=C["grey"], width=0.6)
    for x, v in [(0, gen), (1, cons), (2, gen - cons)]:
        ax.text(x, v + 700, f"{v:,.0f}", ha="center", fontsize=6.6, color=INK2)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Gener-\nation", "Consum-\nption", "Losses &\nown use"], fontsize=6.6)
    ax.set_ylabel("GWh"); ax.set_ylim(0, 72_000); ax.yaxis.set_major_formatter(FMT); ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", fontsize=6.2, handlelength=1)
    ax.set_title("Electricity balance", loc="left"); panel(ax, "a")

    ax = axes[1]
    pl = {"Ibri II Solar IPP": 1585.4, "Sembcorp–Jinko\nShine (PV)": 1420.6, "Wadi Noor Solar": 1375.5,
          "Dhofar I Wind IPP": 124.0, "OPWP purchases": 3.0, "Al Mazyonah": 0.5}
    names = list(pl); y = np.arange(len(names))[::-1]
    b = ax.barh(y, list(pl.values()), color=[C["re"]] * 3 + [C["gas"]] + [C["grey"]] * 2, height=0.62)
    hbar_labels(ax, b, list(pl.values()), lambda v: f"{v:,.1f} ({v / re * 100:.1f}%)", size=6.3)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=6.8); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 2_300); ax.set_xlabel("GWh"); ax.grid(axis="y", visible=False)
    ax.set_title("RE generation by plant, 2025", loc="left"); panel(ax, "b")

    ax = axes[2]
    yrs = [t["year"] for t in R["ts"]]; sh = [t["re_share"] for t in R["ts"]]
    ax.plot(yrs, sh, "-o", color=C["grey"], lw=1.4, ms=3.5, label="Ember / EI series")
    ax.plot(2025, c["re_share_gen"], "o", color=C["re"], ms=6, label="This study (plant data)")
    ax.plot([2025, 2030], [c["re_share_gen"], 30], "--", color=C["re"], lw=1.3, label="OPWP 30% path")
    ax.plot([2025, 2030], [c["re_share_gen"], 20], ":", color=C["gas"], lw=1.3, label="20% national target")
    ax.text(2025.2, c["re_share_gen"] - 2.6, f"{c['re_share_gen']:.2f}%", fontsize=6.6, color=INK2)
    ax.set_xlim(2014.5, 2030.8); ax.set_ylim(0, 33); ax.set_ylabel("Share of generation (%)")
    ax.legend(loc="upper left", fontsize=5.9, handlelength=1.6)
    ax.set_title("RE share 2015–2030", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.4)
    save(fig, "Fig08_electricity")


# ===================================================================== Fig 9 emissions
def fig9():
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.2), gridspec_kw=dict(width_ratios=[1.45, 0.75, 1.3]))
    ax = axes[0]
    cats = list(c["co2"].keys()); vals = list(c["co2"].values())
    short = ["1.A.1.a Grid electricity", "1.A.1.a Desal. & unattrib.", "1.A.1.b Refining", "1.A.1.c LNG plants",
             "1.A.1.c Upstream fuel", "1.A.2 Manufacturing", "1.A.3 Transport", "1.A.4 Residential"]
    cols = ["#6250d6", "#9c91e6", "#eda100", "#6250d6", "#a3a29b", "#2a78d6", "#eb6834", "#1baf7a"]
    y = np.arange(len(cats))[::-1]
    b = ax.barh(y, vals, color=cols, height=0.62)
    hbar_labels(ax, b, vals, lambda v: f"{v:.2f}", size=6.3)
    ax.set_yticks(y); ax.set_yticklabels(short, fontsize=6.6); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 36); ax.set_xlabel("MtCO₂"); ax.grid(axis="y", visible=False)
    mc = R["mc"]["co2_total"]
    ax.set_title(f"By IPCC category: {c['co2_total']:.1f} Mt\n(90% CI {mc['p5']:.1f}–{mc['p95']:.1f})", loc="left")
    panel(ax, "a")

    ax = axes[1]
    f = c["co2_fuel"]
    labs = ["Natural\ngas", "Petro-\nleum", "Coal"]
    v = [f["Natural gas"], f["Petroleum products"], f["Coal & lignite"]]
    b = ax.bar(labs, v, color=[C["gas"], C["products"], C["coal"]], width=0.6)
    for bb, vv in zip(b, v):
        ax.text(bb.get_x() + bb.get_width() / 2, vv + 1, f"{vv:.1f}\n({vv / c['co2_total'] * 100:.0f}%)",
                ha="center", fontsize=6.4, color=INK2)
    ax.set_ylim(0, 80); ax.set_ylabel("MtCO₂"); ax.grid(axis="x", visible=False); ax.tick_params(axis="x", labelsize=6.6)
    ax.set_title("By fuel", loc="left"); panel(ax, "b")

    ax = axes[2]
    eu = c["end_use"]
    names = ["Industrial", "Energy sector (own use, LNG, refining, desalination)", "Transport", "Residential",
             "Commercial", "Government", "Agriculture & other"]
    lbl = ["Industrial", "Energy sector*", "Transport", "Residential", "Commercial", "Government", "Agric. & other"]
    v = [eu[k] for k in names]
    y = np.arange(len(names))[::-1]
    b = ax.barh(y, v, color=["#2a78d6", "#a3a29b", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#8a8984"], height=0.62)
    hbar_labels(ax, b, v, lambda x: f"{x:.1f}", size=6.3)
    ax.set_yticks(y); ax.set_yticklabels(lbl, fontsize=6.8); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 40); ax.set_xlabel("MtCO₂"); ax.grid(axis="y", visible=False)
    ax.set_title("End-use attribution", loc="left"); panel(ax, "c")
    fig.tight_layout(w_pad=1.2)
    save(fig, "Fig09_emissions")


# ===================================================================== Fig 10 time series + LMDI
def fig10():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.2, 1]))
    ax = axes[0]
    ts = R["ts"]; yrs = np.array([t["year"] for t in ts])
    layers = [("Natural gas", [t["gas_co2"] for t in ts], C["gas"]), ("Oil", [t["oil_co2"] for t in ts], C["products"]),
              ("Flaring", [t["flaring_co2"] for t in ts], C["grey"]), ("Coal", [t["coal_co2"] for t in ts], C["coal"])]
    bottom = np.zeros(len(yrs))
    for name, v, col in layers:
        ax.bar(yrs, v, bottom=bottom, color=col, width=0.72, label=name, edgecolor="white", lw=0.5); bottom += np.array(v)
    ax.plot(2025, c["co2_total"], "D", color=INK, ms=5, label="This study 2025")
    mc = R["mc"]["co2_total"]
    ax.errorbar(2025, c["co2_total"], yerr=[[c["co2_total"] - mc["p5"]], [mc["p95"] - c["co2_total"]]], color=INK,
                capsize=2, lw=0.8)
    ax2 = ax.twinx(); ax2.grid(False); ax2.set_yticks([]); ax2.spines["right"].set_visible(False)
    ax.set_xlim(2014.3, 2025.7); ax.set_ylim(0, 100); ax.set_ylabel("MtCO₂ (fuel combustion + flaring)")
    ax.legend(ncol=3, fontsize=6.2, loc="upper left"); ax.set_xticks(range(2015, 2026, 2))
    ax.set_title("CO₂ by fuel, 2015–2024 (GCP) and 2025", loc="left"); panel(ax, "a")

    ax = axes[1]
    d = R["decomp"]; periods = list(d.keys())
    eff = [("pop", "Population", "#1baf7a"), ("aff", "GDP per capita", "#eda100"), ("ei", "Energy intensity", "#eb6834"),
           ("ci", "Carbon intensity", "#2a78d6")]
    x = np.arange(len(periods)); w = 0.18
    for i, (k, lab, col) in enumerate(eff):
        ax.bar(x + (i - 1.5) * w, [d[p][k] for p in periods], w, color=col, label=lab)
    ax.scatter(x, [d[p]["total"] for p in periods], marker="D", color=INK, s=18, zorder=3, label="Net change")
    for xi, p in zip(x, periods):
        ax.text(xi, d[p]["total"] + 1.2, f"{d[p]['total']:+.1f}", ha="center", fontsize=6.6, color=INK)
    ax.axhline(0, color=INK2, lw=0.6); ax.set_xticks(x); ax.set_xticklabels(periods, fontsize=7)
    ax.set_ylabel("ΔCO₂ (Mt)"); ax.legend(fontsize=6.0, loc="upper left", ncol=2); ax.set_ylim(-12, 26)
    ax.grid(axis="x", visible=False)
    ax.set_title("LMDI decomposition of ΔCO₂", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig10_trends_lmdi")


# ===================================================================== Fig 11 uncertainty
def fig11():
    fig = plt.figure(figsize=(7.4, 4.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15], hspace=0.62, wspace=0.42)
    for i, (k, lab, unit, cen) in enumerate([("tpes", "TPES", "ktoe", c["tpes"]), ("ssr", "Self-sufficiency", "%", c["ssr"]),
                                             ("co2_total", "CO₂ emissions", "MtCO₂", c["co2_total"])]):
        ax = fig.add_subplot(gs[0, i])
        v = MC[k]; m = R["mc"][k]
        ax.hist(v, bins=45, color="#9cc3ef", edgecolor="white", lw=0.3)
        for q, ls in [(m["p5"], ":"), (m["p95"], ":"), (cen, "-")]:
            ax.axvline(q, color=C["gas"] if ls == "-" else INK2, lw=1 if ls == "-" else 0.8, ls=ls)
        ax.set_yticks([]); ax.set_xlabel(unit, fontsize=7); ax.tick_params(axis="x", labelsize=6.5)
        if k == "tpes":
            ax.xaxis.set_major_formatter(FMT); ax.locator_params(axis="x", nbins=4)
        ax.set_title(f"{lab}\n{m['p5']:,.1f}–{m['p95']:,.1f}", loc="left", fontsize=8)
        ax.spines["left"].set_visible(False); ax.grid(False)
        panel(ax, "abc"[i])
    names = {"prod_factor_scale": "Product energy factors", "eta_ref": "Refinery efficiency",
             "f_duqm": "Duqm product factor", "eta_lng": "LNG plant efficiency", "chem_feed": "Chemical feedstock",
             "own_comb_share": "Oil-field gas combusted", "lng_fuel_comb": "LNG loss combusted",
             "ref_loss_comb": "Refinery loss combusted", "eta_pp": "Grid fleet efficiency",
             "eta_marg": "Marginal plant efficiency", "alpha_ne": "Non-energy share (naphtha)",
             "lpg_res_share": "LPG to households", "jet_retail_kbbl": "Jet fuel in retail",
             "jet_intl_share": "International jet share", "p_lng": "LNG price", "p_dom": "Domestic gas price",
             "c_liq": "Liquefaction cost"}
    for j, (k, lab) in enumerate([("ssr", "Self-sufficiency ratio"), ("co2_total", "CO₂ emissions")]):
        ax = fig.add_subplot(gs[1, j * 3 // 2: j * 3 // 2 + (2 if j == 0 else 1)] if False else gs[1, [slice(0, 2), slice(2, 3)][j]])
        sv = R["sens"][k]
        top = sorted(sv.items(), key=lambda t: -abs(t[1]))[:6][::-1]
        b = ax.barh(range(len(top)), [t[1] for t in top], color=[C["gas"] if t[1] > 0 else C["oil"] for t in top], height=0.6)
        hbar_labels(ax, b, [t[1] for t in top], lambda v: f"{v:+.2f}", size=6.2)
        ax.set_yticks(range(len(top))); ax.set_yticklabels([names[t[0]] for t in top], fontsize=6.6)
        ax.tick_params(axis="y", length=0); ax.axvline(0, color=INK2, lw=0.6); ax.set_xlim(-1.15, 1.15)
        ax.set_xlabel("Spearman rank correlation", fontsize=7); ax.grid(axis="y", visible=False)
        ax.set_title(f"Drivers of uncertainty: {lab}", loc="left", fontsize=8); panel(ax, "de"[j])
    save(fig, "Fig11_uncertainty")


# ===================================================================== Fig 12 dual dividend
def fig12():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1, 1.15]))
    ax = axes[0]
    gen = 50_973.5; sh = np.linspace(5, 50, 46)
    for eta, col, ls, lab in [(0.35, C["oil"], ":", "OCGT margin (η 0.35)"), (0.45, C["re"], "-", "Central (η 0.45)"),
                              (0.55, C["lng"], "--", "CCGT margin (η 0.55)")]:
        ef = 56.1 * 3.6 / eta / 1000
        ax.plot(sh, sh / 100 * gen * ef / 1000, ls, color=col, lw=1.6, label=lab)
    lo = sh / 100 * gen * 56.1 * 3.6 / 0.55 / 1e6; hi = sh / 100 * gen * 56.1 * 3.6 / 0.35 / 1e6
    ax.fill_between(sh, lo, hi, color=C["re"], alpha=0.10, lw=0)
    ax.plot(c["re_share_gen"], c["avoided"], "o", color=C["re"], ms=5)
    ax.annotate(f"2025: {c['avoided']:.2f} Mt", (c["re_share_gen"], c["avoided"]), xytext=(12, -22),
                textcoords="offset points", fontsize=6.6, color=INK2, arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED))
    ax.axvline(30, color=MUTED, lw=0.6, ls="--"); ax.text(30.6, 0.6, "OPWP\n2030", fontsize=6.2, color=MUTED)
    ax.set_xlabel("Renewable share of generation (%)"); ax.set_ylabel("Avoided CO₂ (Mt yr$^{-1}$)")
    ax.set_xlim(5, 50); ax.set_ylim(0, 15); ax.legend(fontsize=6.2, loc="upper left")
    ax.set_title("Avoided emissions", loc="left"); panel(ax, "a")

    ax = axes[1]
    shs = np.array([8.85, 15, 20, 30, 40, 50]); price = np.array([6, 8, 10, 12, 14])
    eta_l = c["eta_lng"]
    V = np.array([[s / 100 * gen * 3.6 / 0.45 / 41.868 * 39.683e3 / 0.9 * (p * eta_l - 1.0 - 3.0) / 1e9 for s in shs]
                  for p in price])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("g", ["#f1faf6", "#1baf7a", "#0b5a3d"])
    ax.imshow(np.clip(V, 0, None), cmap=cmap, aspect="auto", origin="lower")
    for i in range(len(price)):
        for j in range(len(shs)):
            ax.text(j, i, f"{V[i, j]:.2f}", ha="center", va="center", fontsize=6.4,
                    color="white" if V[i, j] > V.max() * 0.55 else INK)
    ax.set_xticks(range(len(shs))); ax.set_xticklabels([f"{s:g}%" for s in shs], fontsize=7)
    ax.set_yticks(range(len(price))); ax.set_yticklabels([f"${p}" for p in price], fontsize=7)
    ax.set_xlabel("Renewable share of generation"); ax.set_ylabel("LNG price (USD/MMBtu)")
    ax.grid(False); [sp.set_visible(False) for sp in ax.spines.values()]; ax.tick_params(length=0)
    ax.set_title("Rent preserved by freed gas (USD bn yr$^{-1}$)", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig13_dual_dividend")


# ===================================================================== Fig 13 political economy
def fig13():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax = axes[0]
    rf = c["rent_foregone"]; secs = list(rf.keys())
    vols = {"Power & water plants": c["gas_power"], "Industry (fuel & feedstock)": c["gas_industry"],
            "Upstream own use": c["own"]}
    prices = [6, 10, 14]; w = 0.25; x = np.arange(len(secs))
    for i, (p, col) in enumerate(zip(prices, ["#9cc3ef", C["gas"], "#16508f"])):
        m = p * c["eta_lng"] - 1.0 - 3.0
        v = [vols[s] * 39.683e3 / 0.9 * m / 1e9 for s in secs]
        b = ax.bar(x + (i - 1) * w, v, w, color=col, label=f"LNG ${p}/MMBtu")
        vbar_labels(ax, b, v, lambda t: f"{t:.1f}", size=5.9)
    ax.axhline(0.520 * 2.6008, color=C["red"], lw=0.9, ls="--")
    ax.text(-0.45, 0.520 * 2.6008 + 0.1, "Explicit electricity subsidy (2025 budget)", fontsize=6.0, color=C["red"], ha="left")
    ax.set_xticks(x); ax.set_xticklabels([t.replace(" (", "\n(") for t in secs], fontsize=6.8); ax.set_ylabel("USD bn yr$^{-1}$"); ax.set_ylim(0, 5.6)
    ax.legend(fontsize=6.2, loc="upper right"); ax.grid(axis="x", visible=False)
    ax.set_title("Implicit gas rent transferred, 2025", loc="left"); panel(ax, "a")

    ax = axes[1]
    gen = 50_973.5
    growth = np.array([0.0, 0.02, 0.03, 0.04, 0.05])
    base = 4_509 / (8.76 * 0.30) / 1000
    for cf, col, ls in [(0.25, C["oil"], ":"), (0.30, C["re"], "-"), (0.35, C["gas"], "--")]:
        add = (0.30 * gen * (1 + growth) ** 5 - 4_509) / (8.76 * cf) / 1000
        ax.plot(growth * 100, add, ls, marker="o", ms=3.5, color=col, lw=1.5, label=f"Grid 30%: CF {cf:.2f}")
    ax.axhspan(16, 20, color=C["lng"], alpha=0.15, lw=0)
    ax.text(0.1, 18, "Hydrogen 2030 (1.0–1.25 Mt): 16–20 GW", fontsize=6.4, color=C["lng"], va="center")
    ax.axhline(base, color=MUTED, lw=0.7, ls="--"); ax.text(4.9, base + 0.4, f"2025 fleet ≈ {base:.1f} GW", fontsize=6.2,
                                                             color=MUTED, ha="right")
    ax.set_xlabel("Electricity demand growth (% yr$^{-1}$)"); ax.set_ylabel("Additional VRE by 2030 (GW)")
    ax.set_ylim(0, 22); ax.legend(fontsize=6.0, loc="center left")
    ax.set_title("Capacity required by 2030", loc="left"); panel(ax, "b")
    fig.tight_layout(w_pad=2)
    save(fig, "Fig12_rents_capacity")


# ===================================================================== Fig 14 policy
def fig14():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.04, 0.86, 0.92, 0.11, "Evidence layer: reconciled energy accounts with closure diagnostics and uncertainty\n"
        "TPES · TFC by sector × carrier · CO₂ by IPCC category · RE share · gas freed · rent incidence",
        "#2a78d6", ec="#2a78d6", size=7.4, bold=True, tc="white")
    pillars = [("Supply-side decarbonisation", "#e8f6f0",
                "• PV & wind towards 30% by 2030\n• Storage: PHES / CAES\n• Additional VRE for hydrogen\n• Value freed gas in procurement"),
               ("Demand-side efficiency", "#fdf3e1",
                "• Cost-reflective tariffs, targeted\n   household support\n• Building codes; HVAC monitoring\n• Industrial TFEE benchmarking"),
               ("Statistical & fiscal institutions", "#efedfb",
                "• Metered refinery intake & reinjection\n• Power/water fuel split\n• Annual balance + NDC reporting\n• Domestic gas price path")]
    for x, (h, fc, t) in zip([0.02, 0.35, 0.68], pillars):
        box(ax, x, 0.62, 0.30, 0.075, h, fc, size=7.8, bold=True)
        box(ax, x, 0.30, 0.30, 0.30, t, fc, size=7.0)
        arrow(ax, 0.5, 0.86, x + 0.15, 0.70); arrow(ax, x + 0.15, 0.30, 0.5, 0.17)
    box(ax, 0.12, 0.04, 0.76, 0.12, "Outcomes: CO₂ abatement + preserved export rent (dual dividend) · lower implicit\n"
        "rent transfers · verifiable decoupling of growth from domestic fossil use", "#f3f2ef", size=7.4, bold=True)
    save(fig, "Fig14_policy")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13, fig14):
        f()
    print("figures written:", sorted(os.listdir(OUT)))
