"""Production-only configuration checks for external media storage."""

from django.core.checks import Error, Tags, register

from backend.apps.common.cloudinary_storage import cloudinary_configuration_is_valid


@register(Tags.security, deploy=True)
def check_cloudinary_configuration(app_configs, **kwargs):  # type: ignore[no-untyped-def]
    """Fail explicit deployment validation, not unrelated management commands."""
    if cloudinary_configuration_is_valid():
        return []
    return [
        Error(
            "Cloudinary media credentials are missing.",
            hint=(
                "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and "
                "CLOUDINARY_API_SECRET in the production service."
            ),
            id="common.E001",
        )
    ]
