"""Cloudinary-backed Django storage for persistent production media.

The implementation uses Cloudinary's maintained official Python SDK rather
than the unmaintained third-party django-cloudinary-storage package. File
names remain Django storage keys, preserving the existing model schema.
"""

from __future__ import annotations

import os
from typing import Any

import cloudinary
import cloudinary.api
import cloudinary.uploader
import cloudinary.utils
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage


def cloudinary_configuration_is_valid() -> bool:
    """Return whether the configured default storage has all required credentials."""
    from django.conf import settings

    options = settings.STORAGES.get("default", {}).get("OPTIONS", {})
    return all(options.get(key) for key in ("cloud_name", "api_key", "api_secret"))


class CloudinaryMediaStorage(Storage):
    """Store validated admin-uploaded images and videos in Cloudinary.

    This storage is deliberately used only as Django's ``default`` storage in
    production. It never handles static files and does not support directory
    listing, preventing application code from accidentally enumerating an
    entire Cloudinary account.
    """

    is_cloudinary_storage = True

    def __init__(
        self,
        *,
        cloud_name: str | None = None,
        api_key: str | None = None,
        api_secret: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize through Django's ``storage_cls(**OPTIONS)`` contract."""
        super().__init__(**kwargs)
        self.cloud_name = cloud_name or os.environ.get("CLOUDINARY_CLOUD_NAME", "")
        self.api_key = api_key or os.environ.get("CLOUDINARY_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("CLOUDINARY_API_SECRET", "")
        if not all((self.cloud_name, self.api_key, self.api_secret)):
            raise ImproperlyConfigured(
                "Cloudinary media storage requires CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in production."
            )
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def resource_type(name: str) -> str:
        """Map controlled upload namespaces to Cloudinary resource types."""
        return "video" if name.startswith("products/videos/") else "image"

    @staticmethod
    def normalize_name(name: str) -> str:
        """Use POSIX public IDs regardless of the Django host operating system."""
        return name.replace("\\", "/")

    def _save(self, name: str, content: Any) -> str:
        """Validate then upload one privacy-normalized source asset to Cloudinary."""
        name = self.normalize_name(name)
        resource_type = self.resource_type(name)
        try:
            if resource_type == "image":
                # Django model validators run in admin forms, but storage is
                # also reachable through programmatic Model.save(). Enforce
                # validation at this final pre-persistence boundary too.
                from backend.apps.common.media import prepare_secure_image_upload

                content = prepare_secure_image_upload(content)
            content.seek(0)
            cloudinary.uploader.upload(
                content,
                public_id=name,
                resource_type=resource_type,
                overwrite=False,
                unique_filename=False,
                use_filename=False,
            )
        except ImproperlyConfigured:
            raise
        except Exception:
            # Do not translate transport/API failures into image-corruption
            # errors. The caller and Railway logs retain the storage failure.
            raise
        return name

    # ``Storage.open()`` intentionally remains unsupported. Application image
    # validation and responsive delivery use incoming streams and Cloudinary
    # transformation URLs, so a remote CDN download is never part of upload.

    def delete(self, name: str) -> None:
        if name:
            name = self.normalize_name(name)
            cloudinary.uploader.destroy(
                name,
                resource_type=self.resource_type(name),
                invalidate=True,
            )

    def exists(self, name: str) -> bool:
        if not name:
            return False
        name = self.normalize_name(name)
        try:
            cloudinary.api.resource(name, resource_type=self.resource_type(name))
        except Exception:
            return False
        return True

    def url(self, name: str) -> str:
        name = self.normalize_name(name)
        url, _ = cloudinary.utils.cloudinary_url(
            name,
            resource_type=self.resource_type(name),
            secure=True,
        )
        return url

    def size(self, name: str) -> int:
        name = self.normalize_name(name)
        resource = cloudinary.api.resource(name, resource_type=self.resource_type(name))
        return int(resource["bytes"])

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """Names are UUID-generated by upload_to, so collision renaming is unsafe."""
        return self.normalize_name(name)

    def get_modified_time(self, name: str):  # type: ignore[no-untyped-def]
        raise NotImplementedError("Cloudinary media does not expose filesystem timestamps.")

    def path(self, name: str) -> str:
        raise NotImplementedError("Cloudinary media has no local filesystem path.")


def cloudinary_transformed_url(name: str, width: int) -> str:
    """Return one of the fixed, CDN-cached responsive image delivery URLs."""
    url, _ = cloudinary.utils.cloudinary_url(
        name,
        resource_type="image",
        secure=True,
        width=width,
        crop="limit",
        fetch_format="auto",
        quality="auto",
    )
    return url
