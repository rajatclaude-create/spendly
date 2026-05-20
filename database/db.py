import os
import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        (existing,) = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        if existing > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123", method="pbkdf2:sha256")),
        )
        user_id = cursor.lastrowid

        sample_expenses = [
            (user_id, 12.50, "Food",          "2026-05-02", "Lunch at cafe"),
            (user_id, 30.00, "Transport",     "2026-05-04", "Monthly transit pass top-up"),
            (user_id, 85.20, "Bills",         "2026-05-06", "Electricity bill"),
            (user_id, 45.00, "Health",        "2026-05-09", "Pharmacy"),
            (user_id, 18.75, "Entertainment", "2026-05-12", "Movie ticket"),
            (user_id, 64.30, "Shopping",      "2026-05-15", "New running shoes"),
            (user_id, 22.00, "Other",         "2026-05-17", "Birthday gift for friend"),
            (user_id,  9.40, "Food",          "2026-05-19", "Coffee and pastry"),
        ]
        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()
