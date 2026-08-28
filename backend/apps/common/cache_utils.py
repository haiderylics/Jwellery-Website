"""Bounded cache keys and invalidation helpers for public storefront endpoints."""

from collections.abc import Iterable
from datetime import datetime
from math import ceil

from django.core.cache import cache
from django.utils import timezone

CACHE_KEY_HOMEPAGE = "storefront:homepage:v1"
CACHE_KEY_CATEGORIES = "storefront:categories:v1"
CACHE_KEY_ATTRIBUTES = "storefront:attributes:v1"
CACHE_KEY_SITE_SETTINGS = "storefront:site_settings:v1"
CACHE_KEY_DELIVERY_SETTINGS = "storefront:delivery_settings:v1"
CACHE_KEY_PROMOTIONS_ACTIVE = "storefront:promotions_active:v1"
CACHE_KEY_POPUPS_ACTIVE = "storefront:popups_active:v1"
CACHE_KEY_REVIEWS = "storefront:reviews:v1"
CACHE_KEY_GALLERY = "storefront:gallery:v1"
CACHE_KEY_ABOUT = "storefront:about:v1"
CACHE_KEY_ADMIN_METRICS = "admin:dashboard_metrics:v1"
CACHE_KEY_ADMIN_BRANDING = "admin:branding:v1"
CACHE_KEY_PRODUCT_NAMESPACE = "storefront:namespace:product"

STOREFRONT_CACHE_KEYS = [
    CACHE_KEY_HOMEPAGE,
    CACHE_KEY_CATEGORIES,
    CACHE_KEY_ATTRIBUTES,
    CACHE_KEY_SITE_SETTINGS,
    CACHE_KEY_DELIVERY_SETTINGS,
    CACHE_KEY_PROMOTIONS_ACTIVE,
    CACHE_KEY_POPUPS_ACTIVE,
    CACHE_KEY_REVIEWS,
    CACHE_KEY_GALLERY,
    CACHE_KEY_ABOUT,
]


def product_detail_cache_key(slug: str) -> str:
    """Return a slug-specific key within the current product cache namespace."""
    namespace_version = cache.get_or_set(CACHE_KEY_PRODUCT_NAMESPACE, 1, timeout=None)
    return f"storefront:product:{namespace_version}:{slug.strip().lower()}"


def invalidate_product_cache() -> None:
    """Rotate only the product-detail namespace, leaving unrelated caches intact."""
    try:
        cache.incr(CACHE_KEY_PRODUCT_NAMESPACE)
    except ValueError:
        cache.set(CACHE_KEY_PRODUCT_NAMESPACE, 2, timeout=None)


def bounded_schedule_timeout(
    configured_timeout: int,
    boundaries: Iterable[datetime | None],
    *,
    now: datetime | None = None,
) -> int:
    """Never cache scheduled content beyond its next start/end transition."""
    current_time = now or timezone.now()
    future_seconds = [
        (boundary - current_time).total_seconds()
        for boundary in boundaries
        if boundary is not None and boundary > current_time
    ]
    if not future_seconds:
        return max(1, configured_timeout)
    return max(1, min(configured_timeout, ceil(min(future_seconds))))


def invalidate_storefront_cache(keys: list[str] | None = None) -> None:
    """Invalidate specified cache keys or all storefront aggregated keys."""
    target_keys = keys or STOREFRONT_CACHE_KEYS
    cache.delete_many(target_keys)
