import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import (
    create_user,
    get_category_breakdown,
    get_expense_summary,
    get_expenses,
    get_recent_expenses,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
)

app = Flask(__name__)


# ------------------------------------------------------------------ #
# Config                                                              #
# ------------------------------------------------------------------ #

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


# ------------------------------------------------------------------ #
# Error messages                                                      #
# ------------------------------------------------------------------ #

ERR_MISSING_FIELDS = "Please fill in all fields."
ERR_INVALID_EMAIL = "Please enter a valid email address."
ERR_SHORT_PASSWORD = "Password must be at least 8 characters."
ERR_DUPLICATE_EMAIL = "An account with that email already exists."
ERR_INVALID_LOGIN = "Invalid email or password."
ERR_NOT_SIGNED_IN = "Sign in required."


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _valid_email(email):
    local, _, domain = email.partition("@")
    return email.count("@") == 1 and bool(local) and "." in domain


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error=ERR_NOT_SIGNED_IN), 401
        return view(*args, **kwargs)
    return wrapped


def _category_breakdown(user_id, total):
    # breakdown is empty when there are no expenses, so total is never 0 here
    return [
        {
            "category": row["category"],
            "total": row["total"],
            "count": row["count"],
            "pct": round(row["total"] / total * 100, 1),
        }
        for row in get_category_breakdown(user_id)
    ]


def _format_inr(amount):
    return f"₹{amount:,.2f}"


def _format_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.day} {d:%b %Y}"


def _format_member_since(created_at):
    return datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").strftime("%b %Y")


app.add_template_filter(_format_inr, "inr")


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
    if session.get("user_id"):
        return redirect(url_for("profile"))

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


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error=ERR_MISSING_FIELDS, email=email), 400

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error=ERR_INVALID_LOGIN, email=email), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    user = get_user_by_id(session["user_id"])
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    summary = get_expense_summary(user["id"])
    breakdown = _category_breakdown(user["id"], summary["total"])
    recent = [
        {**dict(row), "date_display": _format_date(row["date"])}
        for row in get_recent_expenses(user["id"])
    ]

    return render_template(
        "profile.html",
        user=user,
        member_since=_format_member_since(user["created_at"]),
        summary=summary,
        breakdown=breakdown,
        recent=recent,
    )


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# API: transaction history                                            #
# ------------------------------------------------------------------ #

@app.route("/api/expenses")
@api_login_required
def api_expenses():
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify(error="limit and offset must be integers."), 400

    if not 1 <= limit <= 100:
        return jsonify(error="limit must be between 1 and 100."), 400
    if offset < 0:
        return jsonify(error="offset must be 0 or greater."), 400

    user_id = session["user_id"]
    rows = get_expenses(user_id, limit, offset)
    total = get_expense_summary(user_id)["count"]

    return jsonify(
        expenses=[dict(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


# ------------------------------------------------------------------ #
# API: summary stats                                                  #
# ------------------------------------------------------------------ #

@app.route("/api/summary")
@api_login_required
def api_summary():
    summary = get_expense_summary(session["user_id"])
    return jsonify(
        total=summary["total"],
        count=summary["count"],
        top_category=summary["top_category"],
    )


# ------------------------------------------------------------------ #
# API: category breakdown                                             #
# ------------------------------------------------------------------ #

@app.route("/api/categories")
@api_login_required
def api_categories():
    user_id = session["user_id"]
    summary = get_expense_summary(user_id)
    return jsonify(categories=_category_breakdown(user_id, summary["total"]))


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
