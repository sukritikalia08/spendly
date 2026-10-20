# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spendly is a Flask + SQLite expense tracker (amounts shown in ₹) built as a step-by-step learning project. Each step has a spec in `.claude/specs/<NN>-<slug>.md`, written with `/create-spec`, and is built on its own `feature/<slug>` branch.

Done:

- Step 1: `database/db.py`: `get_db()` (SQLite connection with `row_factory` set and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (a demo user, `demo@spendly.com` / `demo123`, with 8 expenses dated in the last 3 weeks) and query helpers. The DB file is `expense_tracker.db`, which is gitignored. Delete it to reseed.
- Step 2: registration. Step 3: login and logout (`session["user_id"]`, `login_required`). Step 4: profile page design.
- Step 5: the profile page shows real data, and there are login-required JSON endpoints: `/api/expenses` (paginated), `/api/summary` and `/api/categories`.

Still to build: Steps 7–9, adding, editing and deleting expenses (`/expenses/add`, `/expenses/<int:id>/edit`, `/expenses/<int:id>/delete`). These are placeholder routes in `app.py` that return `"... coming in Step N"`. Step 6 isn't defined yet.

## Commands

```bash
source venv/bin/activate            # a virtualenv is already in venv/
pip install -r requirements.txt     # flask, werkzeug, pytest, pytest-flask
python app.py                       # dev server with debug on, http://localhost:5001
pytest                              # run tests (none exist yet)
pytest path/to/test_file.py::test_name   # run a single test
```

The app runs on port **5001**, not Flask's default 5000. There is no linter or build step.

## Architecture

- `app.py` holds every route in one file; there are no blueprints. Pages use `login_required`, which redirects to `/login`. `/api/*` routes use `api_login_required`, which returns 401 JSON. SQL lives only in `database/db.py`, which uses plain `sqlite3` with parameterized queries. The login and register templates show an `{{ error }}` variable if one is passed in.
- `templates/base.html` holds the navbar, the footer (with Terms and Privacy links), the Google Fonts links (DM Serif Display and DM Sans), `style.css` and `main.js`. Child templates override the `title`, `head`, `content` and `scripts` blocks. Link with `url_for(...)` and keep the endpoint names stable.
- Styling: `static/css/style.css` is the global stylesheet and defines the design tokens as CSS variables in `:root` (`--ink*`, `--paper*`, `--accent`, `--accent-2`, `--danger`, `--border`, `--radius-*`, `--font-display`, `--font-body`). Use these tokens rather than hard-coded colors. Styles for a single page go in their own file, loaded through the `head` block (for example `landing.css`).
- JS: plain vanilla JS, no build step. `main.js` is the global script and is currently empty. Scripts for a single page are loaded through the `scripts` block. `landing.js`, which drives the "See how it works" video modal, is the pattern to follow: an IIFE that returns early if its elements are missing.

## Conventions

- Commit messages are prefixed with the area they touch, e.g. `landing: redesign hero section`.
- Comments in Python, CSS and JS use the boxed section-header style (`# ---- #` / `/* ---- */` / `// ---- //` banners).
