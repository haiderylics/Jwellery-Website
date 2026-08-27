"""URL configuration for Jewellery Website."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import include, path

from backend.apps.common.api.views import StorefrontHomeView

# Customize Django Admin branding for business owner
admin.site.site_header = "Jewellery Operations Console"
admin.site.site_title = "Jewellery Admin"
admin.site.index_title = "Storefront Content & Merchandising Management"


def health_liveness_view(request: HttpRequest) -> HttpResponse:
    """Process liveness probe endpoint.

    Returns HTTP 200 OK without leaking sensitive system details.
    """
    return JsonResponse({"status": "ok"}, status=200)


def health_readiness_view(request: HttpRequest) -> HttpResponse:
    """Dependency readiness probe endpoint.

    Verifies active database connectivity with a lightweight query.
    Fails safely with 503 without leaking credentials or infrastructure internals.
    """
    try:
        default_storage_backend = settings.STORAGES.get("default", {}).get("BACKEND", "")
        if (
            default_storage_backend
            == "backend.apps.common.cloudinary_storage.CloudinaryMediaStorage"
        ):
            from backend.apps.common.cloudinary_storage import cloudinary_configuration_is_valid

            if not cloudinary_configuration_is_valid():
                return JsonResponse({"status": "unready"}, status=503)
        connection.ensure_connection()
        return JsonResponse({"status": "ready"}, status=200)
    except Exception:
        return JsonResponse({"status": "unready"}, status=503)


api_v1_patterns = [
    path("home/", StorefrontHomeView.as_view(), name="storefront-home"),
    path("", include("backend.apps.catalog.api.urls")),
    path("", include("backend.apps.content.api.urls")),
    path("", include("backend.apps.promotions.api.urls")),
    path("", include("backend.apps.settings.api.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live/", health_liveness_view, name="health-liveness"),
    path("health/ready/", health_readiness_view, name="health-readiness"),
    path("api/v1/", include((api_v1_patterns, "api-v1"))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
