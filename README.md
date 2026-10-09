# StudySnap

A small Django learning application. Supports self-registration, private subjects, and notes within each subject. Notes require a title (up to 200 characters) and body. Subject names are required, limited to 100 characters, and may repeat. Subjects are sorted by name using SQLite's default ordering.

## Local setup

Use Python 3.12 or newer. From the project directory in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you do not already have one. Generate a local secret key:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
```

Paste the generated value after `DJANGO_SECRET_KEY=` in `.env`. Keep `DJANGO_DEBUG=1` for local development. Then run:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Register at `/accounts/register/`, then log in at `/accounts/login/`. Open `/subjects/` on the local development server to list subjects and `/subjects/new/` to create one. The home page at `/` introduces StudySnap and links to both subject pages.

The project automatically loads `.env` from its root directory. Existing environment variables take priority. `DJANGO_SECRET_KEY` is still required, and debug mode is off by default. Never commit secret values; `.env`, SQLite databases, and the virtual environment are ignored by Git.

## Checks

With `.env` configured:

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Run `migrate` on existing installations to add accounts and notes. Existing subjects retain no owner and are hidden from all users. New subjects are assigned to the logged-in user. Click a subject to list, view, or create its notes. Other users cannot access your subjects or notes. Log out using the navigation button.

This is a local learning app and is not configured for public deployment. Editing/deleting notes, understood status, quizzes, and progress are future work.
