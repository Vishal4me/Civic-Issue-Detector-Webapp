"""
SQLite storage for civic issue reports.

Kept deliberately simple (stdlib sqlite3, no ORM) so the whole project can be
read and explained in a viva without a second library to learn.
"""
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone

DATABASE_PATH = os.environ.get("DATABASE_PATH", "./civic_reports.db")

STATUSES = ["Reported", "Acknowledged", "In Progress", "Resolved"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    address TEXT,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    needs_review INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Reported',
    email_sent INTEGER NOT NULL DEFAULT 0,
    email_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)


def create_report(image_path, latitude, longitude, address, category, confidence,
                   needs_review, email_sent, email_error=None):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO reports
               (image_path, latitude, longitude, address, category, confidence,
                needs_review, status, email_sent, email_error, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'Reported', ?, ?, ?, ?)""",
            (image_path, latitude, longitude, address, category, confidence,
             int(needs_review), int(email_sent), email_error, now, now),
        )
        return cur.lastrowid


def list_reports(category=None, status=None):
    query = "SELECT * FROM reports WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_report(report_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        return dict(row) if row else None


def update_status(report_id, status):
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "UPDATE reports SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, report_id),
        )


def stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM reports").fetchone()["c"]
        by_category = conn.execute(
            "SELECT category, COUNT(*) AS c FROM reports GROUP BY category"
        ).fetchall()
        by_status = conn.execute(
            "SELECT status, COUNT(*) AS c FROM reports GROUP BY status"
        ).fetchall()
        resolved = conn.execute(
            "SELECT COUNT(*) AS c FROM reports WHERE status = 'Resolved'"
        ).fetchone()["c"]
        return {
            "total": total,
            "resolved": resolved,
            "by_category": {r["category"]: r["c"] for r in by_category},
            "by_status": {r["status"]: r["c"] for r in by_status},
        }
