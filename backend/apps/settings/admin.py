"""Django admin operations configuration for site settings, delivery, and social links."""

from django import forms
from django.contrib import admin
from django.http import HttpRequest

from backend.apps.common.validators import validate_safe_url

from .models import DeliverySettings, SiteSettings, SocialLink


class SiteSettingsAdminForm(forms.ModelForm):
    """Custom validation form for SiteSettings singleton."""

    class Meta:
        model = SiteSettings
        fields = [
            "brand_name",
            "tagline",
            "contact_email",
            "contact_phone",
            "whatsapp_number",
            "canonical_site_url",
            "default_seo_title",
            "default_seo_description",
        ]

    def clean_canonical_site_url(self) -> str:
        url = self.cleaned_data.get("canonical_site_url", "")
        if url:
            validate_safe_url(url)
        return url


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Singleton admin operations console for business profile and brand metadata."""

    form = SiteSettingsAdminForm
    list_display = [
        "brand_name",
        "whatsapp_number",
        "contact_email",
        "canonical_site_url",
        "updated_at",
    ]
    readonly_fields = ["updated_at"]

    fieldsets = [
        (
            "Brand Identity & Profile",
            {
                "fields": ("brand_name", "tagline"),
                "description": "Storefront brand name and editorial tagline.",
            },
        ),
        (
            "Customer Contact & WhatsApp Orders",
            {
                "fields": ("whatsapp_number", "contact_email", "contact_phone"),
                "description": "Authoritative WhatsApp number used for storefront customer order handoff. Format: +923001234567.",
            },
        ),
        (
            "Storefront Domain & Canonical URL",
            {
                "fields": ("canonical_site_url",),
                "description": "Base canonical URL for building product share links in WhatsApp messages.",
            },
        ),
        (
            "Default SEO & Meta",
            {
                "fields": ("default_seo_title", "default_seo_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "System Metadata",
            {
                "fields": ("updated_at",),
                "classes": ("collapse",),
            },
        ),
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Prevent creating multiple singleton records
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj: SiteSettings | None = None) -> bool:
        # Protect singleton configuration from accidental deletion
        return False


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    """Singleton admin operations console for authoritative delivery rules."""

    list_display = [
        "__str__",
        "pakistan_delivery_enabled",
        "free_delivery_threshold",
        "pakistan_delivery_charge",
        "international_delivery_mode",
        "updated_at",
    ]
    readonly_fields = ["updated_at"]

    fieldsets = [
        (
            "Domestic Delivery (Pakistan)",
            {
                "fields": (
                    "pakistan_delivery_enabled",
                    "pakistan_delivery_charge",
                    "free_delivery_threshold",
                ),
                "description": "Standard delivery fee (PKR) and free shipping threshold (PKR 5,000 default).",
            },
        ),
        (
            "International Delivery",
            {
                "fields": (
                    "international_delivery_mode",
                    "international_delivery_fixed_charge",
                ),
                "description": "Mode: Disabled, Quote on WhatsApp, or Fixed Rate. Fixed charge applies only if Fixed Rate mode is selected.",
            },
        ),
        (
            "System Metadata",
            {
                "fields": ("updated_at",),
                "classes": ("collapse",),
            },
        ),
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Prevent creating multiple singleton records
        return not DeliverySettings.objects.exists()

    def has_delete_permission(
        self, request: HttpRequest, obj: DeliverySettings | None = None
    ) -> bool:
        # Protect singleton configuration from accidental deletion
        return False


class SocialLinkAdminForm(forms.ModelForm):
    """Custom validation form for SocialLink entities."""

    class Meta:
        model = SocialLink
        fields = ["platform", "url", "is_active", "sort_order"]

    def clean_url(self) -> str:
        url = self.cleaned_data.get("url", "")
        if url:
            validate_safe_url(url)
        return url


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    """Admin operations console for external social media profile links."""

    form = SocialLinkAdminForm
    list_display = ["platform", "url", "is_active", "sort_order"]
    list_filter = ["is_active"]
    search_fields = ["platform"]
    ordering = ["sort_order", "platform"]
