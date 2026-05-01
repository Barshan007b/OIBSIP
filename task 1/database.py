"""
database.py — SQLite database manager for Smart BMI Tracker & Analyzer
Handles all CRUD operations for users and BMI records.
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "bmi_data.db")


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Create tables if they do not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                weight_kg  REAL NOT NULL,
                height_cm  REAL NOT NULL,
                bmi        REAL NOT NULL,
                category   TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


# ─── User operations ──────────────────────────────────────────────────────────

def add_user(name: str) -> int:
    """Insert a new user; return the new row id."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, created_at) VALUES (?, ?)",
            (name.strip(), datetime.now().isoformat(sep=" ", timespec="seconds")),
        )
        conn.commit()
        return cur.lastrowid


def get_all_users() -> list[dict]:
    """Return all users as a list of dicts."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY name COLLATE NOCASE").fetchall()
        return [dict(r) for r in rows]


def get_user_by_name(name: str) -> dict | None:
    """Return a single user dict or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE name = ? COLLATE NOCASE", (name.strip(),)
        ).fetchone()
        return dict(row) if row else None


def delete_user(user_id: int):
    """Delete a user and all their records (cascade)."""
    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()


# ─── BMI record operations ────────────────────────────────────────────────────

def add_bmi_record(user_id: int, weight_kg: float, height_cm: float,
                   bmi: float, category: str) -> int:
    """Insert a BMI record; return the new row id."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO bmi_records
                (user_id, weight_kg, height_cm, bmi, category, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, weight_kg, height_cm,
                round(bmi, 2), category,
                datetime.now().isoformat(sep=" ", timespec="seconds"),
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_records_for_user(user_id: int) -> list[dict]:
    """Return all BMI records for a user, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM bmi_records WHERE user_id = ? ORDER BY recorded_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_stats_for_user(user_id: int) -> dict | None:
    """Return aggregate statistics for a user."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*)   AS total,
                ROUND(AVG(bmi), 2) AS avg_bmi,
                ROUND(MIN(bmi), 2) AS min_bmi,
                ROUND(MAX(bmi), 2) AS max_bmi
            FROM bmi_records
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def delete_record(record_id: int):
    """Delete a single BMI record."""
    with get_connection() as conn:
        conn.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
        conn.commit()


# ─── Bootstrap ────────────────────────────────────────────────────────────────
initialize_db()
