"""Measured query-count regression boundaries for owner admin performance."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from backend.apps.catalog.models import Category, Product
from backend.apps.settings.models import SiteSettings


@pytest.mark.django_db
def test_admin_query_probe() -> None:
    user = get_user_model().objects.create_superuser(
        username="query-probe", email="probe@example.test", password="ProbePassword123!"
    )
    category = Category.objects.create(name="Probe", slug="probe")
    product = Product.objects.create(
        name="Probe Piece",
        slug="probe-piece",
        category=category,
        base_price=Decimal("1000.00"),
        is_published=True,
    )
    SiteSettings.get_solo()
    client = Client()
    client.force_login(user)

    results: dict[str, int] = {}
    for label, url in (
        ("dashboard_cold", "/admin/"),
        ("dashboard_cached", "/admin/"),
        ("product_changelist", "/admin/catalog/product/"),
        ("product_change", f"/admin/catalog/product/{product.pk}/change/"),
    ):
        with CaptureQueriesContext(connection) as captured:
            response = client.get(url)
            assert response.status_code == 200
        results[label] = len(captured)

    public_client = Client()
    for label, url in (
        ("product_detail_cold", f"/api/v1/products/{product.slug}/"),
        ("product_detail_cached", f"/api/v1/products/{product.slug}/"),
        ("site_settings_cold", "/api/v1/site-settings/"),
        ("site_settings_cached", "/api/v1/site-settings/"),
    ):
        with CaptureQueriesContext(connection) as captured:
            response = public_client.get(url)
            assert response.status_code == 200
        results[label] = len(captured)

    print(f"QUERY_PROBE={results}")
    assert results["dashboard_cold"] <= 12
    assert results["dashboard_cached"] <= 8
    assert results["product_changelist"] <= 10
    assert results["product_change"] <= 13
    assert 0 < results["product_detail_cold"] <= 5
    assert results["product_detail_cached"] == 0
    assert 0 < results["site_settings_cold"] <= 2
    assert results["site_settings_cached"] == 0
