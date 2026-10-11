// Manuscript content. Inline markup: **bold**, *italic*. Block types:
// h1, h2, h3, p, eq, bullets, table, fig, pagebreak.
const F = (n, file, w, h, caption) => ({ type: "fig", n, file, w, h, caption });

const meta = {
  title:
    "The Political Economy of Decarbonization in a Rentier State: An IRES-Compliant 2025 National Energy Balance and Sustainable Transition Analysis for Oman",
  runningTitle: "IRES-compliant 2025 energy balance for Oman",
  authors: "[Author 1]ᵃ*, [Author 2]ᵇ, [Author 3]ᵃ",
  affiliations: [
    "ᵃ [Department, Institution, City, Postal code, Sultanate of Oman]",
    "ᵇ [Department, Institution, City, Postal code, Country]",
  ],
  corresponding: "* Corresponding author. E-mail address: [corresponding.author@institution.om]",
  highlights: [
    "First IRES-compliant, independently compiled 2025 national energy balance for Oman.",
    "Restating primary electricity lowers TPES to 37.8 Mtoe; self-sufficiency is 269%.",
    "Industry takes 47.7% of final energy; households take 41.4% of electricity.",
    "Renewables reached 8.85% of generation, avoiding 1.7–3.2 MtCO₂ in 2025.",
    "Displaced gas worth USD 0.26–0.61 bn yr⁻¹ as LNG creates a dual dividend.",
  ],
  abstract:
    "Hydrocarbon-exporting rentier states face a distinctive decarbonization problem: the fuels they would displace at home are also the source of their fiscal rents abroad. Policy for such economies requires granular, internally consistent energy accounts, which are seldom available. This study compiles, to our knowledge, the first independent 2025 National Energy Balance for Oman that conforms to the International Recommendations for Energy Statistics (IRES), linked to an IPCC Tier 1 emissions inventory and a counterfactual analysis of renewable displacement. Three structural corrections are applied to the legacy accounting: liquefied natural gas (LNG) feedstock (599,187 MMscf) is separated from industrial combustion; the foreign crude and product exports of the Duqm refinery are integrated; and total electricity generation is replaced by primary renewable electricity in indigenous production. Indigenous production is 101,590 ktoe, Total Primary Energy Supply (TPES) 37,766 ktoe and Total Final Consumption 25,482 ktoe, implying a self-sufficiency ratio of 269%. Industry accounts for 47.7% of final energy, whereas the residential sector accounts for 41.4% of electricity. Renewable generation reached 4,509 GWh (8.85% of generation) and avoided 1.66–3.19 MtCO₂ against national direct-combustion emissions of 91.48 MtCO₂, 62.4% of which derive from natural gas. A refinery-closure diagnostic reveals an unreconciled feedstock gap of 13,042 ktoe that bounds the self-sufficiency ratio between 200% and 269%. Renewable deployment yields a dual dividend: it abates emissions and frees 1.5 bcm of gas worth USD 0.26–0.61 billion per year at LNG prices. Decarbonization in a rentier state therefore requires supply-side expansion coupled with demand-side efficiency and transparent statistics.",
  keywords: [
    "National energy balance",
    "IRES",
    "Rentier state",
    "Oman",
    "Renewable energy transition",
    "CO₂ emissions accounting",
  ],
};

const abbreviations = [
  ["CCGT", "Combined-cycle gas turbine"],
  ["EF", "Emission factor"],
  ["EKC", "Environmental Kuznets Curve"],
  ["GCC", "Gulf Cooperation Council"],
  ["IEA", "International Energy Agency"],
  ["IPCC", "Intergovernmental Panel on Climate Change"],
  ["IPP", "Independent power project"],
  ["IRES", "International Recommendations for Energy Statistics"],
  ["kbbl", "Thousand barrels"],
  ["ktoe", "Thousand tonnes of oil equivalent (1 toe = 41.868 GJ)"],
  ["LNG", "Liquefied natural gas"],
  ["MMscf", "Million standard cubic feet"],
  ["NCSI", "National Centre for Statistics and Information"],
  ["NCV", "Net calorific value"],
  ["NDC", "Nationally Determined Contribution"],
  ["OCGT", "Open-cycle gas turbine"],
  ["OPWP", "Oman Power and Water Procurement Company"],
  ["SSR", "Self-sufficiency ratio"],
  ["TFC", "Total Final Consumption"],
  ["TFEE", "Total-factor energy efficiency"],
  ["TPES", "Total Primary Energy Supply"],
  ["VRE", "Variable renewable energy"],
];

const body = [
  // ------------------------------------------------------------------ 1
  { type: "h1", text: "1. Introduction" },
  { type: "h2", text: "1.1. Background and context" },
  {
    type: "p",
    text:
      "The economies of the Gulf Cooperation Council (GCC) are organised around the capture and redistribution of hydrocarbon rents. In the classical formulation of the rentier state, external rents accrue directly to the government, which allocates them domestically through public employment, transfers and administered energy prices rather than through taxation (Beblawi and Luciani, 1987; Krane, 2019). Climate change adds a further structural pressure on this model in a region already exposed to extreme heat and water stress (Al-Maamary et al., 2017a). The same fiscal architecture that sustains political stability also locks in high domestic energy demand: subsidised electricity and fuels have produced per-capita consumption and energy intensities that are among the highest in the world (Lahn and Stevens, 2011; Fattouh and El-Katiri, 2013; Al-Badi and AlMubarak, 2019).",
  },
  {
    type: "p",
    text:
      "The Sultanate of Oman occupies a specific position within this group. It is a mid-sized producer with comparatively modest reserves and a recurrent fiscal deficit, which renders the opportunity cost of domestic hydrocarbon use particularly salient (Javed and Husain, 2020; Al-Sarihi and Cherni, 2023). Oman Vision 2040 formalises a strategic pivot towards economic diversification and a low-carbon energy sector, and the government has since pledged net-zero emissions by 2050 and updated its Nationally Determined Contribution (NDC) under the Paris Agreement (Sultanate of Oman, 2020; Argus Media, 2023). The Oman Power and Water Procurement Company (OPWP) targets a 30% renewable share of electricity generation by 2030, and the state-owned Hydrogen Oman (Hydrom) is mandated to develop 1.0–1.25 Mt of renewable hydrogen per year by 2030 (IEA, 2023b; OPWP, 2024).",
  },
  { type: "h2", text: "1.2. Problem statement" },
  {
    type: "p",
    text:
      "Heavily subsidised, centralised petroleum economies exhibit considerable structural inertia. Incumbent institutions, administered prices and long-term export contracts tend to delay the diffusion of renewable technologies even where resource endowments are exceptional (Al-Sarihi and Cherni, 2023; Szalai et al., 2025). A further and less frequently discussed barrier is informational. Robust energy and climate policy requires a national energy balance that traces every unit of energy from production and trade through transformation to final use, because the balance supplies the activity data for emissions inventories, the denominators for efficiency indicators, and the evidence base for subsidy and investment decisions (UNSD, 2018; Nagovnak et al., 2022). In export-oriented hydrocarbon economies, the construction of such a balance is complicated by large transformation sectors (refining, LNG liquefaction and gas-fired power), by special economic zones whose flows are recorded inconsistently, and by fragmented administrative data (Neelis and Pouwelse, 2008; Kuunifaa et al., 2026).",
  },
  {
    type: "p",
    text:
      "For Oman, historical energy balances were adapted from an external template whose product taxonomy and default assumptions did not reflect the country's large LNG export sector, its three refineries or its rapidly expanding renewable fleet. Three consequences followed. First, the national category for gas delivered to “industrial projects” combined LNG liquefaction feedstock with industrial combustion, so that natural gas final consumption appeared as a forced residual of approximately zero. Second, the output of the newly commissioned Duqm refinery entered the balance without its matching crude imports and product exports, which overstated domestic product availability. Third, total electricity generation, including gas-fired generation, was recorded as primary production, which double-counts the gas consumed by power plants. Each of these artefacts distorts the indicators on which decarbonization policy depends.",
  },
  { type: "h2", text: "1.3. Literature review" },
  {
    type: "p",
    text:
      "Three strands of literature frame this study. The first concerns the relationship between growth, energy use and emissions. The Environmental Kuznets Curve (EKC) hypothesis posits an inverted-U relationship between income and environmental pressure (Grossman and Krueger, 1995), although its empirical robustness has been widely questioned (Stern, 2004). For the GCC, panel and time-series studies generally find that energy consumption and growth remain tightly coupled and that CO₂ emissions continue to rise with income, with little evidence of a turning point (Al-Iriani, 2006; Salahuddin and Gow, 2014; Bekhet et al., 2017). Oman-specific analyses reach similar conclusions and attribute persistent coupling to the energy intensity of oil-financed diversification (Javed and Husain, 2020; Abdel-Gadir and Mohammed, 2024).",
  },
  {
    type: "p",
    text:
      "The second strand addresses energy security and the political economy of transition in producer states. Energy security indicators, including the self-sufficiency ratio, capture availability but not affordability, sustainability or governance (Sovacool and Mukherjee, 2011; Ang et al., 2015). For exporters, the transition presents both a threat to rents and an opportunity to monetise new comparative advantages in low-cost renewable electricity and hydrogen (Goldthau and Westphal, 2019; Gielen et al., 2019). Studies of Oman and the United Arab Emirates show that renewable deployment has been rationalised in part as a means of preserving hydrocarbons for export, attracting foreign investment and projecting a modernised international image (Al-Maamary et al., 2017b; Szalai et al., 2025). Regional reviews document the GCC's renewable targets and readiness gaps (Mondal et al., 2016; Praveen et al., 2020; Almasri and Narayan, 2021), whereas Oman-specific work catalogues resource potential, policy barriers and the green hydrogen agenda (Al-Badi et al., 2011; Amoatey et al., 2022; Marzouk, 2024; Leal-Arcas et al., 2025).",
  },
  {
    type: "p",
    text:
      "The third strand concerns the socio-technical integration of variable renewable energy (VRE) into thermal grids. As VRE penetration rises, its market value declines and system flexibility requirements increase (Denholm and Hand, 2011; Hirth, 2013). In Oman, multi-criteria assessments identify pumped hydro and compressed air storage as the preferred long-duration options (Al-Abri et al., 2024), and studies of rooftop photovoltaics document financial, technical and awareness barriers to distributed generation (Mishrif and Khan, 2024; Venkatachalam et al., 2025). Transition theory emphasises that such barriers are embedded in regimes of institutions, infrastructure and practice rather than in technology alone (Geels, 2002; Sovacool, 2016). Table 1 synthesises the studies most relevant to the present contribution.",
  },
  {
    type: "table",
    n: 1,
    caption: "Synthesis of the literature most relevant to this study.",
    widths: [2000, 1700, 2600, 3060],
    header: ["Study", "Scope", "Approach", "Relevance to this study"],
    rows: [
      ["Nagovnak et al. (2022)", "Austria", "IRES-based balance methodology for the energy transition; Sankey representation", "Methodological template for the matrix and flow diagrams"],
      ["Neelis and Pouwelse (2008)", "Netherlands", "Reconciling feedstock and combustion in chemical-industry statistics", "Precedent for separating LNG feedstock from industrial combustion"],
      ["Charabi et al. (2018)", "Oman", "GHG reduction pathways for a hydrocarbon-based economy", "Policy context for NDC tracking"],
      ["Al-Sarihi and Cherni (2023)", "Oman", "Political economy of renewables in a rentier state", "Explains institutional inertia; motivates the evidence base"],
      ["Szalai et al. (2025)", "UAE, Oman", "Political economy of renewable deployment", "Frames renewables as rent preservation (dual dividend)"],
      ["Salahuddin and Gow (2014); Bekhet et al. (2017)", "GCC", "Econometric growth–energy–emissions nexus", "Evidence of persistent coupling; EKC context"],
      ["Al-Abri et al. (2024)", "Oman", "Fuzzy MCDM of energy storage options", "Grid-integration constraints on the 30% target"],
      ["IEA (2023b); Marzouk (2024)", "Oman", "Renewable hydrogen and planned capacity mix", "Scale of hydrogen-driven VRE build-out"],
      ["Liu et al. (2026)", "Global", "Origin of traded fuels in combustion CO₂ accounting", "Limits of Tier 1 territorial accounting for exporters"],
    ],
  },
  {
    type: "p",
    text:
      "Despite this literature, no peer-reviewed study has published a complete, commodity-by-flow energy balance for Oman that is consistent with the International Recommendations for Energy Statistics (IRES), documents its corrections, and connects the balance directly to emissions and policy analysis. Existing Oman studies rely on aggregate indicators from international databases, which mask the transformation flows that matter most for a gas-exporting economy (Charabi et al., 2018; Abdel-Gadir and Mohammed, 2024).",
  },
  { type: "h2", text: "1.4. Contribution of the study" },
  {
    type: "p",
    text:
      "This paper makes four contributions. First, it presents what is, to our knowledge, the first independently constructed and IRES-compliant National Energy Balance for Oman for the reference year 2025, compiled from primary national statistics and fully documented. Second, it identifies and corrects three structural flaws in legacy accounting, namely the conflation of LNG feedstock with industrial gas consumption, the incomplete integration of the Duqm refinery, and the treatment of thermal electricity as primary energy, and it quantifies the effect of each correction. Third, it introduces explicit closure diagnostics, which reveal an unreconciled refinery feedstock gap and bound its effect on headline indicators. Fourth, it links the balance to an IPCC Tier 1 emissions inventory and a counterfactual analysis of renewable displacement, from which the paper derives the “dual dividend” of renewables in a rentier economy and a set of policy instruments. The remainder of the paper is organised as follows: Section 2 describes the methodology; Section 3 presents the results; Section 4 discusses the political economy of the transition; Section 5 sets out policy implications and limitations; and Section 6 concludes.",
  },

  // ------------------------------------------------------------------ 2
  { type: "h1", text: "2. Methodology and data reconciliation" },
  {
    type: "p",
    text:
      "Fig. 1 summarises the research design. We compile primary data, harmonise units and allocation rules, construct the IRES balance with explicit diagnostics, and use the resulting accounts for emissions, indicator and policy analysis. Diagnostics feed back into data harmonisation, so that a failed closure test triggers a revision of the source data rather than a silent residual.",
  },
  F(1, "Fig01_framework.png", 3468, 2245, "Research framework for the construction and analysis of Oman's 2025 National Energy Balance."),
  { type: "h2", text: "2.1. Analytical framework" },
  {
    type: "p",
    text:
      "We follow the IRES framework of the United Nations Statistics Division (UNSD, 2018), which is mirrored in the World Energy Balances of the International Energy Agency (IEA, 2023a) and in the Eurostat balance methodology (Eurostat, 2021). For each commodity *c*, Total Primary Energy Supply is defined as:",
  },
  { type: "eq", n: 1, text: "TPES~c~ = P~c~ + M~c~ − X~c~ − B~c~ ± ΔS~c~" },
  {
    type: "p",
    text:
      "where *P* is indigenous production, *M* imports, *X* exports, *B* international marine bunkers and Δ*S* the stock change. Supply is allocated between transformation, energy-industry own use, losses and final consumption, and the commodity-level balancing identity is:",
  },
  { type: "eq", n: 2, text: "TFC~c~ = TPES~c~ − TI~c~ + TO~c~ − OU~c~ − L~c~ − SD~c~" },
  {
    type: "p",
    text:
      "where *TI* and *TO* denote transformation inputs and outputs, *OU* own use, *L* transmission and distribution losses and *SD* the statistical difference. We retain *SD* explicitly for every commodity. Because a statistical difference close to zero confirms only arithmetic consistency, we also apply a process-level closure test to each transformation activity *k*, defined as its apparent energy efficiency:",
  },
  { type: "eq", n: 3, text: "η~k~ = Σ~c~ TO~c,k~ / Σ~c~ TI~c,k~ ,   with plausibility condition 0 < η~k~ ≤ 1" },
  {
    type: "p",
    text:
      "Following the IRES physical energy content convention, primary electricity comprises only electricity from sources that are not themselves fuels, which in Oman means solar and wind generation. Electricity from gas-fired plants is a transformation output and does not enter indigenous production (UNSD, 2018; IEA, 2023a).",
  },
  { type: "h2", text: "2.2. Data sources and unit conversion" },
  {
    type: "p",
    text:
      "We compile the balance exclusively from official statistics and primary company data (Table 2). Where a figure could not be sourced and no defensible estimate was possible, it is recorded as an explicit and visible gap rather than as an implicit zero.",
  },
  {
    type: "table",
    n: 2,
    caption: "Principal data sources for the 2025 balance.",
    widths: [2700, 4460, 2200],
    header: ["Source", "Data obtained", "Coverage"],
    rows: [
      ["NCSI Statistical Year Book 2026", "Crude oil production and exports; refinery output (Sohar, Mina Al Fahal); natural gas production and sectoral use; LNG and condensate exports; electricity generation, consumption and sectoral split; GDP; population", "2021–2025"],
      ["Ministry of Energy and Minerals", "Monthly crude oil and condensate production; gas consumption by sector; LPG output", "2025"],
      ["Renewable Energy Bulletin", "Monthly renewable generation by plant and company", "2022–2026"],
      ["Duqm refinery (OQ8) project data", "Crude throughput, foreign crude imports, product slate and exports", "2025"],
      ["Oman Customs external trade data", "Coal and lignite imports and exports by HS code", "2025"],
      ["Bunkering dataset (five ports)", "Monthly marine bunker deliveries (export, import, net)", "2024–2026"],
      ["IPCC (2006)", "Default NCV-based CO₂ emission factors by fuel", "International default"],
      ["OPWP", "Renewable generation share target (30% by 2030)", "Policy target"],
    ],
  },
  {
    type: "p",
    text:
      "We convert physical quantities to thousand tonnes of oil equivalent (ktoe) on a net calorific value basis (1 toe = 41.868 GJ) with the factors in Table 3. For the heterogeneous category of refined products, we derive a single factor as the production-mix-weighted average of IPCC default values for the constituent products and document it as a derived rather than primary factor (IPCC, 2006). The factors are implemented as a conversion calculator in the companion workbook, so that new data can be converted consistently.",
  },
  {
    type: "table",
    n: 3,
    caption: "Unit conversion factors applied in the balance.",
    widths: [2400, 1700, 2300, 2960],
    header: ["Commodity", "Native unit", "Factor", "Basis"],
    rows: [
      ["Crude oil", "kbbl", "0.136 ktoe/kbbl", "Standard density-based conversion"],
      ["Refined products (blended)", "kbbl", "0.145 ktoe/kbbl", "Production-mix-weighted IPCC (2006) values"],
      ["Natural gas", "MMscf", "0.02549 ktoe/MMscf", "Standard gas heat content; 1 toe = 41.868 GJ"],
      ["LNG", "Mt", "1,090 ktoe/Mt", "1.09 toe/t"],
      ["Coal and lignite", "t", "0.00065 ktoe/t", "0.65 ktoe/kt, IPCC-consistent default"],
      ["Electricity", "GWh", "0.086 ktoe/GWh", "Physical energy content (1 GWh = 3.6 TJ)"],
    ],
  },
  { type: "h2", text: "2.3. Sectoral allocation and structural corrections" },
  { type: "h3", text: "2.3.1. Natural gas and LNG feedstock" },
  {
    type: "p",
    text:
      "Natural gas production in 2025 was 2,018,799.2 MMscf (454,706.5 MMscf associated and 1,564,092.7 MMscf non-associated), equivalent to 51,459.2 ktoe. The national category “industrial projects” combines LNG liquefaction feedstock with industrial combustion. We disaggregate it using the estimated LNG feedstock requirement of 599,187 MMscf (15,273.3 ktoe), which we record as a transformation input matched against LNG output derived from reported exports of 11.3 Mt (12,317 ktoe). The remaining industrial gas (10,331 ktoe) is recorded as final consumption in the industrial sector, consistent with the treatment of feedstock and combustion in established industrial energy statistics (Neelis and Pouwelse, 2008). The implied liquefaction efficiency of 80.6% lies within the range expected for large liquefaction trains (Lee et al., 2018). All final gas consumption is allocated to industry because Oman has no distribution network for households or small commercial users.",
  },
  { type: "h3", text: "2.3.2. Crude oil and the Duqm refinery" },
  {
    type: "p",
    text:
      "Crude oil production (365,754.4 kbbl) and exports (307,960.9 kbbl) are taken from the Statistical Year Book (NCSI, 2026). Foreign crude imported for the Duqm refinery (71,094.8 kbbl) is recorded as a crude import, and Duqm's product exports are recorded together with those of the Sohar and Mina Al Fahal system in the export row of the refined products column. Total refined product exports amount to 19,008 ktoe, and total energy exports across all commodities to 73,211.0 ktoe. This correction removes the earlier inconsistency whereby Duqm's output entered the balance without its exports. Duqm is also a candidate site for integrated solar power and desalination, so its energy flows will grow in importance (Gastli et al., 2010).",
  },
  { type: "h3", text: "2.3.3. Electricity, renewables and the primary electricity correction" },
  {
    type: "p",
    text:
      "Total generation (50,973.5 GWh) and consumption (45,033.1 GWh) are taken from official statistics. The difference of 5,940.4 GWh (11.65% of generation) combines transmission and distribution losses with power-station own use, which national statistics do not report separately. Renewable generation is compiled at plant level from the Renewable Energy Bulletin. In the as-compiled workbook, the full 4,383.7 ktoe of generation was entered as indigenous production. Under IRES this double-counts the 13,974 ktoe of gas burnt in power stations. We therefore restate primary electricity as solar and wind generation only (4,509.0 GWh, or 387.8 ktoe) and treat thermal electricity as a transformation output. This correction reduces indigenous production and TPES by 3,995.9 ktoe each and leaves TFC unchanged.",
  },
  { type: "h3", text: "2.3.4. Coal, bunkers and petroleum product allocation" },
  {
    type: "p",
    text:
      "Oman has no domestic coal production. Customs records distinguish coal (HS 2701; 246,603.5 t) from lignite (HS 2704.00.10; 18,153.2 t), with 5,143.9 t of coal re-exported, which gives net supply of 168.7 ktoe used mainly by the cement industry. International marine bunkers (453.8 ktoe in the compiled balance) are derived from port records, which are known to be incomplete, and are excluded from TFC under IRES. No product-by-sector consumption survey exists. We therefore use retail distribution sales (gasoline, diesel and jet fuel; 43,699.8 kbbl or 6,336.5 ktoe) as the observed base and apply an indicative split agreed by the project steering group (70% transport, 15% industry, 5% residential and 10% other). Because this split is indicative, we report a product-specific alternative in which gasoline and jet fuel are allocated wholly to transport (Section 3.2). The gap of 4,772.5 ktoe between implied domestic product availability (11,109.0 ktoe) and retail sales most plausibly reflects fuel oil and LPG delivered directly to industrial and power users, and it is reported as an unallocated residual rather than forced into a sector.",
  },
  { type: "h3", text: "2.3.5. Closure diagnostics" },
  {
    type: "p",
    text:
      "Every commodity column closes with a statistical difference below 1 ktoe. The process-level test of Eq. (3), however, reveals that the refinery account does not close. Recorded crude input to refineries, defined as production less exports plus imports, is 128,888 kbbl (17,528.8 ktoe), whereas reported refinery output is 210,833.1 kbbl (30,570.8 ktoe), which implies η = 1.74. The product-resolved slate (115,140 kbbl, or 16,695 ktoe) is consistent with the recorded crude input (η ≈ 0.95), which suggests that the discrepancy concerns the remaining refinery output, most probably crude delivered to the Duqm special economic zone that is recorded within the crude export series. We do not impute the missing 13,042 ktoe. Instead, we report it transparently in the balance and bound its effect on headline indicators under two hypotheses: that the gap reflects under-recorded production, or that it reflects over-recorded crude exports (Section 3.1).",
  },
  { type: "h2", text: "2.4. Emissions estimation methodology" },
  {
    type: "p",
    text:
      "We estimate territorial, direct-combustion CO₂ emissions with the IPCC (2006) Tier 1 method on an NCV basis (Volume 2, Table 1.4; Appendix A):",
  },
  { type: "eq", n: 4, text: "E~s,f~ = A~s,f~ × EF~f~" },
  {
    type: "p",
    text:
      "where *A* is fuel consumption (toe) of fuel *f* in sector *s* and *EF* the default emission factor (tCO₂/toe). The estimate covers Scope 1 combustion only. It excludes fugitive and flaring emissions, non-combustion process emissions such as clinker calcination, and emissions embodied in exported LNG and products (Elvidge et al., 2018; Liu et al., 2026). We additionally reallocate power-sector emissions to end-use sectors in proportion to electricity consumption, which yields an end-use attribution complementary to the direct-combustion view.",
  },
  {
    type: "p",
    text:
      "Emissions avoided by renewable generation are estimated against a counterfactual in which the same output is supplied by gas-fired plants:",
  },
  { type: "eq", n: 5, text: "ΔE = G~RE~ × EF~grid~ ,   EF~grid~ = E~power~ / G~thermal~" },
  {
    type: "p",
    text:
      "where *G*~RE~ is renewable generation and *EF*~grid~ the implied fleet-average emission factor, computed from 2025 power-sector emissions (32.82 MtCO₂) and thermal generation (46,464.5 GWh) as 0.706 tCO₂/MWh. Because the displaced plant at the margin may be more efficient than the fleet average, we test the sensitivity of the result to marginal factors for open-cycle (0.577 tCO₂/MWh at 35% efficiency) and combined-cycle gas turbines (0.367 tCO₂/MWh at 55% efficiency), in line with the literature on marginal emission factors (Siler-Evans et al., 2012). Gas displaced by renewables is estimated with the fleet-average heat rate (12.6 GJ/MWh) and converted into LNG-equivalent export value at the observed liquefaction efficiency (80.6%) for prices between USD 6 and 14/MMBtu.",
  },

  // ------------------------------------------------------------------ 3
  { type: "h1", text: "3. Results: Oman's 2025 energy architecture" },
  { type: "h2", text: "3.1. Macroeconomic aggregates and self-sufficiency" },
  {
    type: "p",
    text:
      "Table 4 presents the complete IRES balance, and Fig. 2 traces the corresponding energy flows in a Sankey representation (Schmidt, 2008; Soundararajan et al., 2014). Indigenous production totals 101,589.6 ktoe, of which natural gas contributes 50.7%, crude oil 49.0% and solar and wind 0.4%. After imports of 9,841.0 ktoe, exports of 73,211.0 ktoe and bunkers of 453.8 ktoe, TPES is 37,765.8 ktoe. Total Final Consumption is 25,481.7 ktoe, equivalent to 67.5% of TPES.",
  },
  { type: "balance" },
  F(2, "Fig02_sankey.png", 4004, 2714, "Energy flow (Sankey) diagram of Oman's 2025 IRES-restated National Energy Balance (ktoe). The hatched ribbon represents refinery output that is not matched by recorded crude input (Section 2.3.5)."),
  {
    type: "p",
    text:
      "Table 5 and Fig. 3 compare the headline indicators under three accounting states. In the as-compiled workbook, indigenous production was 105,585.5 ktoe and TPES 41,761.7 ktoe, which gave a self-sufficiency ratio (SSR) of 252.8%. Restating primary electricity raises the SSR to 269.0%, because the correction removes the same absolute quantity from a smaller denominator. When the refinery-closure gap is incorporated, the SSR falls to between 199.9% (if crude exports are over-recorded) and 225.6% (if production is under-recorded). Under every accounting state, Oman remains a major net energy exporter that produces two to almost three times its domestic primary requirement.",
  },
  {
    type: "table",
    n: 5,
    caption: "Headline indicators under alternative accounting states, 2025.",
    widths: [3160, 1900, 1900, 2400],
    header: ["Indicator", "As compiled", "IRES-restated", "With refinery closure"],
    rows: [
      ["Indigenous production (ktoe)", "105,585.5", "101,589.6", "101,589.6–114,631.6"],
      ["TPES (ktoe)", "41,761.7", "37,765.8", "50,807.8"],
      ["TFC (ktoe)", "25,481.7", "25,481.7", "25,481.7"],
      ["Self-sufficiency ratio (%)", "252.8", "269.0", "199.9–225.6"],
      ["TFC / TPES (%)", "61.0", "67.5", "50.2"],
      ["Energy intensity (toe per RO million)", "1,040.7", "941.1", "1,266.1"],
      ["Per-capita TPES (kgoe)", "7,792.0", "7,046.4", "9,479.8"],
      ["Renewable share of TPES (%)", "0.93", "1.03", "0.76"],
      ["Memo: GDP (RO million); population", "40,130; 5,359,557", "", ""],
    ],
  },
  F(3, "Fig03_reconciliation.png", 4315, 1762, "Effect of the methodological corrections. (a) Reconciliation of TPES from the as-compiled to the IRES-restated balance. (b) Sensitivity of the self-sufficiency ratio to the accounting state and to the treatment of the refinery-closure gap."),
  {
    type: "p",
    text:
      "Fig. 4 decomposes supply. Natural gas (51,459 ktoe) and crude oil retained for refining (17,529 ktoe) are the positive contributors to TPES, whereas the net export of secondary products (LNG, −12,317 ktoe; refined products and bunkers, −19,462 ktoe) reduces it. On the uses side, conversion losses in LNG trains and power plants (12,934 ktoe) and own use with grid losses (12,391 ktoe) together absorb a quantity of energy comparable to that delivered to final consumers. This pattern characterises an economy in which the energy sector is itself the largest energy user.",
  },
  F(4, "Fig04_supply_aggregates.png", 4581, 1707, "Supply aggregates, 2025. (a) Indigenous production by fuel. (b) Contribution of each commodity to TPES; negative values denote net exports of secondary products. (c) Sources and uses of TPES, which shows the unreconciled refinery gain."),
  {
    type: "p",
    text:
      "Crude oil production averaged 1,002.1 kbbl/d, and 84.2% of output was exported (Fig. 5a). The product-resolved refinery slate (Fig. 5b) is dominated by diesel and gas oil (30.6%), naphtha and other products (24.4%) and the two gasoline grades (27.3%). Natural gas is allocated to LNG feedstock (29.7%), power generation (27.2%), oil-field own use (23.1%) and industrial final consumption (20.1%) (Fig. 6a). Imported coal and lignite contribute 168.7 ktoe (Fig. 6b).",
  },
  F(5, "Fig05_oil.png", 4331, 1702, "Oil account, 2025. (a) Crude oil disposition and refinery throughput (million barrels). (b) Product-resolved refinery output by product (thousand barrels)."),
  F(6, "Fig06_gas_coal.png", 4287, 1643, "(a) Natural gas allocation by use after separation of LNG feedstock (ktoe). (b) Coal and lignite trade by HS code (thousand tonnes)."),
  { type: "h2", text: "3.2. Sectoral consumption asymmetries" },
  {
    type: "p",
    text:
      "Table 6 and Fig. 7a present TFC by sector and carrier. Industry is the largest final consumer (12,150.1 ktoe; 47.7%), and 85.0% of its demand is met by natural gas used in gas-based manufacturing, cement and aluminium smelting. Sohar Aluminium alone operates a captive gas-fired plant of approximately 1,000 MW. The other and unallocated category (21.7%) consists mainly of the off-retail petroleum residual. Transport accounts for 17.4%, and residential, commercial and government buildings together account for 13.1%.",
  },
  {
    type: "table",
    n: 6,
    caption: "Total Final Consumption by sector, 2025 (ktoe).",
    widths: [2160, 1300, 1200, 1300, 1500, 1900],
    header: ["Sector", "TFC (balance)", "Share (%)", "of which electricity", "Principal fuels", "TFC, product-specific split*"],
    rows: [
      ["Industrial", "12,150.1", "47.7", "699.7", "Gas, products, coal", "11,526.2 (45.2%)"],
      ["Other / unallocated", "5,541.3", "21.7", "135.1", "Petroleum (residual)", "4,907.6 (19.3%)"],
      ["Transport", "4,435.5", "17.4", "–", "Gasoline, diesel, jet", "5,893.1 (23.1%)"],
      ["Residential", "1,918.6", "7.5", "1,601.7", "Electricity, LPG", "1,718.3 (6.7%)"],
      ["Commercial", "1,045.9", "4.1", "1,045.9", "Electricity", "1,045.9 (4.1%)"],
      ["Government", "390.3", "1.5", "390.3", "Electricity", "390.3 (1.5%)"],
      ["Total", "25,481.7", "100.0", "3,872.8", "", "25,481.4 (100%)"],
    ],
    note: "*Gasoline and jet fuel allocated wholly to transport, and diesel split according to the retail distribution data (Fig. 7c).",
  },
  {
    type: "p",
    text:
      "Electricity shows a markedly different structure (Fig. 7b and Fig. 8a). Of the 45,033.1 GWh consumed, the residential sector accounts for 41.4%, the commercial sector for 27.0%, industry for 18.1%, government for 10.1% and other users for 3.5%. The residential predominance reflects the space-cooling load of an extreme summer climate under subsidised tariffs (Almasri and Narayan, 2021). The policy implication is a bifurcation of instruments. Tariff reform, building codes and appliance standards address the residential and commercial electricity load, whereas industrial gas pricing, benchmarking and fuel switching address the sector that dominates aggregate final energy demand (Tanaka, 2008). The petroleum allocation is sensitive to the split adopted. Under the product-specific allocation, transport rises to 5,893 ktoe (23.1% of TFC), and the other category falls accordingly (Table 6; Fig. 7c).",
  },
  F(7, "Fig07_sectoral.png", 4223, 2950, "Sectoral consumption, 2025. (a) TFC by sector and carrier (ktoe). (b) Electricity consumption by sector (GWh). (c) Sensitivity of sectoral petroleum consumption to the allocation rule (ktoe)."),
  F(8, "Fig08_electricity.png", 4500, 1702, "Electricity and renewables, 2025. (a) Electricity balance (GWh). (b) Renewable generation by plant (GWh). (c) Renewable share of generation compared with the OPWP 30% and the 20% national trajectory to 2030."),
  { type: "h2", text: "3.3. The renewable energy surge" },
  {
    type: "p",
    text:
      "Renewable generation reached 4,509.0 GWh in 2025, equivalent to 8.85% of generation and 10.01% of consumption, compared with 4.89% of generation in 2024 (Fig. 8c). Three utility-scale photovoltaic plants supplied 97.2% of the total: the Ibri II Solar IPP (1,585.4 GWh), the Sembcorp–Jinko Shine plant (1,420.6 GWh) and Wadi Noor Solar Power (1,375.5 GWh). The Dhofar I Wind IPP contributed 124.0 GWh, and minor purchases contributed 3.5 GWh (Fig. 8b). The renewable share of TPES remains small (1.03%) because renewables enter at their physical energy content, whereas thermal generation carries the conversion losses of gas-fired plants. Reaching OPWP's 30% target requires an average gain of 4.2 percentage points per year to 2030, slightly above the 3.96 points observed between 2024 and 2025. The IEA (2023b) analysis refers to national targets of 20% of electricity by 2030 and 39% by 2040 and finds them cost-effective, which places OPWP’s 30% objective at the ambitious end of the feasible range.",
  },
  { type: "h2", text: "3.4. Greenhouse gas emissions inventory" },
  {
    type: "p",
    text:
      "Direct-combustion CO₂ emissions are estimated at 91.48 MtCO₂ in 2025, equivalent to 17.1 tCO₂ per capita and 2.42 tCO₂ per toe of TPES (Table 7; Fig. 9). Power generation is the largest source (32.82 MtCO₂; 35.9%), followed by industry (27.81 MtCO₂; 30.4%), the other and unallocated category (16.60 MtCO₂; 18.1%) and transport (13.29 MtCO₂; 14.5%). By fuel, natural gas accounts for 57.09 MtCO₂ (62.4%), petroleum products for 33.69 MtCO₂ (36.8%) and coal and lignite for 0.70 MtCO₂ (0.8%). The source report presented these fuel totals in MtCO₂ as if they were percentage shares, which we correct here.",
  },
  {
    type: "table",
    n: 7,
    caption: "Direct-combustion CO₂ emissions by sector and fuel, and end-use attribution, 2025 (MtCO₂).",
    widths: [2160, 1150, 1150, 1000, 1150, 1100, 1650],
    header: ["Sector", "Gas", "Petroleum", "Coal", "Direct total", "Share (%)", "End-use attribution"],
    rows: [
      ["Power generation", "32.82", "–", "–", "32.82", "35.9", "(reallocated)"],
      ["Industrial", "24.27", "2.84", "0.70", "27.81", "30.4", "33.74"],
      ["Other / unallocated", "–", "16.60", "–", "16.60", "18.1", "17.75"],
      ["Transport", "–", "13.29", "–", "13.29", "14.5", "13.29"],
      ["Residential", "–", "0.95", "–", "0.95", "1.0", "14.52"],
      ["Commercial", "–", "–", "–", "–", "–", "8.86"],
      ["Government", "–", "–", "–", "–", "–", "3.31"],
      ["Total", "57.09", "33.69", "0.70", "91.48", "100.0", "91.48"],
    ],
  },
  {
    type: "p",
    text:
      "End-use attribution changes the ranking considerably (Fig. 9a). When power-sector emissions are reallocated in proportion to electricity consumption, residential buildings account for 14.52 MtCO₂ (15.9%), commercial buildings for 8.86 MtCO₂ and industry for 33.74 MtCO₂ (36.9%). Buildings as a whole are therefore responsible for over one-quarter of national CO₂, which the direct-combustion view conceals.",
  },
  F(9, "Fig09_emissions.png", 4407, 1763, "CO₂ emissions, 2025. (a) Direct emissions and emissions attributed through electricity use, by end-use sector. (b) Emissions by fuel. (c) Sector-by-fuel emission matrix (MtCO₂)."),

  // ------------------------------------------------------------------ 4
  { type: "h1", text: "4. Discussion: the political economy of Oman's transition" },
  { type: "h2", text: "4.1. The economics of emissions displacement" },
  {
    type: "p",
    text:
      "Renewable generation in 2025 avoided 3.19 MtCO₂ against the fleet-average counterfactual, a 3.37% reduction relative to a scenario without renewables (Fig. 10). If the displaced plant at the margin is a combined-cycle unit, the avoided quantity falls to 1.66 MtCO₂, and an open-cycle margin gives 2.60 MtCO₂. At OPWP's 30% target and constant 2025 generation, avoided emissions would reach 5.6–10.8 MtCO₂ per year. Each percentage point of renewable share avoids approximately 0.36 MtCO₂ at the fleet-average factor. Expressed in this way, renewable deployment can be stated directly in terms of the metric used for NDC reporting.",
  },
  F(10, "Fig10_avoided_emissions.png", 4284, 1702, "Avoided CO₂ emissions. (a) Avoided emissions as a function of renewable share under three displaced-plant emission factors, with 2025 generation held constant. (b) Range of estimates for 2025 and for the 30% target."),
  {
    type: "p",
    text:
      "The distinctive feature of decarbonization in a rentier economy is that the displaced fuel has an export value. With the fleet-average heat rate, the 2025 renewable output freed 1,356 ktoe of gas (1.51 bcm), which corresponds to roughly 1.0 Mt of LNG after liquefaction losses. At LNG prices between USD 6 and 14/MMBtu, the gross export value of this gas is USD 0.26–0.61 billion per year, and at a 30% share it would rise to USD 0.88–2.06 billion per year (Fig. 11). Renewables therefore yield a dual dividend of emissions abatement and preserved hydrocarbon rent. In import-dependent economies, by contrast, the principal benefit is a lower import bill (Al-Maamary et al., 2017b; Szalai et al., 2025). These values are gross and are not net of liquefaction capacity, contractual constraints or the capital cost of renewables, so they should be read as indicating orders of magnitude.",
  },
  F(11, "Fig11_dual_dividend.png", 4284, 1763, "The dual dividend. (a) Natural gas freed from power generation as a function of renewable share (bcm per year) under fleet-average and CCGT heat rates. (b) Gross LNG-equivalent export value of the freed gas by renewable share and LNG price (USD billion per year)."),
  {
    type: "p",
    text:
      "The dual dividend also helps to explain the political economy of the transition. Because renewables protect rather than erode rents in the short run, they can be supported by the same coalitions that defend the hydrocarbon sector. This finding is consistent with interpretations of Gulf renewables as instruments of rent extension rather than of radical regime change (Szalai et al., 2025). The same logic, however, exposes a limitation: if the freed gas is simply exported or burnt in new domestic industry, global emissions do not fall by the full amount of the territorial saving (Davis et al., 2011; Liu et al., 2026).",
  },
  { type: "h2", text: "4.2. Demand-side management and energy efficiency" },
  {
    type: "p",
    text:
      "Energy efficiency has historically been under-prioritised in the GCC, largely because administered prices weaken incentives to conserve (Fattouh and El-Katiri, 2013; Almasri and Narayan, 2021). The balance quantifies the stakes. At 941 toe per RO million of GDP and 7.0 toe per capita, Oman's energy intensity is high for an upper-middle-income economy. Partial indicators such as the ratio of energy to GDP conflate structural change with efficiency (Patterson, 1996). The total-factor energy efficiency (TFEE) framework, which treats energy as one input alongside labour and capital, offers a more defensible benchmark for both the macroeconomy and industrial plants (Hu and Wang, 2006). Applied to the industrial gas users identified in this balance, TFEE benchmarking would establish efficiency frontiers against which negotiated agreements could be set.",
  },
  {
    type: "p",
    text:
      "On the electricity side, the residential and commercial sectors together consume 68.4% of electricity, mostly for cooling. Cost-reflective tariffs with protection for vulnerable households, mandatory building codes, and IoT-based monitoring and control of heating, ventilation and air conditioning (HVAC) are the instruments most directly supported by the evidence. Unless baseline demand growth is constrained, renewable capacity additions will mainly serve incremental load rather than displace gas. Fig. 12a shows that each additional percentage point of annual demand growth raises the VRE capacity required to reach 30% by 2030 by approximately 0.3 GW. Demand-side efficiency therefore directly lowers the capital cost of the supply-side transition.",
  },
  { type: "h2", text: "4.3. The green hydrogen vanguard" },
  {
    type: "p",
    text:
      "Hydrom's mandate of 1.0–1.25 Mt of renewable hydrogen by 2030, rising to 3.75 Mt by 2040 and 8.5 Mt by 2050, is an infrastructure challenge of a different order of magnitude from the grid transition (IEA, 2023b). Assuming electrolysis at approximately 55 kWh per kg of hydrogen and a hybrid solar–wind capacity factor of about 0.40, producing 1.0–1.25 Mt requires 55–69 TWh of electricity and therefore approximately 16–20 GW of dedicated renewable capacity. This compares with an implied 2025 VRE fleet of approximately 1.7 GW and grid additions of about 5 GW needed for the 30% target (Fig. 12). Marzouk (2024) shows that planned projects would raise renewables to approximately 83% of a total capacity of about 83 GW, almost entirely because of hydrogen. Wind-to-hydrogen and hydrogen refuelling studies confirm that Oman's resources are favourable (Ahshan et al., 2022; Barhoumi et al., 2023), and the IEA estimates cumulative investment of approximately USD 33 billion for 1 Mt by 2030 (IEA, 2023b). The energy balance provides the accounting framework required to verify the additionality of this capacity, that is, to ensure that renewable electricity for electrolysers does not displace grid supply and thereby increase gas burn elsewhere in the system (Amoatey et al., 2025).",
  },
  F(12, "Fig12_capacity.png", 4287, 1699, "Capacity requirements. (a) Additional VRE capacity required to reach a 30% share of generation by 2030, by demand growth rate and capacity factor. (b) Implied 2025 VRE fleet, grid-target additions and hydrogen-dedicated capacity for 2030 (GW)."),
  { type: "h2", text: "4.4. Green finance and value-chain localisation" },
  {
    type: "p",
    text:
      "The capital required for the transition exceeds what the state budget can supply under volatile oil prices. Private capital mobilisation depends on credible taxonomies, environmental, social and governance (ESG) disclosure and bankable offtake. Recent Omani green bonds, sukuk and sustainable finance frameworks indicate growing market depth, but overlapping agency mandates continue to raise transaction costs (Ali, 2025). A unified green taxonomy aligned with established international classifications, such as the EU taxonomy (European Union, 2020), would reduce greenwashing risk and give investors regulatory certainty. Value-chain localisation offers a complementary hedge against supply-chain volatility. JA Solar's planned USD 565 million plant in the Sohar Freezone, with 6 GW of cell and 3 GW of module capacity, would place Oman upstream in the photovoltaic value chain (pv magazine, 2024; Enterprise AM, 2025). Copper deposits and potential lithium brines associated with the Umm as Samim and Mahout sabkhas could similarly anchor a transition-minerals sector (Mishrif and Khan, 2023; IEA, 2021). For these strategies to support decarbonization rather than simply add new energy-intensive industry, their energy demand must be tracked in the balance from the outset.",
  },

  // ------------------------------------------------------------------ 5
  { type: "h1", text: "5. Policy implications and limitations" },
  { type: "h2", text: "5.1. Strategic policy recommendations" },
  {
    type: "p",
    text:
      "Fig. 13 organises the recommendations into supply-side, demand-side and enabling pillars that rest on a common evidence layer, and Table 8 links each instrument to the empirical finding that motivates it.",
  },
  F(13, "Fig13_policy_framework.png", 3468, 2152, "Policy framework that links the energy-balance evidence layer to supply-side, demand-side and enabling instruments and to transition outcomes."),
  {
    type: "table",
    n: 8,
    caption: "Policy instruments, supporting evidence and indicative responsibilities.",
    widths: [2500, 3000, 2160, 1700],
    header: ["Instrument", "Evidence from the balance", "Lead institutions", "Horizon"],
    rows: [
      ["Adopt the balance as the official basis for NDC and net-zero reporting", "Tier 1 inventory of 91.48 MtCO₂ with sector × fuel resolution", "MEM; Environment Authority; NCSI", "Short term"],
      ["Prioritise industrial fuel switching and TFEE benchmarking", "Industry 47.7% of TFC; 24.27 MtCO₂ from industrial gas", "MEM; industrial zones; large consumers", "Medium term"],
      ["Reform electricity tariffs and enforce building codes and HVAC monitoring", "Buildings 78.5% of electricity; 26.7 MtCO₂ end-use attribution", "APSR; municipalities", "Short to medium term"],
      ["Value gas displacement in renewable procurement", "1.51 bcm of gas freed in 2025; USD 0.26–0.61 bn yr⁻¹", "OPWP; Ministry of Finance", "Short term"],
      ["Use the balance to appraise megaprojects (refining, desalination, hydrogen)", "Hydrogen requires 16–20 GW versus about 5 GW for the grid target", "Hydrom; OIA; MEM", "Medium term"],
      ["Benchmark against GCC-STAT and IEA statistics", "IRES-consistent structure enables comparison without ad hoc reconciliation", "NCSI; GCC-STAT", "Ongoing"],
    ],
  },
  {
    type: "p",
    text:
      "Three priorities follow. First, the balance and its emissions inventory should be institutionalised as the evidentiary basis for NDC and net-zero reporting, with an annual update governed by a documented standard operating procedure, so that accounting artefacts of the kind corrected here are not reintroduced (Charabi et al., 2018; Kuunifaa et al., 2026). Second, investment appraisal for refinery expansion, desalination, power siting and hydrogen should draw on the unified dataset rather than on figures maintained separately by individual entities. Third, policy attention should shift towards industrial fuel switching, electrification of process heat and waste-heat recovery, because industry dominates final energy demand (Al-Janabi and Al-Azri, 2020; Tanaka, 2008).",
  },
  { type: "h2", text: "5.2. Methodological limitations and future work" },
  {
    type: "p",
    text:
      "Table 9 catalogues the remaining data gaps. The most material is the refinery-closure gap of 13,042 ktoe, which affects TPES and the SSR but not TFC or the emissions inventory, both of which are built from observed end-use and transformation data. Its resolution requires the reconciliation of NCSI crude disposition statistics with OQ8 throughput records and the recording of crude deliveries to the Duqm special economic zone. Other limitations include incomplete marine bunkering data, the absence of company-reported energy data for cement and Sohar Aluminium, the lack of biomass statistics, stock changes assumed to be zero, and the indicative petroleum allocation. The Tier 1 inventory excludes fugitive methane, flaring and process emissions, all of which are significant in an upstream-intensive economy (Elvidge et al., 2018). Future work should build a consistent time series for 2015–2025, which would enable index decomposition of emission drivers and econometric testing of decoupling, and should move key categories to Tier 2 factors using measured fuel properties.",
  },
  {
    type: "table",
    n: 9,
    caption: "Remaining data gaps and their effect on results.",
    widths: [2700, 3700, 2960],
    header: ["Gap", "Effect", "Required action"],
    rows: [
      ["Refinery feedstock closure (13,042 ktoe)", "TPES and SSR uncertain (SSR 200–269%); TFC unaffected", "Reconcile NCSI crude exports with OQ8 throughput and Duqm SEZ deliveries"],
      ["Marine bunkering", "Bunkers (453.8 ktoe) indicative", "Port-level reconciliation with Ministry of Transport and port operators"],
      ["Cement and Sohar Aluminium energy use", "Industrial fuel mix partly estimated", "Company-reported metered consumption"],
      ["Petroleum products by sector", "Transport 17.4–23.1% of TFC", "Distribution-company and vehicle-fleet surveys"],
      ["Biomass", "Recorded as explicit gap", "Survey of traditional biomass and waste-to-energy"],
      ["Stock changes", "Assumed zero", "Storage-level reporting"],
      ["Non-combustion emissions", "Fugitive, flaring and process CO₂ excluded", "Extend inventory to IPCC Tier 2 for oil and gas and cement"],
    ],
  },

  // ------------------------------------------------------------------ 6
  { type: "h1", text: "6. Conclusion" },
  {
    type: "p",
    text:
      "This paper has constructed an IRES-compliant National Energy Balance for Oman for 2025, corrected three structural flaws in legacy accounting, and connected the balance to an emissions inventory and a political-economy analysis of the transition. Oman remains overwhelmingly a hydrocarbon economy. It produces 101.6 Mtoe, against TPES of 37.8 Mtoe (an SSR of 200–269% depending on refinery reconciliation), and it emits 91.48 MtCO₂ from fuel combustion, of which 62.4% derives from natural gas. Industry dominates final energy demand, whereas households dominate electricity demand, so the two segments call for distinct policy instruments.",
  },
  {
    type: "p",
    text:
      "The 2025 data also show that the objectives of Oman Vision 2040 are technically and economically attainable. Renewable generation nearly doubled its share to 8.85% within a single year and displaced 1.5 bcm of gas and up to 3.19 MtCO₂. In a rentier state, this displacement yields a dual dividend of climate mitigation and preserved export rent, which helps explain why renewables have gained political traction. The same dividend, however, will not deliver deep decarbonization on its own. Decoupling economic growth from fossil fuel use requires supply-side expansion of solar, wind, storage and hydrogen to be integrated with stringent demand-side efficiency, subsidy reform and an annually maintained, transparent energy balance that allows progress to be verified.",
  },
];

const backMatter = [
  { type: "h1", text: "CRediT authorship contribution statement" },
  { type: "p", text: "**[Author 1]:** Conceptualization, Methodology, Data curation, Formal analysis, Writing – original draft. **[Author 2]:** Validation, Visualization, Writing – review & editing. **[Author 3]:** Supervision, Writing – review & editing. [Edit to reflect actual contributions.]" },
  { type: "h1", text: "Declaration of competing interest" },
  { type: "p", text: "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper." },
  { type: "h1", text: "Funding" },
  { type: "p", text: "[State funding sources, or: This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.]" },
  { type: "h1", text: "Data availability" },
  { type: "p", text: "The energy balance workbook, conversion calculator and the Python scripts used to generate all figures are available from the corresponding author on reasonable request. [Alternatively, provide a repository DOI.]" },
  { type: "h1", text: "Declaration of generative AI and AI-assisted technologies in the writing process" },
  { type: "p", text: "During the preparation of this work the authors used an AI assistant (Claude, Anthropic) to support drafting, figure scripting and language editing. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the publication." },
  { type: "h1", text: "Acknowledgements" },
  { type: "p", text: "The authors thank the National Energy Balance Unit, the National Centre for Statistics and Information and the Ministry of Energy and Minerals for providing data. [Edit as appropriate.]" },
];

const appendixA = {
  caption: "Table A.1. IPCC (2006) default carbon contents and CO₂ emission factors (NCV basis).",
  widths: [2800, 2160, 2200, 2200],
  header: ["Fuel", "Carbon content (kg C/GJ)", "EF (kg CO₂/TJ)", "EF (tCO₂/toe)"],
  rows: [
    ["Crude oil", "20.0", "73,300", "3.0689"],
    ["Motor gasoline", "18.9", "69,300", "2.9015"],
    ["Jet kerosene", "19.5", "71,500", "2.9936"],
    ["Gas/diesel oil", "20.2", "74,100", "3.1024"],
    ["LPG", "17.2", "63,100", "2.6419"],
    ["Residual fuel oil", "21.1", "77,400", "3.2406"],
    ["Naphtha/other", "20.0", "73,300", "3.0689"],
    ["Natural gas", "15.3", "56,100", "2.3488"],
    ["Anthracite (coal)", "26.8", "98,300", "4.1156"],
    ["Lignite", "27.6", "101,000", "4.2287"],
    ["Petroleum coke", "26.6", "97,500", "4.0821"],
  ],
  note: "Source: IPCC (2006), Volume 2, Chapter 1, Table 1.4.",
};

const appendixB = {
  caption: "Table B.1. Priority indicator set for institutional monitoring (dashboard specification).",
  widths: [500, 2700, 1900, 1700, 2560],
  header: ["#", "Indicator", "2025 value (restated)", "Visual", "Computation / source field"],
  rows: [
    ["1", "Total Primary Energy Supply", "37,765.8 ktoe", "KPI card", "Balance, TPES row"],
    ["2", "Total Final Consumption", "25,481.7 ktoe", "KPI card", "Balance, TFC row"],
    ["3", "Self-sufficiency ratio", "269.0% (200–269%)", "Gauge", "Production ÷ TPES"],
    ["4", "Refinery output by product", "Fig. 5b", "Bar", "Oil products sheet"],
    ["5", "Electricity consumption by sector", "Fig. 7b", "Bar", "Electricity by sector table"],
    ["6", "TFC by sector and carrier", "Fig. 7a", "Stacked bar", "Balance, sector block"],
    ["7", "Renewable share of TPES", "1.03%", "Gauge", "Primary RE ÷ TPES"],
    ["8", "Renewable share of generation", "8.85%", "Gauge + trend", "Electricity sheet"],
    ["9", "Emission reduction from renewables", "3.37% (1.7–3.2 MtCO₂)", "Gauge", "Avoided ÷ counterfactual"],
    ["10", "Total national CO₂ emissions", "91.48 MtCO₂", "KPI + trend", "Emissions baseline sheet"],
  ],
};

const references = [
  "Abdel-Gadir, S.E.M. and Mohammed, M.G.A. (2024) ‘Oman’s green horizon: steering towards sustainability through decarbonization and energy transition’, *Sustainability*, 16(21), 9375. https://doi.org/10.3390/su16219375",
  "Ahshan, R., Onen, A. and Al-Badi, A.H. (2022) ‘Assessment of wind-to-hydrogen (Wind-H2) generation prospects in the Sultanate of Oman’, *Renewable Energy*, 200, pp. 271–282. https://doi.org/10.1016/j.renene.2022.09.116",
  "Al-Abri, Z.M., Alawasa, K.M., Al-Abri, R.S., Al-Hinai, A.S. and Awad, A.S.A. (2024) ‘Multi-criteria decision-making approach for optimal energy storage system selection and applications in Oman’, *Energies*, 17(20), 5197. https://doi.org/10.3390/en17205197",
  "Al-Badi, A. and AlMubarak, I. (2019) ‘Growing energy demand in the GCC countries’, *Arab Journal of Basic and Applied Sciences*, 26(1), pp. 488–496. https://doi.org/10.1080/25765299.2019.1687396",
  "Al-Badi, A.H., Malik, A. and Gastli, A. (2011) ‘Sustainable energy usage in Oman—opportunities and barriers’, *Renewable and Sustainable Energy Reviews*, 15(8), pp. 3780–3788. https://doi.org/10.1016/j.rser.2011.06.007",
  "Ali, M.J. (2025) ‘The impact of green financing in advancing renewable energy and smart infrastructure in Oman’, *International Journal of Research and Innovation in Social Science*, 9(9), pp. 8574–8593. https://doi.org/10.47772/IJRISS.2025.909000701",
  "Al-Iriani, M.A. (2006) ‘Energy–GDP relationship revisited: an example from GCC countries using panel causality’, *Energy Policy*, 34(17), pp. 3342–3350.",
  "Al-Janabi, A. and Al-Azri, N. (2020) ‘Effect of recovering the industrial waste heat in Oman on energy and environment’, *Energy Reports*, 6, pp. 526–531. https://doi.org/10.1016/j.egyr.2020.11.203",
  "Al-Maamary, H.M.S., Kazem, H.A. and Chaichan, M.T. (2017a) ‘Climate change: the game changer in the Gulf Cooperation Council region’, *Renewable and Sustainable Energy Reviews*, 76, pp. 555–576. https://doi.org/10.1016/j.rser.2017.03.048",
  "Al-Maamary, H.M.S., Kazem, H.A. and Chaichan, M.T. (2017b) ‘The impact of oil price fluctuations on common renewable energies in GCC countries’, *Renewable and Sustainable Energy Reviews*, 75, pp. 989–1007. https://doi.org/10.1016/j.rser.2016.11.079",
  "Almasri, R.A. and Narayan, S. (2021) ‘A recent review of energy efficiency and renewable energy in the Gulf Cooperation Council (GCC) region’, *International Journal of Green Energy*, 18(14), pp. 1441–1468. https://doi.org/10.1080/15435075.2021.1904941",
  "Al-Sarihi, A. and Cherni, J.A. (2023) ‘Political economy of renewable energy transition in rentier states: the case of Oman’, *Environmental Policy and Governance*, 33(4), pp. 423–439.",
  "Amoatey, P., Al-Hinai, A., Al-Mamun, A. and Said Baawain, M. (2022) ‘A review of recent renewable energy status and potentials in Oman’, *Sustainable Energy Technologies and Assessments*, 51, 101919. https://doi.org/10.1016/j.seta.2021.101919",
  "Amoatey, P., Al-Nadabi, A., Chen, M., Nikoo, M.R., Al-Maktoumi, A., Al-Hinai, A. and Izady, A. (2025) ‘Transition to sustainable hydrogen energy in Oman: implication for future socio-economic transformation and environmental well-being’, *Environment, Development and Sustainability*, 27(7), pp. 15213–15234. https://doi.org/10.1007/s10668-024-04657-8",
  "Ang, B.W., Choong, W.L. and Ng, T.S. (2015) ‘Energy security: definitions, dimensions and indexes’, *Renewable and Sustainable Energy Reviews*, 42, pp. 1077–1093. https://doi.org/10.1016/j.rser.2014.10.064",
  "Argus Media (2023) ‘COP: Oman updates NDC with more ambitious 2030 goal’, *Argus Media*, 30 November. Available at: https://www.argusmedia.com/en/news-and-insights/latest-market-news/2514405-cop-oman-updates-ndc-with-more-ambitious-2030-goal",
  "Barhoumi, E.M., Salhi, M.S., Okonkwo, P.C., Ben Belgacem, I., Farhani, S., Zghaibeh, M. and Bacha, F. (2023) ‘Techno-economic optimization of wind energy based hydrogen refueling station case study Salalah city Oman’, *International Journal of Hydrogen Energy*, 48, pp. 9529–9539. https://doi.org/10.1016/j.ijhydene.2022.12.148",
  "Beblawi, H. and Luciani, G. (eds) (1987) *The Rentier State*. London: Croom Helm.",
  "Bekhet, H.A., Matar, A. and Yasmin, T. (2017) ‘CO2 emissions, energy consumption, economic growth, and financial development in GCC countries: dynamic simultaneous equation models’, *Renewable and Sustainable Energy Reviews*, 70, pp. 117–132. https://doi.org/10.1016/j.rser.2016.11.089",
  "Charabi, Y., Al-Awadhi, T. and Choudri, B.S. (2018) ‘Strategic pathways and regulatory choices for effective GHG reduction in hydrocarbon based economy: case of Oman’, *Energy Reports*, 4, pp. 653–659. https://doi.org/10.1016/j.egyr.2018.10.005",
  "Davis, S.J., Peters, G.P. and Caldeira, K. (2011) ‘The supply chain of CO2 emissions’, *Proceedings of the National Academy of Sciences*, 108(45), pp. 18554–18559. https://doi.org/10.1073/pnas.1107409108",
  "Denholm, P. and Hand, M. (2011) ‘Grid flexibility and storage required to achieve very high penetration of variable renewable electricity’, *Energy Policy*, 39(3), pp. 1817–1830. https://doi.org/10.1016/j.enpol.2011.01.019",
  "Elvidge, C.D., Bazilian, M.D., Zhizhin, M., Ghosh, T., Baugh, K. and Hsu, F.C. (2018) ‘The potential role of natural gas flaring in meeting greenhouse gas mitigation targets’, *Energy Strategy Reviews*, 20, pp. 156–162. https://doi.org/10.1016/j.esr.2017.12.012",
  "Enterprise AM (2025) ‘Sohar Freezone inks land agreement for USD 565 mn solar cell plant’, *Enterprise AM*, 30 April. Available at: https://enterpriseam.com/logistics/2025/04/30/sohar-freezone-inks-land-agreement-for-usd-565-mn-solar-cell-plant/",
  "European Union (2020) ‘Regulation (EU) 2020/852 of the European Parliament and of the Council of 18 June 2020 on the establishment of a framework to facilitate sustainable investment’, *Official Journal of the European Union*, L 198, pp. 13–43.",
  "Eurostat (2021) *Energy Balance Guide: Methodology Guide for the Construction of Energy Balances*. Luxembourg: European Commission.",
  "Fattouh, B. and El-Katiri, L. (2013) ‘Energy subsidies in the Middle East and North Africa’, *Energy Strategy Reviews*, 2(1), pp. 108–115. https://doi.org/10.1016/j.esr.2012.11.004",
  "Gastli, A., Charabi, Y. and Zekri, S. (2010) ‘GIS-based assessment of combined CSP electric power and seawater desalination plant for Duqum—Oman’, *Renewable and Sustainable Energy Reviews*, 14(2), pp. 821–827. https://doi.org/10.1016/j.rser.2009.08.020",
  "Geels, F.W. (2002) ‘Technological transitions as evolutionary reconfiguration processes: a multi-level perspective and a case-study’, *Research Policy*, 31(8–9), pp. 1257–1274. https://doi.org/10.1016/S0048-7333(02)00062-8",
  "Gielen, D., Boshell, F., Saygin, D., Bazilian, M.D., Wagner, N. and Gorini, R. (2019) ‘The role of renewable energy in the global energy transformation’, *Energy Strategy Reviews*, 24, pp. 38–50. https://doi.org/10.1016/j.esr.2019.01.006",
  "Goldthau, A. and Westphal, K. (2019) ‘Why the global energy transition does not mean the end of the petrostate’, *Global Policy*, 10(2), pp. 279–283. https://doi.org/10.1111/1758-5899.12649",
  "Grossman, G.M. and Krueger, A.B. (1995) ‘Economic growth and the environment’, *The Quarterly Journal of Economics*, 110(2), pp. 353–377. https://doi.org/10.2307/2118443",
  "Hirth, L. (2013) ‘The market value of variable renewables: the effect of solar wind power variability on their relative price’, *Energy Economics*, 38, pp. 218–236. https://doi.org/10.1016/j.eneco.2013.02.004",
  "Hu, J.-L. and Wang, S.-C. (2006) ‘Total-factor energy efficiency of regions in China’, *Energy Policy*, 34(17), pp. 3206–3217. https://doi.org/10.1016/j.enpol.2005.06.015",
  "IEA (2021) *The Role of Critical Minerals in Clean Energy Transitions*. Paris: International Energy Agency.",
  "IEA (2023a) *World Energy Balances: Database Documentation*. Paris: International Energy Agency.",
  "IEA (2023b) *Renewable Hydrogen from Oman: A Producer Economy in Transition*. Paris: International Energy Agency.",
  "IPCC (2006) *2006 IPCC Guidelines for National Greenhouse Gas Inventories, Volume 2: Energy*. Prepared by the National Greenhouse Gas Inventories Programme, Eggleston, H.S., Buendia, L., Miwa, K., Ngara, T. and Tanabe, K. (eds). Hayama: Institute for Global Environmental Strategies.",
  "Javed, S. and Husain, U. (2020) ‘An ARDL investigation on the nexus of oil factors and economic growth: a time-series evidence from Sultanate of Oman’, *Cogent Economics & Finance*, 8(1), 1838418. https://doi.org/10.1080/23322039.2020.1838418",
  "Krane, J. (2019) *Energy Kingdoms: Oil and Political Survival in the Persian Gulf*. New York: Columbia University Press.",
  "Kuunifaa, C.B., Dzamesi, S.K.A., Kabo-Bah, A.T., Domfeh, M.K., Tutu-Benefoh, D. and Sey, N.E.N. (2026) ‘The challenges of greenhouse gas emission reporting in emerging economies: lessons from Ghana’s energy sector’, *Energy and Climate Change*, 7, 100249. https://doi.org/10.1016/j.egycc.2026.100249",
  "Lahn, G. and Stevens, P. (2011) *Burning Oil to Keep Cool: The Hidden Energy Crisis in Saudi Arabia*. London: Chatham House.",
  "Leal-Arcas, R., Almashloum, S., Jazzar, R., Bin Saleh, N. and Almunifi, R. (2025) ‘Energy policy of Oman: pursuing decarbonization’, *Energies*, 18(5), 1270. https://doi.org/10.3390/en18051270",
  "Lee, I., Park, J. and Moon, I. (2018) ‘Key issues and challenges on the liquefied natural gas (LNG) value chain: a review from the process systems engineering point-of-view’, *Industrial & Engineering Chemistry Research*, 57(17), pp. 5805–5818. https://doi.org/10.1021/acs.iecr.7b03899",
  "Liu, B., Shan, Y., Guan, Y., Davis, S.J., Hang, Y., Jing, L., Ji, X., Wang, W. and Hubacek, K. (2026) ‘Global combustion CO2 accounting neglects the origin of traded fossil fuels’, *Environmental Science & Technology*, 60(36), pp. 25385–25396. https://doi.org/10.1021/acs.est.6c01630",
  "Marzouk, O.A. (2024) ‘Portrait of the decarbonization and renewables penetration in Oman’s energy mix, motivated by Oman’s national green hydrogen plan’, *Energies*, 17(19), 4769. https://doi.org/10.3390/en17194769",
  "Mishrif, A. and Khan, A. (2023) ‘Clean energy transition through the sustainable exploration and use of lithium in Oman’, *Sustainability*, 15(20), 15173. https://doi.org/10.3390/su152015173",
  "Mishrif, A. and Khan, A. (2024) ‘Non-industrial solar energy use, barriers, and readiness: case study of Oman’, *Energies*, 17(16), 3917. https://doi.org/10.3390/en17163917",
  "Mondal, M.A.H., Hawila, D., Kennedy, S. and Mezher, T. (2016) ‘The GCC countries RE-readiness: strengths and gaps for development of renewable energy technologies’, *Renewable and Sustainable Energy Reviews*, 54, pp. 1114–1128. https://doi.org/10.1016/j.rser.2015.10.098",
  "Nagovnak, P., Kienberger, T., Baumann, M., Binderbauer, P. and Vouk, T. (2022) ‘Improving the methodology of national energy balances to adapt to the energy transition’, *Energy Strategy Reviews*, 44, 100994. https://doi.org/10.1016/j.esr.2022.100994",
  "NCSI (2026) *Statistical Year Book 2026*. Muscat: National Centre for Statistics and Information.",
  "Neelis, M.L. and Pouwelse, J.W. (2008) ‘Towards consistent and reliable Dutch and international energy statistics for the chemical industry’, *Energy Policy*, 36(7), pp. 2719–2733. https://doi.org/10.1016/j.enpol.2008.03.024",
  "OPWP (2024) *OPWP’s 7-Year Statement (2024–2030)*. Muscat: Oman Power and Water Procurement Company.",
  "Patterson, M.G. (1996) ‘What is energy efficiency? Concepts, indicators and methodological issues’, *Energy Policy*, 24(5), pp. 377–390. https://doi.org/10.1016/0301-4215(96)00017-1",
  "Praveen, R.P., Keloth, V., Abo-Khalil, A.G., Alghamdi, A.S., Eltamaly, A.M. and Tlili, I. (2020) ‘An insight to the energy policy of GCC countries to meet renewable energy targets of 2030’, *Energy Policy*, 147, 111864. https://doi.org/10.1016/j.enpol.2020.111864",
  "pv magazine (2024) ‘JA Solar to invest in solar manufacturing hub in Oman’, *pv magazine*, 24 December.",
  "Salahuddin, M. and Gow, J. (2014) ‘Economic growth, energy consumption and CO2 emissions in Gulf Cooperation Council countries’, *Energy*, 73, pp. 44–58. https://doi.org/10.1016/j.energy.2014.05.054",
  "Schmidt, M. (2008) ‘The Sankey diagram in energy and material flow management’, *Journal of Industrial Ecology*, 12(1), pp. 82–94. https://doi.org/10.1111/j.1530-9290.2008.00004.x",
  "Siler-Evans, K., Azevedo, I.L. and Morgan, M.G. (2012) ‘Marginal emissions factors for the U.S. electricity system’, *Environmental Science & Technology*, 46(9), pp. 4742–4748. https://doi.org/10.1021/es300145v",
  "Soundararajan, K., Ho, H.K. and Su, B. (2014) ‘Sankey diagram framework for energy and exergy flows’, *Applied Energy*, 136, pp. 1035–1042. https://doi.org/10.1016/j.apenergy.2014.08.070",
  "Sovacool, B.K. (2016) ‘How long will it take? Conceptualizing the temporal dynamics of energy transitions’, *Energy Research & Social Science*, 13, pp. 202–215. https://doi.org/10.1016/j.erss.2015.12.020",
  "Sovacool, B.K. and Mukherjee, I. (2011) ‘Conceptualizing and measuring energy security: a synthesized approach’, *Energy*, 36(8), pp. 5343–5355. https://doi.org/10.1016/j.energy.2011.06.043",
  "Stern, D.I. (2004) ‘The rise and fall of the environmental Kuznets curve’, *World Development*, 32(8), pp. 1419–1439. https://doi.org/10.1016/j.worlddev.2004.03.004",
  "Sultanate of Oman (2020) *Oman Vision 2040*. Muscat: Oman Vision 2040 Implementation Follow-up Unit.",
  "Szalai, M., Shamieh, R. and Colombo, M. (2025) *Cutting through the Green Hype: The Political Economy of Renewable Energy in the UAE and Oman*. The Hague: Clingendael Institute.",
  "Tanaka, K. (2008) ‘Assessment of energy efficiency performance measures in industry and their application for policy’, *Energy Policy*, 36(8), pp. 2887–2902. https://doi.org/10.1016/j.enpol.2008.03.032",
  "UNSD (2018) *International Recommendations for Energy Statistics (IRES)*. Statistical Papers, Series M, No. 93. New York: United Nations.",
  "Venkatachalam, S.D., Al Nadabi, A., Al Shukaili, A.A., Al Hinai, A.S., Al Shuaili, A.S. and Al Shukaili, I.S. (2025) ‘Performance and suitability analysis of rooftop solar PV in Oman: a case study of university branches’, *Heliyon*, 11, e42578. https://doi.org/10.1016/j.heliyon.2025.e42578",
];

module.exports = { meta, abbreviations, body, backMatter, appendixA, appendixB, references };
