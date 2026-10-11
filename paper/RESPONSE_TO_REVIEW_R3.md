# Response to the second review (revision 3)

Every number comes from `scripts/model.py` (`data/results.json`). Section numbers refer to `Manuscript_anonymised.docx`.

## Critical issues

### 1. The two refinery figures contradict each other

**Resolution (§2.4.1, Fig. 3a, Fig. 5, Table 3).** The two figures are not alternatives. They cover different plants.

| Figure | Coverage | ktoe | Rate vs capacity |
|---|---|---|---|
| 115,140 kbbl (product-resolved, NCSI) | Sohar + Mina Al Fahal only. The source report's data table says NCSI reports products "(Sohar, Mina Al Fahal)". | 14,561 | 315 kb/d vs 304 kb/d nameplate |
| 95,693 kbbl (operator data, no product split) | Duqm | 12,440 | 262 kb/d vs 255 kb/d after the 2025 debottleneck |
| 210,833 kbbl | Sum of the two | 27,001 | — |

**Duqm conversion factor.** Duqm has no product split, so it is converted at 0.130 ktoe/kbbl (0.125–0.135). The Appendix B slate now applies to Sohar and Mina Al Fahal only, and its caption says so.

### 2. H1 and H2 are physically doubtful; H0 (double counting) is likelier

**Resolution.**
- **The reviewer's capacity figure is outdated.** Duqm was raised to **255 kb/d** in 2025 (Argus; QCIntel), so national nameplate is about 559 kb/d.
- **Plant-level output fits capacity.** Each plant group's output is 2–4% above its own nameplate, which is the expected volume gain from turning crude into lighter products.
- **H0 (double counting) is rejected at plant level.** Duqm's output is not part of the NCSI product slate, so no barrel is in both figures.
- **Independent oil data support the output.** Implied domestic oil use is 11.6 Mtoe, against EI oil consumption extrapolated to 2025 of 10.6 Mtoe (+9%). If output were double-counted by the size of the gap, domestic supply would be negative.
- **H1 (exports over-recorded) is not supported.** Recorded exports (844 kb/d) match IMF-based (830–842 kb/d) and OPEC-based (~897 kb/d) series.
- **H2 (production under-recorded) is rejected.** Recorded production (1,002 kb/d) matches crude 775 + condensate 233 kb/d.
- **What the paper does now.** The paper no longer attributes the gap (10,893 ktoe, 219 kb/d). It is carried as an explicit **crude statistical difference**, as the IEA does.
- **Two TPES measures are reported:**
  - supply side: 25,822 ktoe;
  - use side (central): 36,715 ktoe, 90% CI 35,830–40,250.
- **Candidate explanations** are listed: unrecorded Duqm crude imports, Ras Markaz stock draws, and terminal liftings to domestic refineries recorded as exports.

### 3. Circular validation

**Resolution (§2.1, §3.2, Fig. 3c, Table 6).**
- **Calibration is now labelled as calibration (C).** The combusted share of oil-field gas is fitted to EI gas consumption extrapolated to 2025 (GCV, converted to NCV), giving 32%. The text states that the gas match is "by construction".
- **Calibration depends on the dataset.** If the EI data were already on an NCV basis, the share would be 58%. Calibrating to GCP gas CO₂ gives 73%.
  - This range enters the Monte Carlo as Tri(0.20, 0.32, 0.75).
  - The GCP calibration is also reported as an alternative case: CO₂ 88.9 Mt, SSR 227%.
- **Validation (V) uses only data that were never used for calibration:**
  - production (−0.6%);
  - EI oil consumption (+9%);
  - Ember 2025 generation (−3.5%);
  - plant capacities.
- **Highlight removed:** "within 1.3% of independent estimates" is gone.

### 4. Heating-value basis

**Resolution (§2.3, Table 3).**
- **NCV everywhere.** 0.02549 ktoe/MMscf (≈1,012 Btu/scf) is treated as gross. All gas is converted to NCV (×0.9), consistent with the IPCC emission factors.
- **Effect on totals:** TPES falls by 5,146 ktoe (Fig. 3b), and gas CO₂ no longer carries the ~11% bias.
- **LNG check on a consistent basis.** The reported feedstock now implies an LNG efficiency of **96.8%**, which is impossible (plants burn 7–12% of feed).
- **LNG feed is now derived from output.** It uses η = 90.5% (88–93%), giving 14,703 ktoe, 7% above the reported estimate. The difference comes out of the combined "industrial projects" category, so total gas still closes.

### 5. Gas feedstock treated as fuel

**Resolution (§2.4.2, Fig. 6a, Table 8).**
- **Feedstock moved to non-energy use:** 1,887 ktoe (1,400–2,300).
- **Basis:** about 2 Mt of methanol capacity (Oman Methanol Company, Sohar, 1.05 Mt; Salalah Methanol, 3,000 t/d) and about 2 Mt of ammonia capacity (OMIFCO Sur; SIUCI Sohar, 2,000 t/d), each at roughly 20 GJ of feedstock per tonne.
- **Ammonia process CO₂** is noted as IPCC category 2.B, outside the scope of this inventory.
- **Result:** manufacturing CO₂ falls to 19.6 Mt.

### 6. Thermal EOR

**Resolution.**
- **Higher combusted share.** It rises from 15% to 32% (central). Thermal EOR steam (Amal, Qarn Alam, Mukhaizna) and upstream power are named explicitly.
- **Cross-check:** an order-of-magnitude engineering estimate of 3–4.5 Mtoe agrees with the calibration.
- **Range:** the upper bound is 75%.
- **Upstream CO₂:** 8.0 Mt.
- **Still the dominant uncertainty:** ρ = +0.87, and the paper says so (§3.7, §5.2).

## Moderate issues

- **Year mismatch:** all external 2024 values are now extrapolated to 2025 with 2019–2024 growth rates. Ember 2025 data are used directly.
- **Unfocused discussion:** §4.4 hydrogen is cut to a single paragraph tied to Fig. 12b. The green finance, lithium and Sohar PV section is removed, along with its references (IJRISS, pv magazine, Enterprise AM, EU taxonomy, IEA critical minerals).
- **Weak sources:**
  - Siler-Evans et al. removed; the displaced-plant efficiency is now bounded by Oman's own OCGT/CCGT fleet (OPWP, 2024).
  - Gas price now cited to Fattouh & El-Katiri (2013), a peer-reviewed source on GCC gas pricing, and widened to USD 1.5–4.5.
  - IJRISS removed.
- **References:**
  - Liu et al. (2026) is confirmed on PMC (PMC13585052) and ACS (10.1021/acs.est.6c01630).
  - Kuunifaa et al. (2026) is confirmed on ScienceDirect (S2666278726000152; 10.1016/j.egycc.2026.100249).
  - Szalai et al. (2025) is confirmed on JSTOR (resrep69151).
  - Al-Sarihi & Cherni (2023) is confirmed via DOI 10.1002/eet.2041.
- **Novelty framing (§1.4):** the paper now states explicitly that the checks are routine for IEA and Eurostat compilers. The contribution is their plant-level application to a producer state, the calibration/validation separation, and the link to rent incidence.
- **Zenodo placeholder:** removed. The Data availability statement now points to the public repository (https://github.com/AnasGhawanmeh/JB, `paper/`) and says a Zenodo DOI will be minted on acceptance. **Make sure the repository is public, or upload to Zenodo and paste the DOI.**

## Headline numbers, revision 2 → revision 3

| Indicator | Rev. 2 | Rev. 3 (90% CI) |
|---|---|---|
| Production (ktoe) | 91,492 | 89,139 |
| TPES, use side (ktoe) | 38,923 | 36,715 (35,830–40,250) |
| TPES, supply side (ktoe) | — | 25,822 |
| SSR (%) | 235 | 243 (230–248) |
| CO₂ (Mt) | 88.1 | 78.4 (76.0–87.2) |
| Gas share of CO₂ | 74% | 71% |
| Avoided CO₂ (Mt) | 2.02 | 2.02 (1.75–2.38) |
| Implicit gas rent (% GDP) | 4.7 | 5.2 (1.5–9.4) |

## Still needed from the authors

1. **Refinery data:** metered refinery intake by crude origin from the Ministry of Energy and Minerals and OQ8. This would locate the crude statistical difference.
2. **Field data:** field-level reinjection, EOR steam and fuel-gas volumes. These would replace the calibrated oil-field share.
3. **Duqm data:** Duqm output by product. This would replace the 0.130 factor.
4. **Capacity sources:** confirm the Sohar (198 kb/d) and Mina Al Fahal (106 kb/d) nameplate figures and their sources. They are currently cited to Oxford Business Group (2019).
5. **Permission and repository:** ministry permission, plus a public repository or Zenodo DOI.
