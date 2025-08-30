import sqlite3
from datetime import datetime

DB_NAME = "reward_logs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS reward_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        reference_text TEXT,
        score REAL,
        similarity REAL,
        readability REAL,
        errors INTEGER,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_reward(text, reference_text, metrics: dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    INSERT INTO reward_logs (text, reference_text, score, similarity, readability, errors, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        text,
        reference_text,
        metrics.get("score"),
        metrics.get("similarity"),
        metrics.get("readability"),
        metrics.get("errors"),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def fetch_logs(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM reward_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
