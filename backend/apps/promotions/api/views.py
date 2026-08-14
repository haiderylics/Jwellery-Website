"""Views for promotions and popup public storefront APIs."""

from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.promotions.models import Popup, Promotion

from .serializers import PopupSerializer, PromotionSerializer


class ActivePromotionsView(generics.ListAPIView):
    """Public read-only listing of currently active promotions."""

    permission_classes = [AllowAny]
    serializer_class = PromotionSerializer
    pagination_class = None
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        return Promotion.objects.active_now().order_by("priority", "-created_at")


class ActivePopupView(APIView):
    """Public read-only retrieval of the currently active promotional popup."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        popup = Popup.objects.active_now().order_by("-created_at").first()
        if not popup:
            return Response(
                {"data": None, "message": "No active popup at this time."},
                status=status.HTTP_200_OK,
            )
        serializer = PopupSerializer(popup, context={"request": request})
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
