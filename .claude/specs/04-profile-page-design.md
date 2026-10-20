# Spec: Profile Page Design

## Overview

Build the page that signed-in users land on at `/profile`. It is their account overview: who they are, how much they have spent and where the money went. Step 3 already redirects to `/profile` after login, and the navbar links the user's name there. The route and data helpers already exist in `app.py` and `database/db.py`, but `templates/profile.html` and `static/css/profile.css` have been removed. Right now `/profile` errors out with `TemplateNotFound`. This step designs and builds that page from scratch: a user header, summary stat cards, a category breakdown and a recent-expenses list, all in Spendly's existing visual language. It is also where the "Add expense" entry point (Step 7) first appears.

## Depends on

- Step 1, Database Setup: the `users` and `expenses` tables, and the seeded demo user (`demo@spendly.com` / `demo123`) with 8 expenses
- Step 2, Registration: new accounts, which have no expenses, so they exercise the empty state
- Step 3, Login and Logout: `session["user_id"]`, the `login_required` decorator and the signed-in navbar

## Routes

No new routes. The existing route is used as it is:

- `GET /profile`: renders `profile.html` for the signed-in user. Signed-out users are redirected to `/login`. If the session points to a user that no longer exists, the session is cleared and the user is redirected to `/login`. Access: logged-in

## Database changes

No database changes. Verified against `database/db.py`, which already provides:

- `get_user_by_id(user_id)`: `id`, `name`, `email`, `created_at`
- `get_expense_summary(user_id)`: `{"total", "count", "top_category"}`. `top_category` is `None` when the user has no expenses
- `get_category_breakdown(user_id)`: one row per category with `category`, `total` and `count`, sorted by total, descending
- `get_recent_expenses(user_id, limit=5)`: `id`, `amount`, `category`, `date`, `description`

## Templates

- **Create:**
  - `templates/profile.html`: extends `base.html`, sets the title to "Profile · Spendly" and loads `css/profile.css` in the `head` block. Uses the context variables the route already passes in (`user`, `member_since`, `summary`, `breakdown`, `recent`). Sections:
    1. **Profile header**: a circular avatar showing the user's initial, the name in `--font-display`, the email and "Member since {{ member_since }}". An "Add expense" button links to `url_for('add_expense')`
    2. **Stat cards** (3 in a row, stacked on mobile): Total spent (`summary.total | inr`), Expenses (`summary.count`) and Top category (`summary.top_category`, or "—")
    3. **Spending by category**: one row per item in `breakdown`, showing the category name, `total | inr`, `pct`% and a horizontal bar whose width is `pct`% (inline `style="width: {{ pct }}%"`, colored with tokens)
    4. **Recent expenses**: a list of `recent` showing the description (or the category if there is none), a category pill, `date_display` and the amount, right-aligned with `| inr`
    5. **Empty state**: if `summary.count == 0`, hide sections 3 and 4 and show a friendly card ("No expenses yet") with an "Add your first expense" button that links to `url_for('add_expense')`
- **Modify:** none

## Files to change

- None. The `profile` route in `app.py`, the `inr` template filter and the `.nav-user` navbar link already exist. Only the endpoint names (`profile`, `add_expense`) are relied on, and they must stay the same

## Files to create

- `templates/profile.html`: the page described above
- `static/css/profile.css`: page-only styles (header, avatar, stat-card grid, category bars, recent list, category pills, empty state, mobile layout below about 720px). Uses the boxed `/* ---- */` section-header comments

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only. Don't add SQL to `app.py`. Any new query belongs in `database/db.py`
- Passwords hashed with werkzeug (not touched in this step, and never shown on the page)
- Use CSS variables, never hardcode hex values. Use the `--ink*`, `--paper*`, `--accent*`, `--border*`, `--radius-*` and `--font-*` tokens from `style.css`. If you need a new color, add a token to `:root` in `style.css` first
- All templates extend `base.html`
- Page-specific CSS goes in `profile.css` and is loaded through the `head` block. Don't add profile styles to `style.css`
- Link with `url_for(...)` only, with no hard-coded paths
- Amounts are always shown in ₹ through the `inr` filter
- Rely on Jinja autoescaping for user-supplied text (name, description). Never use `| safe`
- No JavaScript is required. If any is added, it goes in a page-specific IIFE loaded through the `scripts` block, following the `landing.js` pattern

## Definition of done

- [ ] `python app.py` starts without errors, and `http://localhost:5001/profile` while signed out redirects to `/login`
- [ ] After signing in as `demo@spendly.com` / `demo123`, you land on `/profile` and the page renders with no `TemplateNotFound` error
- [ ] The header shows the "D" avatar, "Demo User", `demo@spendly.com` and "Member since <Mon YYYY>"
- [ ] The stat cards show Total spent as `₹6,399.00`, Expenses as `8` and Top category as `Shopping`
- [ ] Spending by category lists 7 categories, highest first (Shopping at the top), and each bar's width matches its percentage
- [ ] Recent expenses shows exactly 5 items, newest first, each with a ₹ amount and a date like `22 Oct 2026`
- [ ] The "Add expense" button goes to `/expenses/add` (the Step 7 placeholder)
- [ ] A newly registered account sees the empty state instead of the breakdown and recent lists, with ₹0.00 and 0 in the stat cards and "—" for the top category
- [ ] The tab title reads "Profile · Spendly", and the navbar shows the user's name and "Sign out"
- [ ] At a phone width of about 375px, the stat cards stack, nothing scrolls horizontally, and the text stays readable
- [ ] `grep -E '#[0-9a-fA-F]{3,6}' static/css/profile.css` returns nothing (no hard-coded colors)
- [ ] `/`, `/login`, `/register`, `/terms` and `/privacy` still render as before
