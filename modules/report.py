import io
import pandas as pd
from typing import Dict, Tuple

def _week_window(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # last 7 days
    max_ts = df["timestamp"].max()
    start = max_ts - pd.Timedelta(days=7)
    return df[df["timestamp"] >= start]

def generate_weekly_summary(df: pd.DataFrame) -> Dict:
    if df.empty:
        return {}

    dfw = _week_window(df)
    if dfw.empty:
        dfw = df.copy()

    # Daily rollup
    dfw["date"] = dfw["timestamp"].dt.date
    metrics = [c for c in ["heart_rate","steps","sleep_hours","calories","glucose"] if c in dfw.columns]
    agg = {m: "mean" for m in metrics}
    agg["anomaly_flag"] = "sum"
    daily = dfw.groupby("date", as_index=False).agg(agg).rename(columns={"anomaly_flag":"anomalies"})
    daily["anomalies"] = daily["anomalies"].astype(int)

    # Drivers
    top_drivers = "N/A"
    if "anomaly_drivers" in dfw.columns:
        d = dfw[dfw["anomaly_flag"] == 1]["anomaly_drivers"]
        d = d[d.astype(str).str.len() > 0]
        if len(d) > 0:
            top_drivers = ", ".join(d.value_counts().head(3).index.tolist())

    interpretation = (
        "This weekly summary highlights recent trends and any data points that were flagged as unusual compared "
        "to the user's recent baseline. A higher anomaly count does not automatically indicate a medical issue; "
        "it may reflect sensor noise, schedule changes, or one-time events. Use flagged periods as prompts to review context."
    )

    date_range = f"{daily['date'].min()} to {daily['date'].max()}"

    return {
        "date_range": date_range,
        "records": int(len(dfw)),
        "anomalies": int(dfw["anomaly_flag"].sum()),
        "top_drivers": top_drivers,
        "interpretation": interpretation,
        "daily_df": daily,
        "table_html": daily.to_html(index=False, classes=None, border=0)
    }

def to_report_csv_bytes(daily_df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    daily_df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")
