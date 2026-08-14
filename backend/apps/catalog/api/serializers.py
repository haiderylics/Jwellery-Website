"""Serializers for catalog public storefront APIs."""

from rest_framework import serializers

from backend.apps.catalog.models import (
    Category,
    Product,
    ProductAttributeType,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
    ProductVideo,
)
from backend.apps.common.media import get_variant_url


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer for navigation and filter chips."""

    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "sort_order",
            "product_count",
        ]


class CompactCategorySerializer(serializers.ModelSerializer):
    """Minimal category metadata for product cards."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Individual attribute value serializer."""

    attribute_type_name = serializers.CharField(source="attribute_type.name", read_only=True)
    attribute_type_slug = serializers.CharField(source="attribute_type.slug", read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = [
            "id",
            "value",
            "slug",
            "attribute_type_name",
            "attribute_type_slug",
            "sort_order",
        ]


class ProductAttributeTypeSerializer(serializers.ModelSerializer):
    """Attribute type serializer containing nested allowed values."""

    values = ProductAttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttributeType
        fields = ["id", "name", "slug", "sort_order", "values"]


class ProductImageSerializer(serializers.ModelSerializer):
    """Product gallery image serializer with responsive WebP variants."""

    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    medium_url = serializers.SerializerMethodField()
    large_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image_url",
            "thumbnail_url",
            "medium_url",
            "large_url",
            "is_primary",
            "alt_text",
            "sort_order",
        ]

    def get_image_url(self, obj: ProductImage) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_thumbnail_url(self, obj: ProductImage) -> str | None:
        return get_variant_url(obj.image, "thumb", self.context.get("request"))

    def get_medium_url(self, obj: ProductImage) -> str | None:
        return get_variant_url(obj.image, "medium", self.context.get("request"))

    def get_large_url(self, obj: ProductImage) -> str | None:
        return get_variant_url(obj.image, "large", self.context.get("request"))


class ProductVariantSerializer(serializers.ModelSerializer):
    """Product variant option serializer."""

    effective_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "name",
            "sku",
            "price_override",
            "effective_price",
            "is_available",
            "stock_status",
            "sort_order",
        ]

    def get_stock_status(self, obj: ProductVariant) -> str:
        if not obj.is_available or obj.stock_quantity <= 0:
            return "out_of_stock"
        if obj.stock_quantity <= 3:
            return "low_stock"
        return "in_stock"


class ProductVideoSerializer(serializers.ModelSerializer):
    """Product demonstration video serializer."""

    video_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductVideo
        fields = ["id", "video_url", "title"]

    def get_video_url(self, obj: ProductVideo) -> str | None:
        if obj.video_url:
            return obj.video_url
        if obj.video_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None


class ProductListSerializer(serializers.ModelSerializer):
    """Optimized, compact serializer for storefront catalog grids and search listings."""

    category = CompactCategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "base_price",
            "compare_at_price",
            "primary_image",
            "category",
            "availability_status",
            "is_featured",
            "is_new_arrival",
            "is_custom_order",
            "stock_status",
            "updated_at",
        ]

    def get_primary_image(self, obj: Product) -> dict | None:
        images = list(obj.images.all())
        primary = next((img for img in images if img.is_primary), None)
        if not primary and images:
            primary = images[0]
        if primary:
            return ProductImageSerializer(primary, context=self.context).data
        return None

    def get_stock_status(self, obj: Product) -> str:
        stock = obj.effective_stock
        if obj.availability_status == Product.AvailabilityStatus.OUT_OF_STOCK or stock <= 0:
            return "out_of_stock"
        if stock <= 3:
            return "low_stock"
        return "in_stock"


class ProductDetailSerializer(serializers.ModelSerializer):
    """Comprehensive product detail serializer."""

    category = CompactCategorySerializer(read_only=True)
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    video = ProductVideoSerializer(read_only=True)
    stock_status = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "base_price",
            "compare_at_price",
            "availability_status",
            "is_featured",
            "is_new_arrival",
            "is_custom_order",
            "category",
            "attributes",
            "images",
            "variants",
            "video",
            "stock_status",
            "seo",
            "updated_at",
        ]

    def get_stock_status(self, obj: Product) -> str:
        stock = obj.effective_stock
        if obj.availability_status == Product.AvailabilityStatus.OUT_OF_STOCK or stock <= 0:
            return "out_of_stock"
        if stock <= 3:
            return "low_stock"
        return "in_stock"

    def get_seo(self, obj: Product) -> dict:
        return {
            "title": obj.seo_title or obj.name,
            "description": obj.seo_description or obj.short_description or "",
        }
