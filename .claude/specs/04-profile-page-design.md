# Spec: Profile Page Design

## Overview

Replace the `/profile` placeholder with a real page that a user lands on after signing in. Step 3 already redirects to `/profile` after login and registration, but the route still returns "Profile page — coming in Step 4". This step builds a read-only page. It shows the signed-in user's details (name, email, member-since date), a summary of their spending (total spent in ₹, number of expenses, top category), a breakdown by category with simple CSS bars, and their most recent expenses. It also brings in a `login_required` guard that the expense routes in Steps 7–9 will reuse. Editing the profile and changing the password are out of scope.

## Depends on

- Step 1, Database Setup: the `users` and `expenses` tables, `get_db()`, `CATEGORIES`, and the seeded demo user with 8 expenses in the current month
- Step 2, Registration: new accounts with no expenses, which drive the empty state
- Step 3, Login and Logout: `session["user_id"]` / `session["user_name"]`, `app.secret_key`, and the signed-in navbar

> Note: Steps 2 and 3 are not merged into `main` yet. This branch is stacked on `feature/login-and-logout`.

## Routes

- `GET /profile`: renders `profile.html` with the user, the summary stats, the category breakdown and the recent expenses. If the user is signed out, it redirects to `/login`. If `session["user_id"]` points at a user who no longer exists, it clears the session and redirects to `/login`. Access: logged-in

There are no other new paths. The endpoint name `profile` stays the same.

## Database changes

No database changes. Verified against `database/db.py`: `users` has `id`, `name`, `email` and `created_at`. `expenses` has `user_id`, `amount`, `category`, `date` (ISO `YYYY-MM-DD`) and `description`. Everything the page needs comes from these columns.

New query helpers go in `database/db.py`, under a new `# Expenses` section header (and `get_user_by_id` under `# Users`):

- `get_user_by_id(user_id)`: returns a `sqlite3.Row` (`id`, `name`, `email`, `created_at`) or `None`. Never select `password_hash` for this page
- `get_expense_summary(user_id)`: returns a dict with three keys:
  - `total`: `COALESCE(SUM(amount), 0)`
  - `count`: `COUNT(*)`
  - `top_category`: the category with the highest sum, or `None` if there are no expenses
- `get_category_breakdown(user_id)`: one row per category with `category`, `total` and `count`, ordered by `total DESC`. It covers only categories that have expenses
- `get_recent_expenses(user_id, limit=5)`: the newest expenses, ordered by `date DESC, id DESC`, with `id`, `amount`, `category`, `date` and `description`

Every query filters by `user_id = ?` and uses parameters.

## Templates

- **Create:**
  - `templates/profile.html`: extends `base.html` and loads `profile.css` through the `head` block. Sections, top to bottom:
    1. **Header card**: an avatar circle with the user's initial, the name (in `--font-display`), the email, and "Member since <Mon YYYY>" built from `created_at`. It also has an "Add expense" button that links to `url_for('add_expense')`
    2. **Stat tiles** (3 across, stacked on mobile): Total spent (`₹12,345.00`), Expenses (count), Top category (or "—")
    3. **Spending by category**: one row per category with its name, a horizontal bar whose width is that category's share of the total (an inline `style="width: N%"` is fine, since it isn't a colour), and the ₹ amount
    4. **Recent expenses**: a list or table of up to 5 items showing date (`20 Oct 2026`), description (or the category if blank), a category pill, and the ₹ amount right-aligned
    5. **Empty state**: if `count == 0`, sections 3 and 4 are replaced by one card that says "No expenses yet" and has an "Add your first expense" link to `url_for('add_expense')`
- **Modify:**
  - `templates/base.html`: inside the signed-in branch of `.nav-links`, wrap the `.nav-user` name in a link to `url_for('profile')` so the user can get back to the page

## Files to change

- `app.py`:
  - add `from functools import wraps`
  - add a `login_required` decorator in the `# Helpers` section. If `session.get("user_id")` is falsy, it redirects to `url_for("login")`
  - import the new db helpers
  - replace the `/profile` placeholder with the real view, decorated with `@login_required`
  - move `profile` out of the "Placeholder routes" section into "Routes"
  - add a small `_format_inr(amount)` helper, registered as a Jinja filter `inr`, that returns `f"₹{amount:,.2f}"`
- `database/db.py`: add `get_user_by_id`, `get_expense_summary`, `get_category_breakdown` and `get_recent_expenses`
- `templates/base.html`: link the navbar name to `/profile`

## Files to create

- `templates/profile.html`
- `static/css/profile.css`: page-only styles (`.profile-*`, `.stat-tile`, `.category-bar`, `.expense-row`, `.empty-state`), with a single-column layout below 720px

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. All SQL lives in `database/db.py`, and every expense query filters by `user_id = ?`
- Passwords hashed with werkzeug. This page never reads, selects or displays `password_hash`
- Use CSS variables, never hardcode hex values. Use the existing tokens (`--paper-card`, `--border`, `--accent`, `--accent-light`, `--accent-2`, `--ink-muted`, `--radius-md`, `--font-display`, …). If a new colour is truly needed, add it as a token in `:root` in `style.css`
- All templates extend `base.html`
- Format money only through the `inr` filter so every amount on the page looks the same
- Do the date formatting in Python (in the view or a helper), not with string slicing in Jinja
- Read the user from the database by `session["user_id"]`. Don't trust `session["user_name"]` for the page body
- Edit and delete links on recent expenses are out of scope, because those routes are still stubs until Steps 8–9
- No JavaScript is required. Don't add a `profile.js` unless there is real behaviour
- Comments use the boxed section-header style (`# ---- #`, `/* ---- */`)

## Definition of done

- [ ] Visiting `/profile` while signed out redirects (302) to `/login`
- [ ] Signing in as `demo@spendly.com` / `demo123` lands on `/profile`, which shows "Demo User", `demo@spendly.com` and a "Member since" date
- [ ] The Total spent tile shows `₹6,399.00`, the Expenses tile shows `8`, and Top category shows `Shopping` for the demo user
- [ ] Spending by category lists all 7 seeded categories, sorted from highest (Shopping ₹2,299.00) to lowest (Transport ₹120.00), with bar widths in proportion to each share
- [ ] Recent expenses shows the 5 newest demo expenses, newest first, with dates like `22 Oct 2026` and ₹ amounts
- [ ] A newly registered user sees ₹0.00, 0 expenses, "—" for top category, and the "No expenses yet" empty state with no errors
- [ ] One user never sees another user's expenses (register a second account and check)
- [ ] Clicking the name in the navbar opens `/profile`. "Sign out" still works and `/profile` then redirects to `/login`
- [ ] Deleting the signed-in user's row from the DB and reloading `/profile` clears the session and redirects to `/login` instead of crashing
- [ ] The layout stacks to one column at mobile width (about 375px) with no horizontal scroll
- [ ] `grep -nE '#[0-9a-fA-F]{3,6}' static/css/profile.css templates/profile.html` returns nothing
- [ ] `/`, `/login`, `/register`, `/terms` and `/privacy` still render, and the app starts on port 5001 without errors
