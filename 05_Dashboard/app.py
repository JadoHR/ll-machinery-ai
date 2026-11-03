"""
L&L Machinery AI prototype dashboard.
Run from the repository root:
    streamlit run 05_Dashboard/app.py

Place trained .joblib artifacts in 03_Models/ before using predictions.
"""
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "03_Models"
DATA_DIR = ROOT / "01_Data" / "simulated"

st.set_page_config(
    page_title="L&L Machinery AI | Intelligent Manufacturing",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ L&L Machinery")
st.subheader("Intelligent Manufacturing & Decision Support")
st.caption("Internship prototype | Machine price estimation • Production status • Lead-time estimation")
st.warning(
    "DEMONSTRATION ONLY — Current models were trained on simulated data. "
    "Predictions are not actual company quotations or operational decisions."
)

@st.cache_resource
def load_artifact(filename):
    path = MODEL_DIR / filename
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception as exc:
        st.error(f"Could not load {filename}: {exc}")
        return None

@st.cache_data
def load_reference_data(filename):
    path = DATA_DIR / filename
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def choices_from(data, column, fallback):
    if column in data.columns:
        vals = data[column].dropna().astype(str).unique().tolist()
        if vals:
            return sorted(vals)
    return fallback

specs = load_reference_data("SIMULATED_machine_specifications.csv")
production = load_reference_data("SIMULATED_production_records.csv")

price_artifact = load_artifact("price_prediction_model.joblib")
status_artifact = load_artifact("production_status_model.joblib")
lead_artifact = load_artifact("lead_time_model.joblib")

price_tab, status_tab, lead_tab, about_tab = st.tabs([
    "💰 Price Estimator",
    "🏭 Production Status",
    "📅 Completion-Time Estimator",
    "ℹ️ About & Model Status",
])

with price_tab:
    st.header("Machine Selling-Price Estimator")
    st.write("Enter machine specifications to estimate a selling price from the trained model.")
    if price_artifact is None:
        st.error("Price model file not found.")
        st.code("03_Models/price_prediction_model.joblib")
        st.info("Train Notebook 02 and place its saved model file in the repository's 03_Models folder.")
    else:
        price_features = price_artifact.get("feature_columns", [])
        with st.form("price_form"):
            c1, c2 = st.columns(2)
            values = {}
            with c1:
                if "machine_type" in price_features:
                    values["machine_type"] = st.selectbox("Machine type", choices_from(specs, "machine_type", ["CNC", "Conventional"]))
                if "model_series" in price_features:
                    values["model_series"] = st.selectbox("Model series", choices_from(specs, "model_series", ["SIM-CV-1", "SIM-CV-2", "SIM-CNC-A", "SIM-CNC-B", "SIM-CNC-C"]))
                numeric_specs = [
                    ("swing_over_bed_mm", "Swing over bed (mm)", 360, 1200, 420, 10),
                    ("distance_between_centers_mm", "Distance between centers (mm)", 500, 3000, 1500, 50),
                    ("spindle_bore_mm", "Spindle bore (mm)", 40, 120, 66, 2),
                    ("spindle_motor_kw", "Spindle motor (kW)", 5.5, 30.0, 11.0, 0.5),
                ]
                for key, label, lo, hi, default, step in numeric_specs:
                    if key in price_features:
                        values[key] = st.number_input(label, min_value=float(lo), max_value=float(hi), value=float(default), step=float(step))
            with c2:
                if "chuck_size_inch" in price_features:
                    values["chuck_size_inch"] = st.selectbox("Chuck size (inch)", choices_from(specs, "chuck_size_inch", ["6.0", "8.0", "10.0", "12.0", "15.0"]), format_func=lambda x: str(x))
                if "turret_stations" in price_features:
                    values["turret_stations"] = st.selectbox("Turret stations", choices_from(specs, "turret_stations", [0, 8, 10, 12]))
                for key, label in [("live_tooling", "Live tooling"), ("bar_feeder", "Bar feeder"), ("chip_conveyor", "Chip conveyor")]:
                    if key in price_features:
                        values[key] = int(st.checkbox(label))
                if "tailstock_type" in price_features:
                    values["tailstock_type"] = st.selectbox("Tailstock type", choices_from(specs, "tailstock_type", ["hydraulic", "programmable"]))
                if "controller" in price_features:
                    values["controller"] = st.selectbox("Controller", choices_from(specs, "controller", ["NONE", "CTRL-A"]))
            submitted = st.form_submit_button("Estimate selling price", type="primary")
        if submitted:
            row = {}
            for feature in price_features:
                value = values.get(feature)
                if feature == "chuck_size_inch" and value is not None:
                    value = float(value)
                row[feature] = value
            try:
                prediction = float(price_artifact["model"].predict(pd.DataFrame([row], columns=price_features))[0])
                st.success("Estimated selling price")
                st.metric("Model estimate (price units)", f"{prediction:,.2f}")
                st.caption("The source dataset does not define a confirmed currency. Confirm currency and pricing conventions with the company.")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

with status_tab:
    st.header("Production Status Predictor")
    st.write("Enter information available at a production snapshot. Elapsed days should reflect the current snapshot date.")
    if status_artifact is None:
        st.error("Production status model file not found.")
        st.code("03_Models/production_status_model.joblib")
        st.info("Train Notebook 03 and place its saved model file in the repository's 03_Models folder.")
    else:
        features = status_artifact.get("feature_columns", [])
        with st.form("status_form"):
            a, b = st.columns(2)
            vals = {}
            with a:
                if "machine_type" in features:
                    vals["machine_type"] = st.selectbox("Machine type", choices_from(production, "machine_type", ["CNC", "Conventional"]), key="status_machine")
                if "model_series" in features:
                    vals["model_series"] = st.selectbox("Model series", choices_from(production, "model_series", ["SIM-CV-1", "SIM-CV-2", "SIM-CNC-A", "SIM-CNC-B", "SIM-CNC-C"]), key="status_series")
                if "quantity" in features:
                    vals["quantity"] = st.number_input("Order quantity", min_value=1, max_value=100, value=1, step=1)
                if "n_custom_options" in features:
                    vals["n_custom_options"] = st.number_input("Number of custom options", min_value=0, max_value=30, value=2, step=1)
            with b:
                if "open_orders_at_order_date" in features:
                    vals["open_orders_at_order_date"] = st.number_input("Open orders at order date", min_value=0, max_value=100, value=5, step=1)
                if "planned_lead_time_days" in features:
                    vals["planned_lead_time_days"] = st.number_input("Planned lead time (days)", min_value=1, max_value=365, value=60, step=1)
                if "elapsed_days" in features:
                    vals["elapsed_days"] = st.number_input("Elapsed days at snapshot", min_value=0, max_value=730, value=30, step=1)
            submitted_status = st.form_submit_button("Predict production status", type="primary")
        if submitted_status:
            try:
                frame = pd.DataFrame([{f: vals.get(f) for f in features}], columns=features)
                model = status_artifact["model"]
                predicted = model.predict(frame)[0]
                st.metric("Predicted production status", str(predicted))
                if hasattr(model, "predict_proba"):
                    probabilities = model.predict_proba(frame)[0]
                    classes = model.named_steps["model"].classes_
                    prob_df = pd.DataFrame({"Status": classes, "Model confidence": probabilities}).sort_values("Model confidence", ascending=False)
                    st.write("Model class probabilities")
                    st.bar_chart(prob_df.set_index("Status"))
                st.caption("The model has weaker recall for Delayed and Testing in the current simulated test set. Treat these predictions as experimental.")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

with lead_tab:
    st.header("Expected Completion-Time Estimator")
    st.write("Estimate total lead time from order placement, using order-time information.")
    if lead_artifact is None:
        st.error("Lead-time model file not found.")
        st.code("03_Models/lead_time_model.joblib")
        st.info("Train Notebook 03 and place its saved model file in the repository's 03_Models folder.")
    else:
        features = lead_artifact.get("feature_columns", [])
        with st.form("lead_form"):
            a, b = st.columns(2)
            vals = {}
            with a:
                if "machine_type" in features:
                    vals["machine_type"] = st.selectbox("Machine type", choices_from(production, "machine_type", ["CNC", "Conventional"]), key="lead_machine")
                if "model_series" in features:
                    vals["model_series"] = st.selectbox("Model series", choices_from(production, "model_series", ["SIM-CV-1", "SIM-CV-2", "SIM-CNC-A", "SIM-CNC-B", "SIM-CNC-C"]), key="lead_series")
                if "quantity" in features:
                    vals["quantity"] = st.number_input("Order quantity", min_value=1, max_value=100, value=1, step=1, key="lead_quantity")
            with b:
                if "n_custom_options" in features:
                    vals["n_custom_options"] = st.number_input("Number of custom options", min_value=0, max_value=30, value=2, step=1, key="lead_options")
                if "open_orders_at_order_date" in features:
                    vals["open_orders_at_order_date"] = st.number_input("Open orders at order date", min_value=0, max_value=100, value=5, step=1, key="lead_open")
                if "planned_lead_time_days" in features:
                    vals["planned_lead_time_days"] = st.number_input("Planned lead time (days)", min_value=1, max_value=365, value=60, step=1, key="lead_planned")
            submitted_lead = st.form_submit_button("Estimate completion time", type="primary")
        if submitted_lead:
            try:
                frame = pd.DataFrame([{f: vals.get(f) for f in features}], columns=features)
                days = max(0.0, float(lead_artifact["model"].predict(frame)[0]))
                st.metric("Estimated total lead time", f"{days:.1f} days")
                st.caption("This is an estimate from order placement, not a live remaining-time calculation.")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

with about_tab:
    st.header("About this prototype")
    st.write("This dashboard connects three saved machine-learning pipelines. It is designed for demonstration and future validation with approved company records.")
    st.subheader("Model artifact checklist")
    for filename in ["price_prediction_model.joblib", "production_status_model.joblib", "lead_time_model.joblib"]:
        exists = (MODEL_DIR / filename).exists()
        st.write(("✅ " if exists else "⬜ ") + filename)
    st.subheader("Important limitations")
    st.markdown(
        "- All current training and evaluation results use simulated records.\n"
        "- The price output's currency/unit must be confirmed with the company.\n"
        "- Production status classification has weaker detection of Delayed and Testing.\n"
        "- Do not enter confidential customer, quotation, or order information into a public deployment.\n"
        "- Obtain permission and retrain/validate on real company data before operational use."
    )

st.divider()
st.caption("L&L Machinery AI Prototype • Built for internship demonstration")
