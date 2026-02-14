import io
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

REQUIRED_COLS = []
NUMERIC_COLS = [
    "heart_rate", "steps", "sleep_hours", "calories",
    "blood_pressure_systolic", "blood_pressure_diastolic", "glucose"
]

def read_csv_flex(file_bytes: bytes) -> pd.DataFrame:
    # Accept comma-separated CSV or tab-separated TSV automatically
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    first_line = text.splitlines()[0] if text else ""
    sep = "\t" if "\t" in first_line else ","

    return pd.read_csv(io.StringIO(text), sep=sep)


def validate_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    # Normalize column
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return False, f"Missing required column(s): {', '.join(missing)}"
    return True, ""


def coerce_types_and_fill(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Timestamp coercion
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out = out.dropna(subset=["timestamp"])
    out = out.sort_values("timestamp")

    # Coerce numeric cols if present
    for c in NUMERIC_COLS:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    # Fill missing values
    for c in NUMERIC_COLS:
        if c in out.columns:
            out[c] = out[c].interpolate(limit_direction="both")
            out[c] = out[c].fillna(out[c].median())

    return out

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["timestamp"])

def clip_outliers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in NUMERIC_COLS:
        if c in out.columns:
            lo, hi = out[c].quantile(0.01), out[c].quantile(0.99)
            if pd.notna(lo) and pd.notna(hi) and lo < hi:
                out[c] = out[c].clip(lo, hi)
    return out

def clean_health_df(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    df2.columns = [str(c).strip().lower() for c in df2.columns]

    # Create timestamp if missing
    if "timestamp" not in df2.columns:
        df2["timestamp"] = pd.date_range(
            end=pd.Timestamp.now(),
            periods=len(df2),
            freq="H"
        )

    df2 = remove_duplicates(df2)
    df2 = coerce_types_and_fill(df2)
    df2 = clip_outliers(df2)
    return df2


def to_db_rows(df: pd.DataFrame) -> List[Dict]:
    # Convert
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "timestamp": r["timestamp"].isoformat(),
            "heart_rate": float(r["heart_rate"]) if "heart_rate" in df.columns else None,
            "steps": float(r["steps"]) if "steps" in df.columns else None,
            "sleep_hours": float(r["sleep_hours"]) if "sleep_hours" in df.columns else None,
            "calories": float(r["calories"]) if "calories" in df.columns else None,
            "blood_pressure_systolic": float(r["blood_pressure_systolic"]) if "blood_pressure_systolic" in df.columns else None,
            "blood_pressure_diastolic": float(r["blood_pressure_diastolic"]) if "blood_pressure_diastolic" in df.columns else None,
            "glucose": float(r["glucose"]) if "glucose" in df.columns else None,
        })
    return rows
