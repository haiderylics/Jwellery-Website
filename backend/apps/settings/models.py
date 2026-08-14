"""Store settings domain models for Jewellery Website.

Defines SiteSettings (singleton), DeliverySettings (singleton), and SocialLink models.
"""

from decimal import Decimal

from django.db import models
from django.db.models import Q


class SiteSettings(models.Model):
    """Authoritative business profile and storefront metadata (Singleton)."""

    singleton_guard = models.PositiveSmallIntegerField(
        default=1,
        editable=False,
        help_text="Enforces single database record",
    )
    brand_name = models.CharField(max_length=100, default="Jewellery Brand")
    tagline = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(
        max_length=30,
        help_text="Normalized business WhatsApp number for orders, e.g. '+923001234567'",
    )
    canonical_site_url = models.URLField(
        blank=True,
        help_text="Canonical storefront URL (e.g. 'https://www.example.com')",
    )
    default_seo_title = models.CharField(max_length=70, blank=True)
    default_seo_description = models.CharField(max_length=160, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
        constraints = [
            models.UniqueConstraint(
                fields=["singleton_guard"],
                name="unique_site_settings_singleton",
            ),
            models.CheckConstraint(
                condition=Q(singleton_guard=1),
                name="check_site_settings_singleton_guard_is_one",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.brand_name} Settings"

    @classmethod
    def get_solo(cls) -> "SiteSettings":
        """Retrieve the authoritative singleton instance, creating it with defaults if absent."""
        obj, _ = cls.objects.get_or_create(
            singleton_guard=1,
            defaults={"brand_name": "Jewellery Brand"},
        )
        return obj


class DeliverySettings(models.Model):
    """Authoritative delivery rates and thresholds (Singleton)."""

    class InternationalMode(models.TextChoices):
        DISABLED = "disabled", "Disabled"
        WHATSAPP_QUOTE = "whatsapp_quote", "Quote on WhatsApp"
        FIXED = "fixed", "Fixed Rate"

    singleton_guard = models.PositiveSmallIntegerField(
        default=1,
        editable=False,
        help_text="Enforces single database record",
    )
    pakistan_delivery_enabled = models.BooleanField(
        default=True,
        help_text="Enable delivery anywhere in Pakistan",
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("5000.00"),
        help_text="Subtotal threshold in PKR for free Pakistan delivery",
    )
    pakistan_delivery_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("250.00"),
        help_text="Standard Pakistan delivery fee in PKR",
    )
    international_delivery_mode = models.CharField(
        max_length=20,
        choices=InternationalMode.choices,
        default=InternationalMode.WHATSAPP_QUOTE,
        help_text="International order handling strategy",
    )
    international_delivery_fixed_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fixed international shipping fee if fixed rate mode is selected",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delivery Settings"
        verbose_name_plural = "Delivery Settings"
        constraints = [
            models.UniqueConstraint(
                fields=["singleton_guard"],
                name="unique_delivery_settings_singleton",
            ),
            models.CheckConstraint(
                condition=Q(singleton_guard=1),
                name="check_delivery_settings_singleton_guard_is_one",
            ),
            models.CheckConstraint(
                condition=Q(free_delivery_threshold__gte=0),
                name="check_delivery_free_threshold_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(pakistan_delivery_charge__gte=0),
                name="check_delivery_pakistan_charge_non_negative",
            ),
            models.CheckConstraint(
                condition=(
                    Q(international_delivery_fixed_charge__isnull=True)
                    | Q(international_delivery_fixed_charge__gte=0)
                ),
                name="check_delivery_intl_charge_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return "Delivery Settings"

    @classmethod
    def get_solo(cls) -> "DeliverySettings":
        """Retrieve the authoritative delivery settings singleton instance."""
        obj, _ = cls.objects.get_or_create(singleton_guard=1)
        return obj


class SocialLink(models.Model):
    """External social media and communication profile links."""

    platform = models.CharField(
        max_length=50,
        help_text="Platform identifier, e.g. 'Instagram', 'Facebook', 'TikTok', 'WhatsApp'",
    )
    url = models.URLField(help_text="Full profile or contact URL")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"
        ordering = ["sort_order", "platform"]
        constraints = [
            models.UniqueConstraint(
                fields=["platform"],
                name="unique_social_platform",
            ),
        ]

    def __str__(self) -> str:
        return self.platform
