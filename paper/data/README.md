# Data package: Reconciled energy accounts for Oman, 2015–2025

This package reproduces every number, table and figure in the manuscript
"Closing the books of a rentier energy economy: reconciled energy accounts, CO₂ drivers and the renewable dual dividend in Oman, 2015–2025".

## Contents

| File | Description |
|---|---|
| `reconciled_balance_2025_ktoe.csv` | Reconciled 2025 energy balance (Table 5), ktoe |
| `co2_inventory_2025.csv` | CO₂ from fuel combustion by IPCC category, 2025 (Mt) |
| `monte_carlo_summary.csv` | 5th, 50th and 95th percentiles of key indicators (10,000 draws) |
| `mc_draws.npz` | All Monte Carlo draws (NumPy) |
| `timeseries_2015_2024.csv` | Population, GDP, primary energy, CO₂ by fuel, electricity (from Our World in Data) |
| `results.json` | Full model output used by the figure and manuscript scripts |
| `external/owid-*-data_oman.csv` | Oman rows of the Our World in Data CO₂ and energy datasets (CC BY 4.0) |
| `../scripts/model.py` | Reconciliation, emissions, Monte Carlo and LMDI model |
| `../scripts/make_figures.py` | Figure generation |
| `../scripts/build_docx.js` | Manuscript build |

## Reproduce

```
pip install numpy matplotlib
npm install docx
cd scripts
python model.py && python make_figures.py && node build_docx.js
```

## Key results (central case, 90% interval)

* TPES: 38,923 ktoe (37,101–40,669)
* Self-sufficiency ratio: 235.1% (228.3–242.9)
* CO₂ from fuel combustion: 88.1 Mt (83.4–92.6)
* Avoided CO₂ from renewables: 2.02 Mt (1.76–2.39)

## Inputs

The 2025 activity data are aggregate national statistics (NCSI Statistical Year Book 2026; Ministry of Energy and Minerals; Renewable Energy Bulletin; customs and port records), entered as constants in `model.py` (`OBS`). No confidential company-level data are included.

## Licence

Data and code: CC BY 4.0. The Our World in Data extracts remain under their original CC BY 4.0 licence.
