from rest_framework import serializers

from backend.apps.common.media import get_variant_url
from backend.apps.content.models import AboutSection, GalleryItem, Review


class ReviewSerializer(serializers.ModelSerializer):
    """Customer testimonial serializer."""

    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "customer_name",
            "review_text",
            "rating",
            "image_url",
            "thumbnail_url",
            "is_verified",
            "created_at",
        ]

    def get_image_url(self, obj: Review) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_thumbnail_url(self, obj: Review) -> str | None:
        return get_variant_url(obj.image, "thumb", self.context.get("request"))


class GalleryItemSerializer(serializers.ModelSerializer):
    """Event, exhibition, and brand moment photography serializer."""

    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    medium_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryItem
        fields = [
            "id",
            "title",
            "caption",
            "image_url",
            "thumbnail_url",
            "medium_url",
            "item_type",
            "event_date",
            "created_at",
        ]

    def get_image_url(self, obj: GalleryItem) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_thumbnail_url(self, obj: GalleryItem) -> str | None:
        return get_variant_url(obj.image, "thumb", self.context.get("request"))

    def get_medium_url(self, obj: GalleryItem) -> str | None:
        return get_variant_url(obj.image, "medium", self.context.get("request"))


class AboutSectionSerializer(serializers.ModelSerializer):
    """Brand heritage and craftsmanship story serializer."""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutSection
        fields = [
            "id",
            "title",
            "subtitle",
            "story_text",
            "image_url",
            "updated_at",
        ]

    def get_image_url(self, obj: AboutSection) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
