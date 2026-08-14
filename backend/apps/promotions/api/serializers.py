"""Serializers for promotions and popup public storefront APIs."""

from rest_framework import serializers

from backend.apps.promotions.models import Popup, Promotion


class PromotionSerializer(serializers.ModelSerializer):
    """Active promotion campaign and announcement banner serializer."""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "subtitle",
            "announcement_text",
            "image_url",
            "cta_label",
            "cta_url",
            "show_in_announcement_bar",
            "priority",
        ]

    def get_image_url(self, obj: Promotion) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class PopupSerializer(serializers.ModelSerializer):
    """Active modal announcement popup serializer."""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Popup
        fields = [
            "id",
            "title",
            "message",
            "image_url",
            "cta_label",
            "cta_url",
            "delay_seconds",
        ]

    def get_image_url(self, obj: Popup) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
