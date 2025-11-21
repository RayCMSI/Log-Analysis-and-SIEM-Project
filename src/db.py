import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "db.sqlite3"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn

def init_db():
    with get_conn() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            source TEXT, --'Apache', 'auth', etc.
            ts     TEXT, -- ISO 8601 timestamp
            ip     TEXT,
            user   TEXT,
            action TEXT,
            result TEXT,
            raw    TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_logs_ts ON logs (ts);
        CREATE INDEX IF NOT EXISTS idx_logs_ip ON logs (ip);
        CREATE INDEX IF NOT EXISTS idx_logs_user ON logs (user);
        
        CREATE TABLE IF NOT EXISTS alerts (
            id          INTEGER PRIMARY KEY,
            ts          TEXT,
            rule_id     TEXT,
            severity   TEXT,
            entity      TEXT,
            summary     TEXT,
            details     TEXT
        );
        """)