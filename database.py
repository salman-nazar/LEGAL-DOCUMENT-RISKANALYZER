"""
database.py
SQLite database layer for RiskAnalyzer.
Handles table creation and CRUD operations for users, documents, and analysis results.
"""

import sqlite3
import json
from datetime import datetime

DB_NAME = "RiskAnalyzer.db"


def get_connection():
    """Return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all required tables if they do not already exist. Safe to call every app run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            clauses_json TEXT,
            risks_json TEXT,
            summary_json TEXT,
            risk_score INTEGER,
            analyzed_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------- USER FUNCTIONS ----------------------

def create_user(username, email, password_hash):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, datetime.now().isoformat())
        )
        conn.commit()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------- DOCUMENT FUNCTIONS ----------------------

def save_document(user_id, filename, filepath):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO documents (user_id, filename, filepath, uploaded_at) VALUES (?, ?, ?, ?)",
        (user_id, filename, filepath, datetime.now().isoformat())
    )
    conn.commit()
    doc_id = cur.lastrowid
    conn.close()
    return doc_id


def get_documents_for_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document_by_id(document_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------- ANALYSIS FUNCTIONS ----------------------

def save_analysis(document_id, clauses, risks, summary, risk_score):
    conn = get_connection()
    conn.execute(
        """INSERT INTO analysis
           (document_id, clauses_json, risks_json, summary_json, risk_score, analyzed_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            document_id,
            json.dumps(clauses),
            json.dumps(risks),
            json.dumps(summary),
            risk_score,
            datetime.now().isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_analysis_by_document(document_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM analysis WHERE document_id = ? ORDER BY analyzed_at DESC LIMIT 1",
        (document_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["clauses"] = json.loads(data["clauses_json"])
    data["risks"] = json.loads(data["risks_json"])
    data["summary"] = json.loads(data["summary_json"])
    return data


def get_all_documents_with_scores(user_id):
    """Used by the dashboard to list documents along with their latest risk score."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.id, d.filename, d.uploaded_at, a.risk_score
        FROM documents d
        LEFT JOIN analysis a ON a.document_id = d.id
        WHERE d.user_id = ?
        ORDER BY d.uploaded_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]