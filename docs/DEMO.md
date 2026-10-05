# Three-minute demo script

Before recording, run `init-db`, `seed-demo`, and the Flask server. Open the login page. Use fictional data only.

| Time | Show and explain |
| --- | --- |
| 0:00–0:25 | Introduce JobTrack: a Python/Flask app that keeps job applications and deadlines together. Log in with the demo account. |
| 0:25–0:55 | Explain the status counts and upcoming deadlines. Search for Orbit, filter Interviewing, then reset. |
| 0:55–1:30 | Add a fictional application with company, title, date, deadline, posting link, and notes. Show the saved details. |
| 1:30–1:55 | Edit the status to Interviewing and add an interview note. Return to the dashboard to show updated counts. |
| 1:55–2:15 | Open deletion confirmation, choose Keep application, then confirm deletion on a second visit. |
| 2:15–2:35 | Log out and register a new account. Show that it starts with an empty dashboard and has no access to the demo user's records. |
| 2:35–3:00 | Explain Flask blueprints, SQLite models, password hashing, CSRF, ownership checks, and pytest. Mention future additions such as reminders. |

## Manual acceptance checklist

- Navigation links, form labels, keyboard focus, login/logout, and cancel actions work.
- Blank/invalid input displays feedback and does not save records.
- Canceling deletion preserves the application; confirming removes it.
- Search/filter reset works, with a helpful empty state when nothing matches.
- Dashboard and form fit a mobile viewport; long company/title/notes remain usable.
- Browser back/refresh after logout cannot retrieve protected pages from the server.
- Follow the README from a fresh environment and verify demo credentials.

A short silent browser recording is included at `recordings/jobtrack-walkthrough.webm`. It shows login, search/filter, creation, editing, deletion cancel/confirm, registration, an empty account, and a rejected cross-account URL. Use the script above for a three-minute narrated presentation.
