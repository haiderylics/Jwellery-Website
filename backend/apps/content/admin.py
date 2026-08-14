"""Django admin operations configuration for content and trust domain models."""

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .models import AboutSection, GalleryItem, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin operations console for customer testimonials and WhatsApp reviews."""

    list_display = [
        "customer_name",
        "rating_stars",
        "is_verified",
        "is_published",
        "sort_priority",
        "created_at",
    ]
    list_filter = ["is_published", "is_verified", "rating"]
    search_fields = ["customer_name", "review_text"]
    ordering = ["sort_priority", "-created_at"]
    list_per_page = 25

    fieldsets = [
        (
            "Customer Review Details",
            {
                "fields": ("customer_name", "review_text", "rating", "image"),
                "description": "Customer name and approved review text. Do not expose private contact information.",
            },
        ),
        (
            "Verification & Publication",
            {
                "fields": ("is_verified", "is_published", "sort_priority"),
                "description": "Mark as verified only if purchase or consultation occurred.",
            },
        ),
        (
            "System Metadata",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    ]
    readonly_fields = ["created_at"]

    actions = ["publish_reviews", "unpublish_reviews", "mark_verified", "unmark_verified"]

    @admin.display(description="Rating", ordering="rating")
    def rating_stars(self, obj: Review) -> str:
        filled = "★" * obj.rating
        empty = "☆" * (5 - obj.rating)
        return format_html(
            '<span style="color: #c9a227; font-size: 1.1em;">{}{}</span> ({})',
            filled,
            empty,
            obj.rating,
        )

    @admin.action(description="Publish selected reviews", permissions=["change"])
    def publish_reviews(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} review(s) published.", messages.SUCCESS)

    @admin.action(description="Unpublish selected reviews", permissions=["change"])
    def unpublish_reviews(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} review(s) unpublished.", messages.SUCCESS)

    @admin.action(description="Mark selected reviews as Verified Purchaser", permissions=["change"])
    def mark_verified(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} review(s) marked as verified.", messages.SUCCESS)

    @admin.action(
        description="Remove Verified status from selected reviews", permissions=["change"]
    )
    def unmark_verified(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} review(s) marked as unverified.", messages.SUCCESS)


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    """Admin operations console for exhibition and event photography."""

    list_display = [
        "title",
        "item_type",
        "is_published",
        "sort_priority",
        "event_date",
        "created_at",
    ]
    list_filter = ["is_published", "item_type"]
    search_fields = ["title", "caption"]
    ordering = ["sort_priority", "-created_at"]
    list_per_page = 25

    fieldsets = [
        (
            "Gallery Item Details",
            {
                "fields": ("title", "caption", "image", "item_type", "event_date"),
                "description": "Exhibition, seminar, or brand photography item.",
            },
        ),
        (
            "Publication & Ordering",
            {
                "fields": ("is_published", "sort_priority"),
            },
        ),
        (
            "System Metadata",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    ]
    readonly_fields = ["created_at"]

    actions = ["publish_items", "unpublish_items"]

    @admin.action(description="Publish selected gallery items", permissions=["change"])
    def publish_items(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} gallery item(s) published.", messages.SUCCESS)

    @admin.action(description="Unpublish selected gallery items", permissions=["change"])
    def unpublish_items(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} gallery item(s) unpublished.", messages.SUCCESS)


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    """Admin console for About Us and craftsmanship brand storytelling."""

    list_display = ["title", "subtitle", "is_active", "updated_at"]
    fields = ["title", "subtitle", "story_text", "image", "is_active", "updated_at"]
    readonly_fields = ["updated_at"]
