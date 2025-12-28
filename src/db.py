import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("instance") / "app.db"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            score REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_log(text: str, prediction: str, score):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
<<<<<<< Updated upstream
        "INSERT INTO logs (created_at, text, prediction, score) VALUES (?, ?, ?, ?)",
=======
>>>>>>> Stashed changes
        (datetime.now().isoformat(timespec="seconds"), text, prediction, score)
    )
    conn.commit()
    conn.close()

def fetch_logs(limit=300):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, created_at, text, prediction, score
        FROM logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
