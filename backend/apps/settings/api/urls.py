"""URL routing for settings public APIs."""

from django.urls import path

from .views import DeliverySettingsPublicView, SiteSettingsPublicView

urlpatterns = [
    path("site-settings/", SiteSettingsPublicView.as_view(), name="site-settings-public"),
    path(
        "delivery-settings/", DeliverySettingsPublicView.as_view(), name="delivery-settings-public"
    ),
]
