# Product Requirements

This document describes the intended course-registration MVP. The repository currently has a Vite frontend starter and a FastAPI backend foundation; the product features below are still being built.

## Goal

A student can browse available classes, sign in, register for a class, see their registrations, and drop a class. The app is a learning project for the full path from a React screen to a database and back.

## How the App Works

React sends HTTP requests to FastAPI. FastAPI reads or changes data in PostgreSQL through SQLAlchemy. Supabase Auth signs users in and gives React an access token. React includes that token on protected requests; FastAPI checks it before using the user's identity.

```text
React --HTTP/JSON--> FastAPI --SQLAlchemy--> PostgreSQL (Supabase)
  |
  +---- sign in / token ----> Supabase Auth
  +---- token on protected requests ----> FastAPI
```

## Data

Supabase manages the `auth.users` table. The app owns three tables:

| Table | Fields and rules | Relationship |
| --- | --- | --- |
| `courses` | `id` integer primary key, `name` text, `credits` positive integer | One course can have many classes. |
| `classes` | `id` integer primary key, `course_id` foreign key, `class_code` unique text, `teacher` text, `capacity` non-negative integer, `registered` integer defaulting to zero and no greater than capacity, `tuition` integer, `schedule` text | Each class belongs to one course. |
| `registrations` | `id` UUID primary key, `user_id` UUID foreign key to `auth.users.id`, `class_id` foreign key, `created_at` timestamp; `(user_id, class_id)` is unique | Joins one Supabase user to one class. |

`registrations.user_id` refers to `auth.users.id`; the backend does not create or manage Supabase users. A registration's user ID comes from the verified access token, never from client-supplied data.

Important behavior:

- A user cannot register for the same class twice.
- A class cannot exceed its capacity.
- Dropping a class removes only the current user's registration.
- Class availability is shown as `registered / capacity`.

Database constraints and concurrent requests are covered in [Later Topics](docs/later-topics.md).

## API

An API endpoint is a URL that accepts a request and returns a status code and, usually, JSON. These are the MVP endpoints:

| Method and path | Sign-in required? | Result |
| --- | --- | --- |
| `GET /classes` | No | `200` with the class list, including course details. An empty database returns `[]`. |
| `GET /registrations/me` | Yes | `200` with the current user's registrations. |
| `POST /registrations` | Yes | Accepts `{ "class_id": 1 }`; creates a registration and returns `201`. |
| `DELETE /registrations/{class_id}` | Yes | Drops the current user's registration and returns `204`. |

Protected requests use:

```http
Authorization: Bearer <supabase-access-token>
```

Invalid or missing credentials return `401`. A class that does not exist returns `404`. A full class or duplicate registration returns `409`. Invalid request data returns `422`.

## User Experience

The first version is a single page with:

- A class catalog that is available while signed out.
- Sign-in and sign-out controls using Supabase Auth.
- A registration list visible only to the signed-in user.
- Register and drop actions with clear loading, empty, and error states.

Email sign-in is sufficient for the first pass. Google sign-in is an optional provider, not a requirement for completing the core flow.

## MVP Completion

- A signed-out visitor can browse classes.
- A user can sign in and out.
- FastAPI verifies the user's access token on protected routes.
- A signed-in user can register for and drop a class.
- Registrations persist in Supabase PostgreSQL and are associated with the correct `auth.users.id`.
- Duplicate registrations and registrations beyond class capacity are rejected.

## Out of Scope

Teacher/admin tools, course authoring, role-based access, payments, registration history, search, and pagination are not part of this MVP. See [the architecture guide](architecture.md) for how the main pieces fit together and [the learning roadmap](docs/todos.md) for the build order.