## Online Assignment Management System (Flask)

This project is a role-based **online assignment management system** built with **Flask**.  
It supports three main roles:
- **Admin** – manages users, roles, teachers, students, and assignments.
- **Teacher** – creates classes and assignments, views and grades submissions.
- **Student** – joins classes, views assignments, and submits work.

The app uses **Flask blueprints**, **SQLAlchemy**, and **Flask-Login** with a clean separation between routes, models, templates, and utility helpers.

---

## Features

- **Authentication & Authorization**
  - User registration and login with hashed passwords.
  - Role-based access: `admin`, `teacher`, `student`.
  - Admin-only routes protected by a custom `@admin_required` decorator.
  - Admin whitelist (`ADMIN_WHITELIST`) to control who can become an admin.

- **User & Role Management (Admin)**
  - View dashboard statistics for users, teachers, students, and assignments.
  - Create, edit, and delete users.
  - Assign and change user roles (`admin`, `teacher`, `student`).
  - Manage teacher and student profiles.
  - View activity logs (registrations, assignments, grading events).

- **Teacher Workflows**
  - Manage classes and enrolled students.
  - Create and manage assignments.
  - View submissions and enter grades.

- **Student Workflows**
  - Join classes.
  - View assigned work and due dates.
  - Upload assignment submissions.
  - View grades and feedback.

- **File Uploads**
  - Upload folders for assignments, submissions, and avatars.
  - Basic validation of allowed file extensions and max file size (16MB default).

- **Error Handling & Logging**
  - Custom `403`, `404`, and `500` error pages.
  - Rotating file logs under `logs/` when not running in debug mode.

---

## Tech Stack

- **Backend**: Flask, Flask-Login, Flask-WTF, Flask-SQLAlchemy, (optional) Flask-Migrate
- **Database**: SQLite by default (can be switched using `DATABASE_URL`)
- **Templates**: Jinja2 (`templates/`)
- **Frontend**: Bootstrap (CSS/JS in `static/`)
- **Testing**: Basic tests under `tests/`

---

## Project Structure

Key directories and files:

- `app.py` – application factory (`create_app()`), extension initialization, database setup, error handlers, and root `/` route.
- `config.py` – configuration class (`Config`) for database URL, uploads, sessions, CSRF, and `ADMIN_WHITELIST`.
- `extensions.py` – instances of `db`, `login_manager`, and `csrf`.
- `models/`
  - `user.py` – `User` model (`users` table) with `role` and helper methods `is_admin()`, `is_teacher()`, `is_student()`.
  - `student.py`, `teacher.py`, `class_model.py`, `assignment.py`, `submission.py` – domain models for classes, assignments, submissions, and profiles.
  - `models.py` – imports all models so they are registered with SQLAlchemy.
- `routes/`
  - `auth.py` – registration, login, logout, and debug route to list users.
  - `admin.py` – all admin-only routes (dashboard, manage users/roles/teachers/students/assignments, activity log).
  - `teacher.py` – teacher dashboard and related views.
  - `student.py` – student dashboard and related views.
- `templates/`
  - `base.html`, `home.html`, `login.html`, `register.html`.
  - `admin/`, `teacher/`, `student/` – role-specific pages.
  - `errors/` – `403.html`, `404.html`, `500.html`.
- `static/`
  - `css/`, `js/` – frontend assets.
  - `uploads/` – runtime upload directories for assignments, submissions, and avatars.
- `requirements.txt` – Python dependencies.

---

## Data Model & Roles

At a high level, the ERD consists of:

- **`users`**
  - Common account data: `id`, `username`, `email`, `password`, `role`, `status`, `created_at`, `last_login`.
  - `role` can be `admin`, `teacher`, or `student`.
  - One-to-one relationships to:
    - `students` (via `student_profile`).
    - `teachers` (via `teacher_profile`).

- **`teachers`**
  - Detailed teacher profile (first name, last name, department, subject, avatar, etc.).
  - 1:N with `classes` and `assignments`.

- **`students`**
  - Detailed student profile (first name, last name, major, year, section, etc.).
  - M:N with `classes` through a join table (e.g. `class_student`).

- **`classes`**
  - Course/class information, references a `teacher`.
  - Related to `assignments` and enrolled `students`.

- **`assignments`**
  - Belong to a class and typically a teacher.
  - Have title, description, due date, status, and files.

- **`submissions`**
  - Link a `student` to an `assignment` with submitted file, grade, feedback, timestamps.

**Admins** do **not** have a separate table. An admin is simply a `User` where `role = 'admin'`.

---

## Getting Started (from GitHub)

### 1. Clone the Repository

```bash
git clone <your-repo-url>.git
cd <your-repo-folder>
```

Replace `<your-repo-url>` and `<your-repo-folder>` with your actual GitHub values.

### 2. Create & Activate a Virtual Environment (Recommended)

On Windows (PowerShell):

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

This project reads configuration from environment variables with sensible defaults defined in `config.py`.

Common settings:

- **`SECRET_KEY`**
  - Used for session security and CSRF.
  - Set in your shell or `.env` file:
  - Example:

    ```bash
    set SECRET_KEY="change-this-in-production"
    ```

- **`DATABASE_URL`**
  - Optional. If not set, defaults to a SQLite database at `instance/database.db`.
  - To use another database, set:

    ```bash
    set DATABASE_URL="sqlite:///instance/database.db"
    ```

    or a different database URL supported by SQLAlchemy.

- **`ADMIN_WHITELIST`**
  - Controls which accounts can register as admin or be granted admin role.
  - Comma-separated list of emails/usernames, for example:

    ```bash
    set ADMIN_WHITELIST="admin@example.com,superadmin@example.com,admin_user"
    ```

  - The list is normalized (lowercased, trimmed) in `Config`.

- **`FLASK_DEBUG`**
  - Set to `"true"` to enable debug mode in development:

    ```bash
    set FLASK_DEBUG=true
    ```

- **`PORT`**
  - Override the default port `5000` when running the app.

You can also create a `.env` file and use `python-dotenv` (already supported in `config.py`) so the variables load automatically.

---

## Initial Database Setup

On first run, the app will:

- Import models from `models/models.py`.
- Create the SQLite database (if it does not exist) at `instance/database.db`.
- Call `db.create_all()` to create all tables.

If you ever need to **force-recreate** the database schema (for development only), you can set:

```bash
set RECREATE_DB=true
python app.py
```

This will drop all existing tables and recreate them.

---

## Running the Application Locally

With your virtual environment activated and dependencies installed:

```bash
python app.py
```

By default:

- The app runs on `http://127.0.0.1:5000/`.
- The home page is served at `/`.
- The login and register pages are at `/login` and `/register`.

If you set `FLASK_DEBUG=true`, the server will run in debug mode.

---

## User Roles & Access

- **Admin**
  - Can access routes under `/admin/...`.
  - Has access to dashboards, user/role management, teachers, students, assignments, and system settings.
  - All admin routes use the `@admin_required` decorator.
  - Only users in the `ADMIN_WHITELIST` can register or be upgraded to `admin`.

- **Teacher**
  - Can access teacher-specific dashboard and menus (e.g., manage assignments and classes).
  - Typically redirected to `teacher_bp.dashboard` after login.

- **Student**
  - Can access student-specific pages (classes, assignments, grades, profile).
  - Typically redirected to `student_bp.dashboard` after login.

Role-based redirects are configured in `routes/auth.py` after login.

---

## File Uploads

File uploads are configured in both `app.py` and `config.py`:

- `UPLOAD_FOLDER` and `SUBMISSION_FOLDER` define where assignment and submission files are stored.
- Allowed extensions are controlled via `ALLOWED_EXTENSIONS`.
- Maximum file size is limited by `MAX_CONTENT_LENGTH` (16MB by default).
- Upload folders (`static/uploads/...`) are created automatically on app startup if they do not exist.

---

## Testing

There are starter tests located in the `tests/` directory:

- `tests/test_auth.py` – basic tests around authentication.
- `tests/test_login.py` – login-specific tests.

To run tests (from the project root with the virtual environment activated):

```bash
python -m pytest
```

If `pytest` is not installed, you can add it and update `requirements.txt` as needed.

---

## Logging

When the app is **not** in debug mode:

- A rotating log file is created under the `logs/` directory (`logs/app.log` and rotated backups).
- Logs include timestamp, log level, message, and origin file/line.

Use these logs to debug errors in production-like environments.

---

## Deployment Notes

- Use a production-ready WSGI server (e.g., Gunicorn or uWSGI) and a reverse proxy (e.g., Nginx) in real deployments.
- Set:
  - `SECRET_KEY` to a strong, unique value.
  - `SESSION_COOKIE_SECURE = True` for HTTPS.
  - A proper `DATABASE_URL` for your production database.
- Configure file system permissions for the `logs/` and `static/uploads/` directories so the app can write to them.

---

## Troubleshooting

- **Database schema errors or missing columns**
  - Set `RECREATE_DB=true` and re-run the app to drop and recreate tables (development only).

- **Cannot log in as admin**
  - Make sure the email/username is listed (lowercased) in `ADMIN_WHITELIST`.
  - Confirm the user row in the `users` table has `role = 'admin'`.

- **Uploads failing**
  - Check file size and extension against `MAX_CONTENT_LENGTH` and `ALLOWED_EXTENSIONS`.
  - Ensure `static/uploads/` subfolders exist and are writable.

---

## License

Add your chosen license here (for example, MIT, GPL, or “All rights reserved”). If you are submitting this for a university assignment, include any required attribution or academic integrity notes.


