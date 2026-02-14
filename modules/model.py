import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from sklearn.ensemble import IsolationForest

FEATURE_COLS_DEFAULT = ["heart_rate", "steps", "sleep_hours", "calories", "glucose"]

def _available_feature_cols(df: pd.DataFrame, candidates: List[str]) -> List[str]:
    return [c for c in candidates if c in df.columns]

def fit_isolation_forest(df: pd.DataFrame, contamination: float = 0.03, random_state: int = 7) -> Tuple[IsolationForest, List[str]]:
    feature_cols = _available_feature_cols(df, FEATURE_COLS_DEFAULT)
    if not feature_cols:
        raise ValueError("No numeric feature columns found for modeling.")
    X = df[feature_cols].astype(float).values
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state
    )
    model.fit(X)
    return model, feature_cols

def score_anomalies(df: pd.DataFrame, contamination: float = 0.03) -> pd.DataFrame:
    out = df.copy()
    model, cols = fit_isolation_forest(out, contamination=contamination)

    X = out[cols].astype(float).values
    # Higher score = less anomalous in sklearn; we invert to make "higher = more anomalous"
    raw_score = model.decision_function(X)  # higher is more normal
    anomaly_score = (-raw_score - (-raw_score).min()) / ((-raw_score).max() - (-raw_score).min() + 1e-9)

    pred = model.predict(X)  # -1 anomaly, 1 normal
    out["anomaly_flag"] = (pred == -1).astype(int)
    out["anomaly_score"] = anomaly_score

    # Simple driver attribution: z-score magnitude per feature for flagged points
    drivers = []
    mu = out[cols].mean()
    sd = out[cols].std().replace(0, 1e-9)
    z = ((out[cols] - mu) / sd).abs()
    for i in range(len(out)):
        if out.loc[out.index[i], "anomaly_flag"] == 1:
            top = z.iloc[i].sort_values(ascending=False).head(2).index.tolist()
            drivers.append(", ".join(top))
        else:
            drivers.append("")
    out["anomaly_drivers"] = drivers
    return out
