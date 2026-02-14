import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DB_PATH_DEFAULT = os.path.join("instance", "app.db")

def get_conn(db_path: str = DB_PATH_DEFAULT) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH_DEFAULT) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        email TEXT
    );
    """)
    # Health records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        heart_rate REAL,
        steps REAL,
        sleep_hours REAL,
        calories REAL,
        blood_pressure_systolic REAL,
        blood_pressure_diastolic REAL,
        glucose REAL,
        anomaly_flag INTEGER DEFAULT 0,
        anomaly_score REAL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)
    conn.commit()
    conn.close()

def create_user(username: str, password_hash: str, role: str = "user", email: str = None,
                db_path: str = DB_PATH_DEFAULT) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users(username, password_hash, role, email) VALUES(?,?,?,?)",
        (username, password_hash, role, email)
    )
    conn.commit()
    conn.close()

def get_user_by_username(username: str, db_path: str = DB_PATH_DEFAULT):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def list_users(db_path: str = DB_PATH_DEFAULT):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role, email FROM users ORDER BY user_id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

def insert_health_records(user_id: int, rows: List[Dict[str, Any]], db_path: str = DB_PATH_DEFAULT) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO health_records (
            user_id, timestamp, heart_rate, steps, sleep_hours, calories,
            blood_pressure_systolic, blood_pressure_diastolic, glucose,
            anomaly_flag, anomaly_score
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        [
            (
                user_id,
                r.get("timestamp"),
                r.get("heart_rate"),
                r.get("steps"),
                r.get("sleep_hours"),
                r.get("calories"),
                r.get("blood_pressure_systolic"),
                r.get("blood_pressure_diastolic"),
                r.get("glucose"),
                int(r.get("anomaly_flag", 0)),
                r.get("anomaly_score"),
            )
            for r in rows
        ]
    )
    conn.commit()
    conn.close()

def get_health_records(user_id: int, limit: Optional[int] = None, db_path: str = DB_PATH_DEFAULT):
    conn = get_conn(db_path)
    cur = conn.cursor()
    q = "SELECT * FROM health_records WHERE user_id = ? ORDER BY timestamp ASC"
    params = [user_id]
    if limit is not None:
        q += " LIMIT ?"
        params.append(limit)
    cur.execute(q, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return rows

def count_health_records(user_id: int, db_path: str = DB_PATH_DEFAULT) -> int:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM health_records WHERE user_id = ?", (user_id,))
    c = int(cur.fetchone()["c"])
    conn.close()
    return c

def count_all_health_records(db_path: str = DB_PATH_DEFAULT) -> int:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM health_records")
    c = int(cur.fetchone()["c"])
    conn.close()
    return c

def delete_user_records(user_id: int, db_path: str = DB_PATH_DEFAULT) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM health_records WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def reset_db(db_path: str = DB_PATH_DEFAULT) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS health_records")
    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    conn.close()
    init_db(db_path)
