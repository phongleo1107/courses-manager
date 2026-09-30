# Courses Manager

A full-stack course registration application built to practice modern web development with React, FastAPI, SQLAlchemy, PostgreSQL, and Supabase Auth.

## Overview

The application focuses on the student course registration flow:

* Browse available classes without signing in
* Sign in with Supabase Auth
* Register for a class
* View registered classes
* Drop a registered class
* Enforce class capacity and prevent duplicate registrations

Teacher/admin course management and role-based access control are currently **out of scope**.

## Architecture

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

See [`architecture.md`](./architecture.md) for the detailed architecture, database design, authentication flow, and technical decisions.

## Tech Stack

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

## Project Structure

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
│   └── .env.example
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

## Getting Started

### Prerequisites

* Python 3.14
* [uv](https://docs.astral.sh/uv/)
* Node.js 18+
* npm
* A Supabase project

### 1. Clone the repository

```bash
git clone https://github.com/phongleo1107/courses-manager.git
cd courses-manager
```

### 2. Configure Supabase

Create a Supabase project and configure PostgreSQL and authentication. Google OAuth is optional.

Create the local environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Fill in the required values.

See [`docs/supabase-setup.md`](./docs/supabase-setup.md) for the complete setup process.

### 3. Set up the backend

```bash
cd backend

uv sync
uv run alembic upgrade head
uv run python scripts/seed.py
```

Start FastAPI:

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

API documentation:

* http://localhost:8000/docs
* http://localhost:8000/health

> Some backend commands depend on features that are still being implemented. See [`docs/todos.md`](./docs/todos.md).

### 4. Set up the frontend

```bash
cd frontend

npm install
npm run dev
```

The frontend runs on:

```text
http://localhost:5173
```

See [`docs/frontend-setup.md`](./docs/frontend-setup.md) for detailed frontend setup instructions.

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
