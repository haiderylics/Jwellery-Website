import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured

from backend.config.settings import development as dev_settings


def test_development_settings_defaults() -> None:
    """Verify development settings establish expected developer-friendly defaults."""
    assert dev_settings.DEBUG is True
    assert "backend.apps.catalog.apps.CatalogConfig" in dev_settings.INSTALLED_APPS
    assert "backend.apps.content.apps.ContentConfig" in dev_settings.INSTALLED_APPS
    assert "backend.apps.promotions.apps.PromotionsConfig" in dev_settings.INSTALLED_APPS
    assert "backend.apps.settings.apps.SettingsConfig" in dev_settings.INSTALLED_APPS
    assert "backend.apps.common.apps.CommonConfig" in dev_settings.INSTALLED_APPS
    assert dev_settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert dev_settings.X_FRAME_OPTIONS == "DENY"


def test_production_settings_fails_without_secret_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production settings fail to import if DJANGO_SECRET_KEY is missing."""
    monkeypatch.delenv("DJANGO_SECRET_KEY", raising=False)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    with pytest.raises(
        ImproperlyConfigured, match="DJANGO_SECRET_KEY environment variable is mandatory"
    ):
        importlib.reload(importlib.import_module("backend.config.settings.production"))


def test_production_settings_fails_with_insecure_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production settings fail if an insecure development key is provided."""
    monkeypatch.setenv("DJANGO_SECRET_KEY", "django-insecure-short-dev-key")
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    with pytest.raises(
        ImproperlyConfigured, match="DJANGO_SECRET_KEY must be at least 50 characters"
    ):
        importlib.reload(importlib.import_module("backend.config.settings.production"))


def test_production_settings_fails_without_allowed_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production settings fail if DJANGO_ALLOWED_HOSTS is empty."""
    valid_key = "a" * 55
    monkeypatch.setenv("DJANGO_SECRET_KEY", valid_key)
    monkeypatch.delenv("DJANGO_ALLOWED_HOSTS", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    with pytest.raises(
        ImproperlyConfigured, match="DJANGO_ALLOWED_HOSTS environment variable is mandatory"
    ):
        importlib.reload(importlib.import_module("backend.config.settings.production"))


def test_production_settings_fails_without_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production settings reject non-PostgreSQL database schemes."""
    valid_key = "a" * 55
    monkeypatch.setenv("DJANGO_SECRET_KEY", valid_key)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("DATABASE_URL", "mysql://user:pass@localhost:3306/db")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "test-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "test-key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "test-secret")

    with pytest.raises(ImproperlyConfigured, match="Production requires PostgreSQL"):
        importlib.reload(importlib.import_module("backend.config.settings.production"))


def test_production_settings_loads_with_valid_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify production settings load cleanly and apply security controls with valid config."""
    valid_key = "super-secure-cryptographically-random-production-key-55-chars-minimum"
    monkeypatch.setenv("DJANGO_SECRET_KEY", valid_key)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "example.com,api.example.com")
    monkeypatch.setenv("DJANGO_CSRF_TRUSTED_ORIGINS", "https://example.com")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dbuser:dbpass@localhost:5432/proddb")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "test-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "test-key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "test-secret")

    prod_settings = importlib.reload(importlib.import_module("backend.config.settings.production"))

    assert prod_settings.DEBUG is False
    assert prod_settings.ALLOWED_HOSTS == ["example.com", "api.example.com"]
    assert prod_settings.CSRF_TRUSTED_ORIGINS == ["https://example.com"]
    assert prod_settings.SECURE_SSL_REDIRECT is True
    assert prod_settings.SESSION_COOKIE_SECURE is True
    assert prod_settings.CSRF_COOKIE_SECURE is True
    assert prod_settings.SECURE_HSTS_SECONDS == 31536000
    assert prod_settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert prod_settings.DATABASES["default"]["NAME"] == "proddb"
    assert prod_settings.STATIC_URL == "/static/"
    assert (
        prod_settings.STORAGES["staticfiles"]["BACKEND"]
        == "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )
    security_middleware = "django.middleware.security.SecurityMiddleware"
    whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"
    assert prod_settings.MIDDLEWARE.index(whitenoise_middleware) == (
        prod_settings.MIDDLEWARE.index(security_middleware) + 1
    )
    assert prod_settings.STORAGES["default"]["BACKEND"] == (
        "backend.apps.common.cloudinary_storage.CloudinaryMediaStorage"
    )


def test_production_settings_require_cloudinary_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DJANGO_SECRET_KEY", "a" * 55)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    with pytest.raises(ImproperlyConfigured, match="CLOUDINARY_CLOUD_NAME"):
        importlib.reload(importlib.import_module("backend.config.settings.production"))
