# Course Registration Learning Roadmap

This roadmap follows the code from one small request to the complete registration flow. Each step names what you will learn and where to work. Finish a step, run its check, and then move on at your own pace.

The product scope stays the same: browse classes without signing in; sign in; register for a class; view and drop your registrations; prevent duplicate registrations and registrations beyond class capacity.

## Already in Place

- [x] Backend dependencies are managed by `uv` in `backend/pyproject.toml`.
- [x] FastAPI starts and returns `{"status":"ok"}` from `GET /health`.
- [x] Settings, a SQLAlchemy database session, and an empty model base are configured. Local development defaults to SQLite.
- [x] Alembic is configured, but there is no application schema migration yet.
- [x] A small health/settings test suite runs with `uv run pytest`.
- [x] The frontend is a Vite + React + TypeScript starter; the course-registration screens are not built yet.

Start the current backend from `backend/`:

```bash
uv sync
uv run uvicorn backend.main:app --reload --port 8000
```

Check `http://localhost:8000/health`. Stop the server with Ctrl+C.

## Essential MVP Steps

### 1. Return a class list from FastAPI

**Learn:** A REST API receives an HTTP request and returns a status code plus JSON. `GET` reads data and does not change it.

**Work in:** `backend/src/backend/main.py` (or a small classes route module, if you introduce one).

Return a short hard-coded list of classes first. Try it with `curl` and inspect the JSON response before connecting a database.

**Done when:** `GET /classes` returns `200` and a JSON list, including an empty list when there are no classes.

### 2. Store courses and classes in a database

**Learn:** A database stores related information in tables. SQLAlchemy models describe those tables in Python; a migration creates the tables in the database.

**Work in:** `backend/src/backend/models/`, `backend/src/backend/db/base.py`, and `backend/alembic/`.

Start with `Course` and `Class` and their one-to-many relationship. Use the local SQLite default while learning, create an Alembic migration, and add a few sample rows. Keep the required fields from the [PRD](../PRD.md).

**Done when:** You can create the tables, insert a course and class, and read them back. The migration can be applied to a fresh local database.

### 3. Read database rows through the API

**Learn:** FastAPI turns database rows into a response. Pydantic response models control the JSON shape sent to the browser.

**Work in:** `backend/src/backend/schemas/` and the `GET /classes` route.

Replace the hard-coded list with a SQLAlchemy query. Include each class's course information in the response. Test with `curl` before moving on.

**Done when:** `GET /classes` returns the rows in the database as JSON, and an empty database returns `200 []`.

### 4. Connect the database to Supabase Postgres

**Learn:** `DATABASE_URL` tells SQLAlchemy which database and driver to use. Alembic applies the same schema changes to that database.

**Work in:** `backend/.env`, `backend/.env.example`, and the Alembic migration environment.

Create a Supabase project and use its PostgreSQL connection string. Keep the real URL in the ignored `.env` file, never in source control. Apply the migration and confirm the tables exist. See [Supabase setup](supabase-setup.md) and [backend setup](backend-setup.md).

**Done when:** The API reads the same class data from Supabase Postgres. The database password is not committed or sent to the frontend.

### 5. Show the public class list in React

**Learn:** The browser uses `fetch` to send an HTTP request; the frontend and backend are separate programs. CORS lets the browser call the API from the Vite development server.

**Work in:** `frontend/src/App.tsx` and the backend CORS settings in `backend/src/backend/main.py`.

Fetch `GET /classes` and display the course and class fields. Add a simple loading, empty, and error message.

**Done when:** The class list comes from FastAPI, not from hard-coded frontend data, and anonymous visitors can see it.

### 6. Add Supabase sign-in and learn what a token is

**Learn:** Supabase Auth checks a user's credentials. After sign-in, it gives the frontend a signed access token. A JWT is a readable set of claims with a signature that lets the backend check who issued it and whether it is valid.

**Work in:** `frontend/src/lib/` for the Supabase client, `frontend/src/` for the sign-in UI, and the Supabase dashboard.

Start with email sign-in. After it works, inspect the session and learn which value is the access token. Google sign-in can be added as another provider.

**Done when:** A user can sign in and sign out, and the frontend can access the current session. Keep the anon/publishable key in the frontend; never put a database password or service-role key there.

### 7. Let FastAPI recognize the signed-in user

**Learn:** The frontend sends `Authorization: Bearer <token>` with a protected request. FastAPI verifies the token before trusting its user ID (`sub`).

**Work in:** `backend/src/backend/core/` and a small authentication dependency used by a test endpoint.

Begin with signature, expiry, issuer, and audience checks using the Supabase project settings. Use a real token only in your local browser session; use test tokens for automated tests.

**Done when:** A request without a token is rejected, and a valid signed-in request identifies the expected user. Keep the class-list endpoint public.

### 8. Save and show a user's registrations

**Learn:** A registration row connects one user to one class. `POST` creates a registration; `GET` reads the signed-in user's registrations; `DELETE` drops one.

**Work in:** `backend/src/backend/models/`, `backend/src/backend/schemas/`, and the registration routes.

Add the `Registration` table and build one operation at a time: list my registrations, register for a class, then drop a class. Take the user ID from the verified token, not from the request body. Reject duplicate registrations and full classes.

**Done when:** Registrations persist in Supabase Postgres, belong to the correct `auth.users.id`, and users cannot view or drop another user's registrations.

### 9. Finish the register/drop flow in React

**Learn:** The UI reflects the response from the API. A successful write should update both the user's registrations and the class availability.

**Work in:** `frontend/src/App.tsx` and, as the UI grows, small components for the class list and registrations.

Connect the register and drop actions. Show useful feedback when a class is full or a request fails.

**Done when:** The MVP requirements below work through the browser from a fresh sign-in.

## MVP Check

- Anonymous visitors can browse classes.
- A user can sign in and out with Supabase Auth.
- FastAPI accepts valid user tokens and rejects missing or invalid tokens on protected routes.
- A signed-in user can register, see their registrations, and drop a class.
- Registrations persist for the correct user; duplicate registrations and registrations over capacity are rejected.

## Later

Caching signing keys, key rotation, concurrent last-seat requests, deeper database constraints, structured error codes, token refresh/retry behavior, request logging, and deployment checks are useful follow-ups. They are described in [Later Topics](later-topics.md); they do not need to be completed before learning the basic request and database flow.

Teacher/admin tools, roles, course authoring, payments, search, and pagination remain outside the MVP scope.