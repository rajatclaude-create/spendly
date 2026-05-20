---
description: Run the Spendly Flask dev server on port 5001
allowed-tools: Bash
---

Start the Spendly Flask development server in the background using the project's local venv interpreter. The server runs on port 5001 in debug mode.

Steps:
1. Check if anything is already listening on port 5001. If so, report it to the user and stop — do not kill it.
2. Otherwise, run `venv/bin/python app.py` in the background from the repo root.
3. Wait briefly, then confirm the server is responding (e.g. `curl -sI http://127.0.0.1:5001/`) and report the URL to the user.
