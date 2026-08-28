"""Django admin operations configuration for catalog domain models."""

from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from backend.apps.common.cache_utils import (
    CACHE_KEY_ADMIN_METRICS,
    CACHE_KEY_CATEGORIES,
    CACHE_KEY_HOMEPAGE,
    invalidate_product_cache,
    invalidate_storefront_cache,
)

from .models import (
    Category,
    Product,
    ProductAttributeType,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
    ProductVideo,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin console for Category management."""

    list_display = [
        "name",
        "slug",
        "product_count_display",
        "sort_order",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["sort_order", "name"]
    list_per_page = 25

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(product_count=Count("products"))

    @admin.display(description="Total Products", ordering="product_count")
    def product_count_display(self, obj: Category) -> int:
        return getattr(obj, "product_count", 0)


class ProductAttributeValueInline(admin.TabularInline):
    """Inline editing for attribute values directly within Attribute Type."""

    model = ProductAttributeValue
    extra = 1
    prepopulated_fields = {"slug": ("value",)}
    fields = ["value", "slug", "sort_order"]
    ordering = ["sort_order", "value"]


@admin.register(ProductAttributeType)
class ProductAttributeTypeAdmin(admin.ModelAdmin):
    """Admin console for Product Attribute Types (e.g. Material, Purity)."""

    list_display = ["name", "slug", "values_count_display", "sort_order"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductAttributeValueInline]
    ordering = ["sort_order", "name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(values_count=Count("values"))

    @admin.display(description="Values Configured", ordering="values_count")
    def values_count_display(self, obj: ProductAttributeType) -> int:
        return getattr(obj, "values_count", 0)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    """Standalone fallback admin for individual attribute values."""

    list_display = ["value", "attribute_type", "slug", "sort_order"]
    list_filter = ["attribute_type"]
    search_fields = ["value", "slug", "attribute_type__name"]
    autocomplete_fields = ["attribute_type"]
    prepopulated_fields = {"slug": ("value",)}
    ordering = ["attribute_type", "sort_order", "value"]


class ProductVariantInline(admin.TabularInline):
    """Inline manager for product variants (sizes, colors, finishes)."""

    model = ProductVariant
    extra = 0
    fields = ["name", "sku", "price_override", "stock_quantity", "is_available", "sort_order"]
    ordering = ["sort_order", "name"]
    classes = ["collapse"]


class ProductImageInline(admin.TabularInline):
    """Inline manager for product images."""

    model = ProductImage
    extra = 0
    fields = ["image_preview", "image", "is_primary", "alt_text", "sort_order"]
    readonly_fields = ["image_preview"]
    ordering = ["sort_order", "-is_primary"]

    @admin.display(description="Current photo")
    def image_preview(self, obj: ProductImage) -> str:
        if not obj or not obj.image:
            return "No photo uploaded"
        try:
            image_url = obj.image.url
        except (AttributeError, ValueError):
            return "Preview unavailable"
        return format_html(
            '<img src="{}" alt="" loading="lazy" class="admin-product-thumbnail">',
            image_url,
        )


class ProductVideoInline(admin.StackedInline):
    """Inline manager for optional product video demonstration."""

    model = ProductVideo
    extra = 0
    max_num = 1
    fields = ["video_file", "video_url", "title"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Comprehensive operations console for Jewellery Products."""

    list_display = [
        "name",
        "category",
        "formatted_base_price",
        "effective_stock_display",
        "availability_status",
        "is_published",
        "is_featured",
        "is_new_arrival",
        "updated_at",
    ]
    list_filter = [
        "is_published",
        "availability_status",
        "is_featured",
        "is_new_arrival",
        "is_custom_order",
        "category",
    ]
    search_fields = ["name", "slug", "category__name", "short_description"]
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["category"]
    filter_horizontal = ["attributes"]
    inlines = [ProductImageInline, ProductVariantInline, ProductVideoInline]
    ordering = ["sort_priority", "-created_at"]
    list_per_page = 20

    readonly_fields = ["effective_stock_display", "created_at", "updated_at"]

    fieldsets = [
        (
            "Basic Information",
            {
                "fields": ("name", "slug", "short_description", "description"),
            },
        ),
        (
            "Pricing (PKR)",
            {
                "fields": ("base_price", "compare_at_price"),
                "description": "Base price is authoritative. Compare-at price is optional for strike-through sales display.",
            },
        ),
        (
            "Inventory & Stock",
            {
                "fields": ("stock_quantity", "availability_status", "effective_stock_display"),
                "description": "Base stock applies when no variants exist. If variants are added below, variant inventory governs effective stock.",
            },
        ),
        (
            "Taxonomy & Attributes",
            {
                "fields": ("category", "attributes"),
                "description": "Assign primary category and relevant secondary attributes (Material, Purity, etc.).",
            },
        ),
        (
            "Merchandising & Storefront Placement",
            {
                "fields": (
                    "is_published",
                    "is_featured",
                    "is_new_arrival",
                    "is_custom_order",
                    "sort_priority",
                ),
            },
        ),
        (
            "Search Engine Optimization (SEO)",
            {
                "fields": ("seo_title", "seo_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "System Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    ]

    actions = [
        "make_published",
        "make_unpublished",
        "mark_featured",
        "unmark_featured",
        "mark_new_arrival",
        "unmark_new_arrival",
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("category").prefetch_related("variants")

    @admin.display(description="Base Price", ordering="base_price")
    def formatted_base_price(self, obj: Product) -> str:
        return f"PKR {obj.base_price:,.2f}"

    @admin.display(description="Total Stock")
    def effective_stock_display(self, obj: Product) -> str:
        stock = obj.effective_stock
        if obj.has_variants:
            return format_html("<strong>{}</strong> <em>(via variants)</em>", stock)
        return str(stock)

    @staticmethod
    def _invalidate_bulk_product_changes() -> None:
        invalidate_product_cache()
        invalidate_storefront_cache(
            [CACHE_KEY_HOMEPAGE, CACHE_KEY_CATEGORIES, CACHE_KEY_ADMIN_METRICS]
        )

    # Safe Admin Bulk Actions
    @admin.action(description="Publish selected products", permissions=["change"])
    def make_published(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_published=True)
        self._invalidate_bulk_product_changes()
        self.message_user(request, f"{updated} product(s) marked as published.", messages.SUCCESS)

    @admin.action(description="Unpublish selected products (Draft)", permissions=["change"])
    def make_unpublished(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_published=False)
        self._invalidate_bulk_product_changes()
        self.message_user(request, f"{updated} product(s) marked as unpublished.", messages.SUCCESS)

    @admin.action(description="Feature selected products on Homepage", permissions=["change"])
    def mark_featured(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_featured=True)
        self._invalidate_bulk_product_changes()
        self.message_user(request, f"{updated} product(s) marked as featured.", messages.SUCCESS)

    @admin.action(description="Remove selected products from Featured", permissions=["change"])
    def unmark_featured(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_featured=False)
        self._invalidate_bulk_product_changes()
        self.message_user(request, f"{updated} product(s) removed from featured.", messages.SUCCESS)

    @admin.action(description="Mark selected products as New Arrival", permissions=["change"])
    def mark_new_arrival(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_new_arrival=True)
        self._invalidate_bulk_product_changes()
        self.message_user(request, f"{updated} product(s) marked as new arrival.", messages.SUCCESS)

    @admin.action(description="Remove selected products from New Arrival", permissions=["change"])
    def unmark_new_arrival(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_new_arrival=False)
        self._invalidate_bulk_product_changes()
        self.message_user(
            request, f"{updated} product(s) removed from new arrival.", messages.SUCCESS
        )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Standalone admin for searching and viewing all variants."""

    list_display = [
        "name",
        "product",
        "sku",
        "price_override",
        "stock_quantity",
        "is_available",
        "sort_order",
    ]
    list_filter = ["is_available", "product__category"]
    search_fields = ["name", "sku", "product__name"]
    autocomplete_fields = ["product"]
    ordering = ["product", "sort_order", "name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("product")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Standalone admin for searching and managing product images."""

    list_display = ["product", "is_primary", "alt_text", "sort_order", "created_at"]
    list_filter = ["is_primary", "product__category"]
    search_fields = ["product__name", "alt_text"]
    autocomplete_fields = ["product"]
    ordering = ["product", "sort_order", "-is_primary"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("product")
