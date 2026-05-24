# Spec: Registration

## Overview
Enable new users to create a Spendly account by submitting the existing
registration form. This step turns the static `/register` page into a
working POST handler that validates input, hashes the password with
werkzeug, and persists a new row into the `users` table created in
Step 1. It is the first feature that actually writes user data and is a
prerequisite for login, profile, and all expense flows.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()` helper, werkzeug
  installed)

## Routes
- `GET /register` — render the registration form (already exists; keep
  behavior, just add error/form-value handling) — public
- `POST /register` — validate input, create the user, redirect to
  `/login` on success or re-render with an error on failure — public

(The existing `register()` view in `app.py` will be updated to accept
both methods rather than adding a new route.)

## Database changes
No database changes. The `users` table from Step 1 already has every
column needed: `id`, `name`, `email`, `password_hash`, `created_at`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html`
  - Surface server-side validation errors (the `{% if error %}` block
    is already present — keep using it)
  - Repopulate `name` and `email` inputs from a passed-in `form` dict
    so users don't retype on validation failure
  - Leave the password field empty on re-render

## Files to change
- `app.py` — replace the GET-only `register()` view with one that
  handles both `GET` and `POST`, performs validation, hashes the
  password, inserts the user via `get_db()`, and redirects to `/login`
  with a success flash on success
- `templates/register.html` — wire `error` and `form` context into the
  template

## Files to create
- None

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` and
`sqlite3` are already in use.

## Rules for implementation
- No SQLAlchemy or ORMs — use `get_db()` from `database/db.py`
- Parameterised queries only — never f-string or `%` into SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
  using `method="pbkdf2:sha256"` to match the convention in
  `database/db.py::seed_db`
- Use CSS variables for any new styles — never hardcode hex values
- All templates extend `base.html`
- Preserve the `# ---- #` route banner style in `app.py`; the new
  POST handling lives inside the existing `register()` view, not a
  new route
- Email comparison must be case-insensitive on lookup (store the
  email as the user typed it, but check uniqueness against the
  lower-cased value) — keep storage consistent by lower-casing on
  insert
- Validation rules (server-side, all required):
  - `name` — trimmed, 1–80 characters
  - `email` — trimmed, lower-cased, must contain `@` and a `.` in the
    domain part, max 120 characters
  - `password` — minimum 8 characters
- On duplicate email, catch `sqlite3.IntegrityError` and re-render the
  form with an "Email already registered" error rather than 500-ing
- On success, redirect (HTTP 302) to `/login` — do not auto-login
  (login lands in a later step)
- Do not log or print the raw password anywhere

## Definition of done
- [ ] `GET /register` renders the form exactly as it does today
- [ ] Submitting the form with valid input creates a row in `users`
      whose `password_hash` starts with `pbkdf2:sha256:` and is not
      the plaintext password
- [ ] After a successful submit, the browser is redirected to
      `/login`
- [ ] Submitting with an email that already exists re-renders
      `/register` with an "Email already registered" error and a
      non-500 status
- [ ] Submitting with a password shorter than 8 characters re-renders
      with a clear error and does not insert a row
- [ ] Submitting with a missing/blank field re-renders with an error
      and does not insert a row
- [ ] On any validation failure, the previously entered `name` and
      `email` are repopulated in the form; the password field is
      empty
- [ ] `sqlite3` queries used in the handler are parameterised (no
      string interpolation)
- [ ] App still starts cleanly with `venv/bin/python app.py` on port
      5001
