# Author notes: check these before submission

## 1. Corrections made to the source report's numbers

| Issue in the source report | What the paper does |
|---|---|
| Indigenous production counted **all** electricity generation (4,383.7 ktoe), including gas-fired generation, as primary energy. Under IRES this double-counts the 13,974 ktoe of gas burnt in power plants. | Primary electricity is restated as solar and wind only (387.8 ktoe). Production becomes **101,589.6 ktoe**, TPES **37,765.8 ktoe** and SSR **269.0%**. The as-compiled values (105,585.5 / 41,761.7 / 252.8%) are kept in Table 5 for transparency. TFC is unchanged. |
| CO₂ "by fuel" shares (57.1% / 33.7% / 0.7%) are actually **MtCO₂ values**. | Corrected shares are gas **62.4%** (57.09 Mt), petroleum **36.8%** (33.69 Mt) and coal **0.8%** (0.70 Mt). These agree with the pie chart in the original report. |
| The "Residential & Commercial 17.56 MtCO₂" row in the academic draft. | This row was really Other/unallocated (16.60) plus Residential (0.95). The sector table now uses the figure-level values. |
| "73,211.0 thousand barrels" of refined product exports. | 73,211.0 equals the **total energy exports in ktoe** (crude 41,882.7 + products 19,008 + LNG 12,317 + coal 3.3). The paper uses it that way. |
| The renewable-by-plant table in the academic draft (~2,100 / ~850 / ~650 / ~450 GWh). | Replaced with the actual plant values from the report's Fig. 3.8: 1,585.4 / 1,420.6 / 1,375.5 / 124.0 / 3.0 / 0.5 GWh. |
| The petroleum sector split in the text (gasoline and jet fuel fully to transport) does not match the balance, which applies 70/15/5/10 to all retail sales. | The paper reports the balance split and adds the product-specific split as a sensitivity (Table 6, Fig. 7c). |

## 2. Open issue: refinery closure (must resolve with NCSI / OQ8 data)

Recorded crude input to refineries is production − exports + imports = 128,888 kbbl (17,528.8 ktoe). Reported refinery output is 210,833 kbbl (30,570.8 ktoe), so apparent efficiency is **174%**, which is physically impossible. The product-resolved slate (115,140 kbbl) does match the crude input (about 95%). The most likely cause is crude delivered to the Duqm SEZ being recorded as exports.

The paper reports this openly (Sections 2.3.5 and 5.2, Table 4 footnote, Fig. 3b) and bounds the SSR at 200–269%. **If you can reconcile it with the workbook, update the numbers in `scripts/make_figures.py` and `scripts/content.js` and rebuild.** A reviewer will check this.

## 3. References

* All in-text citations have a matching Harvard-style entry, and every entry is cited.
* I checked the following against publisher or indexing records: Leal-Arcas et al. 2025; Abdel-Gadir & Mohammed 2024; Al-Abri et al. 2024; Mishrif & Khan 2023, 2024; Marzouk 2024; Venkatachalam et al. 2025; Szalai, Shamieh & Colombo 2025; Al-Badi & AlMubarak 2019; Almasri & Narayan 2021; Ali 2025; IEA 2023b; Fattouh & El-Katiri 2013; Salahuddin & Gow 2014; Bekhet et al. 2017; Goldthau & Westphal 2019.
* **Please verify** these yourself:
  * **Al-Sarihi & Cherni:** confirm the volume, issue and pages (33(4), 423–439) and the year (2022 online / 2023 issue).
  * **Liu et al. (2026) and Kuunifaa et al. (2026):** taken from your list. I could not find them in search indexes, so check the DOIs.
  * **OPWP (2024) 7-Year Statement:** confirm the edition.
  * **Title wording:** confirm the exact titles of Marzouk (2024) and Mishrif & Khan (2024).
* **Dropped** from the earlier academic draft because they were unverifiable or not peer-reviewed: the placeholder citations "MDPI 2025a–h", "PMC 2020/2021/2025", "Emerald 2021/2024/2025", "AIMS 2023a–c", "TOI 2025a/b", "Asiawind", "IJIRMPS", "IJSmartGrid", "RSIS 2025b", "ESS Oman", "GCC Energy 2023", "Wind Power 2020", "Oman Mining/Minerals", "RePEc 2022", "ResearchGate 2023", "UN SEEA 2025", "Samreen & Shahee 2026", "Baker Institute 2025" and others. Wherever the underlying paper could be identified, it is now cited by its real authors (e.g. "MDPI 2025a" → Leal-Arcas et al., 2025).

## 4. Before submitting

1. Replace the author, affiliation, CRediT, funding and acknowledgement placeholders.
2. Choose one journal. Energy Policy (Harvard style) suits this paper best. RSER expects a review-type framing, and Applied Energy prefers numbered references.
3. Upload the figures separately from `figures/` (600 dpi PNG). Each figure can be regenerated with `python scripts/make_figures.py`.
4. Rebuild the manuscript with `node scripts/build_docx.js`.
