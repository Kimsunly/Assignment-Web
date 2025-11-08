# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key for sessions, CSRF protection, etc.
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")

    # Database (SQLite for local dev)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

    # For future flexibility
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
