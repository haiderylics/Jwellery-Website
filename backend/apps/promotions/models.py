"""Promotions domain models for Jewellery Website.

Defines Promotion (banners, announcements, sales) and Popup models with scheduling support.
"""

from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from backend.apps.common.media import secure_upload_path, validate_secure_image


class ActiveScheduleQuerySet(models.QuerySet):
    """Custom queryset providing timezone-aware active scheduling filtering."""

    def active_now(self, now_dt=None) -> models.QuerySet:
        """Filter items currently active within their scheduled window."""
        if now_dt is None:
            now_dt = timezone.now()
        return self.filter(
            Q(is_active=True)
            & (Q(start_datetime__isnull=True) | Q(start_datetime__lte=now_dt))
            & (Q(end_datetime__isnull=True) | Q(end_datetime__gte=now_dt))
        )


class Promotion(models.Model):
    """Promotional campaigns, sales, and top-of-site announcement bar messaging."""

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    announcement_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short message for top announcement bar (e.g. 'Eid Mubarak Sale: Free Shipping above PKR 5,000')",
    )
    image = models.ImageField(
        upload_to=secure_upload_path("promotions"),
        null=True,
        blank=True,
        validators=[validate_secure_image],
        help_text="Optional campaign banner image",
    )
    cta_label = models.CharField(max_length=50, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Master active switch for this promotion",
    )
    show_in_announcement_bar = models.BooleanField(
        default=True,
        help_text="Display announcement_text in top bar when active",
    )
    start_datetime = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional scheduled activation datetime",
    )
    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional scheduled expiration datetime",
    )
    priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower values take precedence",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveScheduleQuerySet.as_manager()

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ["priority", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(start_datetime__isnull=True)
                    | Q(end_datetime__isnull=True)
                    | Q(end_datetime__gt=F("start_datetime"))
                ),
                name="check_promotion_end_after_start",
            ),
        ]
        indexes = [
            models.Index(
                fields=["is_active", "start_datetime", "end_datetime", "priority"],
            ),
        ]

    def __str__(self) -> str:
        return self.title


class Popup(models.Model):
    """Scheduled modal popup for special announcements or offers."""

    title = models.CharField(max_length=200)
    message = models.TextField()
    image = models.ImageField(
        upload_to=secure_upload_path("popups"),
        null=True,
        blank=True,
        validators=[validate_secure_image],
    )
    cta_label = models.CharField(max_length=50, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Master switch for popup display",
    )
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    delay_seconds = models.PositiveIntegerField(
        default=5,
        help_text="Seconds to wait after page load before displaying popup",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveScheduleQuerySet.as_manager()

    class Meta:
        verbose_name = "Popup Announcement"
        verbose_name_plural = "Popup Announcements"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(start_datetime__isnull=True)
                    | Q(end_datetime__isnull=True)
                    | Q(end_datetime__gt=F("start_datetime"))
                ),
                name="check_popup_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        return self.title
