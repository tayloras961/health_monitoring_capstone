# Proactive Health Monitoring System (Capstone Milestone 3)

A small Flask web app that:
- Authenticates users (role-based: `admin`/`user`)
- Loads sample wearable/EHR-like CSV data or accepts uploads
- Cleans and validates data
- Runs anomaly detection (Isolation Forest) on key health metrics
- Displays trends + anomalies on an interactive dashboard (Plotly)
- Generates a simple weekly summary report (HTML) and exportable CSV

## Quickstart

1) Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Run the app
```bash
python app.py
```

4) Open your browser:
- http://127.0.0.1:5000

## Default accounts (created on first run)
- Admin: `admin` / `admin123`
- User: `user` / `user123`

## CSV format
Required columns:
- `timestamp` (ISO8601 recommended)
- `heart_rate`, `steps`, `sleep_hours`, `calories`
Optional columns:
- `blood_pressure_systolic`, `blood_pressure_diastolic`, `glucose`

If you upload a CSV missing optional columns, the app will continue.

## Project structure
- `app.py` Flask routes / wiring
- `modules/` core logic (db, auth, preprocessing, model, dashboard, report)
- `templates/` HTML templates
- `static/` CSS
- `data/` sample dataset
- `instance/` SQLite database

