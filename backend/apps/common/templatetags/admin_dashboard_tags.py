"""Template tags for custom Django Admin operational dashboard."""

from django import template

from backend.apps.catalog.models import Product
from backend.apps.content.models import Review
from backend.apps.promotions.models import Promotion

register = template.Library()


@register.simple_tag
def get_operational_metrics() -> dict:
    """Fetch lightweight operational counts for the admin dashboard."""
    try:
        total_products = Product.objects.count()
        published_products = Product.objects.filter(is_published=True).count()
        out_of_stock = Product.objects.filter(
            is_published=True, availability_status="out_of_stock"
        ).count()
        active_promotions = Promotion.objects.filter(is_active=True).count()
        published_reviews = Review.objects.filter(is_published=True).count()

        return {
            "total_products": total_products,
            "published_products": published_products,
            "out_of_stock": out_of_stock,
            "active_promotions": active_promotions,
            "published_reviews": published_reviews,
        }
    except Exception:
        return {
            "total_products": 0,
            "published_products": 0,
            "out_of_stock": 0,
            "active_promotions": 0,
            "published_reviews": 0,
        }
