# Spec Document

## 1. Overview

Make the registration form at `/register` work.

The form in `templates/register.html` already `POST`s `name`, `email` and `password` to `/register`, but the route only accepts `GET`. This step lets the route accept `POST`, validates the input, hashes the password and creates a row in the `users` table.

Registration only creates the account. Signing the user in (sessions) belongs to the login step.

---

## 2. Depends on

- Step 1, Database Setup: the `users` table, `get_db()` and the `werkzeug` password hashing in `database/db.py`

---

## 3. Routes

| Method | Path | Behaviour |
| --- | --- | --- |
| GET | `/register` | Renders `register.html` (unchanged) |
| POST | `/register` | Validates the form, creates the user, then redirects to `/login` |

- The endpoint name stays `register`, so existing `url_for('register')` links keep working
- All other routes remain unchanged

---

## 4. Database Schema

- No schema changes
- Uses the existing `users` table from Step 1:

| Column | Used for |
| --- | --- |
| name | Full name from the form (trimmed) |
| email | Email from the form (trimmed, lowercased), unique |
| password_hash | `generate_password_hash(password)` |
| created_at | Filled automatically by its default |

---

## 5. Functions to Implement (`database/db.py`)

---

### A. `get_user_by_email(email)`

- Runs `SELECT * FROM users WHERE email = ?`
- Returns the matching `sqlite3.Row`, or `None`
- Closes the connection before returning
- The login step will reuse this function

---

### B. `create_user(name, email, password)`

- Hashes `password` with `generate_password_hash`
- Inserts the user with a parameterized `INSERT`
- Commits and returns the new user's `id` (`cursor.lastrowid`)
- Lets `sqlite3.IntegrityError` propagate if the email already exists
- Closes the connection in `try/finally`

---

## 6. Changes to `app.py`

- Import `request`, `redirect` and `url_for` from `flask`
- Import `create_user` and `get_user_by_email` from `database.db`
- Change the route to `@app.route("/register", methods=["GET", "POST"])`
- On `POST`:
    1. Read `name`, `email` and `password` from `request.form`. Strip `name` and `email`, and lowercase `email`. Do not strip `password`
    2. Validate them (see section 11). On the first failure, re-render `register.html` with `error`, `name` and `email`, and status `400`
    3. If `get_user_by_email(email)` finds a user, re-render with the error "An account with that email already exists." and status `400`
    4. Call `create_user(...)`. If it raises `sqlite3.IntegrityError`, which can happen if two submissions race, show the same duplicate-email error
    5. On success, `redirect(url_for("login"))`
- On `GET`: render `register.html` as it does now

---

## 7. Files to Change

- `app.py`: make the register route accept `POST` and handle it
- `database/db.py`: add `get_user_by_email()` and `create_user()`
- `templates/register.html`: add `value="{{ name or '' }}"` to the name input and `value="{{ email or '' }}"` to the email input, so the user doesn't have to retype them after an error. The password input is never re-filled

---

## 8. Files to Create

- None

---

## 9. Dependencies

- No new pip packages
- Use:
    - `sqlite3` (standard library)
    - `werkzeug.security.generate_password_hash` (already installed)
    - `flask.request`, `flask.redirect` and `flask.url_for`

---

## 10. Error Messages (Fixed List)

Use exactly these strings:

- "Please fill in all fields."
- "Please enter a valid email address."
- "Password must be at least 8 characters."
- "An account with that email already exists."

---

## 11. Rules for Implementation

- Validation checks run in this order and stop at the first failure:
    1. `name`, `email` and `password` are all non-empty after stripping
    2. `email` contains exactly one `@`, with a non-empty part before it and a `.` in the part after it
    3. `password` is at least 8 characters
    4. `email` is not already registered
- Store emails lowercased, so `Demo@Spendly.com` and `demo@spendly.com` count as the same account
- Never store or log the plain-text password. Store only the hash
- Never echo the password back into the form
- Use **parameterized queries only**, with no string formatting in SQL
- Keep the SQL in `database/db.py`, not in the route
- Keep the `required` attributes in the HTML, but always validate on the server as well
- Comments use the boxed section-header style

---

## 12. Expected Behavior

- A valid submission creates exactly one `users` row and redirects to `/login` (302)
- After a failed submission:
    - the page re-renders with the error in the `.auth-error` box
    - the name and email fields keep what the user typed, and the password field is empty
    - no row is created
- `GET /register` looks the same as before

---

## 13. Error Handling Expectations

- Missing or blank field → "Please fill in all fields.", 400
- Malformed email (e.g. `abc`, `a@b`, `@x.com`) → "Please enter a valid email address.", 400
- Password of 7 characters or fewer → "Password must be at least 8 characters.", 400
- Registering `demo@spendly.com` or `DEMO@spendly.com` → "An account with that email already exists.", 400
- A database `IntegrityError` while inserting → the same duplicate-email message, not a 500

---

## 14. Definition of Done

- [ ]  `POST /register` with valid data creates the user and redirects to `/login`
- [ ]  The stored `password_hash` is a werkzeug hash, and `check_password_hash` accepts the original password
- [ ]  Each invalid case in section 13 shows its exact message with status 400 and creates no row
- [ ]  A duplicate email is rejected regardless of letter case
- [ ]  Name and email are kept after an error, and the password is not
- [ ]  `GET /register` and every other page still render
- [ ]  All queries use parameterized SQL
- [ ]  App starts without errors
