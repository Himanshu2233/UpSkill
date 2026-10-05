# JobTrack

A Flask job application tracker built as a Python development internship final project. Create an account, manage applications, search and filter opportunities, and see active deadlines in one dashboard.

## Run locally (Windows PowerShell)

Python 3.8 or later is required. The dependency versions in `requirements.txt` are compatible with the workspace's Python 3.8. Use a newer supported Python for future development.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app jobtrack init-db
.\.venv\Scripts\python.exe -m flask --app jobtrack seed-demo
.\.venv\Scripts\python.exe -m flask --app jobtrack run
```

Open **http://127.0.0.1:5000**. Demo login: **demo@jobtrack.example** / **DemoPass123!**. These credentials are for fictional local demonstration data only. Register a separate account to try an empty dashboard.

On macOS/Linux, use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.

## Features

- Registration, password hashing, login, and POST-only logout.
- Add, view, edit, and delete applications; deletion requires a confirmation page.
- Company, title, application date, optional HTTP/HTTPS posting link, deadline, status, and notes.
- Applied, Interviewing, Offered, and Rejected statuses.
- Search company/title, filter status, and see account-wide dashboard counts.
- Upcoming deadlines include today through seven days ahead, excluding Offered and Rejected applications. Dates use the machine's local calendar date.
- Ownership checks on every application route, form validation, CSRF protection, and escaped user content.
- Responsive layout with accessible labels and keyboard focus styles.

## Configuration and database

Copy `.env.example` to `.env` if you want to customize `SECRET_KEY` or `DATABASE_URL`. Flask's CLI loads `.env` automatically. If no key is configured, the application generates a persistent local key at `instance/secret.key`. Do not commit the `.env`, instance folder, or secrets.

The default database is `instance/jobtrack.sqlite`. `init-db` creates missing tables without clearing data. `seed-demo` creates six fictional applications with dates relative to today; subsequent runs preserve the existing demo account and its records. To obtain fresh demo dates, use a new database path in `DATABASE_URL` and rerun the commands. No schema migration is needed for this initial version; future schema changes should introduce migrations.

The interface uses Bootstrap 5.3.3. Its stylesheet is vendored locally so the demo works offline. There is no JavaScript dependency.

## Project structure

`jobtrack/__init__.py` creates and configures the app. `extensions.py` contains shared Flask integrations. `models.py` defines User and Application tables. `forms.py` handles form validation. The `auth` and `tracker` blueprints separate authentication from application workflows. `cli.py` contains database and demo commands. Templates and CSS render the interface; `tests/` exercises it with isolated temporary databases.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The suite covers authentication, duplicate emails, invalid forms, CRUD, deletion confirmation, search/filter behavior, dashboard counts, deadline boundaries, HTML escaping, cross-account access, CSRF, empty states, and repeatable demo seeding. Tests never use your demo database.

## Internship submission

Include the source, this README, the screenshots in `docs/screenshots/`, and [the recorded walkthrough](docs/recordings/jobtrack-walkthrough.webm). The included video is a short silent browser walkthrough; use [the three-minute demo script](docs/DEMO.md) to record a narrated presentation. Explain the application factory, blueprints, relationships, validation, and ownership checks during your presentation. Email reminders, AI, scraping, uploads, and hosting are outside this version.

## Optional browser verification

The app itself needs only Python. To rerun the artifact capture tool, install Node.js and Microsoft Edge, start the seeded Flask server, then run:

```powershell
npm.cmd install --no-save --package-lock=false playwright@1.56.1
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.browser-cache"
npx.cmd playwright install ffmpeg
node tools/browser_demo.cjs
```

This tool exercises desktop/mobile workflows, saves screenshots and video, and creates a fictional walkthrough account in the local database. It removes the application it adds. Use a separate demo database if you want to preserve your working database exactly.
