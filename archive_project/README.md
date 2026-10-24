# BAUET Project & Thesis Archive (Django)

A server-rendered web app where students and faculty of **Bangladesh Army University of Engineering & Technology (BAUET)** can publish, browse and download final-year projects and theses.

Built with Django templates and Tailwind CSS.

## Features

- **Accounts**
  - Registration with email activation
  - Two-step login: password, then a 6-digit code sent by email
  - Password reset and password change
  - Profile with photo, designation and department
- **Submissions**
  - Students upload a project or thesis with an abstract, year, department, tags and a document
  - Co-authors and supervisors are added by email
  - New submissions stay hidden until an admin approves them
- **Browsing**
  - Filter by department or tag
  - Search by title, student, supervisor, year, or all fields at once
  - Paginated results
- **Project pages**
  - Abstract, people involved and a file download
  - Comments
  - "Save to reading list" bookmarks
- **Permissions**
  - Only a post's authors, its supervisors or staff can edit or delete it
  - Pending posts are visible only to those same people
- **Admin**
  - Approve posts one at a time or in bulk
  - Manage departments, tags and profiles

## Tech stack

| Layer    | Tools                                                          |
| -------- | -------------------------------------------------------------- |
| Backend  | Python 3.10+, Django 4.2/5.1, django-taggit, django-environ     |
| Frontend | Django templates, Tailwind CSS 3 (via `django-tailwind`)       |
| Database | SQLite by default, PostgreSQL through `DATABASE_URL`           |
| Email    | Console backend in development, any SMTP server in production  |

## Getting started

```bash
cd archive_project

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit values as needed
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000.

### First-time setup in the admin

1. Log in at `/admin/` with the superuser account.
2. Add the **Departments**. Make sure each one has a slug; the admin fills it in from the name.
3. Approve submitted posts from **Posts**: tick `Is approved`, or use the bulk *Approve selected posts* action.

> The superuser also logs in through the normal two-step login. With the default console email backend, the 6-digit code is printed in the terminal running `runserver`.

## Environment variables

All settings are read from `archive_project/.env` (see `.env.example`).

| Variable              | Default                     | Description                                  |
| --------------------- | --------------------------- | -------------------------------------------- |
| `SECRET_KEY`          | insecure dev key            | Django secret key. **Set this in production.** |
| `DEBUG`               | `False`                     | Turn on debug mode, auto-reload and media serving |
| `ALLOWED_HOSTS`       | `127.0.0.1,localhost`       | Comma-separated host names                   |
| `DATABASE_URL`        | SQLite `db.sqlite3`         | e.g. `postgres://user:pass@localhost:5432/bauet_archive` |
| `EMAIL_BACKEND`       | console backend             | Use `django.core.mail.backends.smtp.EmailBackend` to send real mail |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_USE_TLS` | `smtp.gmail.com` / `587` / `True` | SMTP server |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | empty  | SMTP credentials. For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) |
| `DEFAULT_FROM_EMAIL`  | `EMAIL_HOST_USER`           | Sender address for outgoing mail             |

## Styling (Tailwind CSS)

The compiled stylesheet is committed at `theme/static/css/dist/styles.css`, so you don't need Node.js just to run the app.

If you change templates or `theme/static_src/src/styles.css`, rebuild the CSS. This needs Node.js 18+:

```bash
python manage.py tailwind install   # once
python manage.py tailwind start     # watch mode during development
python manage.py tailwind build     # minified production build
```

The shared component classes live in `theme/static_src/src/styles.css`: `btn-primary`, `card`, `input`, `tag` and the rest. Forms pick them up automatically through `core.forms.StyledFormMixin`.

## Running tests

```bash
python manage.py test
```

The tests cover the full registration → activation → OTP login flow, post permissions, search, downloads, comments and the reading list.

## Project structure

```
archive_project/
├── archive_project/      # settings and root URLs
├── accounts/             # registration, OTP login, profiles, password flows
├── posts/                # Post, CustomTag, Comment, Wishlist models and views
├── departments/          # Department model
├── core/                 # home, search, downloads, base templates and partials
├── theme/                # django-tailwind app (source in static_src/, build in static/)
├── media/                # user uploads (git-ignored)
├── requirements.txt
└── .env.example
```

## Main URLs

| URL                          | Page                                |
| ---------------------------- | ----------------------------------- |
| `/`                          | Browse approved projects            |
| `/dept/<slug>/`              | Projects of one department          |
| `/tag/<slug>/`               | Projects with a tag                 |
| `/search/?q=&category=`      | Search (`all`, `title`, `student`, `supervisor`, `year`) |
| `/posts/add/`                | Submit a project                    |
| `/posts/details/<id>/`       | Project details                     |
| `/accounts/register/`        | Create an account                   |
| `/accounts/login/`           | Log in (step 1)                     |
| `/accounts/otp_verify/`      | Log in (step 2)                     |
| `/accounts/profile/`         | Your profile, submissions and reading list |
| `/admin/`                    | Django admin                        |

## Deployment notes

- Set `DEBUG=False`, a strong `SECRET_KEY`, and real `ALLOWED_HOSTS`.
- Use PostgreSQL through `DATABASE_URL`.
- Run `python manage.py tailwind build`, then `python manage.py collectstatic`.
- Serve `staticfiles/` and `media/` from your web server (Nginx or similar). With `DEBUG=False`, Django does not serve uploaded files.
