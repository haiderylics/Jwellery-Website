"""Django admin operations configuration for promotions and announcements."""

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html

from backend.apps.common.validators import validate_safe_url

from .models import Popup, Promotion


class PromotionAdminForm(forms.ModelForm):
    """Custom validation form for Promotion entities."""

    class Meta:
        model = Promotion
        fields = [
            "title",
            "subtitle",
            "announcement_text",
            "image",
            "cta_label",
            "cta_url",
            "is_active",
            "show_in_announcement_bar",
            "start_datetime",
            "end_datetime",
            "priority",
        ]

    def clean_cta_url(self) -> str:
        url = self.cleaned_data.get("cta_url", "")
        if url:
            validate_safe_url(url)
        return url


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Admin operations console for sales, banners, and announcement bar."""

    form = PromotionAdminForm
    list_display = [
        "title",
        "announcement_text",
        "schedule_status_badge",
        "is_active",
        "show_in_announcement_bar",
        "priority",
        "start_datetime",
        "end_datetime",
    ]
    list_filter = ["is_active", "show_in_announcement_bar"]
    search_fields = ["title", "subtitle", "announcement_text"]
    ordering = ["priority", "-created_at"]
    list_per_page = 20

    fieldsets = [
        (
            "Promotion Content",
            {
                "fields": ("title", "subtitle", "announcement_text", "image"),
                "description": "Campaign title and optional top announcement bar text.",
            },
        ),
        (
            "Call to Action (CTA)",
            {
                "fields": ("cta_label", "cta_url"),
                "description": "Optional CTA button label and secure destination link (https:// or /shop/).",
            },
        ),
        (
            "Scheduling & Status",
            {
                "fields": (
                    "is_active",
                    "show_in_announcement_bar",
                    "start_datetime",
                    "end_datetime",
                    "priority",
                ),
                "description": "Set start/end dates to schedule activation automatically. Lower priority numbers display first.",
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
    readonly_fields = ["created_at", "updated_at"]

    actions = ["activate_promotions", "deactivate_promotions"]

    @admin.display(description="Schedule Status")
    def schedule_status_badge(self, obj: Promotion) -> str:
        if not obj.is_active:
            return format_html(
                '<span style="color: #c62828; font-weight: bold;">{}</span>', "Inactive"
            )

        now = timezone.now()
        if obj.start_datetime and now < obj.start_datetime:
            return format_html('<span style="color: #0288d1;">{}</span>', "Upcoming")
        if obj.end_datetime and now > obj.end_datetime:
            return format_html('<span style="color: #757575;">{}</span>', "Expired")
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">{}</span>', "Active Now"
        )

    @admin.action(description="Activate selected promotions", permissions=["change"])
    def activate_promotions(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} promotion(s) activated.", messages.SUCCESS)

    @admin.action(description="Deactivate selected promotions", permissions=["change"])
    def deactivate_promotions(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} promotion(s) deactivated.", messages.SUCCESS)


class PopupAdminForm(forms.ModelForm):
    """Custom validation form for Popup entities."""

    class Meta:
        model = Popup
        fields = [
            "title",
            "message",
            "image",
            "cta_label",
            "cta_url",
            "is_active",
            "start_datetime",
            "end_datetime",
            "delay_seconds",
        ]

    def clean_cta_url(self) -> str:
        url = self.cleaned_data.get("cta_url", "")
        if url:
            validate_safe_url(url)
        return url


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    """Admin operations console for promotional modal popups."""

    form = PopupAdminForm
    list_display = [
        "title",
        "schedule_status_badge",
        "is_active",
        "delay_seconds",
        "start_datetime",
        "end_datetime",
    ]
    list_filter = ["is_active"]
    search_fields = ["title", "message"]
    ordering = ["-created_at"]

    fieldsets = [
        (
            "Popup Content",
            {
                "fields": ("title", "message", "image", "cta_label", "cta_url"),
                "description": "Modal announcement content and secure CTA link.",
            },
        ),
        (
            "Behavior & Schedule",
            {
                "fields": ("is_active", "delay_seconds", "start_datetime", "end_datetime"),
                "description": "Delay controls how many seconds after page load the popup appears.",
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
    readonly_fields = ["created_at", "updated_at"]

    actions = ["activate_popups", "deactivate_popups"]

    @admin.display(description="Schedule Status")
    def schedule_status_badge(self, obj: Popup) -> str:
        if not obj.is_active:
            return format_html(
                '<span style="color: #c62828; font-weight: bold;">{}</span>', "Inactive"
            )

        now = timezone.now()
        if obj.start_datetime and now < obj.start_datetime:
            return format_html('<span style="color: #0288d1;">{}</span>', "Upcoming")
        if obj.end_datetime and now > obj.end_datetime:
            return format_html('<span style="color: #757575;">{}</span>', "Expired")
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">{}</span>', "Active Now"
        )

    @admin.action(description="Activate selected popups", permissions=["change"])
    def activate_popups(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} popup(s) activated.", messages.SUCCESS)

    @admin.action(description="Deactivate selected popups", permissions=["change"])
    def deactivate_popups(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} popup(s) deactivated.", messages.SUCCESS)
