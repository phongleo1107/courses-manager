# Later Topics

This page keeps useful requirements that do not need to be solved while learning the first request, table, or login flow. Return to a topic when the matching feature works at a basic level.

## Data Integrity

Before relying on registration data, enforce these rules in PostgreSQL as well as in the API:

- A user can register for a class only once: `UNIQUE (user_id, class_id)`.
- `capacity` cannot be negative, and `registered` must stay between zero and capacity.
- Course credits must be positive; class codes must be unique.
- A registration must point to an existing class and Supabase user.
- Dropping a registration removes only the signed-in user's row.

Use `ON DELETE CASCADE` for registrations when their user or class is deleted, and `ON DELETE RESTRICT` when deleting a course that still has classes. Index the class-to-course and registration foreign keys used by the API.

Registering changes both `registrations` and `classes.registered`. Keep those changes in one transaction. For simultaneous requests, lock the class row while checking capacity and increment the counter in SQL (`registered = registered + 1`). Decrement the counter only when a registration row was deleted. These steps prevent a class from being oversold or its count from drifting.

A later test pass should cover duplicate registration, full classes, dropping twice, two users registering for the last seat at the same time, and counter values before and after each operation.

Seed data should be safe to insert more than once. Include at least three courses and five classes, including a one-seat class and a full class, so capacity behavior can be tried locally.

## JWT Verification

A JWT is a signed set of claims, not encrypted data. The API should trust a user's identity only after verifying the token's signature, expiry (`exp`), issuer (`iss`), and audience (`aud`). Use the token's `sub` as the user ID; never accept a user ID from a request body.

Security tests should include an expired token, a bad signature, the wrong issuer or audience, a missing subject, and a token from a different project. They can use local test keys and do not need a live Supabase project.

Supabase projects can use asymmetric signing keys published through JWKS or legacy HS256 signing. The normal path is to verify asymmetric tokens using the project's public JWKS keys. Key caching and key-rotation behavior are useful follow-up work. If a project still uses HS256, choose a supported verification approach and document that choice before building the auth dependency.

Never log access tokens or put database passwords, JWT secrets, or Supabase service-role keys in frontend `VITE_*` variables.

## Database Access and RLS

This project sends database requests through FastAPI. Its current architecture leaves Row Level Security (RLS) disabled on application tables and relies on the API to filter registrations by the verified user's ID. This means the browser must not query those tables directly through Supabase.

If the app later uses Supabase's browser-facing database API, enable RLS and write policies before shipping that access. Never expose the database connection string or service-role key to the browser.

## API and Frontend Resilience

Once the basic flows work, add consistent error responses with stable codes such as `class_not_found`, `class_full`, `already_registered`, and `registration_not_found`. Use `404` for missing resources, `409` for conflicts, and `422` for invalid request data.

The frontend should distinguish loading, empty, error, and populated states. When a protected request gets `401`, refresh the Supabase session at most once and retry once; do not retry business errors such as `404` or `409`.

Keep error meanings consistent: `class_not_found` and `registration_not_found` use `404`; `class_full` and `already_registered` use `409`; invalid request data uses `422`. After a register or drop, refresh both the class list and the user's registrations.

## Database and Test Hardening

Before treating the schema as stable:

- Add indexes for foreign keys and common lookups.
- Check that model changes and migrations stay aligned.
- Test that migrations can be applied and rolled back on a disposable database.
- Make sample-data seeding safe to run more than once.
- Test API behavior with both anonymous requests and two distinct users.
- Keep tests that verify JWT rules offline by using locally generated test keys.
- Check that `GET /classes` does not issue one extra database query for every class.

The Supabase schema intentionally has RLS disabled while FastAPI is the only data path. If browser-side table access is ever added, enable RLS with policies before releasing that change.

For deployment, also revisit CORS origins, secret management, database backups, logs, and error responses. Pagination, search, roles, teacher tools, and audit history are outside the current MVP scope.

## Existing Decisions

- Use synchronous SQLAlchemy with `psycopg` for this small learning project.
- Use `uv` and `backend/pyproject.toml` as the backend dependency source of truth; commit `uv.lock`.
- Keep the `registered` counter because the product requirements include it. Revisit whether to derive counts from registrations if the product requirements change.
- Keep Supabase's `auth.users` table outside the SQLAlchemy model layer. Store its verified UUID on each registration instead.
