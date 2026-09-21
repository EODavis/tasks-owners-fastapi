# Tasks-With-Owners API (FastAPI)

A RESTful API where every task belongs to a specific user, built with
Python, FastAPI, SQLAlchemy, and Pydantic. Project 11 in a sequential
backend engineering learning journey — the FastAPI equivalent of the
Node.js Tasks-With-Owners project, combining authentication with
resource relationships and ownership-based authorization.

## Features

- User registration/login (passlib + JWT via python-jose, reused from
  the FastAPI Auth API)
- SQLAlchemy `ForeignKey` + `relationship()` linking tasks to owners
- Nested owner data in task responses via Pydantic schema composition
- Every task route requires `Depends(get_current_user)`
- `403 Forbidden` (not your resource) distinguished from `401
  Unauthorized` (no valid token) and `404 Not Found` (doesn't exist)
- Cascading delete: removing a user removes their tasks (`delete-orphan`)

## Tech Stack

- Python, FastAPI, SQLAlchemy, SQLite
- passlib[bcrypt], python-jose[cryptography]

## Getting Started

```bash
python -m venv venv
source venv/Scripts/activate    # Windows Git Bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server runs on `http://127.0.0.1:8000`. Interactive docs at
`http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Endpoint               | Auth required | Description                       |
|--------|------------------------|---------------|-----------------------------------|
| POST   | /api/auth/register     | No            | Create a new user                 |
| POST   | /api/auth/login        | No            | Log in, receive a JWT             |
| GET    | /api/tasks/            | Yes           | Get the logged-in user's tasks    |
| GET    | /api/tasks/{id}        | Yes           | Get one task (must be owner)      |
| POST   | /api/tasks/            | Yes           | Create a task (owned by caller)   |
| PUT    | /api/tasks/{id}        | Yes           | Update a task (must be owner)     |
| DELETE | /api/tasks/{id}        | Yes           | Delete a task (must be owner)     |

### Accessing task routes

Authorization: Bearer <access_token-from-login>

## Project Structure

app/
├── main.py - App entry point, table creation, router mounting
├── database.py - SQLAlchemy engine, session factory
├── models.py - User + Task ORM models, foreign key + relationship
├── schemas.py - Pydantic schemas, including nested TaskResponse.owner
├── crud.py - Ownership-scoped database queries
├── auth.py - Password hashing, JWT, get_current_user dependency
└── routes.py - Auth routes + task routes with per-route Depends()

## Authorization Model

- **401** — no valid token (authentication failure)
- **403** — valid token, task belongs to someone else (authorization failure)
- **404** — task doesn't exist

## Notes

Mirrors the Node.js Tasks-With-Owners API, but built with SQLAlchemy's
`relationship()` for object-level navigation between users and tasks
(e.g. `task.owner`), and FastAPI's per-route `Depends(get_current_user)`
pattern instead of an Express middleware chain.
