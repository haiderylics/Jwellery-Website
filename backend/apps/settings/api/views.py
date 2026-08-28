"""Views for site settings and delivery public storefront APIs."""

from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.common.api.cache import public_response
from backend.apps.common.cache_utils import (
    CACHE_KEY_DELIVERY_SETTINGS,
    CACHE_KEY_SITE_SETTINGS,
)
from backend.apps.settings.models import DeliverySettings, SiteSettings

from .serializers import DeliverySettingsPublicSerializer, SiteSettingsPublicSerializer


class SiteSettingsPublicView(APIView):
    """Public read-only business profile, WhatsApp number, and SEO defaults."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        payload = cache.get(CACHE_KEY_SITE_SETTINGS)
        timeout = getattr(settings, "PUBLIC_SITE_CACHE_TIMEOUT", 300)
        if payload is None:
            settings_obj = SiteSettings.get_solo()
            payload = SiteSettingsPublicSerializer(settings_obj, context={"request": request}).data
            cache.set(CACHE_KEY_SITE_SETTINGS, payload, timeout=timeout)
        return public_response(request, payload, max_age=min(60, timeout))


class DeliverySettingsPublicView(APIView):
    """Public read-only authoritative delivery rules and thresholds."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        payload = cache.get(CACHE_KEY_DELIVERY_SETTINGS)
        timeout = getattr(settings, "PUBLIC_SITE_CACHE_TIMEOUT", 300)
        if payload is None:
            delivery_obj = DeliverySettings.get_solo()
            payload = DeliverySettingsPublicSerializer(
                delivery_obj, context={"request": request}
            ).data
            cache.set(CACHE_KEY_DELIVERY_SETTINGS, payload, timeout=timeout)
        return public_response(request, payload, max_age=min(60, timeout))
