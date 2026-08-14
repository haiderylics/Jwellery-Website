"""Cache utility keys and invalidation helpers for public storefront endpoints."""

from django.core.cache import cache

CACHE_KEY_HOMEPAGE = "storefront:homepage:v1"
CACHE_KEY_CATEGORIES = "storefront:categories:v1"
CACHE_KEY_ATTRIBUTES = "storefront:attributes:v1"
CACHE_KEY_SITE_SETTINGS = "storefront:site_settings:v1"
CACHE_KEY_DELIVERY_SETTINGS = "storefront:delivery_settings:v1"
CACHE_KEY_PROMOTIONS_ACTIVE = "storefront:promotions_active:v1"
CACHE_KEY_POPUPS_ACTIVE = "storefront:popups_active:v1"
CACHE_KEY_REVIEWS = "storefront:reviews:v1"
CACHE_KEY_GALLERY = "storefront:gallery:v1"

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
]


def invalidate_storefront_cache(keys: list[str] | None = None) -> None:
    """Invalidate specified cache keys or all storefront aggregated keys."""
    target_keys = keys or STOREFRONT_CACHE_KEYS
    cache.delete_many(target_keys)
