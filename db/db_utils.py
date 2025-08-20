# db/db_utils.py
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).resolve().parent / "phm.db"

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS phm_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent TEXT,
    prompt TEXT,
    response TEXT,
    error_type TEXT,
    fix_suggestion TEXT
);

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT,
    value TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT,
    agent_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript(CREATE_TABLES_SQL)
    conn.commit()
    conn.close()
    print(f"Initialized DB at {DB_PATH}")

def insert_log(agent: str, prompt: str, response: str, error_type: Optional[str]=None, fix_suggestion: Optional[str]=None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO phm_logs (agent, prompt, response, error_type, fix_suggestion) VALUES (?, ?, ?, ?, ?)",
        (agent, prompt, response, error_type, fix_suggestion)
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid

def save_memory(key: str, value: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO memories (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid

def get_memory(key: str) -> Optional[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM memories WHERE key = ? ORDER BY id DESC LIMIT 1", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else None

def list_memories(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, key, value, created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def list_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, agent, prompt, response, error_type, fix_suggestion FROM phm_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def last_log() -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, agent, prompt, response, error_type, fix_suggestion FROM phm_logs ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
