"""Django production settings for Jewellery Website.

Applies strict security controls, requires explicit environment variables,
and enforces zero-fallback security invariants.
"""

import os
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

# ------------------------------------------------------------------------------
# 1. Debug Mode
# ------------------------------------------------------------------------------
DEBUG = False

# ------------------------------------------------------------------------------
# 2. Secret Key Validation
# ------------------------------------------------------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is mandatory in production.")

if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be at least 50 characters long in production."
    )

if "insecure" in SECRET_KEY.lower() or "dev-only" in SECRET_KEY.lower():
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY contains an insecure development string. A cryptographically "
        "random key is required in production."
    )

# ------------------------------------------------------------------------------
# 3. Allowed Hosts & CSRF Trusted Origins
# ------------------------------------------------------------------------------
raw_allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in raw_allowed_hosts.split(",") if h.strip()]

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS environment variable is mandatory in production."
    )

raw_csrf_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in raw_csrf_origins.split(",") if o.strip()]

raw_cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in raw_cors_origins.split(",") if o.strip()]

# ------------------------------------------------------------------------------
# 4. HTTPS & Cookie Security
# ------------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Browser Security Headers & Policies
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# Content Security Policy (CSP) Baseline
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_MEDIA_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'",)

# Reverse Proxy SSL Header Trust Assumption:
# Only enable if behind a trusted reverse proxy (e.g. Nginx, Cloudflare, AWS ALB)
# that strips incoming X-Forwarded-Proto headers from client requests.
if os.environ.get("DJANGO_SECURE_PROXY_SSL_HEADER", "").lower() in ("true", "1"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ------------------------------------------------------------------------------
# 5. Database Configuration (PostgreSQL Authoritative in Production)
# ------------------------------------------------------------------------------
database_url = os.environ.get("DATABASE_URL")

if database_url:
    parsed_db = urlparse(database_url)
    if parsed_db.scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured(
            f"Unsupported database scheme '{parsed_db.scheme}' in DATABASE_URL. "
            "Production requires PostgreSQL."
        )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed_db.path.lstrip("/"),
            "USER": parsed_db.username or "",
            "PASSWORD": parsed_db.password or "",
            "HOST": parsed_db.hostname or "",
            "PORT": str(parsed_db.port or "5432"),
            "CONN_MAX_AGE": 600,
            "CONN_HEALTH_CHECKS": True,
        }
    }
else:
    # Check explicit DB environment variables
    pg_db = os.environ.get("POSTGRES_DB")
    pg_user = os.environ.get("POSTGRES_USER")
    pg_password = os.environ.get("POSTGRES_PASSWORD")
    pg_host = os.environ.get("POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")

    if not pg_db or not pg_user or not pg_password:
        raise ImproperlyConfigured(
            "Production database requires either DATABASE_URL or POSTGRES_DB, "
            "POSTGRES_USER, and POSTGRES_PASSWORD environment variables."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": pg_db,
            "USER": pg_user,
            "PASSWORD": pg_password,
            "HOST": pg_host,
            "PORT": pg_port,
            "CONN_MAX_AGE": 600,
            "CONN_HEALTH_CHECKS": True,
        }
    }
