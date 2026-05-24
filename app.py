import sqlite3

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)

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


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


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
