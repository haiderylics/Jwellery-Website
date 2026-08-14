"""Serializers for site settings and delivery public storefront APIs."""

from rest_framework import serializers

from backend.apps.settings.models import DeliverySettings, SiteSettings, SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    """Social media profile serializer."""

    class Meta:
        model = SocialLink
        fields = ["id", "platform", "url", "sort_order"]


class SiteSettingsPublicSerializer(serializers.ModelSerializer):
    """Storefront business identity, WhatsApp number, and SEO serializer."""

    social_links = serializers.SerializerMethodField()
    default_seo = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = [
            "brand_name",
            "tagline",
            "contact_email",
            "contact_phone",
            "whatsapp_number",
            "canonical_site_url",
            "social_links",
            "default_seo",
            "updated_at",
        ]

    def get_social_links(self, obj: SiteSettings) -> list:
        links = SocialLink.objects.filter(is_active=True).order_by("sort_order", "platform")
        return SocialLinkSerializer(links, many=True).data

    def get_default_seo(self, obj: SiteSettings) -> dict:
        return {
            "title": obj.default_seo_title or obj.brand_name,
            "description": obj.default_seo_description or obj.tagline or "",
        }


class DeliverySettingsPublicSerializer(serializers.ModelSerializer):
    """Authoritative delivery rates and policy rules for storefront checkout & cart."""

    class Meta:
        model = DeliverySettings
        fields = [
            "pakistan_delivery_enabled",
            "free_delivery_threshold",
            "pakistan_delivery_charge",
            "international_delivery_mode",
            "international_delivery_fixed_charge",
            "updated_at",
        ]
