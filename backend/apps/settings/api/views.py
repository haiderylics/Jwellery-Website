"""Views for site settings and delivery public storefront APIs."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.settings.models import DeliverySettings, SiteSettings

from .serializers import DeliverySettingsPublicSerializer, SiteSettingsPublicSerializer


class SiteSettingsPublicView(APIView):
    """Public read-only business profile, WhatsApp number, and SEO defaults."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        settings_obj = SiteSettings.get_solo()
        serializer = SiteSettingsPublicSerializer(settings_obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeliverySettingsPublicView(APIView):
    """Public read-only authoritative delivery rules and thresholds."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        delivery_obj = DeliverySettings.get_solo()
        serializer = DeliverySettingsPublicSerializer(delivery_obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
