# Validation results

Validated on Windows with Python 3.8.10 and headless Microsoft Edge.

- **18 pytest cases passed** against temporary SQLite databases. Includes password hashing, registration/login, duplicate accounts, CRUD, invalid fields and URLs, CSRF rejection, HTML escaping, cross-account read/edit/delete rejection, dashboard counts, search/filter, date boundaries, empty states, and repeatable demo seeding.
- **Browser walkthrough passed:** demo login, search plus status filter, reset, add/detail/edit, deletion cancellation and confirmation, logout, registration, empty dashboard, and cross-account URL rejection. No JavaScript page errors were observed.
- **Responsive checks passed:** dashboard and application form fit a 390 × 844 viewport without document horizontal overflow. Desktop capture used 1440 × 1000. Screenshots were reviewed at both sizes.
- **Local startup verified:** dependency installation, database initialization, demo seed, and Flask server start. Bootstrap CSS is served locally.

Screenshots are in `screenshots/`; the silent browser walkthrough is in `recordings/jobtrack-walkthrough.webm`. This validates a local internship demo; public deployment is outside the project's scope.
