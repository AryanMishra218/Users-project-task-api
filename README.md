# Users, Projects & Tasks API

A REST API built with Flask for managing users, projects, and tasks —
Task 2 of the Innovation Hacks Full Stack Development Internship.

This is the backend that Task 1's dashboard and Task 4's platform
will eventually connect to.

## Tech Stack

- Python 3 + Flask
- python-dotenv (environment variable configuration)
- Data storage: **in-memory** for now (Python dictionaries). This is
  intentional — Task 3 replaces `app/store.py` with a real database
  (PostgreSQL/MongoDB) without any route code needing to change.

## Project Structure

```
users-projects-tasks-api/
├── app/
│   ├── __init__.py       # App factory: creates the Flask app, registers routes + error handlers
│   ├── config.py         # Reads settings from environment variables
│   ├── errors.py         # Custom ApiError exception for consistent error responses
│   ├── store.py          # In-memory "database" (dictionaries) — swap this in Task 3
│   ├── validators.py     # Reusable input validation functions
│   └── routes/
│       ├── users.py
│       ├── projects.py
│       └── tasks.py
├── run.py                 # Entry point — run this to start the server
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & Running Locally

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd users-projects-tasks-api

# 2. Create a virtual environment (keeps dependencies isolated)
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env

# 5. Run the server
python run.py
```

The API will be running at `http://127.0.0.1:5000`.

## API Reference

All request/response bodies are JSON. All error responses follow this shape:
```json
{ "error": "Human-readable message", "details": { "...": "optional" } }
```

### Users

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/api/users` | Create a user | 201 | 400 missing/invalid fields, 409 duplicate email |
| GET | `/api/users` | List all users | 200 | — |
| GET | `/api/users/<id>` | Get one user | 200 | 404 not found |
| DELETE | `/api/users/<id>` | Delete a user | 204 | 404 not found |

**Create a user**
```bash
curl -X POST http://127.0.0.1:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Aryan Mishra","email":"aryan@example.com"}'
```

### Projects

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/api/projects` | Create a project | 201 | 400 missing name / invalid owner_id |
| GET | `/api/projects` | List all projects | 200 | — |
| GET | `/api/projects/<id>` | Get one project (includes task_count, tasks_done) | 200 | 404 not found |

**Create a project**
```bash
curl -X POST http://127.0.0.1:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"HealthConnect","description":"Healthcare appointment app","owner_id":1}'
```

### Tasks

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/api/tasks` | Create a task (always starts as `todo`) | 201 | 400 missing/invalid fields |
| GET | `/api/tasks` | List tasks. Supports `?status=` and `?project_id=` filters | 200 | — |
| GET | `/api/tasks/<id>` | Get one task | 200 | 404 not found |
| PUT | `/api/tasks/<id>` | Update title / priority / due_date / assignee_id | 200 | 400 invalid value, 404 not found |
| PATCH | `/api/tasks/<id>/status` | Update ONLY the status | 200 | 400 invalid status, 404 not found |
| DELETE | `/api/tasks/<id>` | Delete a task | 204 | 404 not found |

Valid `status` values: `todo`, `in-progress`, `done`
Valid `priority` values: `low`, `medium`, `high`

**Create a task**
```bash
curl -X POST http://127.0.0.1:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Design DB schema","project_id":1,"assignee_id":1,"priority":"high","due_date":"2026-10-05"}'
```

**Change a task's status**
```bash
curl -X PATCH http://127.0.0.1:5000/api/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"in-progress"}'
```

**Filter tasks**
```bash
curl "http://127.0.0.1:5000/api/tasks?status=in-progress"
curl "http://127.0.0.1:5000/api/tasks?project_id=1"
```

## Environment Variables

See `.env.example`. Copy it to `.env` (which is git-ignored) and adjust:

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Flask secret key | `dev-only-insecure-key` |
| `FLASK_DEBUG` | Enable debug/auto-reload | `true` |
| `PORT` | Port the server listens on | `5000` |

## Error Handling

All errors — whether raised intentionally (`ApiError`) or thrown by
Flask itself (404, 405, 500) — are caught centrally in `app/__init__.py`
and always returned as JSON, so the frontend never has to parse an
HTML error page.

## Notes for Task 3

`app/store.py` is the only file that needs to change to add a real
database. Every route only ever touches `store.users`, `store.projects`,
and `store.tasks` — so as long as the replacement behaves like a
dictionary (or we update those three lines), everything else keeps working.
