# Mapping of Functional Requirements (FR) → Modules/Functions

**Project:** Health Monitoring System

**Legend:** `module.function`

## FR1 – User login and authentication
- `modules.auth.login_user()`
- `modules.auth.logout_user()`
- `modules.auth.require_login()` (route guard)

## FR2 – Upload or load health data
- `app.py` route: `/data/upload`
- `modules.preprocessing.read_csv_flex()`
- `modules.preprocessing.validate_schema()`

## FR3 – Store health data in a database
- `modules.db.init_db()`
- `modules.db.insert_health_records()`
- `modules.db.get_health_records()`

## FR4 – Clean / scrub data
- `modules.preprocessing.clean_health_df()`
- `modules.preprocessing.coerce_types_and_fill()`

## FR5 – Detect anomalies in health metrics
- `modules.model.fit_isolation_forest()`
- `modules.model.score_anomalies()`

## FR6 – Display trends and analytics dashboard
- `app.py` route: `/dashboard`
- `modules.dashboard.build_timeseries_figures()`

## FR7 – Display alerts for abnormal patterns
- `modules.model.score_anomalies()` (produces anomaly flags)
- `app.py` route: `/dashboard` (renders alert counts + highlights)

## FR8 – Generate weekly summary report
- `modules.report.generate_weekly_summary()`

## FR9 – Export report outputs
- `app.py` route: `/report/download`
- `modules.report.to_report_csv_bytes()`

## FR10 – Role-based access (admin-only screens)
- `modules.auth.require_role("admin")`
- `app.py` route: `/admin`