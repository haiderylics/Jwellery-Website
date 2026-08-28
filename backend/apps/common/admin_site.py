"""Owner-focused Django Admin site without exposing technical auth navigation."""

from django.contrib.admin import AdminSite
from django.http import HttpRequest


class OwnerAdminSite(AdminSite):
    """Keep Django auth fully operational while presenting business-facing navigation."""

    site_header = "Jewellery Operations Console"
    site_title = "Jewellery Admin"
    index_title = "Storefront Content & Merchandising Management"

    _app_names = {
        "catalog": "Catalog",
        "content": "Content",
        "promotions": "Offers & Campaigns",
        "settings": "Store Settings",
    }
    _app_order = {label: index for index, label in enumerate(_app_names)}
    _hidden_inline_models = {
        "ProductAttributeValue",
        "ProductImage",
        "ProductVariant",
        "ProductVideo",
    }
    _model_names = {
        "Product": "Jewellery Pieces",
        "ProductAttributeType": "Attributes & Options",
        "Review": "Customer Reviews",
        "GalleryItem": "Gallery Moments",
        "AboutSection": "Brand Story",
        "Promotion": "Offers & Campaigns",
        "Popup": "Popup Announcements",
        "SocialLink": "Social Profiles",
    }

    def get_app_list(self, request: HttpRequest, app_label: str | None = None) -> list[dict]:
        """Hide Django's implementation-centric auth app from all app navigation.

        User administration remains registered and permission-protected at its canonical
        URL. The dashboard exposes that URL as "Staff Access" only to superusers.
        """
        app_list = super().get_app_list(request, app_label)
        visible_apps = [app for app in app_list if app["app_label"] != "auth"]
        for app in visible_apps:
            app["name"] = self._app_names.get(app["app_label"], app["name"])
            app["models"] = [
                model
                for model in app["models"]
                if model["object_name"] not in self._hidden_inline_models
            ]
            for model in app["models"]:
                model["name"] = self._model_names.get(model["object_name"], model["name"])
        return sorted(
            visible_apps,
            key=lambda app: (self._app_order.get(app["app_label"], 99), app["name"]),
        )
