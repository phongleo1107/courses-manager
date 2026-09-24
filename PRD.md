# PRD — Course Registration App (with Supabase Auth)

## 1. Objective

Build a focused full-stack course registration web application to learn and practice:

**React.js (Supabase Client) → FastAPI → SQLAlchemy → PostgreSQL (Supabase)**

### Core Goal
Understand end-to-end data flow with managed authentication:
1. User logs in via Supabase Auth on the frontend.
2. React sends requests to FastAPI containing the Supabase JWT token.
3. FastAPI verifies the user and executes CRUD operations on PostgreSQL via SQLAlchemy.

```text
React (Supabase Client)
  │ (Auth / OAuth)
  ▼
Supabase Auth  ──[ Returns JWT ]──►  React
                                       │
                                       │ HTTP + Authorization Bearer JWT
                                       ▼
                                    FastAPI (Decodes & Verifies JWT)
                                       │
                                       │ SQLAlchemy ORM
                                       ▼
                                    PostgreSQL (Supabase Database)
```

---

## 2. Tech Stack

* **Frontend:** React.js, `@supabase/supabase-js`, Fetch API / Axios.
* **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, PyJWT.
* **Database & Auth:** Supabase (PostgreSQL + Built-in Auth).

---

## 3. Scope & Database Schema

The app consists of **1 main page** (Course Catalog + My Registered Classes).

### Supabase Database Schema

```text
auth.users (Managed automatically by Supabase)
  │
  │ 1
  │
  │ *
registrations (Junction Table)
  │ *
  │
  │ 1
classes
  │ *
  │
  │ 1
courses
```

#### 1. `courses`
* `id` (serial, PK)
* `name` (text)
* `credits` (integer)

#### 2. `classes`
* `id` (serial, PK)
* `course_id` (integer, FK -> `courses.id`)
* `class_code` (text)
* `teacher` (text)
* `capacity` (integer)
* `registered` (integer, default 0)
* `tuition` (integer)
* `schedule` (text)

#### 3. `registrations`
* `id` (uuid or serial, PK)
* `user_id` (uuid, FK -> `auth.users.id`)
* `class_id` (integer, FK -> `classes.id`)
* `created_at` (timestamp)

---

## 4. API Endpoints (FastAPI)

FastAPI verifies the Supabase Bearer Token via a dependency injection layer on protected routes.

| Method | Endpoint | Auth Required? | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/classes` | No | List all available classes (with course info). |
| `GET` | `/registrations/me` | **Yes** | Fetch classes registered by the logged-in user. |
| `POST` | `/registrations` | **Yes** | Register current user for a class (Payload: `{"class_id": 1}`). |
| `DELETE` | `/registrations/{class_id}` | **Yes** | Unregister current user from a class. |

### Backend Auth Middleware / Dependency Flow
1. React includes `Authorization: Bearer <supabase_access_token>` in HTTP headers.
2. FastAPI dependency (`get_current_user`) extracts the token and verifies it against your Supabase JWT secret.
3. FastAPI extracts `user_id` (sub) from the token payload and uses it for database operations.

---

## 5. UI Architecture

A single dashboard page rendering components conditionally based on auth state.

```text
App
├── Navbar (Login / Logout / User Status via Supabase UI or SDK)
├── ClassList (Renders available classes & handles "Register" click)
└── MyRegistrations (Renders user's enrolled classes & handles "Drop" click)
```

---

## 6. Minimal Implementation Flow

### Step 1: User Actions in React
1. User clicks **"Sign in with Google / Email"** → Auth managed by Supabase JS SDK.
2. Supabase returns session data and an `access_token`.

### Step 2: Registering for a Class
1. User clicks **"Register"** next to a class.
2. React makes a request:
   ```http
   POST /registrations
   Authorization: Bearer <SUPABASE_JWT_TOKEN>
   Content-Type: application/json

   { "class_id": 4 }
   ```

### Step 3: FastAPI & Database Processing
1. FastAPI verifies token and gets `user_id`.
2. Checks if `class_id` exists and `registered < capacity`.
3. Inserts row into `registrations` (`user_id`, `class_id`).
4. Increments `registered` count on `classes` table.
5. Commits transaction and returns `201 Created`.

---

## 7. Definition of Done

* [ ] Supabase Auth configured (Email or OAuth).
* [ ] React app handles login/logout states cleanly using the Supabase client.
* [ ] FastAPI backend verifies incoming Supabase JWT tokens.
* [ ] Unauthenticated users can view available classes.
* [ ] Authenticated users can register/unregister for classes.
* [ ] Registrations persist correctly in Supabase PostgreSQL tied to the specific user's `auth.users.id`.