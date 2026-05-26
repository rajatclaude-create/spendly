import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
# Override in production via the SPENDLY_SECRET_KEY env var
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-only-change-me")

# Used to keep failed-login timing consistent whether the email exists or not
_DUMMY_PASSWORD_HASH = generate_password_hash("dummy", method="pbkdf2:sha256")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


def _validate_registration(name, email, password, confirm_password):
    if not name or not email or not password or not confirm_password:
        return "All fields are required."
    if len(name) > 80:
        return "Name must be 80 characters or fewer."
    if "@" not in email or "." not in email.split("@")[-1]:
        return "Please enter a valid email address."
    if len(email) > 120:
        return "Email must be 120 characters or fewer."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if password != confirm_password:
        return "Passwords do not match."
    return None


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=None, form={})

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""

    error = _validate_registration(name, email, password, confirm_password)
    if error:
        return render_template(
            "register.html",
            error=error,
            form={"name": name, "email": email},
        )

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    conn = get_db()
    try:
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Email already registered.",
                form={"name": name, "email": email},
            )
    finally:
        conn.close()

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None, form={})

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    if not email or not password:
        return render_template(
            "login.html",
            error="All fields are required.",
            form={"email": email},
        )

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        check_password_hash(_DUMMY_PASSWORD_HASH, password)
        return render_template(
            "login.html",
            error="Invalid email or password.",
            form={"email": email},
        )

    if not check_password_hash(row["password_hash"], password):
        return render_template(
            "login.html",
            error="Invalid email or password.",
            form={"email": email},
        )

    session.clear()
    session["user_id"] = row["id"]
    session["user_name"] = row["name"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "May 2026",
    }
    stats = {
        "total_spent": 8420,
        "transaction_count": 24,
        "top_category": "Food",
    }
    transactions = [
        {"date": "2026-05-25", "description": "Swiggy - biryani",     "category": "Food",          "amount": 320},
        {"date": "2026-05-24", "description": "Ola - airport",        "category": "Transport",     "amount": 780},
        {"date": "2026-05-22", "description": "Airtel Fiber",         "category": "Bills",         "amount": 1199},
        {"date": "2026-05-21", "description": "Apollo Pharmacy",      "category": "Health",        "amount": 540},
        {"date": "2026-05-19", "description": "Movie - PVR Phoenix",  "category": "Entertainment", "amount": 460},
        {"date": "2026-05-17", "description": "Myntra - sneakers",    "category": "Shopping",      "amount": 2499},
    ]
    breakdown = [
        {"category": "Food",          "total": 2120, "percent": 25},
        {"category": "Shopping",      "total": 2499, "percent": 30},
        {"category": "Bills",         "total": 1399, "percent": 17},
        {"category": "Transport",     "total": 980,  "percent": 12},
        {"category": "Health",        "total": 540,  "percent": 6},
        {"category": "Entertainment", "total": 460,  "percent": 5},
        {"category": "Other",         "total": 422,  "percent": 5},
    ]
    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        breakdown=breakdown,
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
