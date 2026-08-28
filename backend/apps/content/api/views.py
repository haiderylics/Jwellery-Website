"""Views for content public storefront APIs."""

from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.common.api.cache import PublicCacheControlMixin
from backend.apps.content.models import AboutSection, GalleryItem, Review

from .serializers import AboutSectionSerializer, GalleryItemSerializer, ReviewSerializer


class ReviewListView(PublicCacheControlMixin, generics.ListAPIView):
    """Public read-only customer reviews list."""

    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        return Review.objects.filter(is_published=True).order_by("sort_priority", "-created_at")


class GalleryItemListView(PublicCacheControlMixin, generics.ListAPIView):
    """Public read-only gallery moment listing with optional item_type filter."""

    permission_classes = [AllowAny]
    serializer_class = GalleryItemSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        qs = GalleryItem.objects.filter(is_published=True)
        item_type = self.request.query_params.get("type")
        if item_type:
            qs = qs.filter(item_type=item_type.strip()[:30])
        return qs.order_by("sort_priority", "-created_at")


class AboutSectionView(PublicCacheControlMixin, APIView):
    """Public read-only about section brand narrative."""

    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs) -> Response:
        about = AboutSection.objects.filter(is_active=True).first()
        if not about:
            return Response(
                {
                    "error": {
                        "code": "not_found",
                        "message": "About section is currently unavailable.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AboutSectionSerializer(about, context={"request": request})
        return Response(serializer.data)
