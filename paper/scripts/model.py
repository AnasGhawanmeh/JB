"""Reconciled IRES energy balance, CO2 inventory, Monte Carlo uncertainty and LMDI
decomposition for Oman. Single source of every number used in figures and text.

Run:  python model.py      -> writes ../data/results.json and ../data/*.csv
"""
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)

TOE_GJ = 41.868
BBL_M3 = 0.158987

# ------------------------------------------------------------------ inputs
# Physical activity data, 2025 (national statistics as documented in the paper)
OBS = dict(
    crude_prod_kbbl=365_754.4, crude_exp_kbbl=307_960.9, crude_imp_kbbl=71_094.8,
    ref_out_kbbl=210_833.1,
    gas_mmscf=2_018_799.2, gas_assoc_mmscf=454_706.5,
    lng_feed_mmscf=599_187.0, lng_exp_mt=11.3,
    gas_power_ktoe=13_974.0, gas_ind_ktoe=10_331.0, gas_oilfield_ktoe=11_880.0,
    gen_gwh=50_973.5, cons_gwh=45_033.1, re_gwh=4_509.0, re_2024_share=4.89,
    coal_imp_t=246_603.5, lignite_imp_t=18_153.2, coal_exp_t=5_143.9,
    bunker_ktoe=453.8,                         # marine bunkers (port records, energy units)
    prod_exp_kbbl=131_090.0,                   # refined product exports
    retail_transport_kbbl=40_642.1, retail_ind_kbbl=2_253.8, retail_res_kbbl=804.0,
    gdp_ro_m=40_130.0, pop=5_359_557,
)
ELEC_SEC_GWH = {"Residential": 18_624.9, "Commercial": 12_161.8, "Industrial": 8_136.6,
                "Government": 4_538.7, "Agriculture & other": 1_571.1}
RE_PLANTS = {"Ibri II Solar IPP": 1_585.4, "Sembcorp–Jinko Shine (PV)": 1_420.6, "Wadi Noor Solar": 1_375.5,
             "Dhofar I Wind IPP": 124.0, "OPWP purchases": 3.0, "Al Mazyonah": 0.5}
SLATE_KBBL = {"Diesel / gas oil": 35_254, "Naphtha / other": 28_111, "Gasoline 91": 16_540,
              "Gasoline 95": 14_887, "Jet / kerosene": 11_712, "LPG": 8_112, "Fuel oil": 524}

# IPCC (2006) NCV (GJ/t) and typical densities (t/m3)
NCV = {"gasoline": 44.3, "jet": 44.1, "diesel": 43.0, "lpg": 47.3, "rfo": 40.4, "naphtha": 44.5}
RHO = {"gasoline": 0.745, "jet": 0.800, "diesel": 0.845, "lpg": 0.540, "rfo": 0.960, "naphtha": 0.700}
# IPCC (2006) default CO2 factors, t CO2 per toe (NCV basis)
EF = {"gasoline": 2.9015, "jet": 2.9936, "diesel": 3.1024, "lpg": 2.6419, "rfo": 3.2406,
      "naphtha": 3.0689, "gas": 2.3488, "coal": 4.1156, "lignite": 4.2287, "refgas": 2.4116}
SLATE_KIND = {"Diesel / gas oil": "diesel", "Naphtha / other": "naphtha", "Gasoline 91": "gasoline",
              "Gasoline 95": "gasoline", "Jet / kerosene": "jet", "LPG": "lpg", "Fuel oil": "rfo"}

F_CRUDE = 0.136                 # ktoe/kbbl, national crude factor
F_GAS = 0.02549                 # ktoe/MMscf
F_ELEC = 0.086                  # ktoe/GWh
F_COAL = 0.00065                # ktoe/t
LNG_TOE_T = 49.3 / TOE_GJ       # 1.177 toe/t (LNG NCV ~49.3 GJ/t)
MMBTU_PER_TOE = 39.683
USD_PER_RO = 2.6008
SCF_PER_MMSCF_M3 = 28_316.8     # m3 per MMscf


def toe_per_bbl(kind):
    return RHO[kind] * BBL_M3 * NCV[kind] / TOE_GJ


F_PROD = {k: toe_per_bbl(v) for k, v in SLATE_KIND.items()}            # ktoe/kbbl
SLATE_KTOE = {k: SLATE_KBBL[k] * F_PROD[k] for k in SLATE_KBBL}
F_SLATE = sum(SLATE_KTOE.values()) / sum(SLATE_KBBL.values())          # ~0.1265

CENTRAL = dict(
    prod_factor_scale=1.0,      # multiplier on product-specific factors
    eta_ref=0.95,               # refinery net energy efficiency (marketable output / crude intake)
    own_comb_share=0.15,        # share of oil-field gas combusted (rest reinjected)
    lng_fuel_comb=0.90,         # share of LNG-plant loss combusted as fuel
    ref_loss_comb=0.90,         # share of refinery loss combusted as refinery fuel
    eta_pp=0.45,                # grid thermal fleet efficiency (net)
    eta_marg=0.45,              # efficiency of plant displaced at the margin
    alpha_ne=0.80,              # share of naphtha/other residual used as non-energy feedstock
    lpg_res_share=0.70,         # share of LPG residual used by households/commerce
    jet_retail_kbbl=6_000.0,    # jet fuel in retail sales
    jet_intl_share=0.90,        # share of jet fuel used by international aviation (bunkers)
    p_lng=10.0, p_dom=3.0, c_liq=1.0,   # USD/MMBtu
    hypothesis="H1",            # H1 crude exports over-recorded; H2 production under-recorded
)


def balance(p):
    """Build the reconciled balance for parameter set p. Returns dict of results."""
    s = p["prod_factor_scale"]
    fprod = {k: v * s for k, v in F_PROD.items()}
    f_slate = F_SLATE * s
    f_gj = (sum(SLATE_KBBL[k] * fprod[k] for k in ("Gasoline 91", "Gasoline 95"))
            / (SLATE_KBBL["Gasoline 91"] + SLATE_KBBL["Gasoline 95"]))
    f_jet, f_dsl = fprod["Jet / kerosene"], fprod["Diesel / gas oil"]

    r = {}
    # --- oil
    crude_prod = OBS["crude_prod_kbbl"] * F_CRUDE
    crude_exp_rec = OBS["crude_exp_kbbl"] * F_CRUDE
    crude_imp = OBS["crude_imp_kbbl"] * F_CRUDE
    crude_rec_intake = crude_prod - crude_exp_rec + crude_imp
    ref_out = OBS["ref_out_kbbl"] * f_slate
    ref_intake = ref_out / p["eta_ref"]
    gap = ref_intake - crude_rec_intake
    if p["hypothesis"] == "H1":
        crude_exp, crude_prod_adj = crude_exp_rec - gap, crude_prod
    else:
        crude_exp, crude_prod_adj = crude_exp_rec, crude_prod + gap
    ref_loss = ref_intake - ref_out
    prod_exp = OBS["prod_exp_kbbl"] * f_slate
    bunk_marine = OBS["bunker_ktoe"]
    # retail allocation from distribution-company sales by product
    dsl = OBS["retail_ind_kbbl"] / 0.15                       # diesel retail volume
    gas_jet = OBS["retail_transport_kbbl"] - 0.70 * dsl
    jet = min(p["jet_retail_kbbl"], gas_jet)
    gasoline = gas_jet - jet
    jet_intl = jet * p["jet_intl_share"] * f_jet
    transport = gasoline * f_gj + (jet - jet * p["jet_intl_share"]) * f_jet + 0.70 * dsl * f_dsl
    ind_retail = OBS["retail_ind_kbbl"] * f_dsl
    res_retail = OBS["retail_res_kbbl"] * f_dsl
    retail_total = transport + ind_retail + res_retail + jet_intl
    domestic_prod = ref_out - prod_exp - bunk_marine          # before aviation bunkers
    residual = domestic_prod - retail_total
    # residual composition follows the non-retail part of the product slate
    nr = {k: SLATE_KBBL[k] * fprod[k] for k in ("Naphtha / other", "LPG", "Fuel oil")}
    nr_tot = sum(nr.values())
    res_naph = residual * nr["Naphtha / other"] / nr_tot
    res_lpg = residual * nr["LPG"] / nr_tot
    res_rfo = residual * nr["Fuel oil"] / nr_tot
    non_energy = res_naph * p["alpha_ne"]
    naph_ind = res_naph - non_energy
    lpg_res = res_lpg * p["lpg_res_share"]
    lpg_ind = res_lpg - lpg_res
    bunk_total = bunk_marine + jet_intl

    # --- gas
    gas_gross = OBS["gas_mmscf"] * F_GAS
    lng_feed = OBS["lng_feed_mmscf"] * F_GAS
    lng_out = OBS["lng_exp_mt"] * 1000 * LNG_TOE_T
    lng_loss = lng_feed - lng_out
    reinj = OBS["gas_oilfield_ktoe"] * (1 - p["own_comb_share"])
    gas_own = OBS["gas_oilfield_ktoe"] - reinj
    gas_marketable = gas_gross - reinj
    sd_gas = gas_gross - (lng_feed + OBS["gas_power_ktoe"] + OBS["gas_ind_ktoe"] + OBS["gas_oilfield_ktoe"])

    # --- electricity
    re = OBS["re_gwh"] * F_ELEC
    gen = OBS["gen_gwh"] * F_ELEC
    thermal_gwh = OBS["gen_gwh"] - OBS["re_gwh"]
    gas_grid = thermal_gwh * F_ELEC / p["eta_pp"]
    gas_power = OBS["gas_power_ktoe"]
    gas_pw_other = gas_power - gas_grid                       # desalination heat & unattributed
    elec_loss = (OBS["gen_gwh"] - OBS["cons_gwh"]) * F_ELEC
    elec_sec = {k: v * F_ELEC for k, v in ELEC_SEC_GWH.items()}

    # --- coal
    coal_imp = (OBS["coal_imp_t"] + OBS["lignite_imp_t"]) * F_COAL
    coal_exp = OBS["coal_exp_t"] * F_COAL
    coal = coal_imp - coal_exp

    # --- aggregates
    production = crude_prod_adj + gas_marketable + re
    imports = crude_imp + coal_imp
    exports = crude_exp + prod_exp + lng_out + coal_exp
    tpes = production + imports - exports - bunk_total
    sectors = {
        "Industrial": OBS["gas_ind_ktoe"] + coal + elec_sec["Industrial"] + ind_retail + naph_ind + lpg_ind + res_rfo,
        "Transport": transport,
        "Residential": elec_sec["Residential"] + res_retail + lpg_res,
        "Commercial": elec_sec["Commercial"],
        "Government": elec_sec["Government"],
        "Agriculture & other": elec_sec["Agriculture & other"],
        "Non-energy use": non_energy,
    }
    tfc = sum(sectors.values())
    tfc_check = (domestic_prod - jet_intl) + OBS["gas_ind_ktoe"] + coal + OBS["cons_gwh"] * F_ELEC
    # supply-use closure (should be ~0 apart from the gas statistical difference)
    uses = (tfc + (lng_loss) + (gas_power + re - gen) + elec_loss + gas_own + ref_loss)
    closure = tpes - uses

    # --- CO2 (Mt), IPCC categories
    co2 = {}
    co2["1.A.1.a Electricity (grid)"] = gas_grid * EF["gas"] / 1000
    co2["1.A.1.a Desalination heat & unattributed"] = gas_pw_other * EF["gas"] / 1000
    co2["1.A.1.b Petroleum refining"] = ref_loss * p["ref_loss_comb"] * EF["refgas"] / 1000
    co2["1.A.1.c LNG liquefaction"] = lng_loss * p["lng_fuel_comb"] * EF["gas"] / 1000
    co2["1.A.1.c Oil & gas extraction"] = gas_own * EF["gas"] / 1000
    ind_co2 = (OBS["gas_ind_ktoe"] * EF["gas"] + (coal_imp - coal_exp) * (0.931 * EF["coal"] + 0.069 * EF["lignite"])
               + ind_retail * EF["diesel"] + naph_ind * EF["naphtha"] + lpg_ind * EF["lpg"] + res_rfo * EF["rfo"]) / 1000
    co2["1.A.2 Manufacturing industries"] = ind_co2
    tr_co2 = (gasoline * f_gj * EF["gasoline"] + (jet - jet * p["jet_intl_share"]) * f_jet * EF["jet"]
              + 0.70 * dsl * f_dsl * EF["diesel"]) / 1000
    co2["1.A.3 Transport"] = tr_co2
    co2["1.A.4 Residential"] = (res_retail * EF["diesel"] + lpg_res * EF["lpg"]) / 1000
    co2_total = sum(co2.values())
    co2_fuel = {
        "Natural gas": (gas_power + OBS["gas_ind_ktoe"] + gas_own + lng_loss * p["lng_fuel_comb"]) * EF["gas"] / 1000,
        "Petroleum products": (ind_retail * EF["diesel"] + naph_ind * EF["naphtha"] + lpg_ind * EF["lpg"]
                               + res_rfo * EF["rfo"]) / 1000 + tr_co2 + co2["1.A.4 Residential"]
                              + co2["1.A.1.b Petroleum refining"],
        "Coal & lignite": coal * (0.931 * EF["coal"] + 0.069 * EF["lignite"]) / 1000,
    }
    memo_bunkers_co2 = (bunk_marine * EF["rfo"] + jet_intl * EF["jet"]) / 1000

    # --- electricity attribution & avoided emissions
    ef_grid = co2["1.A.1.a Electricity (grid)"] * 1e6 / (thermal_gwh * 1e3)        # t/MWh
    ef_marg = 56.1 * 3.6 / p["eta_marg"] / 1000
    avoided = OBS["re_gwh"] * ef_marg / 1000                                       # Mt
    end_use = {k: 0.0 for k in sectors}
    end_use["Industrial"] = ind_co2
    end_use["Transport"] = tr_co2
    end_use["Residential"] = co2["1.A.4 Residential"]
    grid_per_gwh = co2["1.A.1.a Electricity (grid)"] / OBS["cons_gwh"]
    for k, v in ELEC_SEC_GWH.items():
        end_use[k] += v * grid_per_gwh
    end_use["Energy sector (own use, LNG, refining, desalination)"] = (
        co2["1.A.1.a Desalination heat & unattributed"] + co2["1.A.1.b Petroleum refining"]
        + co2["1.A.1.c LNG liquefaction"] + co2["1.A.1.c Oil & gas extraction"])
    end_use.pop("Non-energy use")

    # --- political economy: rents
    lng_eta = lng_out / lng_feed
    margin = p["p_lng"] * lng_eta - p["c_liq"] - p["p_dom"]         # USD/MMBtu of feed gas
    gas_freed = OBS["re_gwh"] * 3.6 / p["eta_marg"] / TOE_GJ          # ktoe (GWh*3.6 TJ / eta / 41.868 TJ/ktoe)
    rent_preserved = gas_freed * MMBTU_PER_TOE * 1e3 * margin / 1e9   # USD bn
    dom_comb = {"Power & water plants": gas_power, "Industry": OBS["gas_ind_ktoe"], "Upstream own use": gas_own}
    rent_foregone = {k: v * MMBTU_PER_TOE * 1e3 * margin / 1e9 for k, v in dom_comb.items()}
    gdp_usd_bn = OBS["gdp_ro_m"] * USD_PER_RO / 1e3

    r.update(dict(
        crude_prod=crude_prod, crude_prod_adj=crude_prod_adj, crude_exp_rec=crude_exp_rec, crude_exp=crude_exp,
        crude_imp=crude_imp, crude_rec_intake=crude_rec_intake, ref_out=ref_out, ref_intake=ref_intake,
        gap=gap, ref_loss=ref_loss, eta_recorded=ref_out / crude_rec_intake, prod_exp=prod_exp,
        bunk_marine=bunk_marine, jet_intl=jet_intl, bunk_total=bunk_total, domestic_prod=domestic_prod,
        retail_total=retail_total, residual=residual, non_energy=non_energy, naph_ind=naph_ind,
        lpg_res=lpg_res, lpg_ind=lpg_ind, res_rfo=res_rfo, transport=transport, ind_retail=ind_retail,
        res_retail=res_retail, gasoline_kbbl=gasoline, jet_kbbl=jet, diesel_kbbl=dsl,
        gas_gross=gas_gross, lng_feed=lng_feed, lng_out=lng_out, lng_loss=lng_loss, lng_eta=lng_eta,
        reinj=reinj, gas_own=gas_own, gas_marketable=gas_marketable, sd_gas=sd_gas,
        re=re, gen=gen, gas_grid=gas_grid, gas_pw_other=gas_pw_other, gas_power=gas_power, elec_loss=elec_loss,
        coal_imp=coal_imp, coal_exp=coal_exp, coal=coal,
        production=production, imports=imports, exports=exports, tpes=tpes, tfc=tfc, tfc_check=tfc_check,
        closure=closure, ssr=production / tpes * 100, sectors=sectors, elec_sec=elec_sec,
        intensity=tpes * 1000 / OBS["gdp_ro_m"], per_capita=tpes * 1e6 / OBS["pop"],
        re_share_tpes=re / tpes * 100, re_share_gen=OBS["re_gwh"] / OBS["gen_gwh"] * 100,
        co2=co2, co2_total=co2_total, co2_fuel=co2_fuel, memo_bunkers_co2=memo_bunkers_co2,
        ef_grid=ef_grid, ef_marg=ef_marg, avoided=avoided, end_use=end_use,
        co2_per_capita=co2_total * 1e6 / OBS["pop"], co2_per_toe=co2_total * 1e3 / tpes,
        margin=margin, gas_freed=gas_freed, gas_freed_bcm=gas_freed / F_GAS * SCF_PER_MMSCF_M3 / 1e9,
        rent_preserved=rent_preserved, rent_foregone=rent_foregone, rent_total=sum(rent_foregone.values()),
        rent_share_gdp=sum(rent_foregone.values()) / gdp_usd_bn * 100, gdp_usd_bn=gdp_usd_bn,
        f_slate=f_slate, f_prod=fprod, f_retail=retail_total / (OBS["retail_transport_kbbl"] + OBS["retail_ind_kbbl"]
                                                                + OBS["retail_res_kbbl"]),
    ))
    return r


# ------------------------------------------------------------------ Monte Carlo
def tri(rng, a, m, b, n):
    return rng.triangular(a, m, b, n)


def monte_carlo(n=10_000, seed=2025):
    rng = np.random.default_rng(seed)
    draws = dict(
        prod_factor_scale=rng.uniform(0.97, 1.03, n),
        eta_ref=tri(rng, 0.92, 0.95, 0.98, n),
        own_comb_share=rng.uniform(0.0, 0.30, n),
        lng_fuel_comb=rng.uniform(0.80, 1.00, n),
        ref_loss_comb=rng.uniform(0.80, 1.00, n),
        eta_pp=tri(rng, 0.40, 0.45, 0.50, n),
        eta_marg=tri(rng, 0.35, 0.45, 0.55, n),
        alpha_ne=rng.uniform(0.60, 1.00, n),
        lpg_res_share=rng.uniform(0.50, 0.90, n),
        jet_retail_kbbl=rng.uniform(4_000, 9_000, n),
        jet_intl_share=rng.uniform(0.80, 0.95, n),
        p_lng=rng.uniform(6.0, 14.0, n),
        p_dom=rng.uniform(2.0, 4.0, n),
        c_liq=rng.uniform(0.5, 1.5, n),
    )
    keys = ["production", "tpes", "tfc", "ssr", "co2_total", "avoided", "gas_freed_bcm", "rent_preserved",
            "rent_total", "rent_share_gdp", "intensity", "non_energy", "gap"]
    out = {k: np.empty(n) for k in keys}
    for i in range(n):
        p = dict(CENTRAL)
        p.update({k: float(v[i]) for k, v in draws.items()})
        r = balance(p)
        for k in keys:
            out[k][i] = r[k]
    summ = {k: dict(p5=float(np.percentile(v, 5)), p50=float(np.percentile(v, 50)), p95=float(np.percentile(v, 95)),
                    mean=float(v.mean())) for k, v in out.items()}
    # Spearman rank correlations (sensitivity)
    def rank(a):
        return np.argsort(np.argsort(a)).astype(float)
    sens = {}
    for k in ("tpes", "ssr", "co2_total", "avoided", "rent_preserved"):
        ry = rank(out[k])
        sens[k] = {pk: float(np.corrcoef(rank(pv), ry)[0, 1]) for pk, pv in draws.items()}
    return summ, sens, out


# ------------------------------------------------------------------ time series & LMDI
GDP_GROWTH = {2023: 1.3, 2024: 1.7}   # real GDP growth, % (IMF, 2024; NCSI preliminary)


def timeseries():
    rows = {}
    with open(os.path.join(DATA, "external", "owid-co2-data_oman.csv")) as f:
        for x in csv.DictReader(f):
            if x["country"] == "Oman" and 2015 <= int(x["year"]) <= 2024:
                rows[int(x["year"])] = x
    energy = {}
    with open(os.path.join(DATA, "external", "owid-energy-data_oman.csv")) as f:
        for x in csv.DictReader(f):
            if x["country"] == "Oman" and 2015 <= int(x["year"]) <= 2025:
                energy[int(x["year"])] = x
    ts = []
    gdp = None
    for y in range(2015, 2025):
        x = rows[y]
        g = float(x["gdp"]) if x["gdp"] else gdp * (1 + GDP_GROWTH[y] / 100)
        gdp = g
        co2_energy = float(x["co2"]) - float(x["cement_co2"] or 0)          # fossil fuels + flaring
        ts.append(dict(
            year=y, pop=float(x["population"]), gdp=g, pe_twh=float(x["primary_energy_consumption"]),
            co2=co2_energy, gas_co2=float(x["gas_co2"]), oil_co2=float(x["oil_co2"]),
            coal_co2=float(x["coal_co2"] or 0), flaring_co2=float(x["flaring_co2"] or 0),
            cement_co2=float(x["cement_co2"] or 0),
            gen_twh=float(energy[y]["electricity_generation"]),
            re_share=float(energy[y]["renewables_share_elec"] or 0),
            gas_cons_twh=float(energy[y]["gas_consumption"]), oil_cons_twh=float(energy[y]["oil_consumption"]),
        ))
    return ts, {y: dict(gen=float(energy[y]["electricity_generation"]),
                        re_share=float(energy[y]["renewables_share_elec"] or 0)) for y in energy}


def lmdi(ts, y0, y1):
    a = next(t for t in ts if t["year"] == y0)
    b = next(t for t in ts if t["year"] == y1)

    def f(t):
        return dict(pop=t["pop"], aff=t["gdp"] / t["pop"], ei=t["pe_twh"] / t["gdp"], ci=t["co2"] / t["pe_twh"])
    fa, fb = f(a), f(b)
    L = (b["co2"] - a["co2"]) / (np.log(b["co2"]) - np.log(a["co2"]))
    eff = {k: float(L * np.log(fb[k] / fa[k])) for k in fa}
    eff["total"] = b["co2"] - a["co2"]
    return eff


def main():
    c = balance(CENTRAL)
    h2 = balance({**CENTRAL, "hypothesis": "H2"})
    # as-compiled (legacy) reference values
    legacy = dict(production=105_585.5, tpes=41_761.7, tfc=25_481.7, ssr=252.8, co2=91.48)
    # single-correction stepping for the reconciliation waterfall
    steps = []
    tp = legacy["tpes"]
    steps.append(("As compiled", tp))
    d_elec = -(c["gen"] - c["re"]); steps.append(("Primary electricity = solar & wind only", d_elec))
    d_reinj = -c["reinj"]; steps.append(("Exclude reinjected gas from production", d_reinj))
    d_lng = -(c["lng_out"] - 12_317.0); steps.append(("LNG energy content 1.177 toe/t", d_lng))
    d_prod = (19_008.0 - c["prod_exp"]); steps.append(("Product-specific factors (exports)", d_prod))
    d_jet = -c["jet_intl"]; steps.append(("International aviation bunkers", d_jet))
    d_gap = c["gap"]; steps.append(("Crude intake reconciled to refinery output", d_gap))
    steps.append(("Reconciled TPES", c["tpes"]))

    summ, sens, mc = monte_carlo()
    ts, elec_ts = timeseries()
    decomp = {f"{a}-{b}": lmdi(ts, a, b) for a, b in [(2015, 2019), (2019, 2024), (2015, 2024)]}
    chain = []
    for y in range(2016, 2025):
        e = lmdi(ts, y - 1, y)
        chain.append(dict(year=y, **e))

    res = dict(central=c, h2={k: h2[k] for k in ("production", "tpes", "ssr", "exports", "gap")},
               legacy=legacy, steps=steps, mc=summ, sens=sens, ts=ts, elec_ts=elec_ts,
               decomp=decomp, chain=chain, params=CENTRAL, f_prod=F_PROD, f_slate=F_SLATE,
               lng_toe_t=LNG_TOE_T, slate_ktoe=SLATE_KTOE)
    with open(os.path.join(DATA, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    np.savez_compressed(os.path.join(DATA, "mc_draws.npz"), **mc)

    # ---- CSV outputs for the public data package
    with open(os.path.join(DATA, "timeseries_2015_2024.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ts[0].keys())); w.writeheader(); w.writerows(ts)
    with open(os.path.join(DATA, "monte_carlo_summary.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["indicator", "p5", "p50", "p95", "mean"])
        for k, v in summ.items():
            w.writerow([k, v["p5"], v["p50"], v["p95"], v["mean"]])
    with open(os.path.join(DATA, "co2_inventory_2025.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["ipcc_category", "MtCO2"])
        for k, v in c["co2"].items():
            w.writerow([k, round(v, 3)])
    return res


if __name__ == "__main__":
    r = main()
    c = r["central"]
    pr = lambda *a: print(*a)
    pr(f"f_slate {r['f_slate']:.4f}  product factors", {k: round(v, 4) for k, v in r['f_prod'].items()})
    pr(f"ref_out {c['ref_out']:,.1f} intake {c['ref_intake']:,.1f} recorded {c['crude_rec_intake']:,.1f} gap {c['gap']:,.1f} eta_rec {c['eta_recorded']:.3f}")
    pr(f"prod_exp {c['prod_exp']:,.1f} domestic {c['domestic_prod']:,.1f} retail {c['retail_total']:,.1f} residual {c['residual']:,.1f} nonenergy {c['non_energy']:,.1f}")
    pr(f"transport {c['transport']:,.1f} jet_intl {c['jet_intl']:,.1f} gasoline kbbl {c['gasoline_kbbl']:,.0f} diesel kbbl {c['diesel_kbbl']:,.0f}")
    pr(f"LNG out {c['lng_out']:,.1f} eta {c['lng_eta']:.3f} loss {c['lng_loss']:,.1f}; reinj {c['reinj']:,.1f} own {c['gas_own']:,.1f} sd_gas {c['sd_gas']:.1f}")
    pr(f"gas grid {c['gas_grid']:,.1f} pw_other {c['gas_pw_other']:,.1f} ef_grid {c['ef_grid']:.4f} ef_marg {c['ef_marg']:.4f}")
    pr(f"PRODUCTION {c['production']:,.1f} IMPORTS {c['imports']:,.1f} EXPORTS {c['exports']:,.1f} BUNK {c['bunk_total']:,.1f} TPES {c['tpes']:,.1f} TFC {c['tfc']:,.1f} (check {c['tfc_check']:,.1f}) closure {c['closure']:.2f}")
    pr(f"SSR {c['ssr']:.1f} intensity {c['intensity']:.1f} percap {c['per_capita']:.1f} RE/TPES {c['re_share_tpes']:.2f}")
    pr("sectors", {k: round(v, 1) for k, v in c['sectors'].items()})
    pr("co2", {k: round(v, 2) for k, v in c['co2'].items()}, "total", round(c['co2_total'], 2))
    pr("co2 fuel", {k: round(v, 2) for k, v in c['co2_fuel'].items()}, "bunkers memo", round(c['memo_bunkers_co2'], 2))
    pr("end use", {k: round(v, 2) for k, v in c['end_use'].items()})
    pr(f"avoided {c['avoided']:.2f} gas freed {c['gas_freed']:,.1f} ktoe {c['gas_freed_bcm']:.2f} bcm margin {c['margin']:.2f} rent pres {c['rent_preserved']:.3f} rent foregone {c['rent_total']:.2f} ({c['rent_share_gdp']:.1f}% GDP)", {k: round(v, 2) for k, v in c['rent_foregone'].items()})
    pr("H2", {k: round(v, 1) for k, v in r['h2'].items()})
    pr("steps", [(a, round(b, 1)) for a, b in r['steps']])
    pr("MC", {k: (round(v['p5'], 2), round(v['p50'], 2), round(v['p95'], 2)) for k, v in r['mc'].items()})
    pr("decomp", {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in r['decomp'].items()})
    pr("ts", [(t['year'], round(t['co2'], 1), round(t['pe_twh'], 0), round(t['re_share'], 2)) for t in r['ts']])
