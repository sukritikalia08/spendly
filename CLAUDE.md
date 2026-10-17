# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spendly is a Flask + SQLite expense tracker (amounts shown in ₹) built as a step-by-step learning project. Most backend features are still stubs: placeholder routes in `app.py` return strings like `"... coming in Step N"`, and `database/db.py` holds only a comment that describes what it should contain. Build features one step at a time, matching the step numbers in those stubs:

- Step 1: `database/db.py`: `get_db()` (SQLite connection with `row_factory` set and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (sample dev data). The DB file is `expense_tracker.db`, which is gitignored.
- Step 3: logout. Step 4: profile. Steps 7–9: add, edit and delete expenses (`/expenses/add`, `/expenses/<int:id>/edit`, `/expenses/<int:id>/delete`).

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

- `app.py` holds every route in one file; there are no blueprints. The page routes (`/`, `/login`, `/register`, `/terms`, `/privacy`) only render templates. The login and register forms already `POST` to `/login` and `/register`, but those routes don't accept POST yet. Both templates show an `{{ error }}` variable if one is passed in.
- `templates/base.html` holds the navbar, the footer (with Terms and Privacy links), the Google Fonts links (DM Serif Display and DM Sans), `style.css` and `main.js`. Child templates override the `title`, `head`, `content` and `scripts` blocks. Link with `url_for(...)` and keep the endpoint names stable.
- Styling: `static/css/style.css` is the global stylesheet and defines the design tokens as CSS variables in `:root` (`--ink*`, `--paper*`, `--accent`, `--accent-2`, `--danger`, `--border`, `--radius-*`, `--font-display`, `--font-body`). Use these tokens rather than hard-coded colors. Styles for a single page go in their own file, loaded through the `head` block (for example `landing.css`).
- JS: plain vanilla JS, no build step. `main.js` is the global script and is currently empty. Scripts for a single page are loaded through the `scripts` block. `landing.js`, which drives the "See how it works" video modal, is the pattern to follow: an IIFE that returns early if its elements are missing.

## Conventions

- Commit messages are prefixed with the area they touch, e.g. `landing: redesign hero section`.
- Comments in Python, CSS and JS use the boxed section-header style (`# ---- #` / `/* ---- */` / `// ---- //` banners).
