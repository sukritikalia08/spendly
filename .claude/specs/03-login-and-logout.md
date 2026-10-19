# Spec: Login and Logout

## Overview

Make the sign-in form at `/login` work and replace the `/logout` placeholder. Step 2 made it possible to create accounts but gave users no way to sign in. This step checks the submitted email and password against the `users` table with werkzeug's `check_password_hash`. On success it stores the user's `id` and `name` in Flask's signed session cookie, and `/logout` clears that session. This is the first step that needs a logged-in user, so Step 4 (profile) and Steps 7–9 (expenses) all build on it. The navbar also changes depending on whether someone is signed in.

## Depends on

- Step 1, Database Setup: the `users` table, `get_db()` and the seeded demo user (`demo@spendly.com` / `demo123`)
- Step 2, Registration: `get_user_by_email()` in `database/db.py`, the lowercase email storage, the error-message constants and `ERR_MISSING_FIELDS` in `app.py`

## Routes

No new paths. Two existing routes change:

- `GET /login`: renders `login.html`. If the user is already signed in, it redirects to `/profile`. Access: public
- `POST /login`: validates the form, checks the credentials, sets the session and redirects to `/profile`. On failure it re-renders with an error and status 400 (missing fields) or 401 (wrong credentials). Access: public
- `GET /logout`: clears the session and redirects to `/` (landing). It replaces the "coming in Step 3" placeholder. Access: public (safe to hit while signed out)
- `GET /register`: if the user is already signed in, it redirects to `/profile`. Access: public

All endpoint names (`login`, `logout`, `register`, `profile`) stay the same.

## Database changes

No database changes. Verified against `database/db.py`: `users` already has `id`, `name`, `email` (unique, stored lowercased) and `password_hash`, and `get_user_by_email(email)` already returns a `sqlite3.Row` or `None`.

## Templates

- **Create:** none
- **Modify:**
  - `templates/login.html`: add `value="{{ email or '' }}"` to the email input so the user doesn't have to retype it after an error. Never re-fill the password. Change `action="/login"` to `action="{{ url_for('login') }}"`
  - `templates/base.html`: make `.nav-links` conditional. If `session.user_id` is set, show the user's name (`session.user_name`) and a "Sign out" link to `url_for('logout')`. Otherwise keep the current "Sign in" and "Get started" links

## Files to change

- `app.py`:
  - import `session` from `flask` and `check_password_hash` from `werkzeug.security`
  - set `app.secret_key` from `os.environ.get("SECRET_KEY", "dev-secret-change-me")`
  - add the error constant `ERR_INVALID_LOGIN = "Invalid email or password."`
  - make `/login` accept `GET` and `POST`
  - implement `/logout`
  - redirect signed-in users away from `/login` and `/register`
- `templates/login.html`: re-fill the email field and use `url_for` (see Templates)
- `templates/base.html`: switch the navbar between signed-in and signed-out links (see Templates)
- `static/css/style.css`: add a small `.nav-user` style for the signed-in name, using the existing tokens

## Files to create

- None

## New dependencies

No new dependencies. Uses `flask.session` and `werkzeug.security.check_password_hash`, which are already installed.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. Reuse `get_user_by_email()` and keep the SQL in `database/db.py`
- Passwords hashed with werkzeug. Verify with `check_password_hash(user["password_hash"], password)`, and never compare plain text
- Use CSS variables, never hardcode hex values
- All templates extend `base.html`
- On `POST /login`:
  - read `email` (stripped, lowercased) and `password` (not stripped)
  - if either is blank, show `ERR_MISSING_FIELDS` with status 400
  - if the user doesn't exist or the password is wrong, show the same generic `ERR_INVALID_LOGIN` with status 401. Never reveal which part was wrong
- Do **not** enforce the 8-character minimum at login. The seeded demo password `demo123` has 7 characters and must still work
- On success, call `session.clear()` first, then set `session["user_id"]` and `session["user_name"]`, then `redirect(url_for("profile"))`
- On logout, call `session.clear()` and then `redirect(url_for("landing"))`
- Never store the password or its hash in the session, and never log it
- Never echo the password back into the form
- Comments use the boxed section-header style (`# ---- #`, `/* ---- */`)

## Definition of done

- [ ] Signing in as `demo@spendly.com` / `demo123` redirects (302) to `/profile`
- [ ] Signing in with `DEMO@Spendly.com` (mixed case) also works
- [ ] An account created through `/register` can sign in with its password
- [ ] A wrong password shows "Invalid email or password." with status 401, and the email field keeps its value
- [ ] An unknown email shows the same "Invalid email or password." message with status 401
- [ ] A blank email or password shows "Please fill in all fields." with status 400
- [ ] After signing in, the navbar shows the user's name and "Sign out" instead of "Sign in" and "Get started"
- [ ] Visiting `/login` or `/register` while signed in redirects to `/profile`
- [ ] Clicking "Sign out" clears the session, redirects to `/` and restores the signed-out navbar
- [ ] Visiting `/logout` while signed out redirects to `/` without an error
- [ ] The session cookie holds no password data. Browser devtools show only a signed Flask `session` cookie
- [ ] `/`, `/register`, `/terms` and `/privacy` still render, and the app starts without errors on port 5001
