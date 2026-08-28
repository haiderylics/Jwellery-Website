"""Regression tests for bounded public caching and scoped invalidation."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.cache import cache
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from backend.apps.catalog.models import Category, Product, ProductVariant
from backend.apps.common.cache_utils import (
    CACHE_KEY_SITE_SETTINGS,
    bounded_schedule_timeout,
    product_detail_cache_key,
)
from backend.apps.promotions.models import Promotion
from backend.apps.settings.models import SiteSettings


@pytest.mark.django_db
def test_product_detail_second_request_is_database_free(client: Client) -> None:
    category = Category.objects.create(name="Cached Rings", slug="cached-rings")
    product = Product.objects.create(
        name="Cached Ring",
        slug="cached-ring",
        category=category,
        base_price=Decimal("25000"),
        is_published=True,
    )
    url = f"/api/v1/products/{product.slug}/"

    with CaptureQueriesContext(connection) as first_queries:
        first = client.get(url)
    with CaptureQueriesContext(connection) as cached_queries:
        second = client.get(url)

    assert first.status_code == second.status_code == 200
    assert len(first_queries) > 0
    assert len(cached_queries) == 0
    assert second.headers["Cache-Control"].startswith("public")
    assert second.headers["ETag"]


@pytest.mark.django_db
def test_site_settings_second_request_is_database_free(client: Client) -> None:
    SiteSettings.get_solo()
    with CaptureQueriesContext(connection) as first_queries:
        first = client.get("/api/v1/site-settings/")
    with CaptureQueriesContext(connection) as cached_queries:
        second = client.get("/api/v1/site-settings/")

    assert first.status_code == second.status_code == 200
    assert len(first_queries) > 0
    assert len(cached_queries) == 0


@pytest.mark.django_db
def test_product_detail_supports_conditional_get(client: Client) -> None:
    category = Category.objects.create(name="ETag", slug="etag")
    product = Product.objects.create(
        name="ETag Ring",
        slug="etag-ring",
        category=category,
        base_price=Decimal("5000"),
        is_published=True,
    )
    url = f"/api/v1/products/{product.slug}/"
    first = client.get(url)
    conditional = client.get(url, HTTP_IF_NONE_MATCH=first.headers["ETag"])
    assert conditional.status_code == 304
    assert conditional.content == b""


@pytest.mark.django_db(transaction=True)
def test_product_variant_save_rotates_product_detail_namespace() -> None:
    category = Category.objects.create(name="Variants", slug="variants")
    product = Product.objects.create(
        name="Variant Ring",
        slug="variant-ring",
        category=category,
        base_price=Decimal("6000"),
        is_published=True,
    )
    old_key = product_detail_cache_key(product.slug)
    cache.set(old_key, {"stock_status": "in_stock"}, timeout=60)

    ProductVariant.objects.create(product=product, name="Small", stock_quantity=0)

    new_key = product_detail_cache_key(product.slug)
    assert new_key != old_key
    assert cache.get(new_key) is None
    assert cache.get(old_key) is not None  # harmless until TTL/culling


@pytest.mark.django_db(transaction=True)
def test_site_settings_save_invalidates_only_public_site_payload() -> None:
    site = SiteSettings.get_solo()
    cache.set(CACHE_KEY_SITE_SETTINGS, {"brand_name": "Old"}, timeout=300)
    site.brand_name = "Fresh Brand"
    site.save()
    assert cache.get(CACHE_KEY_SITE_SETTINGS) is None


def test_scheduled_cache_timeout_stops_at_next_boundary() -> None:
    now = timezone.now()
    assert bounded_schedule_timeout(300, [now + timedelta(seconds=12.1)], now=now) == 13
    assert bounded_schedule_timeout(10, [now + timedelta(minutes=2)], now=now) == 10
    assert bounded_schedule_timeout(300, [now - timedelta(seconds=1)], now=now) == 300


@pytest.mark.django_db
def test_scheduled_promotion_cache_hit_is_database_free_and_boundary_bounded(
    client: Client,
) -> None:
    now = timezone.now()
    Promotion.objects.create(
        title="Brief Offer",
        is_active=True,
        start_datetime=now - timedelta(minutes=1),
        end_datetime=now + timedelta(seconds=12),
    )
    url = "/api/v1/promotions/active/"
    with CaptureQueriesContext(connection) as first_queries:
        first = client.get(url)
    with CaptureQueriesContext(connection) as cached_queries:
        second = client.get(url)

    assert first.status_code == second.status_code == 200
    assert len(first_queries) > 0
    assert len(cached_queries) == 0
    max_age = int(second.headers["Cache-Control"].split("max-age=")[1].split(",")[0])
    assert 0 <= max_age <= 12
