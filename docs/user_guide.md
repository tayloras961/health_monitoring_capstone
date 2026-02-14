# User Guide — Proactive Health Monitoring System

## Cover / Title / Copyright
**Proactive Health Monitoring System**  

This guide explains how to install and use the application to upload health data, view trends, detect potential anomalies, and generate weekly summaries. The system is intended for demonstration purposes and is not a medical device.

## Table of Contents
1. General Information
2. System Summary
3. Getting Started
4. Using the System
5. Troubleshooting
6. FAQ
7. Help and Contact Details
8. Glossary
9. Accessibility and Safety Notes

## 1) General Information
- **Purpose:** Provide proactive insight into health trends and highlight unusual patterns.
- **Audience:** Non-technical users and technical reviewers.
- **Data:** Upload CSV exports from wearables/EHR-like sources (sample data included).

## 2) System Summary
Features:
- Login (role-based)
- Data upload and cleaning
- Anomaly detection (screening signal)
- Dashboard trends + anomaly highlights
- Weekly summary report + CSV export

## 3) Getting Started
### Install (local)
1. Install Python 3.10+
2. Run:
   - `pip install -r requirements.txt`
   - `python app.py`
3. Open `http://127.0.0.1:5000`

### Default logins
- Admin: `admin` / `admin123`
- User: `user` / `user123`

## 4) Using the System
### Step 1 — Log in
Enter username and password.

### Step 2 — Load or Upload Data
- Click **Data** → upload a CSV file.
- Or click **Load Sample Data**.

### Step 3 — View Dashboard
- Shows time-series charts (heart rate, steps, sleep, calories)
- Anomalies are flagged and summarized at the top.

### Step 4 — Generate Weekly Report
- Click **Report**
- Review weekly summary and download report CSV.

## 5) Troubleshooting
- **Upload fails:** confirm CSV includes `timestamp`.
- **Charts blank:** confirm numeric columns contain numbers.
- **Login issues:** use default accounts or reset DB (delete `instance/app.db`).

## 6) FAQ
- **Does this system replace medical advice?** No. It provides informational analysis only

## 7) Help and Contact Details
- Taylor Shellow 
- TShellow@my.gcu.edu
## 8) Glossary
- **Anomaly detection:** identifying unusual patterns.
- **Time series:** data indexed by time.
- **Role-based access:** permissions based on user role.

## 9) Accessibility and Safety Notes
- Do not rely on color alone: anomaly counts are shown as text.
- Charts include hover tooltips for exact values.
- Safety: “screening” alerts should be interpreted with context and, if needed, discussed with a clinician.
