# L&L Machinery — Intelligent Manufacturing & Price Estimation Prototype

A research and internship prototype for machine-price estimation and production monitoring.

## Project structure
- `01_Data/`: company-data templates, simulated data, and processed data
- `02_Notebooks/`: setup, exploration, price modelling, and production modelling
- `03_Models/`: trained model artifacts (not yet generated)
- `04_Evaluation/`: data dictionary and model evaluation outputs
- `05_Dashboard/`: Streamlit dashboard (currently a placeholder)
- `src/`: reusable configuration, synthetic-data generation, and validation modules

## Data integrity
Files in `01_Data/simulated/` are synthetic examples generated from arbitrary formulas. They are **not** L&L Machinery data and must not be used to claim company-level model accuracy. CSV templates directly under `01_Data/` are header-only templates. Use company records only with permission and anonymize confidential information before external sharing.

## Current status
- [x] Organize repository structure
- [x] Synthetic data generator and validation utilities
- [ ] Implement data exploration and cleaning
- [ ] Implement and evaluate price prediction
- [ ] Implement production-status and lead-time prediction
- [ ] Connect dashboard to validated models

## Google Colab
Open notebooks from `02_Notebooks/`. The setup notebook searches common Drive locations; edit its `PROJECT_ROOT` cell if your folder is stored elsewhere.

## Install dependencies
```bash
pip install -r requirements.txt
```

No trained models or validated company predictions are included yet.
