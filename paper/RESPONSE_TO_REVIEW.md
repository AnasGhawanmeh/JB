# Response to the pre-submission review

Each comment is followed by the action taken and where it appears in `Manuscript_anonymised.docx`. All numbers come from `scripts/model.py` (`data/results.json`).

---

## 1. The balance does not close, so it cannot be called "IRES-compliant"

**Action.**
- **Diagnostic framework (§2.1):** the paper now applies three closure tests:
  - T1, column closure;
  - T2, process-efficiency closure;
  - T3, triangulation against Energy Institute and Global Carbon Project data.
- **Refinery account (§2.4.1, Fig. 3a, Table 6):** this account fails T2 (η = 1.52).
  - Three explanations are tested. Over-recorded output (H0) is rejected because it would make domestic product supply negative, which contradicts metered retail sales.
  - Crude intake is therefore estimated from refinery output at a net efficiency of 0.95 (0.92–0.98).
  - The supply gap (10,537 ktoe) is attributed either to crude recorded as exports (H1, central) or to under-recorded production (H2). Both cases are reported.
- **Result:** the reconciled balance closes in every column. The only residual is a gas statistical difference of 0.9 ktoe.
  - TPES is 38,923 ktoe (90% CI 37,101–40,669).
  - This is within 1.3% of the Energy Institute's independent estimate (Fig. 3c).
- **Title and claims:** "IRES-compliant" has been removed from the title and highlights. The paper now says "reconciled".

**Still needed from you:** metered refinery crude intake from the Ministry of Energy and Minerals and OQ8. This would replace the assumed efficiency and settle H1 versus H2. In `model.py`, replace `ref_intake = ref_out / p["eta_ref"]` with the metered value.

## 2. The refined-product factor of 0.145 is too high

**Action.** Product-specific factors are now used: IPCC NCV × density (Appendix B, Table B.1).
- Diesel 0.138, gasoline 0.125, naphtha 0.118, jet 0.134, LPG 0.097, fuel oil 0.147 ktoe/kbbl.
- The slate average is **0.1265** ktoe/kbbl.
- Refinery output falls by about 3,900 ktoe.
- The energy content of product exports falls by about 2,430 ktoe, which raises TPES.

## 3. Missing combustion CO₂ from own use and LNG

**Action.** The inventory is now organised by IPCC category (Table 9, Fig. 9).

| Category | 2025 (MtCO₂) |
|---|---|
| 1.A.1.b Refining (new) | 3.05 |
| 1.A.1.c LNG plant fuel (new) | 4.16 |
| 1.A.1.c Upstream gas combustion (new) | 4.19 |

- **Oil-field gas (§2.4.2, §3.2):** the 11,880 ktoe is mostly reinjection.
  - If all of it were burnt, gas CO₂ would exceed the GCP estimate by about 26 Mt.
  - The data fit about 15% combustion (0–30% in the Monte Carlo).
  - Under IRES, reinjected gas (10,098 ktoe) is excluded from production. It is shown separately in Fig. 4a and Fig. 6a.
- **Total CO₂:** 88.1 Mt (83.4–92.6).
  - It is lower than the earlier 91.5 Mt, despite the new categories.
  - The reason is that the 16.6 Mt "unallocated" petroleum residual was mostly non-energy use (comment 6).

## 4. Power-plant efficiency of 28.6% is implausible

**Action (§2.4.2, Fig. 6a):**
- Grid electricity is assigned the fuel implied by a 45% net fleet efficiency (40–50% in the Monte Carlo): 8,880 ktoe.
- The remaining 5,094 ktoe is reported as "desalination heat and unattributed". It stays in the inventory but no longer inflates the grid emission factor.
- **Avoided CO₂** now uses the efficiency of the displaced (marginal) plant: 0.45, with a range of 0.35–0.55.
  - Result: 2.02 Mt (1.76–2.39), down from 3.19 Mt.

**Still needed from you:** plant-level fuel, power and water output from OPWP or the Nama group, to replace the assumed split.

## 5. LNG numbers

**Action (§2.3, §2.4.2, Fig. 6b):**
- LNG is now converted at 1.178 toe/t (NCV 49.3 GJ/t).
- Liquefaction efficiency becomes **87.1%**, within the normal plant range.
- **Feedstock method:** the 599,187 MMscf feedstock is now documented as the operator's reported feed-gas requirement.
  - It is cross-checked as 53.0 thousand scf per tonne of LNG, consistent with plant fuel of 8–12%.
- **Dual dividend:** the calculation uses this efficiency.

## 6. "Other / unallocated" is too large

**Action (§2.4.3, Fig. 7c, Table 8):** the residual is replaced by a product-based allocation.
- Retail sales are allocated by product, and international jet fuel (723 ktoe) moves to aviation bunkers.
- The non-retail residual is split by the refinery slate:
  - naphtha and other products go mostly to **non-energy use** (2,496 ktoe, excluded from combustion CO₂);
  - LPG goes to households and industry;
  - fuel oil goes to industry.
- There is no longer an "unallocated" category.
- **TFC independence:** TFC is shown to be independent of the crude reconciliation, because refinery output and product exports are both observed. Its 90% CI is 22,850–23,630 ktoe.

## 7. Weak novelty; "Political Economy" not substantiated

**Action.**
- **Novelty reframed (§1.4):**
  - The paper now acknowledges that IEA, UNSD, EI and GCP already publish data for Oman, and drops the "first balance" claim.
  - The contribution is a transferable diagnostic reconciliation framework for producer-state balances, plus quantified uncertainty.
- **Time series (§2.7, §3.6, Fig. 10, Table 10):** 2015–2024 data with an LMDI decomposition.
  - Total change 2015–2024: +14.1 Mt.
  - Population: +16.9 Mt.
  - Energy intensity: +11.6 Mt.
  - GDP per capita: -8.1 Mt.
  - Carbon intensity: -6.3 Mt.
- **Monte Carlo uncertainty (§2.6, §3.7, Fig. 11):** 10,000 draws, 14 parameters, with Spearman sensitivity.
- **Quantified political economy (§2.8, §4.1, Fig. 12a):**
  - Implicit gas rent transferred to domestic users: USD 4.9 bn, or 4.7% of GDP (1.4–8.0%).
  - This is broken down by sector and compared with the RO 520 million electricity subsidy.
  - Rent preserved by renewables: USD 0.16 bn.
  - Linked to rentier theory and to the strategic-niche-management argument of Al-Sarihi & Cherni (2023).
- **Title** now matches the content: "Closing the books of a rentier energy economy …".

## Journal fit

The paper is now written for **Energy Strategy Reviews**: it has a methods framework, a strategy and policy focus, and Nagovnak et al. (2022) as its anchor. Energy for Sustainable Development and Energy Reports are good alternatives. Applied Energy and RSER are not recommended.

## Before submitting

| Item | Status |
|---|---|
| Written permission from MEM / National Energy Balance Unit | **You must obtain it.** Template in `PERMISSION_REQUEST_TEMPLATE.md`. The title page has a "Data permission" statement to complete. |
| Remove consultancy wording ("as-compiled workbook", "steering group", "source report … which we correct here") | Done. The 2025 inputs are described as national statistics; "as compiled" refers only to the national accounts before reconciliation. |
| Remove placeholders and internal notes ("Target journals", [Author], "[Edit …]") | Done in the manuscript, which is fully anonymised. Author details are only in `Title_page.docx`, which you must fill in. |
| Check every reference | Done; see the reference audit in `AUTHOR_NOTES.md`. Liu et al. 2026, Kuunifaa et al. 2026, Szalai et al. 2025 and Al-Sarihi & Cherni 2023 were all confirmed; the last now carries its DOI 10.1002/eet.2041. Three references that could not be verified were removed. |
| Public data | Zenodo-ready package in `data/` (README, CSVs, scripts, CC BY 4.0, `CITATION.cff`). **Upload it and replace `10.5281/zenodo.XXXXXXX`** in the Data availability statement. |
