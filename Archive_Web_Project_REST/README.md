# BAUET Project & Thesis Archive (REST API + JavaScript frontend)

The same archive idea as the Django template version, split into two parts:

- **Backend**: a Django REST Framework API with token authentication.
- **Frontend**: a static HTML, Tailwind CSS and vanilla JavaScript client that talks to the API. It needs no build step.

## Features

- Registration with email activation
- Token-based login and logout
- Browse approved projects, filter by department, and search by title, abstract, student or supervisor
- Paginated results
- Project detail page with authors, supervisors and a document download
- Submit, edit and delete your own projects:
  - Co-authors and supervisors are added by email
  - New submissions wait for admin approval
- Profile page listing your submissions, including pending ones, with an inline profile editor
- Object-level permissions: only a post's authors, its supervisors or staff can change it

## Tech stack

| Part     | Tools                                                               |
| -------- | ------------------------------------------------------------------- |
| Backend  | Python 3.10+, Django 5.1, Django REST Framework, django-cors-headers |
| Frontend | HTML, Tailwind CSS (browser CDN), ES modules, `fetch`               |
| Database | SQLite by default, PostgreSQL through `DATABASE_URL`                |

## Getting started

### 1. Backend

```bash
cd Backend/archive_rest

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver         # http://127.0.0.1:8000
```

Open `/admin/` and add a few **Departments**. Approve posts there as they come in.

### 2. Frontend

Serve the `Frontend` folder with any static file server on port **5500**. The pages use ES modules, so opening them as `file://` will not work.

```bash
cd Frontend
python -m http.server 5500         # http://127.0.0.1:5500
```

The VS Code *Live Server* extension also works, since it uses port 5500 by default.

The API address is set in `Frontend/js/config.js`:

```js
export const API_BASE = "http://127.0.0.1:8000/api";
```

If you serve the frontend from a different origin, add it to `CORS_ALLOWED_ORIGINS` and set `FRONTEND_URL` in the backend `.env`.

> With the default console email backend, activation emails are printed in the terminal running `runserver`. Copy the link from there to activate a new account.

## Environment variables (`Backend/archive_rest/.env`)

| Variable               | Default                                       | Description                                   |
| ---------------------- | --------------------------------------------- | --------------------------------------------- |
| `SECRET_KEY`           | insecure dev key                              | Django secret key. **Set this in production.** |
| `DEBUG`                | `False`                                       | Debug mode and media serving                  |
| `ALLOWED_HOSTS`        | `127.0.0.1,localhost`                         | Comma-separated host names                    |
| `DATABASE_URL`         | SQLite `db.sqlite3`                           | e.g. `postgres://user:pass@localhost:5432/archive` |
| `CORS_ALLOWED_ORIGINS` | `http://127.0.0.1:5500,http://localhost:5500` | Origins allowed to call the API               |
| `FRONTEND_URL`         | `http://127.0.0.1:5500`                       | Where the activation link redirects after it succeeds |
| `EMAIL_BACKEND`        | console backend                               | Use the SMTP backend to send real mail        |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Gmail SMTP defaults | SMTP settings |

## API reference

Base URL: `http://127.0.0.1:8000/api`

Authenticated requests send the header `Authorization: Token <token>`.

### Accounts

| Method | Endpoint                               | Auth | Description |
| ------ | -------------------------------------- | ---- | ----------- |
| POST   | `/accounts/register/`                  | –    | Create an inactive account and send the activation email. Multipart or JSON. Fields: `username`, `first_name`, `last_name`, `email`, `password`, `confirm_password`, `designation`, optional `dept`, `contact_number`, `address`, `image` |
| GET    | `/accounts/activate/<uid>/<token>/`    | –    | Activation link from the email. Redirects to `FRONTEND_URL/login.html?activated=1` |
| POST   | `/accounts/login/`                     | –    | `{ "username", "password" }` → `{ "token", "user" }` |
| POST   | `/accounts/logout/`                    | ✔    | Revokes the token |
| GET / PATCH | `/accounts/me/`                   | ✔    | Read or update the current user's profile. PATCH accepts multipart for `image` |
| GET    | `/accounts/profiles/`                  | –    | Read-only list of profiles |

### Departments

| Method | Endpoint             | Description |
| ------ | -------------------- | ----------- |
| GET    | `/departments/`      | All departments, each with a `post_count` of approved posts |
| GET    | `/departments/<id>/` | One department |

### Posts

| Method | Endpoint        | Auth           | Description |
| ------ | --------------- | -------------- | ----------- |
| GET    | `/posts/`       | –              | Approved posts, paginated. Query params: `department=<slug>`, `search=<text>`, `year=<yyyy>`, `page`, `page_size` (max 100), `mine=1` (your own posts including pending; needs auth) |
| POST   | `/posts/`       | ✔              | Multipart: `title`, `content`, `year`, `department` (id), `file`, optional `author_emails`, `supervisor_emails` (comma separated) |
| GET    | `/posts/<id>/`  | –              | Post detail. Pending posts are visible only to their authors, supervisors and staff |
| PATCH  | `/posts/<id>/`  | author / supervisor | Update any field. `file` is optional |
| DELETE | `/posts/<id>/`  | author / supervisor | Delete the post |

Paginated responses look like this:

```json
{ "count": 12, "total_pages": 2, "next": "...", "previous": null, "results": [ ... ] }
```

DRF's browsable API is available at the same URLs. Use `/api-auth/login/` to log in with a session there.

## Running tests

```bash
cd Backend/archive_rest
python manage.py test
```

## Project structure

```
Archive_Web_Project_REST/
├── Backend/archive_rest/
│   ├── archive_rest/        # settings, URLs, pagination
│   ├── accounts/            # registration, activation, token login, profile
│   ├── departments/         # read-only department endpoints
│   ├── posts/               # post CRUD, permissions, filtering
│   ├── requirements.txt
│   └── .env.example
└── Frontend/
    ├── index.html           # browse and search
    ├── post.html            # project details
    ├── submit.html          # create and edit a submission
    ├── profile.html         # profile and my submissions
    ├── login.html / register.html
    ├── css/app.css          # shared component styles
    ├── js/config.js         # API base URL
    ├── js/api.js            # fetch wrapper and token storage
    ├── js/ui.js             # layout, cards, toasts, form helpers
    └── js/pages/*.js        # one script per page
```
