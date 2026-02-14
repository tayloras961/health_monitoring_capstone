# Implementation Plan

## 1) Integrated software components
- **Python 3.10+** runtime
- **Flask** web framework for routes, sessions, templating
- **SQLite** database (default) for local persistence
- **Pandas / NumPy** for preprocessing and analysis
- **scikit-learn** for anomaly detection (Isolation Forest baseline)
- **Plotly** for interactive visualizations in the browser

## 2) Deployment as an operational system
### Local deployment (capstone baseline)
1. Install dependencies (`pip install -r requirements.txt`)
2. Run `python app.py`
3. Access via browser at `http://127.0.0.1:5000`
4. First run initializes the database and sample users.

### Optional future deployment (cloud)
- Containerize with Docker for consistent environments.
- Deploy to a PaaS (Render/Fly/Heroku-like) with:
  - `gunicorn` for production WSGI
  - environment variables for SECRET_KEY, DB URL
  - HTTPS termination (platform-managed)

## 3) Strategy, impacts, and activities
### Strategy
- Build a minimal working vertical slice:
  ingestion → cleaning → persistence → modeling → dashboard → report export.
- Prioritize usability and interpretability:
  show trends, highlight anomalies, and summarize weekly insights.

### Potential impacts
- **False positives/negatives** from anomaly model:
  mitigate with configurable sensitivity and clear “screening not diagnosis” wording.
- **Data quality variance** across wearables/EHR exports:
  mitigate with schema validation + robust cleaning.
- **Security risks**:
  mitigate with session auth, password hashing, and role-based access.

### Activities
- Environment setup (venv, deps)
- Database initialization and entity creation
- Module development and integration
- Validation and testing using sample datasets
- Peer code review + fixes
- Documentation updates (mapping, user guide)
- Packaging for submission (zip + screenshots)

## 4) End-user availability activities
- Provide “Getting Started” steps (User Guide)
- Include sample CSV and upload instructions
- Add troubleshooting section for common errors
- Confirm app executes with no errors/warnings in a clean environment
