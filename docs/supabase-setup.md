# Supabase Setup

How to stand up the Supabase project (Auth + Postgres) for this app and produce the credentials that
both `.env` files need.

Covers **Phase 1** in [`todos.md`](./todos.md): tasks **T1.1**, **T1.2**, **T1.3**.
Related: [`backend-setup.md`](./backend-setup.md) (runs migrations), [`frontend-setup.md`](./frontend-setup.md).

> Do the steps in order. Step 3 is a **RISK GATE** — if it reveals the project uses legacy HS256 keys,
> the backend's token verification changes and you must decide before writing `core/security.py`.

## Prerequisites

* A Supabase account.
* Roughly 10 minutes. No CLI is required — the dashboard is enough.

---

## Step 1 — Create the project

1. In the dashboard, create a new project.
2. **Choose the region closest to where the FastAPI backend will run.** This matters: ADR-3 in
   [`../architecture.md`](../architecture.md) rules out per-request Auth-server round-trips partly
   because of cross-region latency, and the same reasoning applies to database round-trips from the API.
3. Set a **database password** and save it in your password manager. It goes into `DATABASE_URL` and is
   shown only once.
4. Wait for provisioning to finish.

**Write down the project ref** — the `<project-ref>` slug in the dashboard URL
(`https://supabase.com/dashboard/project/<project-ref>`). Every value below contains it.

---

## Step 2 — Collect the four credentials

You need four values. All are found under **Project Settings**.

| # | Value | Where | Goes into |
| :-- | :--- | :--- | :--- |
| 1 | **Project URL** | Project Settings → API → Project URL | backend `SUPABASE_URL`, and frontend `VITE_SUPABASE_URL` |
| 2 | **anon / publishable key** | Project Settings → API Keys → `anon` / `publishable` | frontend `VITE_SUPABASE_ANON_KEY` |
| 3 | **Connection string** | Project Settings → Database → Connection string | backend `DATABASE_URL` |
| 4 | **JWT secret** *(maybe)* | Project Settings → API → JWT Settings | backend `SUPABASE_JWT_SECRET` — **only if Step 3 says you need it** |

### About the connection string (value 3)

The dashboard gives you several variants. Use the **Session pooler** string, then make two edits:

1. **Change the scheme.** The dashboard shows `postgresql://`. SQLAlchemy needs a driver-qualified URL:
   ```
   postgresql+psycopg://
   ```
   Pasting the raw string without this change is the single most common setup failure — SQLAlchemy
   raises `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql`.

2. **Substitute the real password** for the `[YOUR-PASSWORD]` placeholder.

Resulting shape:
```bash
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:<db-password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

> **Avoid the transaction pooler** (port `6543`) for this project. It does not support all the session
> features Alembic and `SELECT ... FOR UPDATE` rely on. The session pooler on port `5432` behaves like a
> normal Postgres connection and is the calmer choice for local development.

---
## Step 3 — Determine the JWT signing key type — **RISK GATE**

The backend verifies tokens **offline** using the project's public keys (ADR-3). Whether that is possible
depends on which signing-key system your project uses, so establish this now.

### 3a. Check for a public JWKS document

```bash
curl -s "https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json" \
  -H "apikey: <anon-key>" | head -c 400
```

* **Returns `{"keys":[ ... ]}`** → asymmetric keys (`ES256`/`RS256`). This is the expected, recommended
  setup. Continue with Step 3b, and leave `SUPABASE_JWT_SECRET` commented out in `.env`.
* **Returns an error or no keys** → the project is on the legacy JWT secret. Skip to Step 3c.

The JWKS URL is not arbitrary: per Supabase's documentation it is the token's `iss` claim plus
`/.well-known/jwks.json`.

### 3b. Confirm the algorithm and claims on a real token

Sign in through the dashboard (or any temporary client) and capture an access token, then decode its
header and payload:

```bash
ACCESS_TOKEN="<paste-access-token>"

python3 - "$ACCESS_TOKEN" <<'PY'
import base64, json, sys

def part(token, i):
    b = token.split('.')[i]
    return json.loads(base64.urlsafe_b64decode(b + '=' * (-len(b) % 4)))

print("header :", json.dumps(part(sys.argv[1], 0), indent=2))
print("payload:", json.dumps(part(sys.argv[1], 1), indent=2))
PY
```

Confirm three things and note them down:

| Check | Expected | Why it matters |
| :--- | :--- | :--- |
| header `alg` | `ES256` or `RS256` | `HS256` means you must use Step 3c instead |
| payload `iss` | `https://<project-ref>.supabase.co/auth/v1` | The backend asserts this, so a token from a *different* project is rejected |
| payload `aud` | `authenticated` | The backend asserts this, so a `service_role` token cannot call user routes |

Put the observed `iss` into `SUPABASE_URL` (without the trailing `/auth/v1`) and `aud` into
`SUPABASE_JWT_AUDIENCE`. Do **not** guess these — a wrong `aud` makes every authenticated request return
`401` with no obvious cause.

### 3c. Only if `alg` is `HS256`

Uncomment `SUPABASE_JWT_SECRET` in `backend/.env`, copy the value from **Project Settings → API → JWT
Settings → JWT Secret**, and record the deviation in [`../architecture.md`](../architecture.md) §8 ADR-3.

Two options, both described in ADR-3:
* **(a) shared-secret verification** — simplest, but reintroduces the secret Supabase now discourages.
* **(b) Auth-server introspection** — call `GET /auth/v1/user` per request; no secret stored locally, but
  it puts the Auth server in the hot path of every request.

> Supabase states the legacy JWT secret is **"No longer recommended"** and is retained only for backward
> compatibility. If you have the choice, enable asymmetric signing keys in the dashboard and use Step 3b.

---

## Step 4 — Enable the auth providers

Authentication → Providers:

* **Email** — enable. Create at least one test user, and confirm it if "Confirm email" is on.
* **Google** — enable if you want the OAuth button from PRD §6 Step 1 to work. This needs an OAuth client
  in Google Cloud Console with an **Authorized redirect URI** of:
  ```
  https://<project-ref>.supabase.co/auth/v1/callback
  ```
  Paste the resulting Client ID and Client Secret into Supabase.

Then Authentication → URL Configuration:

* **Site URL** → `http://localhost:5173`
* **Redirect URLs** → add `http://localhost:5173/**`

If the redirect allowlist is wrong, sign-in appears to succeed and then drops you back on the page with
no session — a failure mode that looks like a frontend bug but is not.

---
## Step 5 — Create the `.env` files

This is the step that turns the credentials from Step 2 into working configuration. Both apps read a
local `.env` that is **gitignored**; the committed `.env.example` templates are the source of truth for
which variables exist.

```bash
cd <repo-root>
cp backend/.env.example  backend/.env
cp frontend/.env.example frontend/.env
```

### 5a. Fill in `backend/.env`

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `DATABASE_URL` | Step 2, value 3 | Must start `postgresql+psycopg://`, not `postgresql://` |
| `SUPABASE_URL` | Step 2, value 1 | Project URL, **without** a trailing `/auth/v1` |
| `SUPABASE_JWKS_URL` | `https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json` | Optional — this is the default. Only set it if you use a custom domain |
| `SUPABASE_JWT_AUDIENCE` | `authenticated` | Use the `aud` you actually observed in Step 3b |
| `SUPABASE_JWT_SECRET` | *leave commented out* | Only if Step 3c applied |
| `CORS_ORIGINS` | `http://localhost:5173` | Must match the frontend origin exactly |

### 5b. Fill in `frontend/.env`

| Variable | Value |
| :--- | :--- |
| `VITE_SUPABASE_URL` | Step 2, value 1 (same as backend `SUPABASE_URL`) |
| `VITE_SUPABASE_ANON_KEY` | Step 2, value 2 — the **anon / publishable** key |
| `VITE_API_BASE_URL` | `http://localhost:8000` — the FastAPI origin |

> **Everything in `frontend/.env` is public.** Vite inlines `VITE_*` values into the shipped JavaScript,
> so these end up readable by anyone using the app. That is fine for the Supabase URL and anon key, which
> are designed to be public. It is **never** fine for `DATABASE_URL`, `SUPABASE_JWT_SECRET`, or the
> Supabase **secret / service_role** key. See [`../architecture.md`](../architecture.md) §7.1.

### 5c. Confirm the secrets are not tracked

```bash
git status --porcelain --untracked-files=all | grep -E '\.env$' || echo "OK: no .env files visible to git"
```

The grep must print nothing. If it prints a `.env` path, your `.gitignore` is wrong — fix it **before**
committing.

---

## Step 6 — Apply the database schema

The three application tables (`courses`, `classes`, `registrations`) are created by Alembic migrations
that live in the backend, not by clicking in the dashboard. Once `backend/.env` is filled in, follow
[`backend-setup.md`](./backend-setup.md) to run:

```bash
cd backend
uv sync
uv run alembic upgrade head
```

### About Row Level Security

**RLS is deliberately left disabled** on these tables (ADR-2). All data access goes through FastAPI, which
authorises every request via the verified JWT — so RLS policies would never be consulted, because the
backend connects with a privileged role that bypasses them.

Two consequences to keep in mind:

* This design assumes the browser **never** queries these tables directly via PostgREST.
* The Supabase **secret / service_role** key must never be shipped to the frontend. Only the anon key goes
  to the browser, and it is used here solely for Auth.

If you later want direct browser access, enable RLS and add policies (`user_id = auth.uid()` on
`registrations`; read-only on `courses`/`classes`) — see ADR-2's consequences section.

---

## Step 7 — Verify the setup

Tick these off before moving to the backend or frontend guides:

- [ ] `docs/supabase-setup.md` Steps 1–5 complete, both `.env` files filled in
- [ ] `git status --porcelain --untracked-files=all | grep '\.env$'` prints nothing
- [ ] The JWKS URL from Step 3a returns a `keys` array
- [ ] `iss` and `aud` from Step 3b are recorded in `backend/.env`
- [ ] At least one Email user exists and can sign in
- [ ] Google OAuth enabled *and* the redirect allowlist contains `http://localhost:5173/**` (or you have
      consciously skipped Google)
- [ ] `cd backend && uv run alembic upgrade head` succeeds
- [ ] The three tables are visible in the dashboard's Table Editor

---

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql` | Connection string was pasted verbatim | Prefix the scheme with `+psycopg` → `postgresql+psycopg://` |
| `password authentication failed` | `[YOUR-PASSWORD]` left as a placeholder, or wrong database password | Use the database password from Step 1, not your Supabase account password |
| `could not translate host name` | Using the direct-connection host from a network that blocks IPv6 | Switch to the Session pooler connection string |
| JWKS endpoint returns an error / no `keys` | Project uses the legacy JWT secret | Step 3c — decide between shared-secret and introspection |
| Every authenticated request returns `401` | `SUPABASE_URL` includes `/auth/v1`, or `SUPABASE_JWT_AUDIENCE` is wrong | `SUPABASE_URL` must be the bare project URL; `aud` must be the value observed in Step 3b |
| Google sign-in returns to the page with no session | Redirect URL not allowlisted | Authentication → URL Configuration → add `http://localhost:5173/**` |
| `permission denied for table ...` | Migrations ran with a role lacking privileges | Re-run migrations using the `postgres` role from `DATABASE_URL` |

Next: [`backend-setup.md`](./backend-setup.md) → [`frontend-setup.md`](./frontend-setup.md)


