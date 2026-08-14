"""Django development settings for Jewellery Website.

Suitable ONLY for local development. Never use in production.
"""

import os

from .base import *  # noqa: F403
from .base import BASE_DIR

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-not-for-production-key-jewellery-2026-phase1",
)

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Database: SQLite for zero-configuration local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CSRF Trusted Origins for local Vite frontend dev server
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CORS configuration for frontend Vite development server
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Development Email Backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
