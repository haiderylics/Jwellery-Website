"""Aggregated storefront homepage view."""

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.catalog.api.serializers import CategorySerializer, ProductListSerializer
from backend.apps.catalog.models import Category, Product
from backend.apps.common.api.cache import (
    public_response,
    schedule_cache_timeout,
    scheduled_cache_entry,
    unpack_scheduled_cache_entry,
)
from backend.apps.common.cache_utils import CACHE_KEY_HOMEPAGE
from backend.apps.content.api.serializers import (
    AboutSectionSerializer,
    GalleryItemSerializer,
    ReviewSerializer,
)
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.api.serializers import PopupSerializer, PromotionSerializer
from backend.apps.promotions.models import Popup, Promotion
from backend.apps.settings.api.serializers import (
    DeliverySettingsPublicSerializer,
    SiteSettingsPublicSerializer,
)
from backend.apps.settings.models import DeliverySettings, SiteSettings


class StorefrontHomeView(APIView):
    """Public aggregated homepage endpoint.

    Consolidates initial storefront landing data into a single efficient response,
    avoiding multiple client round-trips while backed by cache.
    """

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        cached_entry = cache.get(CACHE_KEY_HOMEPAGE)
        if cached_entry is not None:
            cached_payload, browser_max_age = unpack_scheduled_cache_entry(
                cached_entry, browser_max_age=30
            )
            return public_response(request, cached_payload, max_age=browser_max_age)

        # 1. Active Promotions & Announcement Bar
        promotions_qs = Promotion.objects.active_now().order_by("priority", "-created_at")
        announcements = PromotionSerializer(
            promotions_qs.filter(show_in_announcement_bar=True),
            many=True,
            context={"request": request},
        ).data

        # 2. Active Popup
        active_popup_obj = Popup.objects.active_now().order_by("-created_at").first()
        active_popup = (
            PopupSerializer(active_popup_obj, context={"request": request}).data
            if active_popup_obj
            else None
        )

        # 3. Site Settings & Delivery
        site_settings_data = SiteSettingsPublicSerializer(
            SiteSettings.get_solo(), context={"request": request}
        ).data
        delivery_settings_data = DeliverySettingsPublicSerializer(
            DeliverySettings.get_solo(), context={"request": request}
        ).data

        # 4. Featured Categories (up to 8)
        categories_qs = (
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_published=True)))
            .order_by("sort_order", "name")[:8]
        )
        categories_data = CategorySerializer(
            categories_qs, many=True, context={"request": request}
        ).data

        # 5. Featured Products (up to 8)
        featured_products_qs = (
            Product.objects.filter(is_published=True, is_featured=True)
            .select_related("category")
            .prefetch_related("images", "variants", "attributes")
            .order_by("sort_priority", "-created_at")[:8]
        )
        featured_products_data = ProductListSerializer(
            featured_products_qs, many=True, context={"request": request}
        ).data

        # 6. New Arrivals (up to 8)
        new_arrivals_qs = (
            Product.objects.filter(is_published=True, is_new_arrival=True)
            .select_related("category")
            .prefetch_related("images", "variants", "attributes")
            .order_by("-created_at")[:8]
        )
        new_arrivals_data = ProductListSerializer(
            new_arrivals_qs, many=True, context={"request": request}
        ).data

        # 7. Reviews (up to 6)
        reviews_qs = Review.objects.filter(is_published=True).order_by(
            "sort_priority", "-created_at"
        )[:6]
        reviews_data = ReviewSerializer(reviews_qs, many=True, context={"request": request}).data

        # 8. Gallery Highlights (up to 8)
        gallery_qs = GalleryItem.objects.filter(is_published=True).order_by(
            "sort_priority", "-created_at"
        )[:8]
        gallery_data = GalleryItemSerializer(
            gallery_qs, many=True, context={"request": request}
        ).data

        # 9. About Story (if active)
        about_obj = AboutSection.objects.filter(is_active=True).first()
        about_data = (
            AboutSectionSerializer(about_obj, context={"request": request}).data
            if about_obj
            else None
        )

        payload = {
            "site_settings": site_settings_data,
            "delivery_settings": delivery_settings_data,
            "announcements": announcements,
            "active_popup": active_popup,
            "featured_categories": categories_data,
            "featured_products": featured_products_data,
            "new_arrivals": new_arrivals_data,
            "reviews": reviews_data,
            "gallery_moments": gallery_data,
            "about": about_data,
        }

        timeout = schedule_cache_timeout(Promotion, Popup, configured_timeout=600)
        cache.set(
            CACHE_KEY_HOMEPAGE,
            scheduled_cache_entry(payload, timeout),
            timeout=timeout,
        )
        return public_response(
            request,
            payload,
            max_age=min(30, getattr(settings, "PUBLIC_PRODUCT_CACHE_TIMEOUT", 60)),
        )
