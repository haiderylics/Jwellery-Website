"""Catalog domain models for Jewellery Website.

Defines Category, ProductAttributeType, ProductAttributeValue, Product,
ProductVariant, ProductImage, and ProductVideo entities.
"""

from decimal import Decimal

from django.db import models
from django.db.models import F, Q

from backend.apps.common.media import (
    secure_upload_path,
    validate_secure_image,
    validate_secure_video,
)


class Category(models.Model):
    """Primary product taxonomy classification."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return self.name


class ProductAttributeType(models.Model):
    """Attribute category axis (e.g. Material, Purity, Gemstone, Collection)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Product Attribute Type"
        verbose_name_plural = "Product Attribute Types"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class ProductAttributeValue(models.Model):
    """Specific value for an attribute type (e.g. Stainless Steel, Gold Plated, 1 Carat)."""

    attribute_type = models.ForeignKey(
        ProductAttributeType,
        on_delete=models.CASCADE,
        related_name="values",
    )
    value = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Product Attribute Value"
        verbose_name_plural = "Product Attribute Values"
        ordering = ["attribute_type", "sort_order", "value"]
        constraints = [
            models.UniqueConstraint(
                fields=["attribute_type", "slug"],
                name="unique_attribute_value_per_type",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.attribute_type.name}: {self.value}"


class Product(models.Model):
    """Core Jewellery product entity."""

    class AvailabilityStatus(models.TextChoices):
        IN_STOCK = "in_stock", "In Stock"
        LOW_STOCK = "low_stock", "Low Stock"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
        COMING_SOON = "coming_soon", "Coming Soon"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    short_description = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    attributes = models.ManyToManyField(
        ProductAttributeValue,
        blank=True,
        related_name="products",
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Authoritative base price in PKR",
    )
    compare_at_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional original price in PKR for compare/strike-through display",
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Base inventory quantity when no variants are configured",
    )
    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.IN_STOCK,
        db_index=True,
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Controls storefront visibility",
    )
    is_custom_order = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates customizability via WhatsApp consultation",
    )
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Highlights product on homepage featured section",
    )
    is_new_arrival = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Highlights product on homepage new arrivals section",
    )
    sort_priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower values display first",
    )
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["sort_priority", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(base_price__gte=0),
                name="check_product_base_price_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(compare_at_price__isnull=True) | Q(compare_at_price__gte=0),
                name="check_product_compare_at_price_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(compare_at_price__isnull=True)
                | Q(compare_at_price__gt=F("base_price")),
                name="check_product_compare_at_gt_base_price",
            ),
        ]
        indexes = [
            models.Index(fields=["is_published", "category", "sort_priority"]),
            models.Index(fields=["is_published", "is_featured", "sort_priority"]),
            models.Index(fields=["is_published", "is_new_arrival", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def has_variants(self) -> bool:
        """Helper indicating if product has variant options configured."""
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "variants" in self._prefetched_objects_cache
        ):
            return len(self.variants.all()) > 0
        return self.variants.exists()

    @property
    def effective_stock(self) -> int:
        """Calculates total available stock.

        If variants exist, sums all available variant stock quantities.
        Prefetch-aware: uses in-memory variants if prefetched to avoid N+1 queries.
        """
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "variants" in self._prefetched_objects_cache
        ):
            available_variants = [v for v in self.variants.all() if v.is_available]
            if available_variants:
                return sum(v.stock_quantity for v in available_variants)
            # If no available variants exist but variants were configured, effective stock is 0
            if len(self.variants.all()) > 0:
                return 0
            return self.stock_quantity

        if self.variants.exists():
            return (
                self.variants.filter(is_available=True).aggregate(
                    total=models.Sum("stock_quantity")
                )["total"]
                or 0
            )
        return self.stock_quantity


class ProductVariant(models.Model):
    """Specific variant option (e.g. Size, Color, Finish) for a product."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(
        max_length=100,
        help_text="Variant label, e.g. 'Size 7 / Rose Gold'",
    )
    sku = models.CharField(max_length=50, blank=True)
    price_override = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional variant-specific price override in PKR",
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Stock quantity for this specific variant",
    )
    is_available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        ordering = ["sort_order", "name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price_override__isnull=True) | Q(price_override__gte=0),
                name="check_variant_price_override_non_negative",
            ),
            models.UniqueConstraint(
                fields=["product", "name"],
                name="unique_variant_name_per_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"

    @property
    def effective_price(self) -> Decimal:
        """Return price override if specified, otherwise the parent product base price."""
        if self.price_override is not None:
            return self.price_override
        return self.product.base_price


class ProductImage(models.Model):
    """Product gallery imagery."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to=secure_upload_path("products/images"),
        validators=[validate_secure_image],
    )
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(
        default=False,
        help_text="Flag indicating the primary hero image for catalog display",
    )
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["sort_order", "-is_primary", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="unique_primary_image_per_product",
            ),
        ]
        indexes = [
            models.Index(fields=["product", "sort_order"]),
        ]

    def __str__(self) -> str:
        primary_badge = " [Primary]" if self.is_primary else ""
        return f"Image for {self.product.name}{primary_badge}"


class ProductVideo(models.Model):
    """Optional product video demonstration."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="video",
    )
    video_file = models.FileField(
        upload_to=secure_upload_path("products/videos"),
        blank=True,
        null=True,
        validators=[validate_secure_video],
        help_text="Uploaded product video file (MP4/WebM)",
    )
    video_url = models.URLField(
        blank=True,
        help_text="Optional external video link or CDN stream URL",
    )
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Video"
        verbose_name_plural = "Product Videos"

    def __str__(self) -> str:
        return f"Video for {self.product.name}"
