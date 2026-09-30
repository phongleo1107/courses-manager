# Frontend Setup (React + Vite)

How to run the frontend scaffold and connect it to the planned Supabase Auth flow.

Covers **Phase 0** (**T0.4**) and **Phases 5–6**, plus **T5.6** in [`todos.md`](./todos.md).
Related: [`supabase-setup.md`](./supabase-setup.md) (do this first), [`backend-setup.md`](./backend-setup.md).

> **Current state.** `frontend/` is a Vite + React + TypeScript starter app. The registration UI and
> Supabase integration are not implemented. The Supabase client package is already in
> `package.json`; the source files listed below describe the planned application, not files currently
> present in the repository.

## Prerequisites

* **Node.js 18+** and npm (use `node --version` to check).
* A filled-in `frontend/.env` — see [`supabase-setup.md`](./supabase-setup.md) Step 5.
* The backend running on `http://localhost:8000` for the authenticated parts.

---

## Step 1 — Install dependencies

The Vite project is already scaffolded. From the repository root:

```bash
npm --prefix frontend install
```


## Step 2 — Runtime dependencies

`@supabase/supabase-js` is already listed in `frontend/package.json`. The application can use the
browser's `fetch` API for backend requests; no separate HTTP client is required. The available package
scripts are `dev`, `build`, `preview`, and `lint`.

---

## Step 3 — Create `frontend/.env`

```bash
cd frontend
cp .env.example .env
```

Fill in the three variables:

| Variable | Value | Source |
| :--- | :--- | :--- |
| `VITE_SUPABASE_URL` | `https://<project-ref>.supabase.co` | [`supabase-setup.md`](./supabase-setup.md) Step 2 value 1 |
| `VITE_SUPABASE_ANON_KEY` | the **anon / publishable** key | Step 2 value 2 |
| `VITE_API_BASE_URL` | `http://localhost:8000` | the FastAPI origin |

### Environment variable exposure

**Every `VITE_*` variable is inlined into the shipped JavaScript bundle.** Vite substitutes these values at
build time, so they are readable by anyone who loads the app. Supabase's own JWT documentation calls out
this exact `NEXT_PUBLIC_` / `VITE_` / `PUBLIC_` prefix trap as a common way secrets leak.

* **Safe:** `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` — designed to be public.
* **Never:** `DATABASE_URL`, `SUPABASE_JWT_SECRET`, the Supabase **secret / service_role** key.

All database access goes through FastAPI (PRD §1), so the browser never needs a database credential.

Verify the secret is not tracked:

```bash
git status --porcelain --untracked-files=all | grep -E '\.env$' || echo "OK: .env not tracked"
```

> Only `.env` is read by Vite — `.env.example` is a template. Changing
> `.env.example` has no effect at runtime.

---
## Step 4 — Run the dev server

```bash
cd frontend
npm run dev
```

Serves on **<http://localhost:5173>** by default. That exact origin must appear in the backend's
`CORS_ORIGINS` and in Supabase's redirect allowlist.

If port 5173 is taken, Vite picks the next free port — and then CORS fails, because the origin no longer
matches `CORS_ORIGINS`. Either free the port or update `CORS_ORIGINS` in `backend/.env` and restart the
API.

### Step 4a — Implement the application modules [not yet implemented — T5.1–T5.4, T6.x]

The current `App.tsx` is the Vite demo. The files below are planned work for Phases 5–6; the target
component tree is in [`../architecture.md`](../architecture.md) §5.

| File | Purpose | Task |
| :--- | :--- | :--- |
| `src/lib/supabase.ts` | single `createClient` instance from the env vars | T5.1 |
| `src/context/AuthContext.tsx` | session state via `onAuthStateChange`, exposes `useAuth()` | T5.2 |
| `src/components/Navbar.tsx` | login / logout / user status | T5.3 |
| `src/App.tsx` | composes Navbar + ClassList + MyRegistrations | T5.4 |
| `src/lib/api.ts` | fetch wrapper: injects `Bearer`, refreshes once on `401` | T6.1 |
| `src/hooks/useClasses.ts` | `GET /classes` | T6.2 |
| `src/hooks/useMyRegistrations.ts` | `GET /registrations/me` | T6.4 |
| `src/components/ClassList.tsx` + `ClassCard.tsx` | catalog + Register | T6.3 |
| `src/components/MyRegistrations.tsx` + `RegistrationRow.tsx` | enrolled classes + Drop | T6.5 |

---

## Step 5 — Verify the auth flow

1. Start the backend **and** the frontend.
2. Open <http://localhost:5173>.
3. **Signed out:** the class catalog must still render (PRD §7). If it shows a CORS error, fix
   `CORS_ORIGINS` in `backend/.env` and restart the API.
4. Click **Sign in**, complete the Email or Google flow.
5. The Navbar should show your email, and a hard reload must keep you signed in. If you are bounced back
   signed out, the Supabase redirect allowlist is wrong — see
   [`supabase-setup.md`](./supabase-setup.md) Step 4.

### Verifying the token is being sent

In DevTools → Network → any request to `http://localhost:8000`:

* **Request Headers** must contain `Authorization: Bearer eyJ...`
* A `401` response means the header is missing or the token was rejected. Check the backend log first —
  it reports the reason (`expired`, `bad_signature`, `wrong_audience`) without logging the token itself.
* A `CORS` error instead of a real status code means `Authorization` is missing from the backend's
  `allow_headers`, not that the token is wrong.

---

## Step 6 — Check the frontend

```bash
cd frontend
npm run lint
npm run build
```

There is no test script or test runner configured yet. Add the auth tests described in task T5.6 when a
test framework is selected.

---

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `import.meta.env.VITE_X is undefined` | `.env` missing, or the dev server was started before it was created | Create `.env` and **restart** `npm run dev` — Vite reads env vars at startup only |
| Env var still `undefined` after adding it | Variable name lacks the `VITE_` prefix | Rename it; unprefixed vars are deliberately not exposed |
| CORS error in the console, `curl` works | `CORS_ORIGINS` does not exactly match the browser origin | Match scheme, host **and** port; restart the API |
| Every API call returns `401` | No session, or a stale token | Sign in; `lib/api.ts` refreshes once on `401` and retries (T6.1) |
| Sign-in redirects back with no session | Redirect URL not allowlisted | [`supabase-setup.md`](./supabase-setup.md) Step 4 |
| Catalog visible but "Register" does nothing | Not signed in — this is intended | The button is disabled for anonymous users (T6.3) |
| `npm create vite` deleted `.env.example` | "Remove existing files" was chosen | Re-create it from git: `git checkout -- frontend/.env.example` |


