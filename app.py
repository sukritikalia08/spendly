import sqlite3

from flask import Flask, redirect, render_template, request, url_for

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)

ERR_MISSING_FIELDS = "Please fill in all fields."
ERR_INVALID_EMAIL = "Please enter a valid email address."
ERR_SHORT_PASSWORD = "Password must be at least 8 characters."
ERR_DUPLICATE_EMAIL = "An account with that email already exists."


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _valid_email(email):
    local, _, domain = email.partition("@")
    return email.count("@") == 1 and bool(local) and "." in domain


# ------------------------------------------------------------------ #
# Database setup                                                      #
# ------------------------------------------------------------------ #

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    error = None
    if not name or not email or not password.strip():
        error = ERR_MISSING_FIELDS
    elif not _valid_email(email):
        error = ERR_INVALID_EMAIL
    elif len(password) < 8:
        error = ERR_SHORT_PASSWORD
    elif get_user_by_email(email):
        error = ERR_DUPLICATE_EMAIL

    if not error:
        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            error = ERR_DUPLICATE_EMAIL
        else:
            return redirect(url_for("login"))

    return render_template("register.html", error=error, name=name, email=email), 400


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
