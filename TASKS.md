# Course Registration MVP - Task Checklist

## Phase 0: Project Setup & Foundations
- [x] **Backend:** Initialize FastAPI project structure (e.g., `main.py`, `database.py`, `models.py`, `schemas.py`).
- [x] **Database:** Set up a local PostgreSQL instance (or Supabase DB).
- [x] **Backend:** Install dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary` or `asyncpg`).
- [x] **Backend:** Set up SQLAlchemy engine and SessionLocal in `database.py`.
- [x] **Frontend:** Initialize React app using Vite (`npm create vite@latest client -- --template react`).
- [x] **Frontend:** Install basic dependencies (`axios` or `fetch` is built-in, `react-router-dom` if needed later).

## Phase 1: The "Read-Only" Slice (Courses)
*Goal: Get data from Postgres to the React UI using SQLAlchemy.*

- [ ] **Database:** Define `Course` SQLAlchemy model in `models.py` (id, name, credits). 
- [ ] **Database:** Create tables in Postgres using SQLAlchemy `Base.metadata.create_all()`.
- [ ] **Database:** Manually insert 3-4 dummy courses (using a Python script or pgAdmin).
- [ ] **Backend:** Define Pydantic schema for `Course` in `schemas.py`.
- [ ] **Backend:** Create `GET /courses` endpoint to fetch all courses.
- [ ] **Frontend:** Create a simple `CourseList` component to fetch and display courses.

## Phase 2: The "Teacher" Slice (Create Classes)
*Goal: Implement the foreign key relationship and a POST request.*

- [ ] **Database:** Define `Class` SQLAlchemy model in `models.py` (id, course_id, class_code, teacher, capacity, registered, tuition, schedule).
- [ ] **Database:** Ensure `course_id` is set up as a ForeignKey linking to `courses.id`.
- [ ] **Backend:** Define Pydantic schemas for creating and reading a `Class`.
- [ ] **Backend:** Create `POST /classes` endpoint (accepts course_id, teacher, capacity, etc.).
- [ ] **Backend:** Create `GET /classes` endpoint.
- [ ] **Frontend:** Create a "Teacher Dashboard" page/view.
- [ ] **Frontend:** Build a form to create a class (include a dropdown populated with courses fetched from Phase 1).
- [ ] **Frontend:** Display the list of created classes.

## Phase 3: The "Student" Slice (Registration Logic)
*Goal: Implement backend business logic and state updates.*

- [ ] **Backend:** Create `POST /classes/{id}/register` endpoint.
- [ ] **Backend:** Add logic to check if `registered < capacity`.
- [ ] **Backend:** Add logic to increment `registered` by 1 and save to DB.
- [ ] **Backend:** Return a 400 error if the class is full.
- [ ] **Frontend:** Add a "Register" button next to classes on the student view.
- [ ] **Frontend:** Wire up the button to call the register endpoint.
- [ ] **Frontend:** Update the UI to reflect the new `registered` count, and handle/display "Class Full" errors.

## Phase 4: Authentication (Supabase)
*Goal: Secure routes and link users to actions.*

- [ ] **Supabase:** Set up Supabase Auth (Email/Password).
- [ ] **Supabase:** Create a `profiles` table linking to Auth User ID, with a `role` column ('teacher' or 'student').
- [ ] **Backend:** Install Supabase Python client.
- [ ] **Backend:** Create a FastAPI dependency to verify Supabase JWT tokens from request headers.
- [ ] **Backend:** Protect `POST /classes` (Teacher only).
- [ ] **Backend:** Protect `POST /classes/{id}/register` (Student only).
- [ ] **Frontend:** Install `@supabase/supabase-js`.
- [ ] **Frontend:** Create Login/Register pages.
- [ ] **Frontend:** Store session and attach JWT to API requests.
- [ ] **Frontend:** Conditionally render UI based on user role (hide teacher forms from students, etc.).

## Technical Notes / Reminders
- **MVP Simplification:** Storing `registered` as an integer on the Class model (rather than a separate registrations table) is intentional for simplicity. 
- **Data Types:** Keep `credits` as an Integer in the SQLAlchemy model, even if the ERD says string.
- **Async vs Sync:** Stick to standard synchronous SQLAlchemy (`Session`) to reduce complexity, rather than jumping straight into Async SQLAlchemy.