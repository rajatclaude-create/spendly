# Spec: Login and Logout

## Overview
Wire up real authentication for Spendly. Today `/login` only renders
its form (`app.py:80-82`) and `/logout` returns the placeholder
string `"Logout — coming in Step 3"` (`app.py:99-101`). This step
makes both work using Flask's signed-cookie `session`: a successful
POST to `/login` verifies the password against the hash stored by
Step 02, persists `user_id` and `user_name` in the session, and
redirects to the user's home (`/profile` for now, which still
renders its placeholder until Step 04). `/logout` clears the session
and returns to the landing page. The navbar also starts showing
context-aware links — Sign in/Get started when anonymous, the user's
name + Logout when authenticated — so the user can see their auth
state. Login/logout is the gate every subsequent step (profile,
expense CRUD) needs.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`)
- Step 02 — Registration (real user rows with `pbkdf2:sha256` hashes
  exist in the `users` table)

## Routes
- `GET /login` — render the form (already exists; keep behaviour,
  pass `error`/`form` context) — public
- `POST /login` — validate credentials, set session, redirect to
  `/profile` on success or re-render with an error on failure —
  public
- `GET /logout` — clear the session and redirect to `/` — accessible
  to anyone (no-op when already logged out)

(The existing `login()` and `logout()` views in `app.py` are
updated in place; no new routes are added.)

## Database changes
No database changes. The `users` table from Step 01 already has the
`id`, `email`, `password_hash`, and `name` columns this step reads.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — surface validation errors using the
    existing `{% if error %}` block (already present) and repopulate
    the `email` input from a passed-in `form` dict (password stays
    blank)
  - `templates/base.html` — make `.nav-links` conditional on
    `session.user_id`:
    - logged out: `Sign in` + `Get started` (today's links)
    - logged in: a muted "Hi, {{ session.user_name }}" label and a
      `Logout` link styled like the existing nav links (use
      `url_for('logout')`)

## Files to change
- `app.py`
  - Set `app.secret_key` from `os.environ.get("SPENDLY_SECRET_KEY")`
    with a development fallback string so the dev server keeps
    working without extra setup; document the env var in a one-line
    comment
  - Import `session` from `flask` and
    `check_password_hash` from `werkzeug.security`
  - Replace the GET-only `login()` view with a GET/POST handler:
    trim + lower-case email, look up the user via parameterised
    `SELECT`, verify with `check_password_hash`, on success set
    `session.clear()` then `session["user_id"]` / `session["user_name"]`,
    redirect to `url_for('profile')`; on failure re-render with a
    single generic error ("Invalid email or password.") so we don't
    leak which field was wrong, repopulating only the email input
  - Replace the placeholder `logout()` view with one that calls
    `session.clear()` and `redirect(url_for('landing'))`
- `templates/login.html` — see Templates section above
- `templates/base.html` — see Templates section above

## Files to create
- None

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` ships
with the version already pinned in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — use `get_db()` from `database/db.py`
- Parameterised queries only — `?` placeholders, never f-strings
  or `%` into SQL
- Passwords compared with `werkzeug.security.check_password_hash`
  against the stored hash; **never** rehash and compare strings
- Use CSS variables for any new styles — never hardcode hex values
  (likely no new CSS needed; reuse `.nav-links`, `.nav-cta`,
  `.auth-error`)
- All templates extend `base.html`
- Preserve the `# ---- #` route banner style in `app.py`; logout
  moves up out of the "students will implement" banner into the
  real routes section
- Always lower-case the email before lookup to match the storage
  convention from Step 02
- Run the password check **even when the user row is missing** (use
  a constant dummy hash) so failed-login timing doesn't reveal
  whether an email exists — keep it simple: a single dummy
  `check_password_hash` call gated on the missing-row branch is
  fine
- On success: `session.clear()` first, then assign `user_id` and
  `user_name` — clearing prevents stale keys from surviving a
  re-login on the same browser
- Do not log or print the submitted email/password
- `app.secret_key`: read from `SPENDLY_SECRET_KEY` env var; fall
  back to a hard-coded dev string so the dev server still starts
  without extra setup; the fallback must be obviously
  non-production (e.g. `"dev-only-change-me"`)

## Definition of done
- [ ] `GET /login` renders the form exactly as it does today, no
      session side effects
- [ ] Submitting valid credentials for a seeded user
      (`demo@spendly.com` / `demo123`) redirects (302) to `/profile`
- [ ] After successful login, `GET /` shows "Hi, Demo User" and a
      "Logout" link in the nav instead of Sign in / Get started
- [ ] Submitting a wrong password re-renders `/login` with
      "Invalid email or password." and HTTP 200 (not 500)
- [ ] Submitting an email that doesn't exist re-renders with the
      same generic error and takes a comparable amount of time to
      the wrong-password case (dummy hash branch hit)
- [ ] Submitting with a blank field re-renders with a clear error
      and does not touch the session
- [ ] On any failure, the previously typed `email` is repopulated;
      the password input is empty
- [ ] `GET /logout` clears the session and redirects (302) to `/`;
      the navbar reverts to Sign in / Get started
- [ ] `GET /logout` while not logged in still 302s to `/` without
      erroring
- [ ] All SQL in the login handler is parameterised (no string
      interpolation)
- [ ] App still starts cleanly with `venv/bin/python app.py` on
      port 5001, with or without `SPENDLY_SECRET_KEY` set
