# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is **Spendly**, an expense tracker web app built as a step-by-step teaching project. `app.py` and `database/db.py` contain placeholder routes and stub functions labeled with "students will implement" / "coming in Step N". When editing, preserve that pedagogical structure — don't fill in stubs unless explicitly asked. The numbered Steps referenced in comments (Step 1 = DB setup, Step 3 = logout, Step 4 = profile, Step 7-9 = expense CRUD) define the intended implementation order.

## Commands

The project uses a local `venv/` (gitignored but present on disk). Always invoke the venv interpreter directly rather than relying on `python` on PATH (system `python` is not installed; `python3` exists but lacks Flask).

```bash
# Run the dev server (debug mode, port 5001)
venv/bin/python app.py

# Install/update dependencies
venv/bin/pip install -r requirements.txt

# Run tests
venv/bin/pytest
venv/bin/pytest path/to/test_file.py::test_name   # single test
```

Note: the app currently hardcodes `port=5001` (not the Flask default 5000) and runs with `debug=True`.

## Folder structure

```
expense-tracker/
├── app.py                  # Flask app entry point — all routes live here
├── requirements.txt        # Python dependencies
├── expense_tracker.db      # SQLite database (gitignored, created at runtime)
├── database/
│   ├── __init__.py
│   └── db.py               # get_db(), init_db(), seed_db() (stubs)
├── templates/              # Jinja2 templates, all extend base.html
│   ├── base.html           # Layout with navbar, footer, block slots
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── privacy.html
│   └── terms.html
├── static/
│   ├── css/style.css       # Single global stylesheet
│   └── js/main.js          # Single global script
└── venv/                   # Local virtualenv (gitignored)
```

## Architecture

- **`app.py`** — single-file Flask app. All routes live here; there are no blueprints yet. Static template routes (`/`, `/register`, `/login`, `/terms`, `/privacy`) are real; auth and expense routes are placeholder strings returning "coming in Step N".
- **`database/db.py`** — intended home for `get_db()`, `init_db()`, `seed_db()` against SQLite. The DB file is `expense_tracker.db` at repo root (gitignored). `row_factory` and foreign keys must be enabled in `get_db()` per the stub comments.
- **`templates/`** — Jinja2 templates extend `base.html`, which wires up the navbar, footer, `static/css/style.css`, and `static/js/main.js`. Brand name is "Spendly"; use `url_for(...)` for all internal links and static assets.
- **`static/`** — single `css/style.css` and `js/main.js`; no build step, no framework.

## Conventions seen in the codebase

- Routes are grouped by section headers using `# ---- #` comment banners — keep that style when adding routes to `app.py`.
- Templates use the `{% block title %}`, `{% block head %}`, `{% block content %}`, `{% block scripts %}` slots defined in `base.html`.
