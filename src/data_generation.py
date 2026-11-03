"""
data_generation.py - SIMULATED demonstration data (NOT real company data).

!! Every number produced here comes from an arbitrary formula written for
!! teaching/pipeline-testing. They are NOT L&L Machinery prices, costs,
!! lead times or performance. Model names (SIM-*) and regions are placeholders.
Money is in abstract 'SIM units'.

A model trained on this data only re-learns the formula below, so results
must never be reported as findings about the company.
"""
import numpy as np
import pandas as pd
from .config import (RANDOM_STATE, SOURCE_SIM, SPEC_SCHEMA, PRICE_SCHEMA,
                     PRODUCTION_SCHEMA, QUOTATION_COLUMNS)


def generate_specs_and_prices(n: int = 400, seed: int = RANDOM_STATE, inject_noise: bool = True):
    """Return (specs_df, prices_df): the two quotation tables, linked by quote_id."""
    q = generate_quotations(n, seed, inject_noise)
    return q[list(SPEC_SCHEMA)].copy(), q[list(PRICE_SCHEMA)].copy()


def generate_quotations(n: int = 400, seed: int = RANDOM_STATE, inject_noise: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    machine_type = rng.choice(["CNC", "Conventional"], n, p=[0.6, 0.4])
    is_cnc = machine_type == "CNC"
    series = np.where(is_cnc, rng.choice(["SIM-CNC-A", "SIM-CNC-B", "SIM-CNC-C"], n),
                      rng.choice(["SIM-CV-1", "SIM-CV-2"], n))
    swing = rng.choice([360, 420, 500, 600], n)
    centers = rng.choice([750, 1000, 1500, 2000, 3000], n)
    bore = rng.choice([52, 66, 80, 105], n)
    kw = rng.choice([7.5, 11, 15, 22], n)
    chuck = rng.choice([8, 10, 12, 15], n)
    turret = np.where(is_cnc, rng.choice([8, 10, 12], n), 0)
    live = (is_cnc & (rng.random(n) < 0.35)).astype(int)
    bar = (rng.random(n) < 0.25).astype(int)
    chip = (rng.random(n) < 0.50).astype(int)
    tail = rng.choice(["manual", "hydraulic", "programmable"], n, p=[0.3, 0.5, 0.2])
    ctrl = np.where(is_cnc, rng.choice(["CTRL-A", "CTRL-B", "CTRL-C"], n), "NONE")
    region = rng.choice(["Region_1", "Region_2", "Region_3", "Region_4"], n)
    dates = pd.Timestamp("2022-01-01") + pd.to_timedelta(rng.integers(0, 1460, n), unit="D")

    tail_cost = pd.Series(tail).map({"manual": 0, "hydraulic": 40, "programmable": 90}).to_numpy()
    material = (np.where(is_cnc, 500, 200) + 0.35 * swing + 0.08 * centers + 1.2 * bore + 6 * kw
                + 4 * chuck + 12 * turret + 90 * live + 70 * bar + 40 * chip + tail_cost) \
               * rng.lognormal(0, 0.05, n)
    labor_hours = np.where(is_cnc, 160, 110) + 0.05 * centers + 0.1 * swing + rng.normal(0, 10, n)
    mfg_cost = (material + 1.5 * labor_hours) * 1.10          # 10% overhead (arbitrary)
    margin = pd.Series(region).map({"Region_1": .20, "Region_2": .25, "Region_3": .30, "Region_4": .22}).to_numpy()
    drift = 1.02 ** (dates.year - 2022).to_numpy()            # arbitrary 2%/yr price drift
    quoted = mfg_cost * (1 + margin) * drift * rng.lognormal(0, 0.04, n)
    final = quoted * (1 - rng.uniform(0, 0.08, n))            # negotiated discount

    df = pd.DataFrame({
        "quote_id": [f"SIMQ-{i:05d}" for i in range(1, n + 1)],
        "quote_date": dates.strftime("%Y-%m-%d"),
        "machine_type": machine_type, "model_series": series,
        "swing_over_bed_mm": swing, "distance_between_centers_mm": centers,
        "spindle_bore_mm": bore, "spindle_motor_kw": kw, "chuck_size_inch": chuck,
        "turret_stations": turret, "live_tooling": live, "bar_feeder": bar,
        "chip_conveyor": chip, "tailstock_type": tail, "controller": ctrl,
        "customer_region": region, "material_cost": material.round(1),
        "labor_hours": labor_hours.round(1), "manufacturing_cost": mfg_cost.round(1),
        "quoted_price": quoted.round(1), "final_selling_price": final.round(1),
        "data_source": SOURCE_SIM,
    })

    if inject_noise:  # deliberately dirty, so the cleaning step has real work to do
        idx = rng.choice(n, int(0.04 * n), replace=False)
        df.loc[idx, "labor_hours"] = np.nan
        idx = rng.choice(n, int(0.03 * n), replace=False)
        df.loc[idx, "chuck_size_inch"] = np.nan
        out = rng.choice(n, 4, replace=False)
        df.loc[out, "final_selling_price"] = (df.loc[out, "final_selling_price"] * 8).round(1)
        df = pd.concat([df, df.sample(5, random_state=seed)], ignore_index=True)  # duplicates
    return df[QUOTATION_COLUMNS]


def generate_production(n: int = 500, seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Each row = one order with a status check taken at a random date (snapshot_date)."""
    rng = np.random.default_rng(seed + 1)
    is_cnc = rng.random(n) < 0.6
    series = np.where(is_cnc, rng.choice(["SIM-CNC-A", "SIM-CNC-B", "SIM-CNC-C"], n),
                      rng.choice(["SIM-CV-1", "SIM-CV-2"], n))
    qty = rng.choice([1, 2, 3, 5], n, p=[0.6, 0.2, 0.1, 0.1])
    custom = rng.integers(0, 5, n)
    backlog = rng.integers(0, 15, n)
    order_date = pd.Timestamp("2022-01-01") + pd.to_timedelta(rng.integers(0, 1460, n), unit="D")

    planned = np.where(is_cnc, 60, 45) + 10 * (qty - 1)
    delay = np.maximum(0, rng.normal(0.8 * backlog + 2.5 * custom, 6))
    actual = np.round(planned + delay)
    completion = order_date + pd.to_timedelta(actual, unit="D")
    elapsed = np.maximum(1, np.round(rng.uniform(0.02, 1.35, n) * actual)).astype(int)
    snap = order_date + pd.to_timedelta(elapsed, unit="D")   # when status was recorded
    done = elapsed >= actual

    frac = elapsed / actual
    status = np.select(
        [done, elapsed > planned, frac < 0.15, frac < 0.55, frac < 0.85],
        ["Completed", "Delayed", "Material preparation", "Machining", "Assembly"],
        default="Testing")

    return pd.DataFrame({
        "order_id": [f"SIMO-{i:05d}" for i in range(1, n + 1)],
        "order_date": order_date.strftime("%Y-%m-%d"),
        "machine_type": np.where(is_cnc, "CNC", "Conventional"), "model_series": series,
        "quantity": qty, "n_custom_options": custom, "open_orders_at_order_date": backlog,
        "planned_lead_time_days": planned,
        "planned_completion_date": (order_date + pd.to_timedelta(planned, unit="D")).strftime("%Y-%m-%d"),
        "actual_completion_date": np.where(done, completion.strftime("%Y-%m-%d"), None),
        "actual_lead_time_days": np.where(done, actual, np.nan),   # unknown while open
        "snapshot_date": snap.strftime("%Y-%m-%d"), "elapsed_days": elapsed,
        "production_status": status, "data_source": SOURCE_SIM,
    })[list(PRODUCTION_SCHEMA)]
