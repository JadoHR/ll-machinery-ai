# L&L Machinery - Intelligent Manufacturing & Price Estimation (ML prototype)

Industrial Engineering internship project. Python, scikit-learn, XGBoost, Streamlit.

## DATA PROVENANCE
- `01_Data/*.csv` = slots for REAL company data. They contain **headers only** until real records are added.
- `01_Data/simulated/SIMULATED_*.csv` = artificial demonstration data from arbitrary formulas.
  **Not L&L data. Never report results from it as company performance.**

## Structure
| Folder | Purpose |
|---|---|
| 01_Data | Real data slots, `simulated/`, `processed/` |
| 02_Notebooks | 00 setup + simulated data (working); 01-03 to be built step by step |
| 03_Models | Saved models (after notebook 02) |
| 04_Evaluation | Data dictionary, model comparison |
| 05_Dashboard | Streamlit app (placeholder) |
| src | Reusable Python modules (config, validation, data generation) |

## How to use in Google Colab
Upload the folder to Google Drive (My Drive/LL_MACHINERY_AI_PROJECT), open
`02_Notebooks/00_setup_and_simulated_data.ipynb` in Colab, and run all cells.
