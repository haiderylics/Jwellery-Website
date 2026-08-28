"""Django Admin application configuration for the owner-focused AdminSite."""

from django.contrib.admin.apps import AdminConfig


class OwnerAdminConfig(AdminConfig):
    default_site = "backend.apps.common.admin_site.OwnerAdminSite"
