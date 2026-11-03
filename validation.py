"""
validation.py - Schema checks and data-provenance guards.

These functions are the project's "safety net": they stop simulated data
from being mistaken for real data and catch broken CSVs early.
"""
import pandas as pd
from .config import SOURCE_REAL, SOURCE_SIM, SIM_PREFIX


def validate_schema(df: pd.DataFrame, schema: dict, name: str = "dataset") -> pd.DataFrame:
    """Return a table of problems found (empty table = no problems)."""
    issues = []
    for col, (kind, _, required) in schema.items():
        if col not in df.columns:
            if required:
                issues.append((name, col, "MISSING required column"))
            continue
        s = df[col]
        if required and s.isna().all():
            issues.append((name, col, "required column is entirely empty"))
        if kind in ("num", "int"):
            bad = pd.to_numeric(s, errors="coerce").isna() & s.notna()
            if bad.any():
                issues.append((name, col, f"{int(bad.sum())} non-numeric values"))
        if kind == "date":
            bad = pd.to_datetime(s, errors="coerce").isna() & s.notna()
            if bad.any():
                issues.append((name, col, f"{int(bad.sum())} unparseable dates"))
    extra = [c for c in df.columns if c not in schema]
    if extra:
        issues.append((name, ",".join(extra), "columns not in schema (check spelling)"))
    id_col = next(iter(schema))
    if id_col in df.columns and df[id_col].duplicated().any():
        issues.append((name, id_col, f"{int(df[id_col].duplicated().sum())} duplicate IDs"))
    return pd.DataFrame(issues, columns=["dataset", "column", "issue"])


def provenance_summary(df: pd.DataFrame) -> pd.Series:
    """Count rows per data_source label."""
    return df["data_source"].value_counts(dropna=False)


def require_single_source(df: pd.DataFrame) -> str:
    """Raise if REAL and SIMULATED rows are mixed; return the single label."""
    labels = set(df["data_source"].dropna().unique())
    if labels == {SOURCE_REAL, SOURCE_SIM}:
        raise ValueError("REAL and SIMULATED rows are mixed. Separate them before modelling.")
    if not labels <= {SOURCE_REAL, SOURCE_SIM}:
        raise ValueError(f"Unknown data_source labels: {labels}")
    return labels.pop()


def save_dataset(df: pd.DataFrame, path) -> None:
    """Save a CSV, enforcing the naming/label rules for simulated data."""
    from pathlib import Path
    path = Path(path)
    label = require_single_source(df)
    if label == SOURCE_SIM and not path.name.startswith(SIM_PREFIX):
        raise ValueError(f"Simulated files must be named '{SIM_PREFIX}*.csv'")
    if label == SOURCE_REAL and path.name.startswith(SIM_PREFIX):
        raise ValueError("Real data must not use the simulated file prefix")
    df.to_csv(path, index=False)
