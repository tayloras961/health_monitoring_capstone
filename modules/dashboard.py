import pandas as pd
from typing import Any, Dict, List
import plotly.graph_objects as go
import json
from plotly.utils import PlotlyJSONEncoder

# Metrics shown on dashboard
METRICS = [
    ("heart_rate", "Heart Rate (bpm)"),
    ("steps", "Steps"),
    ("sleep_hours", "Sleep (hours)"),
    ("calories", "Calories"),
    ("glucose", "Glucose (mg/dL)"),
]

def build_timeseries_figures(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Builds Plotly figures for dashboard time-series visualization.
    Returns figures in JSON-safe dict form for Jinja templates.
    """

    figs = []

    # Ensure ordering
    df = df.sort_values("timestamp")

    for metric, title in METRICS:
        if metric not in df.columns:
            continue

        normal = df[df.get("anomaly_flag", 0) == 0]
        anomalies = df[df.get("anomaly_flag", 0) == 1]

        fig = go.Figure()

        # Normal data trace
        fig.add_trace(go.Scatter(
            x=normal["timestamp"],
            y=normal[metric],
            mode="lines+markers",
            name="Normal",
        ))

        # Anomaly trace
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies["timestamp"],
                y=anomalies[metric],
                mode="markers",
                name="Anomaly",
                marker=dict(size=10, symbol="circle-open"),
                hovertext=anomalies.get("anomaly_drivers", ""),
            ))

        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=360,
            xaxis_title="Time",
            yaxis_title=title,
        )

        # Convert figure to JSON-safe structure
        fig_dict = fig.to_plotly_json()

        # Sanitize numpy arrays & timestamps
        fig_dict = json.loads(
            json.dumps(fig_dict, cls=PlotlyJSONEncoder)
        )

        figs.append({
            "title": title,
            "div_id": f"fig_{metric}",
            "data": fig_dict["data"],
            "layout": fig_dict["layout"],
        })

    return figs
