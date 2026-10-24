# BAUET Project & Thesis Archive

A digital archive of final-year projects and theses for **Bangladesh Army University of Engineering & Technology (BAUET)**. Students upload their work, supervisors are linked to it, admins approve it, and everyone can browse, search and download approved submissions by department.

This repository contains two implementations of the same idea:

| Project | Description | Docs |
| ------- | ----------- | ---- |
| [`archive_project`](archive_project) | Full-stack Django app with server-rendered Tailwind templates, email activation, OTP login, tags, comments and a reading list | [README](archive_project/README.md) |
| [`Archive_Web_Project_REST`](Archive_Web_Project_REST) | Django REST Framework API with token auth, plus a static HTML/JS frontend that consumes it | [README](Archive_Web_Project_REST/README.md) |

## Quick start

Each project is self-contained and has its own `requirements.txt` and `.env.example`.

```bash
# Django template version
cd archive_project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py createsuperuser
python manage.py runserver
```

```bash
# REST version (two terminals)
cd Archive_Web_Project_REST/Backend/archive_rest
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py createsuperuser
python manage.py runserver

cd Archive_Web_Project_REST/Frontend
python -m http.server 5500
```

See each project's README for features, configuration, the API reference and deployment notes.

## Team

Built by **Team Extreme**, BAUET.
