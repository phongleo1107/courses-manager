# Courses Manager

A small course-registration app for learning how a React frontend, a FastAPI API, and a database work together.

## Project Status

The frontend is the Vite starter. The backend currently provides a health endpoint, local settings, a SQLAlchemy session, and Alembic configuration. The course catalog, database models and migrations, authentication, and registration features are the next steps.

The intended MVP lets anyone browse classes and lets a signed-in user register for, view, and drop classes. See the [PRD](PRD.md) for the full requirements.

## Run Locally

Install [uv](https://docs.astral.sh/uv/) and Python 3.14. Install Node.js and npm for the frontend.

Start the backend from the repository root:

```bash
uv sync --directory backend
uv run --directory backend uvicorn backend.main:app --reload --port 8000
```

The backend uses local SQLite by default and does not need Supabase credentials for the health check. Open <http://localhost:8000/health>; it should return `{"status":"ok"}`.

In a second terminal, start the frontend:

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

The frontend is still the Vite demo; it does not call the backend yet.

Run backend checks with:

```bash
uv run --directory backend pytest
uv run --directory backend ruff check .
```

## Learning Path

Follow [docs/todos.md](docs/todos.md) one step at a time. The [architecture guide](architecture.md) explains how the pieces fit together. The [later topics](docs/later-topics.md) page keeps security, concurrency, and production hardening details for when they become useful.

## Supabase Setup

The app is intended to use Supabase Auth and PostgreSQL. The local environment templates are [backend/.env.example](backend/.env.example) and [frontend/.env.example](frontend/.env.example). Copy them to `.env` only when you begin the Supabase steps in [docs/supabase-setup.md](docs/supabase-setup.md). Keep real credentials out of source control, and never expose database credentials or the service-role key to the frontend.

## Out of Scope

Teacher/admin tools, course authoring, user roles, payments, search, and pagination are not part of the MVP.