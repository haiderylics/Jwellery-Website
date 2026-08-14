"""Views for catalog public storefront APIs."""

from django.db.models import Count, Q, QuerySet
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from backend.apps.catalog.models import Category, Product, ProductAttributeType

from .serializers import (
    CategorySerializer,
    ProductAttributeTypeSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)

ORDERING_MAP = {
    "newest": ["-created_at"],
    "price_low": ["base_price", "id"],
    "price_high": ["-base_price", "id"],
    "featured": ["-is_featured", "sort_priority", "-created_at"],
    "priority": ["sort_priority", "-created_at"],
}


class ProductListView(generics.ListAPIView):
    """Public read-only product catalog listing with bounded filtering and search."""

    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        qs = (
            Product.objects.filter(is_published=True)
            .select_related("category")
            .prefetch_related("images", "variants", "attributes")
        )

        request: Request = self.request
        params = request.query_params

        # 1. Category Filter (slug)
        category_slug = params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug.strip()[:100])

        # 2. Attribute Slug Filter
        attribute_slug = params.get("attribute")
        if attribute_slug:
            qs = qs.filter(attributes__slug=attribute_slug.strip()[:100])

        # 3. Merchandising Boolean Flags
        if params.get("featured", "").lower() in ("true", "1"):
            qs = qs.filter(is_featured=True)

        if params.get("new_arrival", "").lower() in ("true", "1"):
            qs = qs.filter(is_new_arrival=True)

        if params.get("custom_order", "").lower() in ("true", "1"):
            qs = qs.filter(is_custom_order=True)

        # 4. Keyword Search (bounded to 100 chars)
        query = params.get("q", "").strip()[:100]
        if query:
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(short_description__icontains=query)
                | Q(description__icontains=query)
            )

        # 5. Allowlisted Sorting
        sort_key = params.get("ordering", "priority").strip().lower()
        order_fields = ORDERING_MAP.get(sort_key, ORDERING_MAP["priority"])
        return qs.order_by(*order_fields).distinct()


class ProductDetailView(generics.RetrieveAPIView):
    """Public read-only product detail retrieval by unique slug."""

    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        return (
            Product.objects.filter(is_published=True)
            .select_related("category", "video")
            .prefetch_related("images", "variants", "attributes__attribute_type")
        )


class CategoryListView(generics.ListAPIView):
    """Public read-only listing of active product categories."""

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    pagination_class = None
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        return (
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_published=True)))
            .order_by("sort_order", "name")
        )


class AttributeTypeListView(generics.ListAPIView):
    """Public read-only listing of attribute types and their discrete values."""

    permission_classes = [AllowAny]
    serializer_class = ProductAttributeTypeSerializer
    pagination_class = None
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet:
        return ProductAttributeType.objects.prefetch_related("values").order_by(
            "sort_order", "name"
        )
