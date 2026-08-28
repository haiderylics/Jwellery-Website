"""Views for promotions and popup public storefront APIs."""

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.common.api.cache import (
    public_response,
    schedule_cache_timeout,
    scheduled_cache_entry,
    unpack_scheduled_cache_entry,
)
from backend.apps.common.cache_utils import CACHE_KEY_POPUPS_ACTIVE, CACHE_KEY_PROMOTIONS_ACTIVE
from backend.apps.promotions.models import Popup, Promotion

from .serializers import PopupSerializer, PromotionSerializer


class ActivePromotionsView(APIView):
    """Public read-only listing of currently active promotions."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        cached_entry = cache.get(CACHE_KEY_PROMOTIONS_ACTIVE)
        configured_timeout = getattr(settings, "PUBLIC_PROMOTION_CACHE_TIMEOUT", 300)
        if cached_entry is not None:
            payload, browser_max_age = unpack_scheduled_cache_entry(
                cached_entry, browser_max_age=30
            )
        else:
            timeout = schedule_cache_timeout(Promotion, configured_timeout=configured_timeout)
            promotions = Promotion.objects.active_now().order_by("priority", "-created_at")
            payload = PromotionSerializer(promotions, many=True, context={"request": request}).data
            cache.set(
                CACHE_KEY_PROMOTIONS_ACTIVE,
                scheduled_cache_entry(payload, timeout),
                timeout=timeout,
            )
            browser_max_age = min(30, timeout)
        return public_response(request, payload, max_age=browser_max_age)


class ActivePopupView(APIView):
    """Public read-only retrieval of the currently active promotional popup."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        cached_entry = cache.get(CACHE_KEY_POPUPS_ACTIVE)
        configured_timeout = getattr(settings, "PUBLIC_PROMOTION_CACHE_TIMEOUT", 300)
        if cached_entry is not None:
            payload, browser_max_age = unpack_scheduled_cache_entry(
                cached_entry, browser_max_age=30
            )
        else:
            timeout = schedule_cache_timeout(Popup, configured_timeout=configured_timeout)
            popup = Popup.objects.active_now().order_by("-created_at").first()
            if popup:
                serializer = PopupSerializer(popup, context={"request": request})
                payload = {"data": serializer.data}
            else:
                payload = {"data": None, "message": "No active popup at this time."}
            cache.set(
                CACHE_KEY_POPUPS_ACTIVE,
                scheduled_cache_entry(payload, timeout),
                timeout=timeout,
            )
            browser_max_age = min(30, timeout)
        return public_response(
            request,
            payload,
            max_age=browser_max_age,
            status_code=status.HTTP_200_OK,
        )
