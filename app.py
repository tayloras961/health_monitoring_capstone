import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd

from modules import db
from modules import auth
from modules import preprocessing
from modules import model
from modules import dashboard as dash
from modules import report as rep

APP_SECRET = os.environ.get("SECRET_KEY", "dev-secret-change-me")

app = Flask(__name__)
app.secret_key = APP_SECRET

with app.app_context():
    db.init_db()
    auth.ensure_default_users()


def _rows_to_df(rows):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ok, err = auth.login_user(request.form.get("username","").strip(), request.form.get("password",""))
        if ok:
            return redirect(url_for("dashboard"))
        return render_template("login.html", error=err)
    return render_template("login.html")

@app.route("/logout")
def logout():
    auth.logout_user()
    return redirect(url_for("home"))

@app.route("/data")
@auth.require_login()
def data_page():
    c = db.count_health_records(session["user_id"])
    return render_template("data.html", record_count=c)

@app.route("/data/upload", methods=["POST"])
@auth.require_login()
def upload_data():
    f = request.files.get("file")
    if not f:
        return render_template("data.html", record_count=db.count_health_records(session["user_id"]), error="No file uploaded.")
    b = f.read()
    df = preprocessing.read_csv_flex(b)
    ok, err = preprocessing.validate_schema(df)
    if not ok:
        return render_template("data.html", record_count=db.count_health_records(session["user_id"]), error=err)

    df_clean = preprocessing.clean_health_df(df)

    # Run anomaly detection (screening)
    try:
        df_scored = model.score_anomalies(df_clean, contamination=0.03)
    except Exception as e:
        return render_template("data.html", record_count=db.count_health_records(session["user_id"]), error=f"Model error: {e}")

    rows = preprocessing.to_db_rows(df_scored)
    # add flags/scores/drivers
    for i, r in enumerate(rows):
        r["anomaly_flag"] = int(df_scored.iloc[i].get("anomaly_flag", 0))
        r["anomaly_score"] = float(df_scored.iloc[i].get("anomaly_score", 0.0))
    # Insert
    db.insert_health_records(session["user_id"], rows)

    return redirect(url_for("dashboard"))

@app.route("/data/load-sample")
@auth.require_login()
def load_sample():
    # Load sample CSV bundled in /data
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_health_data.csv")
    with open(sample_path, "rb") as fp:
        b = fp.read()
    df = preprocessing.read_csv_flex(b)
    df_clean = preprocessing.clean_health_df(df)
    df_scored = model.score_anomalies(df_clean, contamination=0.03)
    rows = preprocessing.to_db_rows(df_scored)
    for i, r in enumerate(rows):
        r["anomaly_flag"] = int(df_scored.iloc[i].get("anomaly_flag", 0))
        r["anomaly_score"] = float(df_scored.iloc[i].get("anomaly_score", 0.0))
    db.insert_health_records(session["user_id"], rows)
    return redirect(url_for("dashboard"))

@app.route("/data/sample.csv")
def download_sample():
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_health_data.csv")
    return send_file(sample_path, as_attachment=True, download_name="sample_health_data.csv")

@app.route("/data/clear")
@auth.require_login()
def clear_my_data():
    db.delete_user_records(session["user_id"])
    return redirect(url_for("data_page"))

@app.route("/dashboard")
@auth.require_login()
def dashboard():
    rows = db.get_health_records(session["user_id"])
    df = _rows_to_df(rows)
    if df.empty:
        return render_template("dashboard.html", figures=[], summary={"total_records":0,"anomaly_count":0,"anomaly_rate":"0.0"})

    # If DB already has anomaly_flag stored, use it; otherwise compute quickly
    if "anomaly_flag" not in df.columns or df["anomaly_flag"].isna().all():
        df_scored = model.score_anomalies(df, contamination=0.03)
        df["anomaly_flag"] = df_scored["anomaly_flag"]
        df["anomaly_score"] = df_scored["anomaly_score"]

    summary = {
        "total_records": int(len(df)),
        "anomaly_count": int(df["anomaly_flag"].sum()) if "anomaly_flag" in df.columns else 0,
    }
    summary["anomaly_rate"] = round(100.0 * summary["anomaly_count"] / max(summary["total_records"], 1), 2)

    figs = dash.build_timeseries_figures(df)

    return render_template("dashboard.html", figures=figs, summary=summary)

@app.route("/report")
@auth.require_login()
def report():
    rows = db.get_health_records(session["user_id"])
    df = _rows_to_df(rows)
    if df.empty:
        return render_template("report.html", report=None)
    # Ensure anomaly columns exist
    if "anomaly_flag" not in df.columns or df["anomaly_flag"].isna().all():
        df = model.score_anomalies(df, contamination=0.03)
    r = rep.generate_weekly_summary(df)
    # stash daily df in session via csv (small)
    if r:
        session["daily_report_csv"] = r["daily_df"].to_csv(index=False)
        r["table_html"] = r["table_html"]
    return render_template("report.html", report={
        "date_range": r.get("date_range",""),
        "records": r.get("records",0),
        "anomalies": r.get("anomalies",0),
        "top_drivers": r.get("top_drivers","N/A"),
        "interpretation": r.get("interpretation",""),
        "table_html": r.get("table_html","")
    })

@app.route("/report/download")
@auth.require_login()
def download_report():
    csv_text = session.get("daily_report_csv")
    if not csv_text:
        return redirect(url_for("report"))
    import io
    buf = io.BytesIO(csv_text.encode("utf-8"))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="weekly_report.csv", mimetype="text/csv")

@app.route("/admin")
@auth.require_role("admin")
def admin():
    users = db.list_users()
    users_df = pd.DataFrame([dict(u) for u in users])
    users_table = users_df.to_html(index=False, border=0) if not users_df.empty else "<p>No users</p>"
    total_records = db.count_all_health_records()
    return render_template("admin.html", users_table=users_table, total_records=total_records)

@app.route("/admin/reset-db")
@auth.require_role("admin")
def admin_reset_db():
    db.reset_db()
    auth.ensure_default_users()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    # Local dev run
    app.run(debug=True)
