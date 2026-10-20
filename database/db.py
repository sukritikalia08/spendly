import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash


# ------------------------------------------------------------------ #
# Config                                                              #
# ------------------------------------------------------------------ #

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)

CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


# ------------------------------------------------------------------ #
# Connection                                                          #
# ------------------------------------------------------------------ #

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ------------------------------------------------------------------ #
# Schema                                                              #
# ------------------------------------------------------------------ #

def init_db():
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Users                                                               #
# ------------------------------------------------------------------ #

def get_user_by_email(email):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def create_user(name, email, password):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Expenses                                                            #
# ------------------------------------------------------------------ #

def get_expense_summary(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        top = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? "
            "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        return {
            "total": row["total"],
            "count": row["count"],
            "top_category": top["category"] if top else None,
        }
    finally:
        conn.close()


def get_category_breakdown(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT category, SUM(amount) AS total, COUNT(*) AS count "
            "FROM expenses WHERE user_id = ? "
            "GROUP BY category ORDER BY total DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def get_recent_expenses(user_id, limit=5):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, amount, category, date, description FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Seed data                                                           #
# ------------------------------------------------------------------ #

def seed_db():
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cur.lastrowid

        today = date.today()

        def day(d):
            return today.replace(day=d).isoformat()

        expenses = [
            (user_id, 450.0,  "Food",          day(1),  "Groceries"),
            (user_id, 120.0,  "Transport",     day(4),  "Metro card top-up"),
            (user_id, 1800.0, "Bills",         day(7),  "Electricity bill"),
            (user_id, 650.0,  "Health",        day(10), "Pharmacy"),
            (user_id, 500.0,  "Entertainment", day(13), "Movie tickets"),
            (user_id, 2299.0, "Shopping",      day(16), "New shoes"),
            (user_id, 300.0,  "Other",         day(19), "Gift wrapping"),
            (user_id, 280.0,  "Food",          day(22), "Dinner out"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    finally:
        conn.close()
