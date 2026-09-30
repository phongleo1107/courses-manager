# Backend Setup (FastAPI)

Backend setup and the intended development workflow.

Covers **Phase 0** (**T0.3**, **T0.5**), **Phases 2–4**, and the backend test tasks **T8.1–T8.2** in
[`todos.md`](./todos.md).
Related: [`supabase-setup.md`](./supabase-setup.md) (for Supabase integration), [`frontend-setup.md`](./frontend-setup.md).

> **Current state.** The backend foundation is runnable: it includes a FastAPI health endpoint,
> settings, a SQLAlchemy session, and Alembic configuration. Local startup defaults to SQLite and does
> not require Supabase credentials. Domain models, schema migrations, seed data, authentication, and
> registration endpoints remain to be implemented.

## Prerequisites

* **uv** — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`. This repo uses uv, not
  pip/venv directly (ADR-6).
* Python **3.14**, already pinned in `backend/.python-version`. uv downloads it automatically.
* A filled-in `backend/.env` only when connecting to Supabase; local health checks use SQLite by default.

---

## Step 1 — Install dependencies

```bash
cd backend
uv sync
```

`backend/pyproject.toml` is the source of truth for backend dependencies (ADR-6). The repository has no
root `requirements.txt`.

### Step 1a — Dependency configuration

The runtime and development dependencies are declared in `backend/pyproject.toml`; `uv sync` installs
them and updates the committed lockfile. The manifest uses the following extras:

* **`pyjwt[crypto]`** — the `crypto` extra pulls in `cryptography`, which PyJWT needs to verify
  **`ES256`/`RS256`** tokens. Without it, JWKS verification fails.
* **`psycopg[binary]`** — psycopg v3 with prebuilt binaries. Chosen over `asyncpg` partly because this
  project uses synchronous SQLAlchemy (ADR-5).
* Avoid bare `python-jose`; PyJWT is what ADR-3 specifies.

### Step 1b — Verify the imports (T0.3 prerequisite)

Python 3.14 is relatively new, so verify that compatible wheels are available for the selected packages.
Confirm before writing any feature code:

```bash
uv run python -c "import fastapi, sqlalchemy, psycopg, jwt, cryptography, alembic; print('ok')"
```

* Prints `ok` → continue.
* Tries to build from source, or errors → stop and lower the interpreter
  (`backend/.python-version`) to a version with published wheels, then re-run `uv sync`. Record the
  outcome in [`../architecture.md`](../architecture.md) §9.2.

`uv.lock` is committed so contributors resolve the same dependency versions.

---

## Step 2 — Configure the environment

The health endpoint can run without a `.env`; it defaults to a local SQLite URL. To connect to a
Supabase project, copy the committed template and fill in the project values:

```bash
cd backend
cp .env.example .env
```

| Variable                | Where the value comes from                                                                  |
| :------------------------| :--------------------------------------------------------------------------------------------|
| `DATABASE_URL`          | [`supabase-setup.md`](./supabase-setup.md) Step 2 value 3. Must be `postgresql+psycopg://…` |
| `SUPABASE_URL`          | Step 2 value 1 — bare project URL, no trailing `/auth/v1`                                   |
| `SUPABASE_JWKS_URL`     | Optional; defaults to `<SUPABASE_URL>/auth/v1/.well-known/jwks.json`                        |
| `SUPABASE_JWT_AUDIENCE` | `authenticated` — use the `aud` observed in Step 3b                                         |
| `SUPABASE_JWT_SECRET`   | Leave **commented out** unless Step 3c found `alg: HS256`                                   |
| `CORS_ORIGINS`          | `http://localhost:5173` — must match the frontend origin exactly                            |

`.env` is gitignored (`.gitignore` lines 1–4). Verify:

```bash
git status --porcelain --untracked-files=all | grep -E '\.env$' || echo "OK: .env not tracked"
```

These variables are read by `Settings` in `backend/src/backend/core/config.py`.

---
## Step 3 — Database migrations

Alembic is configured and can read the local database URL, but the repository does not yet contain
SQLAlchemy domain models or a schema revision. Do not run `alembic upgrade head` until the initial
migration is added.

### Step 3a — Alembic environment

Alembic is initialized in `backend/alembic/`. Its environment reads the database URL from `Settings`,
not from the placeholder URL in `alembic.ini`. No application migration has been added yet; create one
after defining the SQLAlchemy models.

### Step 3b — Check migration state

```bash
cd backend
uv run alembic current
```

Run Alembic from `backend/`; the environment reads `DATABASE_URL` from `Settings`. Once an initial
migration exists, apply it with `uv run alembic upgrade head`.

Useful commands:

| Command | Purpose |
| :--- | :--- |
| `uv run alembic current` | Show the applied revision |
| `uv run alembic upgrade head` | Apply pending migrations after a revision exists |
| `uv run alembic downgrade base` | Roll migrations back after a revision exists |
| `uv run alembic check` | Compare defined models with the migration schema |

`alembic check` reports model changes that do not have a corresponding migration. A mismatch means the
ORM and database schemas differ.

---

## Step 4 — Seed sample data **[not yet implemented — T1.6]**

```bash
cd backend
uv run python scripts/seed.py
```

Creates at least 3 courses and 5 classes, including one with `capacity = 1` and one that is already full.
Both are needed by the end-to-end tasks T7.5 and T7.6. The script is idempotent, so re-running it is safe.

---

## Step 5 — Run the API

### Step 5a — App module

`backend/src/backend/main.py` defines the FastAPI application, CORS middleware, and `GET /health` route.

### Step 5b — Start the server

```bash
cd backend
uv run uvicorn backend.main:app --reload --port 8000
```

Verify it is alive:

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

Interactive API docs are at <http://localhost:8000/docs>.

### Step 5c — Planned API endpoints

The catalog and registration endpoints are not implemented yet. Their contracts and acceptance checks
are tracked in [`todos.md`](./todos.md) and [`../architecture.md`](../architecture.md).

---

## Step 6 — Run the backend tests

```bash
cd backend
uv run pytest
uv run ruff check .
```

The current suite contains a health-endpoint smoke test. Add auth and registration tests as those
features are implemented.

---

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `uv sync` tries to compile `psycopg` from source | No wheel for Python 3.14 | Lower `backend/.python-version`, re-sync — see Step 1b |
| `import jwt` works but `ES256` verification fails | Missing the `crypto` extra | Confirm `pyjwt[crypto]` is in `pyproject.toml` and `cryptography` imports |
| `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql` | `DATABASE_URL` missing the `+psycopg` driver | See [`supabase-setup.md`](./supabase-setup.md) Step 2 |
| `ModuleNotFoundError: No module named 'backend'` | Running `uvicorn` from the repo root instead of `backend/`, or without uv | `cd backend && uv run uvicorn backend.main:app --reload` |
| `Target database is not up to date` | Pending migrations | `uv run alembic upgrade head` |
| Every request with a valid-looking token returns `401` | `SUPABASE_URL` has a trailing `/auth/v1`, or `SUPABASE_JWT_AUDIENCE` is wrong | Fix `.env`; the `iss`/`aud` values must match Step 3b exactly |
| Browser reports a CORS error, `curl` works fine | `CORS_ORIGINS` does not match the frontend origin exactly, or `Authorization` is missing from `allow_headers` | Fix `.env`, restart the server, see [`frontend-setup.md`](./frontend-setup.md) |
| `409 class_full` when a seat should exist | `classes.registered` drifted from reality | Recompute: it must equal `count(*)` of the class's registrations |

Next: [`frontend-setup.md`](./frontend-setup.md)

