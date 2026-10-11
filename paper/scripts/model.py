"""Reconciled IRES energy balance, CO2 inventory, Monte Carlo uncertainty and LMDI
decomposition for Oman (revision 3). Single source of every number in figures and text.

All energy quantities are on a NET calorific value (NCV) basis, consistent with the IPCC
NCV-based emission factors. Natural gas reported in gross terms (GCV) is converted with
NCV/GCV = 0.9 (UNSD, 2018).

Run:  python model.py  -> ../data/results.json and ../data/*.csv
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
DAYS = 365

# ------------------------------------------------------------------ national activity data, 2025
OBS = dict(
    crude_prod_kbbl=365_754.4,          # crude + condensate
    crude_exp_kbbl=307_960.9, crude_imp_kbbl=71_094.8,
    sm_out_kbbl=115_140.0,              # Sohar + Mina Al Fahal, product-resolved (NCSI)
    duqm_out_kbbl=95_693.1,             # Duqm (operator data) = 210,833.1 total - 115,140
    gas_mmscf=2_018_799.2,
    # gas use by national category, ktoe on the national (gross) factor 0.02549 ktoe/MMscf
    gas_power_gcv=13_974.0, gas_indproj_gcv=15_273.3 + 10_331.0, gas_oilfield_gcv=11_880.0,
    lng_feed_reported_mmscf=599_187.0, lng_exp_mt=11.3,
    gen_gwh=50_973.5, cons_gwh=45_033.1, re_gwh=4_509.0,
    coal_imp_t=246_603.5, lignite_imp_t=18_153.2, coal_exp_t=5_143.9,
    bunker_ktoe=453.8, prod_exp_kbbl=131_090.0,
    retail_transport_kbbl=40_642.1, retail_ind_kbbl=2_253.8, retail_res_kbbl=804.0,
    gdp_ro_m=40_130.0, pop=5_359_557,
)
CAPACITY_KBD = {"Sohar + Mina Al Fahal": 198 + 106, "Duqm": 255}   # nameplate, kb/d
EXT_PROD_KBD = {"crude (OPEC-based)": 774.8, "condensate": 233.0}  # external production estimates, 2025
ELEC_SEC_GWH = {"Residential": 18_624.9, "Commercial": 12_161.8, "Industrial": 8_136.6,
                "Government": 4_538.7, "Agriculture & other": 1_571.1}
SLATE_KBBL = {"Diesel / gas oil": 35_254, "Naphtha / other": 28_111, "Gasoline 91": 16_540,
              "Gasoline 95": 14_887, "Jet / kerosene": 11_712, "LPG": 8_112, "Fuel oil": 524}
NCV = {"gasoline": 44.3, "jet": 44.1, "diesel": 43.0, "lpg": 47.3, "rfo": 40.4, "naphtha": 44.5}
RHO = {"gasoline": 0.745, "jet": 0.800, "diesel": 0.845, "lpg": 0.540, "rfo": 0.960, "naphtha": 0.700}
EF = {"gasoline": 2.9015, "jet": 2.9936, "diesel": 3.1024, "lpg": 2.6419, "rfo": 3.2406,
      "naphtha": 3.0689, "gas": 2.3488, "coal": 4.1156, "lignite": 4.2287, "refgas": 2.4116}
SLATE_KIND = {"Diesel / gas oil": "diesel", "Naphtha / other": "naphtha", "Gasoline 91": "gasoline",
              "Gasoline 95": "gasoline", "Jet / kerosene": "jet", "LPG": "lpg", "Fuel oil": "rfo"}

F_CRUDE = 0.136
F_GAS_GCV = 0.02549                 # national factor, ktoe/MMscf (≈1,012 Btu/scf, gross)
NCV_GCV = 0.90
F_ELEC = 0.086
F_COAL = 0.00065
LNG_TOE_T = 49.3 / TOE_GJ           # NCV of LNG, toe/t
MMBTU_PER_TOE = 39.683
USD_PER_RO = 2.6008
M3_PER_MMSCF = 28_316.8


def toe_per_bbl(kind):
    return RHO[kind] * BBL_M3 * NCV[kind] / TOE_GJ


F_PROD = {k: toe_per_bbl(v) for k, v in SLATE_KIND.items()}
SLATE_KTOE = {k: SLATE_KBBL[k] * F_PROD[k] for k in SLATE_KBBL}
F_SLATE = sum(SLATE_KTOE.values()) / sum(SLATE_KBBL.values())


# ------------------------------------------------------------------ external series (OWID: EI, GCP, Ember)
def load_external():
    co2, en = {}, {}
    with open(os.path.join(DATA, "external", "owid-co2-data_oman.csv")) as f:
        for x in csv.DictReader(f):
            co2[int(x["year"])] = x
    with open(os.path.join(DATA, "external", "owid-energy-data_oman.csv")) as f:
        for x in csv.DictReader(f):
            en[int(x["year"])] = x
    return co2, en


CO2X, ENX = load_external()


def extrap_2025(series):
    """Extrapolate a 2024 value to 2025 with the 2019-2024 compound growth rate; return (value, low, high)."""
    v19, v24 = series[2019], series[2024]
    g = (v24 / v19) ** (1 / 5) - 1
    return v24 * (1 + g), v24 * (1 + min(0, g)), v24 * (1 + max(0, 2 * g))


EI_GAS = {y: float(ENX[y]["gas_consumption"]) * F_ELEC * 1000 for y in range(2015, 2025)}      # ktoe, GCV basis (EI)
EI_OIL = {y: float(ENX[y]["oil_consumption"]) * F_ELEC * 1000 for y in range(2015, 2025)}      # ktoe
GCP_GAS = {y: float(CO2X[y]["gas_co2"]) for y in range(2015, 2025)}
GCP_OIL = {y: float(CO2X[y]["oil_co2"]) for y in range(2015, 2025)}
EI_GAS25, EI_OIL25, GCP_GAS25, GCP_OIL25 = (extrap_2025(EI_GAS), extrap_2025(EI_OIL), extrap_2025(GCP_GAS),
                                            extrap_2025(GCP_OIL))
EMBER_GEN25 = float(ENX[2025]["electricity_generation"]) * 1000   # GWh

CENTRAL = dict(
    prod_factor_scale=1.0, f_duqm=0.130, eta_ref=0.95, eta_lng=0.905, chem_feed=1_887.0,
    own_comb_share=None,            # None -> calibrated to EI gas consumption (2025-extrapolated, GCV basis)
    lng_fuel_comb=0.90, ref_loss_comb=0.90, eta_pp=0.45, eta_marg=0.45, alpha_ne=0.80,
    lpg_res_share=0.70, jet_retail_kbbl=6_000.0, jet_intl_share=0.90,
    p_lng=10.0, p_dom=3.0, c_liq=1.0,
)


def gas_block(p):
    gross = OBS["gas_mmscf"] * F_GAS_GCV * NCV_GCV
    power = OBS["gas_power_gcv"] * NCV_GCV
    indproj = OBS["gas_indproj_gcv"] * NCV_GCV
    oilfield = OBS["gas_oilfield_gcv"] * NCV_GCV
    lng_out = OBS["lng_exp_mt"] * 1000 * LNG_TOE_T
    lng_feed = lng_out / p["eta_lng"]
    industry = indproj - lng_feed
    lng_feed_reported = OBS["lng_feed_reported_mmscf"] * F_GAS_GCV * NCV_GCV
    return dict(gross=gross, power=power, indproj=indproj, oilfield=oilfield, lng_out=lng_out, lng_feed=lng_feed,
                industry=industry, lng_feed_reported=lng_feed_reported,
                eta_lng_reported=lng_out / lng_feed_reported)


def calibrate_own_share(p, target_ncv):
    g = gas_block(p)
    known = g["power"] + g["industry"] + (g["lng_feed"] - g["lng_out"])
    return (target_ncv - known) / g["oilfield"]


def balance(p):
    p = dict(p)
    g = gas_block(p)
    if p["own_comb_share"] is None:
        p["own_comb_share"] = calibrate_own_share(p, EI_GAS25[0] * NCV_GCV)
    s = p["prod_factor_scale"]
    fprod = {k: v * s for k, v in F_PROD.items()}
    f_slate = F_SLATE * s
    f_duqm = p["f_duqm"] * s
    f_gj = (sum(SLATE_KBBL[k] * fprod[k] for k in ("Gasoline 91", "Gasoline 95"))
            / (SLATE_KBBL["Gasoline 91"] + SLATE_KBBL["Gasoline 95"]))
    f_jet, f_dsl = fprod["Jet / kerosene"], fprod["Diesel / gas oil"]

    # --- oil: refinery output by plant group, intake implied by output, crude statistical difference
    out_sm = OBS["sm_out_kbbl"] * f_slate
    out_dq = OBS["duqm_out_kbbl"] * f_duqm
    ref_out = out_sm + out_dq
    ref_intake = ref_out / p["eta_ref"]
    ref_loss = ref_intake - ref_out
    crude_prod = OBS["crude_prod_kbbl"] * F_CRUDE
    crude_exp = OBS["crude_exp_kbbl"] * F_CRUDE
    crude_imp = OBS["crude_imp_kbbl"] * F_CRUDE
    crude_supply = crude_prod - crude_exp + crude_imp
    sd_crude = crude_supply - ref_intake                      # IRES statistical difference (negative)
    f_exp = ref_out / (OBS["sm_out_kbbl"] + OBS["duqm_out_kbbl"])
    prod_exp = OBS["prod_exp_kbbl"] * f_exp
    bunk_marine = OBS["bunker_ktoe"]
    dsl = OBS["retail_ind_kbbl"] / 0.15
    gas_jet = OBS["retail_transport_kbbl"] - 0.70 * dsl
    jet = min(p["jet_retail_kbbl"], gas_jet)
    gasoline = gas_jet - jet
    jet_intl = jet * p["jet_intl_share"] * f_jet
    transport = gasoline * f_gj + jet * (1 - p["jet_intl_share"]) * f_jet + 0.70 * dsl * f_dsl
    ind_retail = OBS["retail_ind_kbbl"] * f_dsl
    res_retail = OBS["retail_res_kbbl"] * f_dsl
    retail_total = transport + ind_retail + res_retail + jet_intl
    domestic_prod = ref_out - prod_exp - bunk_marine
    residual = domestic_prod - retail_total
    nr = {k: SLATE_KBBL[k] * fprod[k] for k in ("Naphtha / other", "LPG", "Fuel oil")}
    nr_tot = sum(nr.values())
    res_naph, res_lpg, res_rfo = (residual * nr[k] / nr_tot for k in ("Naphtha / other", "LPG", "Fuel oil"))
    ne_oil = res_naph * p["alpha_ne"]
    naph_ind = res_naph - ne_oil
    lpg_res = res_lpg * p["lpg_res_share"]
    lpg_ind = res_lpg - lpg_res
    bunk_total = bunk_marine + jet_intl

    # --- gas
    own = g["oilfield"] * p["own_comb_share"]
    reinj = g["oilfield"] - own
    gas_marketable = g["gross"] - reinj
    chem = min(p["chem_feed"], g["industry"])
    ind_fuel = g["industry"] - chem
    lng_loss = g["lng_feed"] - g["lng_out"]
    sd_gas = g["gross"] - (g["lng_feed"] + g["power"] + g["industry"] + g["oilfield"])

    # --- electricity
    re = OBS["re_gwh"] * F_ELEC
    gen = OBS["gen_gwh"] * F_ELEC
    thermal_gwh = OBS["gen_gwh"] - OBS["re_gwh"]
    gas_grid = min(thermal_gwh * F_ELEC / p["eta_pp"], g["power"])
    gas_pw_other = g["power"] - gas_grid
    elec_loss = (OBS["gen_gwh"] - OBS["cons_gwh"]) * F_ELEC
    elec_sec = {k: v * F_ELEC for k, v in ELEC_SEC_GWH.items()}

    coal_imp = (OBS["coal_imp_t"] + OBS["lignite_imp_t"]) * F_COAL
    coal_exp = OBS["coal_exp_t"] * F_COAL
    coal = coal_imp - coal_exp

    # --- aggregates
    production = crude_prod + gas_marketable + re
    imports = crude_imp + coal_imp
    exports = crude_exp + prod_exp + g["lng_out"] + coal_exp
    tpes_supply = production + imports - exports - bunk_total          # IRES supply-side TPES
    tpes = tpes_supply - sd_crude                                      # use-side TPES (central)
    sectors = {
        "Industrial": ind_fuel + coal + elec_sec["Industrial"] + ind_retail + naph_ind + lpg_ind + res_rfo,
        "Transport": transport,
        "Residential": elec_sec["Residential"] + res_retail + lpg_res,
        "Commercial": elec_sec["Commercial"],
        "Government": elec_sec["Government"],
        "Agriculture & other": elec_sec["Agriculture & other"],
        "Non-energy use": ne_oil + chem,
    }
    tfc = sum(sectors.values())
    uses = tfc + lng_loss + (g["power"] + re - gen) + elec_loss + own + ref_loss
    closure = tpes - uses                                              # = sd_gas

    # --- CO2 (Mt) by IPCC category
    co2 = {
        "1.A.1.a Electricity (grid)": gas_grid * EF["gas"] / 1000,
        "1.A.1.a Desalination heat & unattributed": gas_pw_other * EF["gas"] / 1000,
        "1.A.1.b Petroleum refining": ref_loss * p["ref_loss_comb"] * EF["refgas"] / 1000,
        "1.A.1.c LNG liquefaction": lng_loss * p["lng_fuel_comb"] * EF["gas"] / 1000,
        "1.A.1.c Oil & gas extraction": own * EF["gas"] / 1000,
    }
    coal_ef = 0.931 * EF["coal"] + 0.069 * EF["lignite"]
    ind_co2 = (ind_fuel * EF["gas"] + coal * coal_ef + ind_retail * EF["diesel"] + naph_ind * EF["naphtha"]
               + lpg_ind * EF["lpg"] + res_rfo * EF["rfo"]) / 1000
    tr_co2 = (gasoline * f_gj * EF["gasoline"] + jet * (1 - p["jet_intl_share"]) * f_jet * EF["jet"]
              + 0.70 * dsl * f_dsl * EF["diesel"]) / 1000
    co2["1.A.2 Manufacturing industries"] = ind_co2
    co2["1.A.3 Transport"] = tr_co2
    co2["1.A.4 Residential"] = (res_retail * EF["diesel"] + lpg_res * EF["lpg"]) / 1000
    co2_total = sum(co2.values())
    gas_comb = g["power"] + ind_fuel + own + lng_loss * p["lng_fuel_comb"]
    co2_fuel = {"Natural gas": gas_comb * EF["gas"] / 1000,
                "Coal & lignite": coal * coal_ef / 1000}
    co2_fuel["Petroleum products"] = co2_total - co2_fuel["Natural gas"] - co2_fuel["Coal & lignite"]
    memo_bunkers_co2 = (bunk_marine * EF["rfo"] + jet_intl * EF["jet"]) / 1000

    ef_grid = co2["1.A.1.a Electricity (grid)"] * 1e6 / (thermal_gwh * 1e3)
    ef_marg = 56.1 * 3.6 / p["eta_marg"] / 1000
    avoided = OBS["re_gwh"] * ef_marg / 1000
    end_use = {"Industrial": ind_co2, "Transport": tr_co2, "Residential": co2["1.A.4 Residential"],
               "Commercial": 0.0, "Government": 0.0, "Agriculture & other": 0.0}
    for k, v in ELEC_SEC_GWH.items():
        end_use[k] += v * co2["1.A.1.a Electricity (grid)"] / OBS["cons_gwh"]
    end_use["Energy sector (own use, LNG, refining, desalination)"] = sum(
        co2[k] for k in co2 if k.startswith("1.A.1") and "grid" not in k)

    # --- rents (prices per MMBtu on a gross basis)
    margin = p["p_lng"] * p["eta_lng"] - p["c_liq"] - p["p_dom"]
    to_mmbtu_gcv = MMBTU_PER_TOE * 1e3 / NCV_GCV
    gas_freed = OBS["re_gwh"] * 3.6 / p["eta_marg"] / TOE_GJ                     # ktoe NCV
    rent_preserved = gas_freed * to_mmbtu_gcv * margin / 1e9
    dom = {"Power & water plants": g["power"], "Industry (fuel & feedstock)": g["industry"],
           "Upstream own use": own}
    rent_foregone = {k: v * to_mmbtu_gcv * margin / 1e9 for k, v in dom.items()}
    gdp_usd_bn = OBS["gdp_ro_m"] * USD_PER_RO / 1e3

    # --- calibration & validation diagnostics
    gas_cons_ei_def = g["power"] + g["industry"] + lng_loss + own        # NCV, EI consumption definition
    oil_cons_ei_def = domestic_prod + bunk_marine + ref_loss              # inland + bunkers + refinery fuel/loss
    return dict(
        p=p, f_slate=f_slate, f_duqm=f_duqm, f_exp=f_exp,
        crude_prod=crude_prod, crude_exp=crude_exp, crude_imp=crude_imp, crude_supply=crude_supply,
        out_sm=out_sm, out_dq=out_dq, ref_out=ref_out, ref_intake=ref_intake, ref_loss=ref_loss, sd_crude=sd_crude,
        eta_recorded=ref_out / crude_supply, prod_exp=prod_exp, bunk_marine=bunk_marine, jet_intl=jet_intl,
        bunk_total=bunk_total, domestic_prod=domestic_prod, retail_total=retail_total, residual=residual,
        ne_oil=ne_oil, naph_ind=naph_ind, lpg_res=lpg_res, lpg_ind=lpg_ind, res_rfo=res_rfo, transport=transport,
        ind_retail=ind_retail, res_retail=res_retail, gasoline_kbbl=gasoline, jet_kbbl=jet, diesel_kbbl=dsl,
        gas_gross=g["gross"], gas_power=g["power"], gas_indproj=g["indproj"], gas_oilfield=g["oilfield"],
        lng_feed=g["lng_feed"], lng_out=g["lng_out"], lng_loss=lng_loss, eta_lng=p["eta_lng"],
        lng_feed_reported=g["lng_feed_reported"], eta_lng_reported=g["eta_lng_reported"],
        gas_industry=g["industry"], chem=chem, ind_fuel=ind_fuel, own=own, own_share=p["own_comb_share"],
        reinj=reinj, gas_marketable=gas_marketable, sd_gas=sd_gas,
        re=re, gen=gen, gas_grid=gas_grid, gas_pw_other=gas_pw_other, elec_loss=elec_loss, elec_sec=elec_sec,
        eta_pp_implied=thermal_gwh * F_ELEC / g["power"],
        coal_imp=coal_imp, coal_exp=coal_exp, coal=coal,
        production=production, imports=imports, exports=exports, tpes_supply=tpes_supply, tpes=tpes, tfc=tfc,
        closure=closure, ssr=production / tpes * 100, ssr_supply=production / tpes_supply * 100, sectors=sectors,
        intensity=tpes * 1000 / OBS["gdp_ro_m"], per_capita=tpes * 1e6 / OBS["pop"],
        re_share_tpes=re / tpes * 100, re_share_gen=OBS["re_gwh"] / OBS["gen_gwh"] * 100,
        co2=co2, co2_total=co2_total, co2_fuel=co2_fuel, memo_bunkers_co2=memo_bunkers_co2,
        ef_grid=ef_grid, ef_marg=ef_marg, avoided=avoided, end_use=end_use,
        co2_per_capita=co2_total * 1e6 / OBS["pop"],
        margin=margin, gas_freed=gas_freed, gas_freed_bcm=gas_freed / (F_GAS_GCV * NCV_GCV) * M3_PER_MMSCF / 1e9,
        rent_preserved=rent_preserved, rent_foregone=rent_foregone, rent_total=sum(rent_foregone.values()),
        rent_share_gdp=sum(rent_foregone.values()) / gdp_usd_bn * 100, gdp_usd_bn=gdp_usd_bn,
        gas_cons_ei_def=gas_cons_ei_def, oil_cons_ei_def=oil_cons_ei_def,
        ipcc_ammonia_memo=chem,
    )


# ------------------------------------------------------------------ Monte Carlo
def monte_carlo(n=10_000, seed=2025):
    rng = np.random.default_rng(seed)
    c0 = balance(CENTRAL)
    s_cal = c0["own_share"]
    s_gcp = calibrate_own_share(CENTRAL, GCP_GAS25[0] / EF["gas"] * 1000 - 0) if False else None
    draws = dict(
        prod_factor_scale=rng.uniform(0.97, 1.03, n),
        f_duqm=rng.uniform(0.125, 0.135, n),
        eta_ref=rng.triangular(0.92, 0.95, 0.98, n),
        eta_lng=rng.uniform(0.88, 0.93, n),
        chem_feed=rng.uniform(1_400, 2_300, n),
        own_comb_share=rng.triangular(0.20, s_cal, 0.75, n),
        lng_fuel_comb=rng.uniform(0.80, 1.00, n),
        ref_loss_comb=rng.uniform(0.80, 1.00, n),
        eta_pp=rng.triangular(0.40, 0.45, 0.50, n),
        eta_marg=rng.triangular(0.35, 0.45, 0.55, n),
        alpha_ne=rng.uniform(0.60, 1.00, n),
        lpg_res_share=rng.uniform(0.50, 0.90, n),
        jet_retail_kbbl=rng.uniform(4_000, 9_000, n),
        jet_intl_share=rng.uniform(0.80, 0.95, n),
        p_lng=rng.uniform(6.0, 14.0, n),
        p_dom=rng.uniform(1.5, 4.5, n),
        c_liq=rng.uniform(0.5, 1.5, n),
    )
    keys = ["production", "tpes", "tpes_supply", "tfc", "ssr", "co2_total", "avoided", "gas_freed_bcm",
            "rent_preserved", "rent_total", "rent_share_gdp", "intensity", "sd_crude", "reinj"]
    out = {k: np.empty(n) for k in keys}
    out["ne_total"] = np.empty(n)
    out["co2_gas"] = np.empty(n)
    for i in range(n):
        p = dict(CENTRAL)
        p.update({k: float(v[i]) for k, v in draws.items()})
        r = balance(p)
        for k in keys:
            out[k][i] = r[k]
        out["ne_total"][i] = r["sectors"]["Non-energy use"]
        out["co2_gas"][i] = r["co2_fuel"]["Natural gas"]
    summ = {k: dict(p5=float(np.percentile(v, 5)), p50=float(np.percentile(v, 50)),
                    p95=float(np.percentile(v, 95)), mean=float(v.mean())) for k, v in out.items()}

    def rank(a):
        return np.argsort(np.argsort(a)).astype(float)
    sens = {k: {pk: float(np.corrcoef(rank(pv), rank(out[k]))[0, 1]) for pk, pv in draws.items()}
            for k in ("tpes", "ssr", "co2_total", "avoided", "rent_preserved")}
    return summ, sens, out


# ------------------------------------------------------------------ time series & LMDI
GDP_GROWTH = {2023: 1.3, 2024: 1.7}


def timeseries():
    ts, gdp = [], None
    for y in range(2015, 2025):
        x, e = CO2X[y], ENX[y]
        g = float(x["gdp"]) if x["gdp"] else gdp * (1 + GDP_GROWTH[y] / 100)
        gdp = g
        ts.append(dict(year=y, pop=float(x["population"]), gdp=g, pe_twh=float(x["primary_energy_consumption"]),
                       co2=float(x["co2"]) - float(x["cement_co2"] or 0), gas_co2=float(x["gas_co2"]),
                       oil_co2=float(x["oil_co2"]), coal_co2=float(x["coal_co2"] or 0),
                       flaring_co2=float(x["flaring_co2"] or 0), cement_co2=float(x["cement_co2"] or 0),
                       gen_twh=float(e["electricity_generation"]), re_share=float(e["renewables_share_elec"] or 0),
                       gas_cons_twh=float(e["gas_consumption"]), oil_cons_twh=float(e["oil_consumption"])))
    return ts


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
    # alternative calibration of oil-field combustion: GCP gas CO2 (2025-extrapolated)
    gcp_target_comb = GCP_GAS25[0] * 1000 / EF["gas"]          # ktoe NCV combusted
    known_comb = c["gas_power"] + c["ind_fuel"] + c["lng_loss"] * CENTRAL["lng_fuel_comb"]
    own_share_gcp = (gcp_target_comb - known_comb) / c["gas_oilfield"]
    own_share_ei_ncv = calibrate_own_share(CENTRAL, EI_GAS25[0])          # if EI data were NCV
    alt_gcp = balance({**CENTRAL, "own_comb_share": own_share_gcp})

    legacy = dict(production=105_585.5, tpes=41_761.7, tfc=25_481.7, ssr=252.8, co2=91.48)
    # reconciliation waterfall from the as-compiled TPES (each step in ktoe)
    steps = [("As compiled", legacy["tpes"])]
    steps.append(("Primary electricity = solar & wind", -(c["gen"] - c["re"])))
    gas_ncv_effect = -(OBS["gas_mmscf"] * F_GAS_GCV * (1 - NCV_GCV))
    steps.append(("Gas on NCV basis", gas_ncv_effect))
    steps.append(("Reinjection excluded", -c["reinj"]))
    steps.append(("LNG exports at 1.177 toe/t", -(c["lng_out"] - 12_317.0)))
    steps.append(("Product-specific factors (exports)", 19_008.0 - c["prod_exp"]))
    steps.append(("Aviation bunkers", -c["jet_intl"]))
    steps.append(("Crude statistical difference", -c["sd_crude"]))
    steps.append(("Reconciled (use side)", c["tpes"]))
    resid = legacy["tpes"] + sum(v for _, v in steps[1:-1]) - c["tpes"]

    summ, sens, mc = monte_carlo()
    ts = timeseries()
    decomp = {f"{a}-{b}": lmdi(ts, a, b) for a, b in [(2015, 2019), (2019, 2024), (2015, 2024)]}

    calib = dict(
        ei_gas25_gcv=EI_GAS25, ei_gas25_ncv=[v * NCV_GCV for v in EI_GAS25], own_share_ei=c["own_share"],
        own_share_ei_ncv=own_share_ei_ncv, own_share_gcp=own_share_gcp, gcp_gas25=GCP_GAS25,
        co2_total_gcp_cal=alt_gcp["co2_total"], tpes_gcp_cal=alt_gcp["tpes"], ssr_gcp_cal=alt_gcp["ssr"],
    )
    valid = dict(
        refinery=[dict(group="Sohar + Mina Al Fahal", out_kbd=OBS["sm_out_kbbl"] / DAYS,
                       cap_kbd=CAPACITY_KBD["Sohar + Mina Al Fahal"]),
                  dict(group="Duqm", out_kbd=OBS["duqm_out_kbbl"] / DAYS, cap_kbd=CAPACITY_KBD["Duqm"])],
        production_kbd=OBS["crude_prod_kbbl"] / DAYS, ext_production_kbd=sum(EXT_PROD_KBD.values()),
        oil_ours=c["oil_cons_ei_def"], oil_ei25=EI_OIL25,
        gen_ours=OBS["gen_gwh"], gen_ember25=EMBER_GEN25,
        gcp_oil25=GCP_OIL25, oil_co2_ours=c["co2_fuel"]["Petroleum products"],
        intake_kbd=c["ref_intake"] / F_CRUDE / DAYS, crude_supply_kbd=c["crude_supply"] / F_CRUDE / DAYS,
    )
    res = dict(central=c, legacy=legacy, steps=steps, steps_residual=resid, mc=summ, sens=sens, ts=ts,
               decomp=decomp, params=CENTRAL, f_prod=F_PROD, f_slate=F_SLATE, lng_toe_t=LNG_TOE_T,
               slate_ktoe=SLATE_KTOE, calib=calib, valid=valid, capacity=CAPACITY_KBD,
               ember_re25=float(ENX[2025]["renewables_share_elec"]))
    with open(os.path.join(DATA, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    np.savez_compressed(os.path.join(DATA, "mc_draws.npz"), **mc)
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
    print(f"slate {r['f_slate']:.4f} duqm {c['f_duqm']:.3f} exp {c['f_exp']:.4f}")
    print(f"ref out SM {c['out_sm']:,.0f} DQ {c['out_dq']:,.0f} tot {c['ref_out']:,.0f} intake {c['ref_intake']:,.0f} "
          f"crude supply {c['crude_supply']:,.0f} SD {c['sd_crude']:,.0f}")
    print(f"gas gross {c['gas_gross']:,.0f} power {c['gas_power']:,.0f} indproj {c['gas_indproj']:,.0f} LNG feed "
          f"{c['lng_feed']:,.0f} (reported {c['lng_feed_reported']:,.0f}, eta_rep {c['eta_lng_reported']:.3f}) "
          f"industry {c['gas_industry']:,.0f} chem {c['chem']:,.0f} fuel {c['ind_fuel']:,.0f}")
    print(f"oilfield {c['gas_oilfield']:,.0f} own {c['own']:,.0f} share {c['own_share']:.3f} reinj {c['reinj']:,.0f}")
    print(f"grid gas {c['gas_grid']:,.0f} other {c['gas_pw_other']:,.0f} eta_pp_implied {c['eta_pp_implied']:.3f}")
    print(f"PROD {c['production']:,.0f} IMP {c['imports']:,.0f} EXP {c['exports']:,.0f} BUNK {c['bunk_total']:,.0f} "
          f"TPES_supply {c['tpes_supply']:,.0f} TPES {c['tpes']:,.0f} TFC {c['tfc']:,.0f} closure {c['closure']:.2f}")
    print(f"SSR {c['ssr']:.1f} SSR_supply {c['ssr_supply']:.1f} intensity {c['intensity']:.1f}")
    print("sectors", {k: round(v) for k, v in c["sectors"].items()})
    print("co2", {k: round(v, 2) for k, v in c["co2"].items()}, round(c["co2_total"], 2))
    print("fuel", {k: round(v, 2) for k, v in c["co2_fuel"].items()})
    print(f"avoided {c['avoided']:.2f} freed {c['gas_freed_bcm']:.2f} bcm margin {c['margin']:.2f} rent {c['rent_total']:.2f} "
          f"({c['rent_share_gdp']:.1f}%) preserved {c['rent_preserved']:.3f}")
    print("calib", {k: (round(v, 3) if isinstance(v, float) else [round(x, 1) for x in v]) for k, v in r["calib"].items()})
    print("valid", r["valid"])
    print("steps", [(a, round(b)) for a, b in r["steps"]], "resid", round(r["steps_residual"], 1))
    print("MC", {k: (round(v["p5"], 1), round(v["p50"], 1), round(v["p95"], 1)) for k, v in r["mc"].items()})
    print("sens ssr", {k: round(v, 2) for k, v in r["sens"]["ssr"].items() if abs(v) > 0.1})
    print("sens co2", {k: round(v, 2) for k, v in r["sens"]["co2_total"].items() if abs(v) > 0.1})
