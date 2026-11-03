"""
config.py - Central configuration for the L&L Machinery ML prototype.

Everything that other modules need to agree on lives here:
folder layout, random seed, data-provenance labels and the CSV schemas.
Change a column name HERE once, and every module follows.
"""
from pathlib import Path

# ---------------------------------------------------------------- folders
# Root = the folder that contains 01_Data, 02_Notebooks ... (parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIRS = {
    "raw":       PROJECT_ROOT / "01_Data",               # REAL company data only
    "simulated": PROJECT_ROOT / "01_Data" / "simulated", # SIMULATED demo data only
    "processed": PROJECT_ROOT / "01_Data" / "processed", # cleaned, model-ready
    "notebooks": PROJECT_ROOT / "02_Notebooks",
    "models":    PROJECT_ROOT / "03_Models",             # saved model files
    "reports":   PROJECT_ROOT / "04_Evaluation",         # metric tables, figures
    "app":       PROJECT_ROOT / "05_Dashboard",          # Streamlit app
}

# Names of the three real-data files (headers only until you fill them)
FILES = {
    "specs":      "machine_specifications.csv",
    "prices":     "historical_prices.csv",
    "production": "production_records.csv",
}

RANDOM_STATE = 42  # fixed seed -> reproducible results you can defend

# ------------------------------------------------------ data provenance
SOURCE_REAL = "REAL"
SOURCE_SIM = "SIMULATED"
SIM_PREFIX = "SIMULATED_"   # every simulated file name must start with this


def ensure_dirs():
    """Create the project folder tree if it does not exist."""
    for d in DIRS.values():
        d.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------- schemas
# column: (kind, description, required)   kind in {str, num, int, date, bool}
SPEC_SCHEMA = {   # -> machine_specifications.csv  (one row per quotation)
    "quote_id":                  ("str",  "Unique quotation ID (links to historical_prices)", True),
    "machine_type":              ("str",  "CNC or Conventional", True),
    "model_series":              ("str",  "Model / series name", True),
    "swing_over_bed_mm":         ("num",  "Swing over bed (mm)", True),
    "distance_between_centers_mm": ("num", "Distance between centers (mm)", True),
    "spindle_bore_mm":           ("num",  "Spindle bore diameter (mm)", True),
    "spindle_motor_kw":          ("num",  "Main spindle motor power (kW)", True),
    "chuck_size_inch":           ("num",  "Chuck size (inch)", False),
    "turret_stations":           ("int",  "Turret tool stations (0 for conventional)", False),
    "live_tooling":              ("bool", "Live tooling fitted (1/0)", False),
    "bar_feeder":                ("bool", "Bar feeder fitted (1/0)", False),
    "chip_conveyor":             ("bool", "Chip conveyor fitted (1/0)", False),
    "tailstock_type":            ("str",  "manual / hydraulic / programmable", False),
    "controller":                ("str",  "CNC controller brand/type", False),
    "data_source":               ("str",  "REAL or SIMULATED", True),
}

PRICE_SCHEMA = {  # -> historical_prices.csv  (one row per quotation)
    "quote_id":                  ("str",  "Unique quotation ID (links to machine_specifications)", True),
    "quote_date":                ("date", "Date the quotation was issued", True),
    "customer_region":           ("str",  "Customer region/market", False),
    "material_cost":             ("num",  "Material/purchased-parts cost", False),
    "labor_hours":               ("num",  "Estimated labour hours", False),
    "manufacturing_cost":        ("num",  "Total manufacturing cost", False),
    "quoted_price":              ("num",  "First quoted price", False),
    "final_selling_price":       ("num",  "TARGET: price actually agreed", True),
    "data_source":               ("str",  "REAL or SIMULATED", True),
}

PRODUCTION_SCHEMA = {
    "order_id":                  ("str",  "Unique production order ID", True),
    "order_date":                ("date", "Date order was released to production", True),
    "machine_type":              ("str",  "CNC or Conventional", True),
    "model_series":              ("str",  "Model / series name", True),
    "quantity":                  ("int",  "Units in the order", True),
    "n_custom_options":          ("int",  "Number of customer-specific options", False),
    "open_orders_at_order_date": ("int",  "Open orders in the shop when released (workload)", False),
    "planned_lead_time_days":    ("num",  "Planned lead time (days)", True),
    "planned_completion_date":   ("date", "Planned completion date", False),
    "actual_completion_date":    ("date", "Actual completion (blank if still open)", False),
    "actual_lead_time_days":     ("num",  "TARGET (regression): actual lead time", False),
    "snapshot_date":             ("date", "Date the status was recorded", True),
    "elapsed_days":              ("num",  "Days from order_date to snapshot_date", False),
    "production_status":         ("str",  "TARGET (classification): status at snapshot", True),
    "data_source":               ("str",  "REAL or SIMULATED", True),
}

# Combined view (specs + prices) used by the simulator and by modelling notebooks
QUOTATION_COLUMNS = list(dict.fromkeys([*SPEC_SCHEMA, *PRICE_SCHEMA]))
