"""
Plain sqlite3 data layer for Jharkhand Samadhan — no ORM dependency, so the
whole app only needs Flask + Pillow to run.

Rows are hydrated into SimpleNamespace objects so templates can use normal
dot-attribute access (c.status, c.citizen.name, c.deadline.strftime(...)),
with computed fields like is_overdue attached in Python.
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta
from types import SimpleNamespace

from flask import g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "jsamadhan.db")

ROLES = ("citizen", "officer", "admin")
INFRA_CATEGORIES = {"Roads & Infrastructure"}

CATEGORIES = [
    "Roads & Infrastructure", "Water Resources", "Electricity",
    "Sanitation", "Healthcare", "Education", "Public Safety", "Other",
]

DISTRICTS = [
    "Ranchi", "Dhanbad", "Dumka", "Bokaro", "Gumla", "Deoghar",
    "Hazaribagh", "Giridih", "East Singhbhum", "West Singhbhum",
]

RESOLUTION_WINDOW_DAYS = 5

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    district TEXT NOT NULL,
    location_text TEXT,
    latitude REAL,
    longitude REAL,
    image_metadata TEXT,
    image_taken_at TEXT,
    image_latitude REAL,
    image_longitude REAL,
    location_address TEXT,
    location_city TEXT,
    location_state TEXT,
    pincode TEXT,
    photo_filename TEXT,
    is_photo_video INTEGER DEFAULT 0,
    citizen_id INTEGER NOT NULL,
    officer_id INTEGER,
    status TEXT NOT NULL DEFAULT 'Submitted',
    ai_confidence INTEGER,
    ai_note TEXT,
    accepted_at TEXT,
    deadline TEXT,
    resolution_filename TEXT,
    resolution_confidence REAL,
    resolution_note TEXT,
    resolved_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(citizen_id) REFERENCES users(id),
    FOREIGN KEY(officer_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS complaint_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    note TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(complaint_id) REFERENCES complaints(id)
);
"""


# ---------------------------------------------------------------------------
# connection management (one connection per request, via flask.g)
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    complaint_columns = {row[1] for row in conn.execute("PRAGMA table_info(complaints)")}
    for column, column_type in (
        ("latitude", "REAL"), ("longitude", "REAL"),
        ("image_metadata", "TEXT"), ("image_taken_at", "TEXT"),
        ("image_latitude", "REAL"), ("image_longitude", "REAL"),
        ("location_address", "TEXT"), ("location_city", "TEXT"),
        ("location_state", "TEXT"), ("pincode", "TEXT"),
    ):
        if column not in complaint_columns:
            conn.execute(f"ALTER TABLE complaints ADD COLUMN {column} {column_type}")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# hydration helpers — turn sqlite3.Row into attribute-friendly objects
# ---------------------------------------------------------------------------

def _parse_dt(s):
    return datetime.fromisoformat(s) if s else None


def _now():
    return datetime.utcnow()


def hydrate_user(row):
    if row is None:
        return None
    d = dict(row)
    ns = SimpleNamespace(**d)
    ns.created_at = _parse_dt(d.get("created_at"))
    return ns


def hydrate_log(row):
    d = dict(row)
    ns = SimpleNamespace(**d)
    ns.timestamp = _parse_dt(d["timestamp"])
    return ns


def hydrate_complaint(conn, row, with_relations=True):
    if row is None:
        return None
    d = dict(row)
    ns = SimpleNamespace(**d)
    ns.created_at = _parse_dt(d.get("created_at"))
    ns.accepted_at = _parse_dt(d.get("accepted_at"))
    ns.deadline = _parse_dt(d.get("deadline"))
    ns.resolved_at = _parse_dt(d.get("resolved_at"))
    ns.is_photo_video = bool(d.get("is_photo_video"))
    ns.is_infra = d["category"] in INFRA_CATEGORIES
    ns.is_overdue = bool(ns.deadline) and ns.status == "Accepted by Officer" and _now() > ns.deadline
    ns.days_left = (ns.deadline - _now()).days if ns.deadline else None

    if with_relations:
        ns.citizen = hydrate_user(get_user_by_id(conn, d["citizen_id"]))
        ns.officer = hydrate_user(get_user_by_id(conn, d["officer_id"])) if d.get("officer_id") else None
        ns.logs = [hydrate_log(r) for r in
                   conn.execute("SELECT * FROM complaint_logs WHERE complaint_id=? ORDER BY timestamp ASC",
                                (d["id"],)).fetchall()]
    return ns


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------

def create_user(conn, name, email, phone, password, role):
    ph = generate_password_hash(password)
    cur = conn.execute(
        "INSERT INTO users (name, email, phone, role, password_hash, created_at) VALUES (?,?,?,?,?,?)",
        (name, email, phone, role, ph, _now().isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def get_user_by_id(conn, user_id):
    if user_id is None:
        return None
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()


def get_user_by_email(conn, email):
    return conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()


def get_user_by_email_role(conn, email, role):
    return conn.execute("SELECT * FROM users WHERE email=? AND role=?", (email, role)).fetchone()


def verify_password(user_row, password):
    return check_password_hash(user_row["password_hash"], password)


def list_officers(conn):
    return [hydrate_user(r) for r in conn.execute("SELECT * FROM users WHERE role='officer' ORDER BY name").fetchall()]


def count_users(conn, role):
    return conn.execute("SELECT COUNT(*) c FROM users WHERE role=?", (role,)).fetchone()["c"]


# ---------------------------------------------------------------------------
# complaints
# ---------------------------------------------------------------------------

def new_complaint_code(conn):
    while True:
        code = f"JS-{random.randint(10000, 99999)}"
        if not conn.execute("SELECT 1 FROM complaints WHERE code=?", (code,)).fetchone():
            return code


def create_complaint(conn, **fields):
    fields.setdefault("created_at", _now().isoformat())
    fields.setdefault("status", "Submitted")
    cols = ", ".join(fields.keys())
    placeholders = ", ".join("?" for _ in fields)
    cur = conn.execute(f"INSERT INTO complaints ({cols}) VALUES ({placeholders})", tuple(fields.values()))
    conn.commit()
    return cur.lastrowid


def add_log(conn, complaint_id, status, note=""):
    conn.execute(
        "INSERT INTO complaint_logs (complaint_id, status, note, timestamp) VALUES (?,?,?,?)",
        (complaint_id, status, note, _now().isoformat()),
    )


def set_status(conn, complaint_id, status, note="", extra_fields=None):
    fields = dict(extra_fields or {})
    fields["status"] = status
    set_clause = ", ".join(f"{k}=?" for k in fields)
    conn.execute(f"UPDATE complaints SET {set_clause} WHERE id=?", (*fields.values(), complaint_id))
    add_log(conn, complaint_id, status, note)
    conn.commit()


def get_complaint_row(conn, complaint_id=None, code=None):
    if code is not None:
        return conn.execute("SELECT * FROM complaints WHERE code=?", (code,)).fetchone()
    return conn.execute("SELECT * FROM complaints WHERE id=?", (complaint_id,)).fetchone()


def list_by_citizen(conn, citizen_id):
    rows = conn.execute("SELECT * FROM complaints WHERE citizen_id=? ORDER BY created_at DESC",
                         (citizen_id,)).fetchall()
    return [hydrate_complaint(conn, r, with_relations=True) for r in rows]


def list_queue(conn):
    rows = conn.execute(
        "SELECT * FROM complaints WHERE status IN ('Pending Officer Review','AI Verified') ORDER BY created_at ASC"
    ).fetchall()
    return [hydrate_complaint(conn, r, with_relations=True) for r in rows]


def list_my_cases(conn, officer_id):
    rows = conn.execute(
        "SELECT * FROM complaints WHERE officer_id=? AND status IN ('Accepted by Officer','Reopened') "
        "ORDER BY deadline ASC", (officer_id,)
    ).fetchall()
    return [hydrate_complaint(conn, r, with_relations=True) for r in rows]


def list_resolved_by(conn, officer_id, limit=10):
    rows = conn.execute(
        "SELECT * FROM complaints WHERE officer_id=? AND status='Resolved' ORDER BY resolved_at DESC LIMIT ?",
        (officer_id, limit)
    ).fetchall()
    return [hydrate_complaint(conn, r, with_relations=True) for r in rows]


def list_all_complaints(conn):
    rows = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    return [hydrate_complaint(conn, r, with_relations=True) for r in rows]
