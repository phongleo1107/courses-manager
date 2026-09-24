# Frontend Setup (React + Vite)

How to scaffold, configure and run the React frontend, including the Supabase Auth wiring.

Covers **Phase 0** (**T0.4**) and **Phases 5–6**, plus **T5.6** in [`todos.md`](./todos.md).
Related: [`supabase-setup.md`](./supabase-setup.md) (do this first), [`backend-setup.md`](./backend-setup.md).

> **Status.** `frontend/` currently contains only `.env.example`. The app has not been scaffolded and none
> of the Phase 5/6 source files exist yet. Steps marked **[not yet implemented]** are the target workflow.

## Prerequisites

* **Node.js 18+** and npm (use `node --version` to check).
* A filled-in `frontend/.env` — see [`supabase-setup.md`](./supabase-setup.md) Step 5.
* The backend running on `http://localhost:8000` for the authenticated parts.

---

## Step 1 — Scaffold the app **[not yet implemented — T0.4]**

From the **repo root**:

```bash
cd frontend
npm create vite@latest . -- --template react-ts
```

`--template react-ts` matters: the project uses TypeScript, so the response shapes in
[`../architecture.md`](../architecture.md) §6.1 can be typed.

> Vite will warn that the directory is not empty because `.env.example` already exists there. Choose
> **"Ignore files and continue"** so the template is added **without deleting `.env.example`**. Choosing
> "Remove existing files" would delete your committed template.

Then:

```bash
npm install
```

---

## Step 2 — Install the runtime dependencies **[partially done — T0.4]**

`@supabase/supabase-js` is the only library the PRD requires (PRD §2):

```bash
npm install @supabase/supabase-js
```

`fetch` is used for the API calls, so no HTTP client library is needed — architecture.md §5 specifies a
small typed wrapper in `src/lib/api.ts` rather than adding Axios.

Confirm the expected scripts exist in `package.json` (T0.4): `dev`, `build`, `preview`, `lint`.

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

### The one rule that matters

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

> Only `.env` is read by Vite — `.env.example` is inert and exists purely as documentation. Changing
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

### Step 4a — Create the source modules **[not yet implemented — T5.1–T5.4, T6.x]**

The app is scaffolded but empty of app code. The files below are what Phases 5–6 add; the component tree
is in [`../architecture.md`](../architecture.md) §5.

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

## Step 6 — Run the frontend tests

```bash
cd frontend
npm run lint
npm test          # once a test runner is configured (T5.6)
```

The auth tests mock the Supabase client, so they need **no network and no real project** (T5.6). If a test
starts hitting `supabase.co`, the mock is not being applied.

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


