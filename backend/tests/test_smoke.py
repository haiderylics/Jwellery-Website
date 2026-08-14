"""Phase 1 smoke tests validating Django system integrity and baseline endpoints."""

import pytest
from django.core.management import call_command
from django.test import Client


@pytest.mark.django_db
def test_django_system_checks_pass() -> None:
    """Verify that Django's internal system checks pass without errors."""
    call_command("check")


def test_health_liveness_endpoint(client: Client) -> None:
    """Verify that /health/live/ returns HTTP 200 with deterministic JSON payload."""
    response = client.get("/health/live/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["Content-Type"] == "application/json"


def test_admin_endpoint_accessible(client: Client) -> None:
    """Verify that Django Admin route is mounted and returns login page or redirect."""
    response = client.get("/admin/")
    # Admin root redirects unauthenticated users to /admin/login/
    assert response.status_code in (200, 302)
