# Courses Manager

Courses Manager is a course-registration app in development. The repository currently contains a Vite + React starter frontend and a Python backend package scaffold. The registration UI, API, database schema, and authentication flow are planned but not implemented yet.

## Overview

The planned first release focuses on student registration:

* Browse available classes without signing in
* Sign in with Supabase Auth
* Register for a class
* View registered classes
* Drop a registered class
* Enforce class capacity and prevent duplicate registrations

Teacher and admin tools, role-based access control, and course authoring are out of scope for that release.

## Planned Architecture

```text
React + Supabase Client
        │
        ├── Supabase Auth
        │       └── JWT
        │
        ▼
     FastAPI
        │
        ├── JWT verification
        ├── API routes
        └── Service layer
                │
                ▼
          SQLAlchemy
                │
                ▼
       PostgreSQL (Supabase)
```

The diagram describes the target design, not a running end-to-end application. See [`architecture.md`](./architecture.md) for the proposed data model, API contract, and technical decisions.

## Planned Stack

| Layer                 | Technology                |
| --------------------- | ------------------------- |
| Frontend              | React + TypeScript + Vite |
| Authentication        | Supabase Auth             |
| Backend               | Python + FastAPI          |
| Validation / Settings | Pydantic                  |
| ORM                   | SQLAlchemy 2.0            |
| Database              | PostgreSQL via Supabase   |
| Database Driver       | psycopg                   |
| JWT                   | PyJWT + JWKS              |
| Migrations            | Alembic                   |
| Python tooling        | uv                        |
| Testing               | pytest + httpx            |
| Linting               | Ruff                      |

## Repository Layout

```text
courses-manager/
├── backend/
│   ├── src/
│   │   └── backend/
│   ├── .env.example
│   ├── .python-version
│   └── pyproject.toml
│
├── frontend/
│   ├── src/                 # Vite starter app
│   ├── .env.example
│   └── package.json
│
├── docs/
│   ├── backend-setup.md
│   ├── frontend-setup.md
│   ├── supabase-setup.md
│   └── todos.md
│
├── architecture.md
├── PRD.md
├── LICENSE
└── README.md
```

## Current State

The frontend is the default Vite counter/demo app. Its dependencies are installed from `frontend/package-lock.json`, and `npm run build` currently succeeds. The backend package still contains only its initializer; there is no FastAPI application, migration setup, or seed script yet. The setup guides describe what exists today and identify the remaining implementation work.

## Run the Frontend Scaffold

### Prerequisites

* Node.js 18+
* npm

Clone the repository, then start the frontend:

```bash
git clone https://github.com/phongleo1107/courses-manager.git
cd courses-manager
```

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local URL when the server starts. Supabase configuration is not needed by the current demo. The future integration setup is documented in [`docs/supabase-setup.md`](./docs/supabase-setup.md), [`docs/backend-setup.md`](./docs/backend-setup.md), and [`docs/frontend-setup.md`](./docs/frontend-setup.md).

The backend cannot be started yet. Its target setup and outstanding implementation tasks are listed in [`docs/backend-setup.md`](./docs/backend-setup.md) and [`docs/todos.md`](./docs/todos.md).

## Environment Variables

### Backend

Defined in [`backend/.env.example`](./backend/.env.example):

| Variable                | Purpose                                 |
| ----------------------- | --------------------------------------- |
| `DATABASE_URL`          | Supabase PostgreSQL connection          |
| `SUPABASE_URL`          | Supabase project URL                    |
| `SUPABASE_JWKS_URL`     | Public JWT signing keys                 |
| `SUPABASE_JWT_AUDIENCE` | Expected JWT audience                   |
| `SUPABASE_JWT_SECRET`   | Legacy HS256 secret, only when required |
| `CORS_ORIGINS`          | Allowed frontend origins                |

### Frontend

Defined in [`frontend/.env.example`](./frontend/.env.example):

| Variable                 | Purpose                    |
| ------------------------ | -------------------------- |
| `VITE_SUPABASE_URL`      | Supabase project URL       |
| `VITE_SUPABASE_ANON_KEY` | Public Supabase client key |
| `VITE_API_BASE_URL`      | FastAPI base URL           |

**Never expose** database credentials, JWT secrets, or Supabase service-role/secret keys through `VITE_*` variables.

## API

The planned API is:

| Method   | Endpoint                    | Auth     | Description                      |
| -------- | --------------------------- | -------- | -------------------------------- |
| `GET`    | `/classes`                  | Public   | List available classes           |
| `GET`    | `/registrations/me`         | Required | Get current user's registrations |
| `POST`   | `/registrations`            | Required | Register for a class             |
| `DELETE` | `/registrations/{class_id}` | Required | Drop a class                     |

Authenticated requests use:

```http
Authorization: Bearer <supabase-access-token>
```

FastAPI verifies the JWT before accessing protected registration endpoints.

## Development

### Backend

```bash
cd backend

uv sync
uv run pytest
uv run ruff check .
```

### Frontend

```bash
cd frontend

npm install
npm run dev
npm run build
npm run lint
```

## Documentation

| Document                                             | Description                                 |
| ---------------------------------------------------- | ------------------------------------------- |
| [`PRD.md`](./PRD.md)                                 | Product requirements and scope              |
| [`architecture.md`](./architecture.md)               | System architecture and technical decisions |
| [`docs/todos.md`](./docs/todos.md)                   | Implementation plan and acceptance criteria |
| [`docs/supabase-setup.md`](./docs/supabase-setup.md) | Supabase and authentication setup           |
| [`docs/backend-setup.md`](./docs/backend-setup.md)   | Backend setup and development workflow      |
| [`docs/frontend-setup.md`](./docs/frontend-setup.md) | Frontend setup and development workflow     |

## License

This project is licensed under the [MIT License](./LICENSE).
