"""
Matrix-based Well-to-Wheel LCA of Jordan's 2022 transport fleet.

A compact, transparent re-implementation (NumPy) of the computational
structure behind the SimaPro study "Uncovering the 'Grid Penalty' and
Pollution Swaps in Transport Decarbonization" (Ghawanmeh, 2026):

    s = A^-1 f          (Eq. 1 - Life Cycle Inventory)
    g = B s             (elementary flows)
    h = Q g             (Eq. 2 - impact assessment)

The model is calibrated to the published SimaPro baseline (Figure 3) and
scenario totals (Figure 4). Scenario S1 is NOT calibrated: it is predicted
from the EV energy ratio fitted on S4, and serves as an internal check.

Run:  python lca_matrix_model.py      -> writes output/*.png and results.json
"""

import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(2022)
N_MC = 10_000

# --------------------------------------------------------------------------
# 1. Published SimaPro results used as calibration targets / reference data
# --------------------------------------------------------------------------
BASELINE_GWP_GG = {  # Figure 3, Gg CO2-eq
    "Gasoline vehicles": 1270.0,
    "Diesel vehicles": 1080.0,
    "Aviation": 257.0,
    "Hybrid vehicles": 183.0,
    "Other fuels": 2.85,
    "Electric vehicles": 0.0815,
}
SIMAPRO_GWP_GG = {"Baseline": 2800.0, "S1": 2550.0, "S2": 2530.0, "S3": 2490.0, "S4": 448.0}
SIMAPRO_DALY = {"Baseline": 2790.0, "S1": 2540.0, "S2": 2520.0, "S3": 2760.0, "S4": 449.0}
SCENARIO_NAMES = {
    "Baseline": "Baseline 2022",
    "S1": "S1  20% EVs",
    "S2": "S2  Diesel buses",
    "S3": "S3  Euro 6",
    "S4": "S4  Full electrification",
}

# --------------------------------------------------------------------------
# 2. Emission factors (t CO2-eq per TJ fuel, or per GWh electricity)
#    TTW: IPCC 2006 defaults incl. CH4/N2O; WTT: ~20% upstream share
# --------------------------------------------------------------------------
TTW = {"gasoline": 70.0, "diesel": 75.0, "jet": 72.0}
WTT = {"gasoline": 15.0, "diesel": 15.0, "jet": 13.0, "premium": 17.0}
GRID_G_PER_KWH = 391.0  # Low Carbon Power (2022), market for electricity [JO]

# --------------------------------------------------------------------------
# 3. Technology matrix
# --------------------------------------------------------------------------
PRODUCTS = [
    "Gasoline supply [TJ]",
    "Diesel supply [TJ]",
    "Jet fuel supply [TJ]",
    "Premium low-S gasoline [TJ]",
    "Electricity, JO grid [GWh]",
    "Gasoline car fleet [yr]",
    "Diesel vehicle fleet [yr]",
    "Aviation [yr]",
    "Hybrid fleet [yr]",
    "Other-fuel fleet [yr]",
    "EV fleet [yr]",
    "Diesel bus service [yr]",
]
SHORT = ["Gasoline", "Diesel", "Jet fuel", "Premium", "Electricity",
         "Gasoline cars", "Diesel veh.", "Aviation", "Hybrids", "Other fuels", "EVs", "Diesel buses"]
G, D, J, P, E, CAR, DSL, AVI, HYB, OTH, EV, BUS = range(len(PRODUCTS))
FLEETS = [CAR, DSL, AVI, HYB, OTH, EV, BUS]

# Baseline fuel demand implied by the Figure 3 totals (TJ or GWh per year)
FUEL_CAR = BASELINE_GWP_GG["Gasoline vehicles"] * 1e3 / (TTW["gasoline"] + WTT["gasoline"])
FUEL_DSL = BASELINE_GWP_GG["Diesel vehicles"] * 1e3 / (TTW["diesel"] + WTT["diesel"])
FUEL_AVI = BASELINE_GWP_GG["Aviation"] * 1e3 / (TTW["jet"] + WTT["jet"])
FUEL_HYB = BASELINE_GWP_GG["Hybrid vehicles"] * 1e3 / (TTW["gasoline"] + WTT["gasoline"])
OTHER_DIRECT_T = BASELINE_GWP_GG["Other fuels"] * 1e3
ELEC_EV0 = BASELINE_GWP_GG["Electric vehicles"] * 1e3 / GRID_G_PER_KWH
ROAD_FUEL_TJ = FUEL_CAR + FUEL_DSL + FUEL_HYB


def build_system(p):
    """Return (A, B, f) for a parameter dict p.

    A is square: column j = process j, row i = product i.
    Diagonal = 1 unit of output; negative entries = inputs.
    B rows: [fossil CO2-eq at tailpipe (TTW), CO2-eq upstream (WTT + power plants)].
    """
    n = len(PRODUCTS)
    A = np.eye(n)
    B = np.zeros((2, n))

    # supply processes (upstream burden only)
    B[1, G] = WTT["gasoline"]
    B[1, D] = WTT["diesel"]
    B[1, J] = WTT["jet"]
    B[1, P] = WTT["premium"]
    B[1, E] = p["grid"]  # t CO2-eq per GWh == g/kWh

    eff = p["euro6_gain"]  # fractional fuel saving from Euro 6 engines
    cong = p["congestion"]  # real-world driving-cycle multiplier

    # gasoline car fleet: regular + premium gasoline
    car_fuel = FUEL_CAR * (1 - eff) * cong["car"]
    A[G, CAR] = -car_fuel * (1 - p["premium_share"])
    A[P, CAR] = -car_fuel * p["premium_share"]
    B[0, CAR] = car_fuel * TTW["gasoline"]

    dsl_fuel = FUEL_DSL * (1 - eff) * cong["diesel"]
    A[D, DSL] = -dsl_fuel
    B[0, DSL] = dsl_fuel * TTW["diesel"]

    A[J, AVI] = -FUEL_AVI
    B[0, AVI] = FUEL_AVI * TTW["jet"]

    hyb_fuel = FUEL_HYB * (1 - eff) * cong["car"]
    A[G, HYB] = -hyb_fuel * (1 - p["premium_share"])
    A[P, HYB] = -hyb_fuel * p["premium_share"]
    B[0, HYB] = hyb_fuel * TTW["gasoline"]

    B[0, OTH] = OTHER_DIRECT_T

    # EV fleet: electricity scales with the fossil energy it displaces
    A[E, EV] = -p["ev_elec_gwh"] * p["hvac"]

    # diesel bus service
    bus_fuel = p["bus_tj"] * p["bus_factor"]
    A[D, BUS] = -bus_fuel
    B[0, BUS] = bus_fuel * TTW["diesel"]
    return A, B


def scenario_params(name, ev_ratio, bus_ratio, euro6_gain, overrides=None):
    """Final-demand vector f and process parameters for each scenario."""
    p = dict(grid=GRID_G_PER_KWH, euro6_gain=0.0, premium_share=0.0,
             congestion={"car": 1.0, "diesel": 1.0}, hvac=1.0, bus_factor=1.0,
             ev_elec_gwh=ELEC_EV0, bus_tj=0.0)
    f = np.zeros(len(PRODUCTS))
    f[[CAR, DSL, AVI, HYB, OTH, EV]] = 1.0
    if name == "S1":
        f[CAR] = 0.8
        displaced = 0.2 * FUEL_CAR
        p["ev_elec_gwh"] = ELEC_EV0 + displaced * ev_ratio / 3.6
    elif name == "S2":
        f[CAR] = 0.7
        f[BUS] = 1.0
        p["bus_tj"] = 0.3 * FUEL_CAR * bus_ratio
    elif name == "S3":
        p["euro6_gain"] = euro6_gain
        p["premium_share"] = 0.5
    elif name == "S4":
        f[[CAR, DSL, HYB, OTH]] = 0.0
        p["ev_elec_gwh"] = ELEC_EV0 + ROAD_FUEL_TJ * ev_ratio / 3.6
    if overrides:
        p.update(overrides)
    return f, p


def solve(f, p):
    A, B = build_system(p)
    s = np.linalg.solve(A, f)  # Eq. (1)
    g = B @ s  # elementary flows, t CO2-eq
    return s, g, A, B


def gwp_gg(f, p):
    _, g, _, _ = solve(f, p)
    return g.sum() / 1e3


# --------------------------------------------------------------------------
# 4. Calibration (one parameter per scenario: S2, S3, S4). S1 is predicted.
# --------------------------------------------------------------------------
def calibrate():
    # S4: EV electricity per TJ of displaced road fuel
    rest = SIMAPRO_GWP_GG["S4"] - BASELINE_GWP_GG["Aviation"] - BASELINE_GWP_GG["Electric vehicles"]
    ev_ratio = rest * 1e3 / GRID_G_PER_KWH * 3.6 / ROAD_FUEL_TJ
    # S2: bus diesel per TJ of car gasoline shifted
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        f, p = scenario_params("S2", ev_ratio, mid, 0)
        lo, hi = (mid, hi) if gwp_gg(f, p) < SIMAPRO_GWP_GG["S2"] else (lo, mid)
    bus_ratio = (lo + hi) / 2
    # S3: Euro 6 fuel saving
    lo, hi = 0.0, 0.5
    for _ in range(60):
        mid = (lo + hi) / 2
        f, p = scenario_params("S3", ev_ratio, bus_ratio, mid)
        lo, hi = (lo, mid) if gwp_gg(f, p) < SIMAPRO_GWP_GG["S3"] else (mid, hi)
    euro6 = (lo + hi) / 2
    return ev_ratio, bus_ratio, euro6


EV_RATIO, BUS_RATIO, EURO6 = calibrate()
EV_RATIO_PHYSICS = 0.30  # BEV ~0.18 kWh/km vs ICE ~0.6 kWh/km (fuel energy)


def run_deterministic():
    rows = {}
    for sc in SIMAPRO_GWP_GG:
        f, p = scenario_params(sc, EV_RATIO, BUS_RATIO, EURO6)
        s, g, A, B = solve(f, p)
        per_proc = (B * s).sum(axis=0) / 1e3  # Gg by process (direct)
        rows[sc] = {
            "model_gwp_gg": g.sum() / 1e3,
            "tailpipe_gg": g[0] / 1e3,
            "upstream_gg": g[1] / 1e3,
            "grid_gg": per_proc[E],
            "simapro_gwp_gg": SIMAPRO_GWP_GG[sc],
            "simapro_daly": SIMAPRO_DALY[sc],
            "electricity_gwh": s[E],
        }
        fp, pp = scenario_params(sc, EV_RATIO_PHYSICS, BUS_RATIO, EURO6)
        rows[sc]["physics_gwp_gg"] = gwp_gg(fp, pp)
        rows[sc]["physics_electricity_gwh"] = solve(fp, pp)[0][E]
    return rows


def baseline_breakdown():
    """WTW contribution of each fleet split into tailpipe vs upstream (via s = A^-1 f per fleet)."""
    f0, p = scenario_params("Baseline", EV_RATIO, BUS_RATIO, EURO6)
    A, B = build_system(p)
    Ainv = np.linalg.inv(A)
    out = {}
    for j, label in zip([CAR, DSL, AVI, HYB, OTH, EV],
                        ["Gasoline vehicles", "Diesel vehicles", "Aviation",
                         "Hybrid vehicles", "Other fuels", "Electric vehicles"]):
        fj = np.zeros(len(PRODUCTS))
        fj[j] = 1.0
        s = Ainv @ fj
        g = B @ s
        out[label] = {"tailpipe": g[0] / 1e3, "upstream": g[1] / 1e3}
    return out, A, Ainv


# --------------------------------------------------------------------------
# 5. Monte Carlo (10,000 iterations)
# --------------------------------------------------------------------------
def tri(a, m, b, n=N_MC):
    return RNG.triangular(a, m, b, n)


def mc_micro_gwp():
    """Per-km Well-to-Wheel CO2-eq (g/km or g/pkm)."""
    grid = tri(370, 391, 450)
    ev_kwh = tri(0.15, 0.17, 0.20) * tri(1.0, 1.2, 1.5)  # HVAC +20-50%
    return {
        "Gasoline car": RNG.normal(215, 25, N_MC),
        "Euro 6 gasoline car": RNG.normal(200, 22, N_MC),
        "Modern diesel car": RNG.normal(190, 20, N_MC),
        "Domestic flight (per pkm)": RNG.normal(190, 30, N_MC),
        "Battery EV (JO grid)": grid * ev_kwh,
    }


# Primary PM2.5 emission factors (g/vkm), illustrative, calibrated so that the
# conventional diesel bus breaks even with a car at ~27 riders (paper: 25-30).
PM_CAR_G_KM, CAR_OCC = 0.012, 1.5
PM_BUS = {"Conventional diesel bus": (0.18, 0.22, 0.26),
          "Euro VI diesel bus": (0.05, 0.07, 0.10),
          "Electric bus": (0.010, 0.015, 0.020)}


def mc_pollution_swap():
    occ = tri(10, 30, 60)
    car_pkm = PM_CAR_G_KM / CAR_OCC
    res = {k: tri(*v) / occ for k, v in PM_BUS.items()}
    thresholds = {k: v[1] / car_pkm for k, v in PM_BUS.items()}
    return occ, res, car_pkm, thresholds


def mc_macro():
    """Sample uncertain parameters and re-solve the matrix for every scenario."""
    out_gwp = {sc: np.empty(N_MC) for sc in SIMAPRO_GWP_GG}
    out_daly = {sc: np.empty(N_MC) for sc in SIMAPRO_GWP_GG}
    grid = tri(370, 391, 450)
    hvac = tri(1.0, 1.15, 1.35)
    c_car = RNG.normal(1.0, 0.04, N_MC)
    c_dsl = RNG.normal(1.0, 0.04, N_MC)
    bus_f = tri(0.9, 1.0, 1.25)
    e6 = EURO6 * tri(0.5, 1.0, 1.1)
    health_noise = {"Baseline": tri(0.95, 1.0, 1.06), "S1": tri(0.95, 1.0, 1.08),
                    "S2": tri(0.95, 1.0, 1.30), "S3": tri(0.95, 1.0, 1.06),
                    "S4": tri(0.85, 1.0, 1.15)}
    det = {sc: gwp_gg(*scenario_params(sc, EV_RATIO, BUS_RATIO, EURO6)) for sc in SIMAPRO_GWP_GG}
    for i in range(N_MC):
        ov = dict(grid=grid[i], hvac=hvac[i], bus_factor=bus_f[i],
                  congestion={"car": c_car[i], "diesel": c_dsl[i]})
        for sc in SIMAPRO_GWP_GG:
            f, p = scenario_params(sc, EV_RATIO, BUS_RATIO, EURO6, ov)
            if sc == "S3":
                p["euro6_gain"] = e6[i]
            v = gwp_gg(f, p)
            out_gwp[sc][i] = v
            out_daly[sc][i] = SIMAPRO_DALY[sc] * (v / det[sc]) * health_noise[sc][i]
    return out_gwp, out_daly


def grid_sweep():
    xs = np.linspace(0, 600, 121)
    res = {"x": xs}
    for label, ratio in [("calibrated", EV_RATIO), ("physics", EV_RATIO_PHYSICS)]:
        for sc in ["S1", "S4"]:
            ys = []
            for x in xs:
                f, p = scenario_params(sc, ratio, BUS_RATIO, EURO6, {"grid": x})
                ys.append(gwp_gg(f, p))
            res[f"{sc}_{label}"] = np.array(ys)
    return res


# --------------------------------------------------------------------------
# 6. Figures
# --------------------------------------------------------------------------
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.titleweight": "bold", "axes.titlesize": 12, "axes.titlecolor": INK,
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def fig_baseline(bd):
    labels = list(bd)[::-1]
    tp = np.array([bd[k]["tailpipe"] for k in labels])
    up = np.array([bd[k]["upstream"] for k in labels])
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.barh(labels, tp, color=C[0], height=0.6, label="Tailpipe (Tank-to-Wheel)", edgecolor="white", linewidth=1)
    ax.barh(labels, up, left=tp, color=C[1], height=0.6, label="Hidden upstream (Well-to-Tank / power plants)",
            edgecolor="white", linewidth=1)
    for y, (a, b) in enumerate(zip(tp, up)):
        ax.text(a + b + 15, y, f"{a + b:,.0f} Gg" if a + b >= 1 else f"{a + b:.2f} Gg", va="center", color=INK2,
                fontsize=9)
    ax.set_xlabel("Gg CO$_2$-eq per year")
    ax.set_xlim(0, 1500)
    ax.grid(axis="y", visible=False)
    ax.set_title("What the tailpipe hides: Jordan's fleet in 2022 (2,800 Gg CO$_2$-eq)", loc="left")
    ax.legend(loc="lower right", fontsize=8.5)
    fig.savefig(OUT / "fig1_baseline_breakdown.png")
    plt.close(fig)


def fig_scenarios(rows):
    scs = list(rows)
    x = np.arange(len(scs))
    model = [rows[s]["model_gwp_gg"] for s in scs]
    grid_part = [rows[s]["grid_gg"] for s in scs]
    fossil = [m - g for m, g in zip(model, grid_part)]
    sim = [rows[s]["simapro_gwp_gg"] for s in scs]
    fig, ax = plt.subplots(figsize=(7.5, 3.9))
    ax.bar(x, fossil, 0.55, color=C[0], label="Fuel chain (tailpipe + refinery + shipping)", edgecolor="white")
    ax.bar(x, grid_part, 0.55, bottom=fossil, color=C[3], label="Grid penalty (EV charging electricity)",
           edgecolor="white")
    ax.scatter(x, sim, marker="D", s=46, color=INK, zorder=5, label="SimaPro result (paper)")
    ax.axhline(2400, color=C[7], lw=1.5, ls="--", label="Incremental-trap floor ≈ 2,400 Gg")
    for xi, m in zip(x, model):
        ax.text(xi, m + 120, f"{m:,.0f}", ha="center", color=INK, fontsize=9, fontweight="bold")
    ax.set_xticks(x, [SCENARIO_NAMES[s].replace("  ", "\n") for s in scs])
    ax.set_ylabel("Gg CO$_2$-eq per year")
    ax.set_ylim(0, 3300)
    ax.grid(axis="x", visible=False)
    ax.set_title("Four roads forward: only one leaves the trap", loc="left")
    ax.legend(loc="center right", fontsize=8, ncol=1, bbox_to_anchor=(1.0, 0.45))
    fig.savefig(OUT / "fig2_scenarios.png")
    plt.close(fig)


def fig_micro(micro):
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    bins = np.linspace(0, 330, 120)
    order = ["Battery EV (JO grid)", "Modern diesel car", "Domestic flight (per pkm)",
             "Euro 6 gasoline car", "Gasoline car"]
    cols = [C[2], C[6], C[4], C[3], C[1]]
    for k, c in zip(order, cols):
        h, e = np.histogram(micro[k], bins=bins, density=True)
        mid = (e[:-1] + e[1:]) / 2
        ax.plot(mid, h, color=c, lw=2, label=f"{k}  (median {np.median(micro[k]):.0f})")
        ax.fill_between(mid, h, color=c, alpha=0.12)
    ax.set_xlabel("Well-to-Wheel g CO$_2$-eq per vehicle-km (flight: per passenger-km)")
    ax.set_ylabel("Probability density")
    ax.set_title("The grid penalty is real — but the EV still wins (10,000 runs)", loc="left")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_yticks([])
    fig.savefig(OUT / "fig3_micro_density.png")
    plt.close(fig)


def fig_swap(occ, res, car_pkm, thr):
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    idx = RNG.choice(N_MC, 1500, replace=False)
    for (k, v), c in zip(res.items(), [C[7], C[3], C[2]]):
        ax.scatter(occ[idx], v[idx] * 1000, s=8, color=c, alpha=0.45, edgecolors="none",
                   label=f"{k} (break-even ≈ {thr[k]:.0f} riders)")
    ax.axhline(car_pkm * 1000, color=INK, ls="--", lw=1.5)
    ax.text(59, car_pkm * 1000 + 0.4, "Private gasoline car (1.5 occupants)", ha="right", fontsize=8.5, color=INK)
    ax.axvspan(10, thr["Conventional diesel bus"], color=C[7], alpha=0.06)
    ax.text(11, 23, "Pollution-swap zone:\nthe bus is dirtier per\npassenger than the car",
            fontsize=8.5, color=C[7], va="top")
    ax.set_xlabel("Passengers on board")
    ax.set_ylabel("Local PM$_{2.5}$, mg per passenger-km")
    ax.set_ylim(0, 25)
    ax.set_xlim(10, 60)
    ax.set_title("A half-empty diesel bus can harm the street it was meant to heal", loc="left")
    ax.legend(fontsize=8, loc="upper right", markerscale=2.5)
    fig.savefig(OUT / "fig4_pollution_swap.png")
    plt.close(fig)


def fig_macro(mg, md):
    scs = list(mg)
    labels = ["Baseline", "S1\n20% EVs", "S2\nBuses", "S3\nEuro 6", "S4\nFull EV"]
    cols = [MUTED, C[0], C[1], C[3], C[2]]
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.8))
    for ax, data, ttl, yl in [(axes[0], mg, "Climate: total GWP", "Gg CO$_2$-eq"),
                              (axes[1], md, "Health: total damage", "DALYs (healthy life-years lost)")]:
        bp = ax.boxplot([data[s] for s in scs], patch_artist=True, widths=0.55, showfliers=False,
                        medianprops=dict(color=INK, lw=1.5))
        for patch, c in zip(bp["boxes"], cols):
            patch.set_facecolor(c)
            patch.set_alpha(0.75)
            patch.set_edgecolor(INK2)
        ax.set_xticks(range(1, 6), labels, fontsize=8.5)
        ax.set_ylim(0, None)
        ax.set_title(ttl, loc="left", fontsize=11)
        ax.set_ylabel(yl)
        ax.grid(axis="x", visible=False)
    axes[0].axhline(2400, color=C[7], ls="--", lw=1.2)
    fig.suptitle("The incremental trap, 10,000 times over", x=0.01, ha="left", fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "fig5_macro_boxplots.png")
    plt.close(fig)


def fig_sweep(sw):
    x = sw["x"]
    fig, ax = plt.subplots(figsize=(7.5, 3.9))
    ax.plot(x, sw["S1_calibrated"], color=C[0], lw=2, label="S1  20% EVs")
    ax.plot(x, sw["S4_calibrated"], color=C[2], lw=2.4, label="S4  Full electrification (paper calibration)")
    ax.plot(x, sw["S4_physics"], color=C[2], lw=2, ls=":", label="S4  Full electrification (strict physics check)")
    ax.axhline(2800, color=MUTED, lw=1)
    ax.text(600, 2830, "Baseline 2022", ha="right", fontsize=8.5, color=INK2)
    ax.axhline(BASELINE_GWP_GG["Aviation"], color=MUTED, lw=1, ls="--")
    ax.text(600, 290, "Floor: aviation (not electrified)", ha="right", fontsize=8.5, color=INK2)
    ax.axvline(GRID_G_PER_KWH, color=C[7], lw=1.2)
    ax.text(GRID_G_PER_KWH + 6, 2200, "Jordan today\n391 g/kWh", fontsize=8.5, color=C[7])
    ax.axvspan(0, 50, color=C[2], alpha=0.10)
    ax.text(4, 800, "Solar & wind\ngrid", fontsize=8.5, color=C[5])
    ax.set_xlabel("Carbon intensity of the electricity grid (g CO$_2$-eq/kWh)")
    ax.set_ylabel("Sector GWP, Gg CO$_2$-eq")
    ax.set_ylim(0, 3100)
    ax.set_xlim(0, 600)
    ax.set_title("The leapfrog: clean the grid, and every EV gets cleaner with it", loc="left")
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0.10, 0.68))
    fig.savefig(OUT / "fig6_grid_sweep.png")
    plt.close(fig)


# --------------------------------------------------------------------------
def main():
    rows = run_deterministic()
    bd, A, Ainv = baseline_breakdown()
    micro = mc_micro_gwp()
    occ, swap, car_pkm, thr = mc_pollution_swap()
    mg, md = mc_macro()
    sw = grid_sweep()

    fig_baseline(bd)
    fig_scenarios(rows)
    fig_micro(micro)
    fig_swap(occ, swap, car_pkm, thr)
    fig_macro(mg, md)
    fig_sweep(sw)

    q = lambda a: [float(np.percentile(a, v)) for v in (2.5, 25, 50, 75, 97.5)]
    sweep_at = lambda key, g: float(np.interp(g, sw["x"], sw[key]))
    results = {
        "calibration": {"ev_ratio": EV_RATIO, "bus_ratio": BUS_RATIO, "euro6_gain": EURO6,
                        "ev_ratio_physics": EV_RATIO_PHYSICS},
        "deterministic": rows,
        "baseline_breakdown": bd,
        "A_baseline": A.round(4).tolist(),
        "products": PRODUCTS,
        "short": SHORT,
        "micro_medians": {k: float(np.median(v)) for k, v in micro.items()},
        "micro_p_ev_below_all": float(np.mean(micro["Battery EV (JO grid)"] < np.min(
            np.vstack([v for k, v in micro.items() if "EV" not in k]), axis=0))),
        "swap_thresholds": thr,
        "car_pm_mg_pkm": car_pkm * 1000,
        "p_bus_dirtier_than_car": float(np.mean(swap["Conventional diesel bus"] > car_pkm)),
        "macro_gwp_q": {s: q(v) for s, v in mg.items()},
        "macro_daly_q": {s: q(v) for s, v in md.items()},
        "p_below_2400": {s: float(np.mean(v < 2400)) for s, v in mg.items()},
        "p_s4_below_500": float(np.mean(mg["S4"] < 500)),
        "sweep": {f"{k}@{g}": sweep_at(k, g) for k in ["S1_calibrated", "S4_calibrated", "S4_physics", "S1_physics"]
                  for g in (0, 30, 100, 200, 391)},
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({k: results[k] for k in
                      ["calibration", "micro_medians", "swap_thresholds", "p_bus_dirtier_than_car",
                       "p_below_2400", "p_s4_below_500", "macro_gwp_q", "macro_daly_q", "sweep",
                       "micro_p_ev_below_all"]}, indent=1))
    for s, r in rows.items():
        print(s, {k: round(v, 1) for k, v in r.items()})


if __name__ == "__main__":
    main()
