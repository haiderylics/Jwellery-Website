"""Content domain models for Jewellery Website.

Defines Review, GalleryItem, and AboutSection models for brand trust and storytelling.
"""

from django.db import models
from django.db.models import Q

from backend.apps.common.media import secure_upload_path, validate_secure_image


class Review(models.Model):
    """Customer testimonial / WhatsApp feedback."""

    customer_name = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Customer rating from 1 to 5 stars",
    )
    image = models.ImageField(
        upload_to=secure_upload_path("reviews"),
        null=True,
        blank=True,
        validators=[validate_secure_image],
        help_text="Optional customer-approved photo",
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Controls public display on storefront",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Flag indicating verified direct purchaser",
    )
    sort_priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower values display first",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
        ordering = ["sort_priority", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="check_review_rating_1_to_5",
            ),
        ]
        indexes = [
            models.Index(fields=["is_published", "sort_priority", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.customer_name} ({self.rating}★)"


class GalleryItem(models.Model):
    """Event, exhibition, and brand photography gallery entity."""

    class ItemType(models.TextChoices):
        EXHIBITION = "exhibition", "Exhibition"
        SEMINAR = "seminar", "Seminar"
        BRAND = "brand", "Brand Moment"
        OTHER = "other", "Other"

    title = models.CharField(max_length=200)
    caption = models.CharField(max_length=500, blank=True)
    image = models.ImageField(
        upload_to=secure_upload_path("gallery"),
        validators=[validate_secure_image],
    )
    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
        default=ItemType.EXHIBITION,
        db_index=True,
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
    )
    sort_priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower values display first",
    )
    event_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the exhibition or event took place",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"
        ordering = ["sort_priority", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "sort_priority", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_item_type_display()})"


class AboutSection(models.Model):
    """Brand narrative and craftsmanship story."""

    title = models.CharField(max_length=200, default="Our Story")
    subtitle = models.CharField(max_length=300, blank=True)
    story_text = models.TextField(help_text="Brand history and craftsmanship narrative")
    image = models.ImageField(
        upload_to=secure_upload_path("about"),
        null=True,
        blank=True,
        validators=[validate_secure_image],
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Sections"

    def __str__(self) -> str:
        return self.title
