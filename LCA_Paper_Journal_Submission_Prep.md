# Journal Submission Preparation — Jordan Transport WTW LCA Paper

**Paper:** *Uncovering the 'Grid Penalty' and Pollution Swaps in Transport Decarbonization: A Well-to-Wheel Life Cycle Assessment of the Jordanian Fleet*
**Author:** Anas Ghawanmeh
**Prepared:** 29 September 2026

This package does not rewrite the paper. It contains:

1. A technical review listing errors a journal reviewer will find (fix these before submitting)
2. Reference verification results
3. Recommended target journals
4. An AI-use disclosure statement (ready to paste)
5. A plan for adapting the manuscript to a journal
6. A cover letter template

---

## 1. Technical review — problems to fix before submission

These are ranked by how likely each one is to cause rejection. Several are internal contradictions, where the paper states two different numbers or claims for the same thing. Reviewers catch these quickly.

### A. Critical (likely to cause rejection)

| # | Location | Problem | What to do |
|---|----------|---------|------------|
| A1 | §2.2 System boundaries vs. §3.2, §4 | The boundary **excludes vehicle and battery manufacturing**, yet the Results and Discussion claim that Scenario 1 increases **mineral resource scarcity from lithium/cobalt extraction** (single-score discussion, §4 para. on toxicity). If manufacturing is excluded, battery mining impacts cannot show up in your results. | Either (a) include battery manufacturing in the boundary and remodel, or (b) remove every claim about battery mineral/toxicity impacts from the Results and present them only as literature context in the Discussion. |
| A2 | Whole paper | **No functional unit is stated.** §2.1 says goal & scope defines "what functional unit the results are measured against" but none is given. ISO 14040/44 requires it, and reviewers at LCA journals will reject without it. | State it explicitly, e.g., *"total annual road passenger and freight transport activity of Jordan in 2022 (X billion vkm / pkm / tkm)"*. For the micro-level results, use *1 pkm* or *1 vkm*. |
| A3 | Abstract, §3.1, §3.2 | **DALY totals are inconsistent.** §3.1 says *global warming alone* causes 2,790 DALYs, PM2.5 adds 2,220, and diesel carcinogenic toxicity adds 497. That sums to more than 5,500 DALYs. But §3.2 and the abstract give the **total** baseline burden as 2.79×10³ DALYs. | Recheck the SimaPro endpoint output. Report the total human-health DALY and the per-category breakdown so that they add up. |
| A4 | §3.2 Scenario 4 | "The health burden falls by **more than 400 DALYs**, down to 449." From 2,790 to 449 is a fall of about **2,340 DALYs (−84%)**. | Correct the arithmetic. |
| A5 | Abstract, §3.1 vs. §4 | Fossil resource damage is **$1.62 billion** in the abstract and §3.1, but **$1.62 million (USD2013)** in §4, where it is also cited to MEMR (2022) even though it is your own SimaPro result. | Use one value, state the currency year (ReCiPe endpoint is USD2013), and cite your own Table 1 rather than MEMR. |
| A6 | §3.1 | Gasoline $703M + diesel $658M = $1,361M, not $1.62B. The remaining ~$260M is not explained. | Show the full breakdown (LPG? jet fuel? electricity?) in Table 1. |
| A7 | §2.2 vs. §3.2 | The grid is described as **~27% renewable** (NEPCO 2022) in §1/§2.2, but as **~98% fossil-fuelled** in §3.2. | 27% is installed *capacity*; the *generation* share differs. State both clearly, and use the generation mix you actually modelled in SimaPro. |
| A8 | Reference list: MoEnv/UNFCCC (2025) | Your own reference says that **EV penetration reached 21% of the national fleet by 2024** and renewable generation reached 28.5%. Scenario 1 (20% EV uptake) is presented as a future policy scenario, but by your own source it has **already happened**. A reviewer will notice. The reference is also never cited in the text and contains a note instead of a proper citation. | Verify the 21% figure (it may refer to share of *new registrations*, not the fleet). Then reframe Scenario 1 or explain the difference. Remove the note text from the reference entry. |
| A9 | §3.2, §3.3 vs. Discussion | **Scenario 4 cuts GWP by 84% on a fossil-dominated grid.** That contradicts the paper's central "grid penalty" argument that EVs on a fossil grid mainly relocate emissions. §4 also cites Liu and Qiao as showing that fossil power "can cancel out" EV benefits, while your own Monte Carlo shows no overlap and a clear EV advantage. | Decide what the results actually show and frame the grid penalty consistently. For example: *"EVs reduce emissions even on Jordan's grid, but X% of the avoided tailpipe CO₂ reappears at power plants."* Quantify that percentage — it is the grid penalty and currently is never given as a number. |
| A10 | Abstract, §1 vs. §3.2 | The abstract says diesel buses push **health risk higher**. But the deterministic result for Scenario 2 shows DALYs **falling** from 2,790 to 2,520. The "higher risk" claim rests only on the wide right tail in the Monte Carlo box plot. | Rephrase carefully: *"lower on average, but with a higher risk of increased local PM2.5 exposure when occupancy is low."* |

### B. Major (reviewers will ask for revision)

| # | Location | Problem | What to do |
|---|----------|---------|------------|
| B1 | §1, §2.3, §4 | **"Stratospheric ozone depletion"** is described as a local pollution cost of diesel buses. Stratospheric ozone depletion is a *global* impact, caused by ODS/N₂O, and is not a local air-quality problem. You probably mean **ground-level ozone formation** (ReCiPe "Ozone formation, human health"). | Correct the impact category name everywhere. |
| B2 | §2.1, §2.3 | **Bare et al. (2002) is the TRACI paper.** It is cited for the four-stage LCA framework and for the ReCiPe Hierarchist perspective. It supports neither. | Cite **ISO 14040 / ISO 14044** (already in your list but never cited) for the four stages. Cite **Huijbregts et al. (2017)** for ReCiPe and the Hierarchist perspective. |
| B3 | §2.5 Monte Carlo | The macro-level uncertainty uses **triangular distributions placed directly on total GWP and DALYs**. That is not propagated inventory uncertainty. Reviewers will say the uncertainty was assumed, not calculated. The min/mode/max values are not reported, and neither is their source. | Add a table of every distribution (parameter, type, min/mode/max or μ/σ, source). Better still, run the Monte Carlo in SimaPro, which uses ecoinvent pedigree uncertainty, or propagate uncertainty from inventory parameters (fuel use, occupancy, grid mix) in your Python model. Provide the code as supplementary material. |
| B4 | §3.3, §4 | **Overclaiming:** "no statistical overlap", "essentially full confidence", "settle the core question". Monte Carlo results depend on the distributions you chose. | Report overlap as a probability (e.g., "S4 < S1 in 100% of 10,000 paired iterations") and moderate the language. |
| B5 | §2.1 vs. §2.2 | §2.1 says SimaPro gives a **"cradle-to-grave"** view, but §2.2 excludes manufacturing and end-of-life. §2.2 also calls end-of-life "grave-to-cradle", which is the wrong term. | Describe the study as **Well-to-Wheel (operational)**. Remove "cradle-to-grave" and use "end-of-life" for disposal. |
| B6 | §2.1 scope vs. §3.2, Fig. 7 | Scope says **road** transport fleet, but results include **aviation** ("residual footprint from aviation", air travel in Fig. 7). | Either widen the scope to all transport or drop aviation. |
| B7 | §3.3 / §4 | Occupancy threshold is "25–30 passengers" in §3.3 and "under 25 passengers **per passenger-kilometre**" in §4, which is a unit error. | Give one threshold with its confidence interval, in passengers per bus. |
| B8 | §2 intro | "Ecoinvent 3.x" | Give the exact version (e.g., 3.9.1) and the SimaPro version. |
| B9 | §2.5 | Normal distributions for combustion vehicles cite **Cox et al.** for "air-travel conditions". Cox et al. study passenger cars. The summer air-conditioning load cites **Alotaibi et al. (2022)**, which is a survey of EV adoption barriers, not a measurement of AC energy load. | Find sources that actually support these parameter choices. |
| B10 | Missing data section | Fleet size, vehicle-km by category, fuel consumption, load factors and the grid mix are not given anywhere. DoS (2023) and MoT (2023) are in the reference list but **never cited**. | Add a "Life Cycle Inventory data" subsection with a table of activity data and sources. This is essential for reproducibility. |
| B11 | §4 last para. | "sector modelling in **Figure 3** backs up…". Figure 3 is the baseline only. | Use Figure 4 or Figure 9. |
| B12 | §2.1 | "exactly what happened while building the scenarios in **Section 2.3**". Scenarios are in §2.4. | Fix the cross-reference. |
| B13 | §4 | Chester & Horvath (2009) is about infrastructure and supply chains in transport LCA, not bus occupancy toxicity thresholds. | Re-check the claim you attribute to them. |
| B14 | §1 para. 5 | "We call this a 'pollution swap' (Requia et al., 2018)". Claiming a term as your own and citing someone else for it is contradictory. | Either credit the term to others or define it as your term without the citation. |

### C. Minor

- Sections 3.3.1–3.3.3 are numbered "1., 2., 3." as Heading 2. Renumber them 3.3.1–3.3.3.
- Policy Implications (§5) and Conclusion (§6) repeat the same paragraphs almost word for word (Solar-to-EV, CNG/Euro 5/6 dead end, leapfrogging). Journals will ask you to cut this. Keep the policy detail in §5 and make §6 a short summary of findings, limitations and future work.
- There is **no Limitations section.** Add one covering the excluded manufacturing and end-of-life stages, the static 2022 grid, the assumed distributions, and the fleet data quality.
- Use CO₂ with a subscript consistently. Some places use CO2 and others CO₂.
- Use either "Gg" or "×10⁹ kg" throughout, not both.

---

## 2. Reference verification

I checked the less common references against the web. The well-known LCA references (Huijbregts 2017, Nordelöf 2014, Cox 2018/2020, Buberger 2022, Harper 2019, Requia 2018, Igos 2019, Bisinella 2021, Lai 2022, Anenberg 2012) match their real details.

| Reference | Status | Note |
|-----------|--------|------|
| Alghamdi (2026) WEVJ 17(8) 415 | ✅ Verified | [MDPI](https://www.mdpi.com/2032-6653/17/8/415). Your description (25% cut on the Saudi grid) matches. |
| Evensen et al. (2025) TR-D 142, 104714 | ✅ Verified, ⚠️ misused | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1361920925001245). It is a **consumer survey of UAE respondents** about adoption barriers. It is **not** an LCA and does not study grid emissions, "leapfrogging" to renewables, or Solar-to-EV microgrids. About 6 of its 8 citations in your paper attribute claims it does not make (§2.2, Scenario 1, "remote dispersal devices", leapfrogging, and Solar-to-EV in §5 and §6). |
| Aryan et al. (2025) Discover Sustainability 6, 675 | ✅ Verified | [Springer](https://link.springer.com/article/10.1007/s43621-025-01556-4) |
| Jarre et al. (2024) Energies 17(19) 4955 | ✅ Verified | [doi](https://doi.org/10.3390/en17194955) |
| Ahmadi, P. et al. (2022) Energy 259, 125003 | ✅ Verified | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0360544222019004). Canadian case study (Victoria, BC). |
| Alotaibi et al. (2022) Electricity 3(3) 365–395 | ✅ Verified, ⚠️ misused | [MDPI](https://www.mdpi.com/2673-4826/3/3/20). Survey of adoption barriers. It does not supply AC-load distributions (§2.5) or LCA findings (§4). |
| **Qiao et al. (2019) Applied Energy 254, 113687** | ❌ **Mismatch** | The title "Cradle-to-gate GHG emissions of BEV and ICEV in China" is **Qiao et al. 2017, Applied Energy 204, 1399–1411**. Their 2019 paper is "Life cycle GHG emissions of EVs in China: combining the vehicle cycle and fuel cycle", *Energy* 177, 222–233 ([IDEAS](https://ideas.repec.org/a/eee/energy/v177y2019icp222-233.html)). Neither has article number 113687. **Replace with the correct one.** |
| **Liu, Chen & Wu (2019) JCP 233, 1079–1089** | ❌ **Not found** | I could not find a paper with this title, these authors and this volume. **Treat it as possibly fabricated.** Find the real source or remove it. |
| **Grutter (2014) "Real World Performance of Diesel Buses in Developing Countries"** | ❌ **Title not found** | Grütter Consulting's 2014 report is "*Real World Performance of Hybrid and Electric Buses*" ([SLOCAT](https://slocat.net/1325-2/)). That report is about hybrid and e-bus fuel savings, not diesel bus PM2.5 or occupancy. Four claims in your paper rest on this citation. |
| Henriksson et al. (2015) | ⚠️ Check | This is a horizontal-averaging protocol. It is not a general Monte Carlo method reference, so it is fine only as support for data averaging. |
| Bare et al. (2002) | ⚠️ Misused | See B2 above. |
| ISO 14040 / 14044, DoS 2023, MoT 2023, MoEnv/UNFCCC 2025 | ⚠️ Not cited in text | Cite them where they belong or remove them. Most journals reject reference lists that include uncited items. |

**Rule for the final version:** open every reference yourself, confirm that it says what you cite it for, and add a DOI to each journal article. Fabricated or mismatched references are the most common reason AI-drafted papers get desk-rejected or retracted.

---

## 3. Recommended target journals

All of these allow AI-assisted writing **if it is disclosed**, provided the author takes full responsibility and AI is not listed as an author.

| Journal | Publisher | Fit | Notes |
|---------|-----------|-----|-------|
| **Sustainability** or **World Electric Vehicle Journal** | MDPI | Good. Alghamdi (2026), a very similar study, was published in WEVJ. | Fast review (~4–8 weeks). Open-access fee applies. A realistic first choice. |
| **Energy for Sustainable Development** | Elsevier | Good. Focus on developing countries. | Suits the "developing economies" framing well. |
| **Transportation Research Part D** | Elsevier | Strong fit, higher tier | Needs fixes A1–A10 and B3 done well. |
| **International Journal of Life Cycle Assessment** | Springer | Methodologically demanding | Only after the functional unit, boundary, inventory table and uncertainty method are solid. |
| **Journal of Cleaner Production** | Elsevier | Broad | High volume, high desk-rejection rate. |

**Suggestion:** fix sections 1 and 2 of this document, then submit to *World Electric Vehicle Journal* or *Energy for Sustainable Development*.

---

## 4. AI-use disclosure statement (ready to paste)

Adjust the wording so it describes exactly what you did. It has to be true.

**Elsevier format** (placed before the References, under the heading *"Declaration of generative AI and AI-assisted technologies in the writing process"*):

> During the preparation of this work the author used Claude (Anthropic) to assist with drafting and language editing of the manuscript text. The study design, SimaPro modelling, data collection, Monte Carlo simulation, analysis, and interpretation of results were carried out by the author. After using this tool, the author reviewed, verified, and edited the content as needed, checked all references against their original sources, and takes full responsibility for the content of the publication.

**MDPI / Springer format** (in the Acknowledgments or Methods section):

> The author used Claude (Anthropic) to assist in drafting and editing the text of this manuscript. All research design, modelling, data analysis, and conclusions are the author's own. The author reviewed and edited all AI-assisted text, verified all cited sources, and takes full responsibility for the content of this publication.

---

## 5. Adapting the manuscript for a journal

1. **Fix the critical issues first (A1–A10).** Most of them need you to go back to SimaPro and your Python outputs, so only you can do them.
2. **Fix the references (Section 2 above).** Replace Qiao 2019, Liu 2019 and Grutter 2014. Re-check every Evensen 2025 citation.
3. **Add the missing sections:**
   - §2.x *Functional unit and inventory data*, with a table of fleet and activity data and sources
   - §2.5 *Uncertainty parameters*, with a table of distributions
   - §4.x *Limitations*
4. **Cut the repetition.** Merge the overlapping §5 and §6 content. Target length is 6,000–8,000 words for Elsevier and more flexible for MDPI.
5. **Journal extras:** 3–5 *Highlights* (Elsevier, ≤85 characters each), a graphical abstract (you can adapt Figure 4), a CRediT author statement, a data availability statement (share the Python Monte Carlo code on GitHub or Zenodo), and a conflict-of-interest statement.
6. **Co-authorship.** If your advisor (Prof. Hani Abu Qdais) supervised the thesis, journals and universities normally expect them to be a co-author or at least acknowledged. Agree this with them before submitting.
7. **Final pass.** Read the whole paper aloud and make sure every sentence is something you can defend and explain. Reviewers and editors may ask you about any of it.

---

## 6. Cover letter template

> Dear Editor,
>
> Please consider the enclosed manuscript, "*[Title]*", for publication as a research article in *[Journal]*.
>
> Most transport decarbonization roadmaps assume that electric vehicles are charged from a clean grid. This study tests that assumption for a fossil-dependent developing economy. We present a Well-to-Wheel life cycle assessment of Jordan's 2022 national transport fleet (SimaPro, ReCiPe 2016) and evaluate four mitigation scenarios with a 10,000-iteration Monte Carlo analysis. The study quantifies two trade-offs that tailpipe-based accounting misses: the "grid penalty" of electrification on a fossil-heavy grid, and the "pollution swap" of shifting passengers to under-occupied diesel buses.
>
> *[One or two sentences on the key numerical findings once they are corrected.]*
>
> We believe the manuscript fits the scope of *[Journal]* because *[reason: e.g., its focus on transport and environment in developing economies]*. The work is original, has not been published elsewhere, and is not under consideration by another journal. Generative AI assistance in manuscript drafting is disclosed in the manuscript in line with the journal's policy. The author declares no conflicts of interest.
>
> Sincerely,
> Anas Ghawanmeh
> *[Affiliation, email, ORCID]*
