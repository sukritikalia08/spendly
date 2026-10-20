# Spec: Backend Routes for Profile Page

## Overview

Connect the profile page to the signed-in user's real data. Step 4 designed `templates/profile.html` against temporary static data: a `{% set %}` block at the top of the `content` block overrides the `summary`, `breakdown` and `recent` values that the `profile` route in `app.py` already passes in. So every user, including a brand-new one, sees the same made-up ₹14,400 across 24 expenses. This step removes that override so the page shows what the backend computes from the `expenses` table. It also fixes the demo seed data, which places expenses on days 1–22 of the current month, so on any day before the 22nd some of them are dated in the future and show up at the top of "Recent expenses". It's the last step before expenses can be added (Step 7), so the page has to be correct for both the seeded demo user and empty accounts.

## Depends on

- Step 1, Database Setup: the `users` and `expenses` tables, `get_db()` and `seed_db()`
- Step 2, Registration: new accounts with no expenses, which exercise the empty state
- Step 3, Login and Logout: `session["user_id"]` and the `login_required` decorator
- Step 4, Profile Page Design: `templates/profile.html`, `static/css/profile.css` and the context variables it expects (`user`, `member_since`, `summary`, `breakdown`, `recent`)

## Routes

The existing page route keeps working as it does now, and its output now reaches the page:

- `GET /profile`: builds `summary` from `get_expense_summary()`, `breakdown` from the new `_category_breakdown()` helper (shared with `/api/categories`), and `recent` from `get_recent_expenses()` with a `date_display` per row, then renders `profile.html`. Access: logged-in

Three new JSON endpoints expose the same data. Each one is in its own boxed section of `app.py`. Signed-out requests get `401 {"error": "Sign in required."}` from a new `api_login_required` decorator instead of a redirect. Amounts are raw numbers, not ₹ strings, and only the signed-in user's rows are returned.

- `GET /api/expenses?limit=20&offset=0`: transaction history, newest first. `limit` must be an integer from 1 to 100 (default 20) and `offset` an integer ≥ 0 (default 0); anything else returns 400 `{"error": ...}`. Returns `{"expenses": [{id, amount, category, date, description}], "total", "limit", "offset"}`. Access: logged-in
- `GET /api/summary`: `{"total", "count", "top_category"}` (`top_category` is `null` when there are no expenses). Access: logged-in
- `GET /api/categories`: `{"categories": [{category, total, count, pct}]}`, highest total first, `[]` when empty. Access: logged-in

## Database changes

No schema changes. The existing query helpers in `database/db.py` (`get_user_by_id`, `get_expense_summary`, `get_category_breakdown`, `get_recent_expenses`) are used as they are.

One new query helper: `get_expenses(user_id, limit, offset)` is the paginated version of `get_recent_expenses`. It returns the same columns in the same `ORDER BY date DESC, id DESC` order, with `LIMIT ? OFFSET ?`. The total count comes from `get_expense_summary()["count"]`.

Seed data only: in `seed_db()`, replace the `day(d)` helper (`today.replace(day=d)`) with dates counted back from today using `today - timedelta(days=n)`, so no seeded expense is ever in the future. Keep the same 8 expenses, amounts, categories and descriptions, and their order from oldest to newest:

| Description | Days ago |
|---|---|
| Groceries | 21 |
| Metro card top-up | 18 |
| Electricity bill | 15 |
| Pharmacy | 12 |
| Movie tickets | 9 |
| New shoes | 6 |
| Gift wrapping | 3 |
| Dinner out | 0 |

`seed_db()` only runs when the `users` table is empty, so an existing `expense_tracker.db` keeps its old dates. Delete the file and restart the app to reseed.

## Templates

- **Create:** none
- **Modify:**
  - `templates/profile.html`: delete the whole "Temporary static data" block (the boxed Jinja comment and the three `{% set summary %}`, `{% set breakdown %}` and `{% set recent %}` statements). Leave the rest of the markup unchanged

## Files to change

- `templates/profile.html`: remove the static-data override
- `database/db.py`: make the seed dates relative to today (import `timedelta` next to `date`) and add `get_expenses()`
- `app.py`: import `jsonify` and `get_expenses`, add `ERR_NOT_SIGNED_IN`, `api_login_required` and `_category_breakdown()`, switch `profile()` to use the helper, and add the three API sections
- `CLAUDE.md`: update the "Project overview" so it no longer describes `database/db.py`, login and the profile as stubs. List Steps 1–5 as done and Steps 7–9 (add, edit and delete expenses) as the remaining placeholders

## Files to create

- None, apart from this spec

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. Don't add SQL to `app.py`. Any new query belongs in `database/db.py`
- Passwords hashed with werkzeug (not touched in this step)
- Use CSS variables, never hardcode hex values (no CSS changes are expected in this step)
- All templates extend `base.html`
- Don't rename the `profile` or `add_expense` endpoints or change the context variable names the template uses
- Don't change the profile markup or `profile.css` beyond removing the override. This step is about data, not design
- Amounts are always shown through the `inr` filter. User-supplied text relies on Jinja autoescaping, never `| safe`
- Keep the boxed `# ---- #` section-header comment style in Python

## Definition of done

- [ ] `grep -n "{% set" templates/profile.html` returns nothing
- [ ] After deleting `expense_tracker.db` and running `python app.py`, the app starts without errors and recreates the database
- [ ] Signed in as `demo@spendly.com` / `demo123`, the stat cards show Total spent `₹6,399.00`, Expenses `8` and Top category `Shopping`
- [ ] Spending by category lists 7 rows in this order, with matching bar widths: Shopping ₹2,299.00 35.9%, Bills ₹1,800.00 28.1%, Food ₹730.00 11.4%, Health ₹650.00 10.2%, Entertainment ₹500.00 7.8%, Other ₹300.00 4.7%, Transport ₹120.00 1.9%
- [ ] Recent expenses shows exactly 5 items, newest first: Dinner out (today's date), Gift wrapping, New shoes, Movie tickets, Pharmacy. No date is later than today
- [ ] A newly registered account sees ₹0.00, `0` and "—" in the stat cards and the "No expenses yet" empty state, not the old ₹14,400 sample data
- [ ] Inserting an expense for the demo user with `sqlite3 expense_tracker.db` and reloading `/profile` changes Total spent, the category breakdown and Recent expenses to match
- [ ] Signed out, `/profile` still redirects to `/login`
- [ ] Signed out, `/api/expenses`, `/api/summary` and `/api/categories` each return 401 with `{"error": "Sign in required."}`
- [ ] Signed in as the demo user, `/api/summary` returns `{"total": 6399.0, "count": 8, "top_category": "Shopping"}`
- [ ] `/api/categories` returns 7 rows whose `total` and `pct` values match the profile page
- [ ] `/api/expenses` returns all 8 expenses newest first with `"total": 8`. `?limit=3&offset=3` returns items 4–6. `limit=0`, `limit=500`, `limit=abc` and `offset=-1` each return 400
- [ ] A newly registered user gets `count: 0`, `top_category: null`, `categories: []` and `expenses: []`, never the demo user's data
- [ ] `/`, `/login`, `/register`, `/terms` and `/privacy` still render as before
