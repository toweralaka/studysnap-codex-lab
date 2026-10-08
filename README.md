# StudySnap

A small Django learning application. Currently supports a shared subject list and subject creation. Subject names are required, limited to 100 characters, and may repeat. Subjects are sorted by name using SQLite's default ordering.

## Local setup

Use Python 3.12 or newer and the existing checkout:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py runserver
```

Open `/subjects/` on the local development server to list subjects and `/subjects/new/` to create one. The home page at `/` introduces StudySnap and links to both subject pages.

Generate a secret key for each development shell as shown above, or securely supply a stable key through your environment. Never commit secret values. Debug mode is off by default. SQLite databases and the virtual environment are ignored by Git.

## Checks

With the virtual environment activated and `DJANGO_SECRET_KEY` set:

```sh
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

This is a local learning app, with no accounts or subject ownership. It is not configured for public deployment. Notes, quizzes, and progress are future work.
