"""Template tags for custom Django Admin operational dashboard."""

from django import template
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q

from backend.apps.catalog.models import Product
from backend.apps.common.cache_utils import CACHE_KEY_ADMIN_BRANDING, CACHE_KEY_ADMIN_METRICS
from backend.apps.content.models import Review
from backend.apps.promotions.models import Promotion
from backend.apps.settings.models import SiteSettings

register = template.Library()


@register.simple_tag
def get_site_branding() -> dict:
    """Fetch the active configured brand name, monogram, and tagline for Django Admin templates."""
    cached_branding = cache.get(CACHE_KEY_ADMIN_BRANDING)
    if cached_branding is not None:
        return cached_branding
    try:
        site_settings = SiteSettings.objects.first()
        brand_name = (
            site_settings.brand_name
            if (site_settings and site_settings.brand_name)
            else "AHS JEWELLERS"
        )
        monogram = brand_name.strip()[:1].upper() if brand_name else "A"
        tagline = (
            site_settings.tagline
            if (site_settings and site_settings.tagline)
            else "Operations & Merchandising Console"
        )
        branding = {
            "brand_name": brand_name,
            "monogram": monogram,
            "tagline": tagline,
        }
        cache.set(
            CACHE_KEY_ADMIN_BRANDING,
            branding,
            timeout=getattr(settings, "ADMIN_DASHBOARD_CACHE_TIMEOUT", 60),
        )
        return branding
    except Exception:
        return {
            "brand_name": "AHS JEWELLERS",
            "monogram": "A",
            "tagline": "Operations & Merchandising Console",
        }


@register.simple_tag
def get_operational_metrics() -> dict:
    """Fetch lightweight operational counts for the admin dashboard."""
    cached_metrics = cache.get(CACHE_KEY_ADMIN_METRICS)
    if cached_metrics is not None:
        return cached_metrics
    try:
        product_counts = Product.objects.aggregate(
            total_products=Count("id"),
            published_products=Count("id", filter=Q(is_published=True)),
            out_of_stock=Count(
                "id",
                filter=Q(is_published=True, availability_status="out_of_stock"),
            ),
        )
        metrics = {
            **product_counts,
            "active_promotions": Promotion.objects.active_now().count(),
            "published_reviews": Review.objects.filter(is_published=True).count(),
        }
        cache.set(
            CACHE_KEY_ADMIN_METRICS,
            metrics,
            timeout=getattr(settings, "ADMIN_DASHBOARD_CACHE_TIMEOUT", 60),
        )
        return metrics
    except Exception:
        return {
            "total_products": 0,
            "published_products": 0,
            "out_of_stock": 0,
            "active_promotions": 0,
            "published_reviews": 0,
        }
