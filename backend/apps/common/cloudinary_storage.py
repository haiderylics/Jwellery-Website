"""Cloudinary-backed Django storage for persistent production media.

The implementation uses Cloudinary's maintained official Python SDK rather
than the unmaintained third-party django-cloudinary-storage package. File
names remain Django storage keys, preserving the existing model schema.
"""

from __future__ import annotations

import logging
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

import cloudinary
import cloudinary.api
import cloudinary.uploader
import cloudinary.utils
from cloudinary.exceptions import NotFound
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage

logger = logging.getLogger(__name__)

_FORMAT_ALIASES = {"jpeg": "jpg"}
_VIDEO_FORMATS = frozenset({"mov", "mp4", "webm"})
_FORBIDDEN_PUBLIC_ID_CHARACTERS = frozenset("?&#\\%<>+")
_RESERVED_PUBLIC_ID_PATH_SEGMENTS = frozenset({"images", "videos"})
_VERSION_PATH_SEGMENT = re.compile(r"^v\d+$", re.IGNORECASE)
_TRANSFORMATION_LIKE_PATH_SEGMENT = re.compile(r"^[A-Za-z0-9]{1,3}_")
_CANONICAL_NAMESPACE_REWRITES = {
    ("products", "images"): ("catalog", "products", "photos"),
    ("products", "videos"): ("catalog", "products", "clips"),
}


class CloudinaryStorageError(OSError):
    """Raised when Cloudinary returns an invalid or unsuccessful storage response."""


@dataclass(frozen=True, slots=True)
class CloudinaryAssetIdentity:
    """Canonical mapping between a Django storage key and one Cloudinary asset."""

    storage_name: str
    public_id: str
    format: str
    resource_type: str

    @property
    def legacy_extensionful_public_id(self) -> str:
        """Return the extensionful ID used by the oldest broken uploader."""
        return self.storage_name

    @property
    def legacy_reserved_namespace_public_id(self) -> str | None:
        """Return the prior extensionless ID when its path used a reserved namespace."""
        storage_public_id = PurePosixPath(self.storage_name).with_suffix("").as_posix()
        return storage_public_id if storage_public_id != self.public_id else None


def _canonical_public_id(storage_public_id: PurePosixPath) -> str:
    """Rewrite known legacy namespaces and reject unsafe future path elements."""
    parts = storage_public_id.parts
    canonical_parts = parts
    for legacy_prefix, canonical_prefix in _CANONICAL_NAMESPACE_REWRITES.items():
        if parts[: len(legacy_prefix)] == legacy_prefix:
            canonical_parts = (*canonical_prefix, *parts[len(legacy_prefix) :])
            break

    folder_parts = canonical_parts[:-1]
    for part in folder_parts:
        if part.lower() in _RESERVED_PUBLIC_ID_PATH_SEGMENTS:
            raise ValueError(
                "Cloudinary public ID paths may not contain reserved 'images' or 'videos' segments."
            )
        if _VERSION_PATH_SEGMENT.fullmatch(part):
            raise ValueError("Cloudinary public ID paths may not contain version-like segments.")
        if _TRANSFORMATION_LIKE_PATH_SEGMENT.match(part):
            raise ValueError(
                "Cloudinary public ID paths may not contain transformation-like segments."
            )

    return PurePosixPath(*canonical_parts).as_posix()


def cloudinary_asset_identity(name: str) -> CloudinaryAssetIdentity:
    """Translate a Django storage name into canonical Cloudinary identity fields.

    Django keeps the extension in its storage key. Cloudinary image/video public
    IDs do not: the format is a separate delivery attribute.
    """
    normalized = str(name).replace("\\", "/").strip()
    if not normalized or normalized.startswith("/"):
        raise ValueError("Cloudinary storage names must be non-empty relative POSIX paths.")

    raw_parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ValueError("Cloudinary storage names may not contain empty or traversal segments.")
    if any(character in normalized for character in _FORBIDDEN_PUBLIC_ID_CHARACTERS):
        raise ValueError("Cloudinary storage name contains a forbidden public ID character.")

    path = PurePosixPath(normalized)
    suffix = path.suffix.lower()
    if not suffix:
        raise ValueError("Cloudinary image/video storage names must include a format extension.")

    asset_format = _FORMAT_ALIASES.get(suffix[1:], suffix[1:])
    public_id = _canonical_public_id(path.with_suffix(""))
    resource_type = "video" if asset_format in _VIDEO_FORMATS else "image"
    return CloudinaryAssetIdentity(
        storage_name=path.as_posix(),
        public_id=public_id,
        format=asset_format,
        resource_type=resource_type,
    )


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
        return cloudinary_asset_identity(name).resource_type

    @staticmethod
    def normalize_name(name: str) -> str:
        """Use POSIX public IDs regardless of the Django host operating system."""
        return cloudinary_asset_identity(name).storage_name

    @staticmethod
    def asset_identity(name: str) -> CloudinaryAssetIdentity:
        """Return the single canonical identity used by every storage operation."""
        return cloudinary_asset_identity(name)

    @staticmethod
    def _validate_upload_response(
        response: Any, identity: CloudinaryAssetIdentity
    ) -> Mapping[str, Any]:
        """Reject incomplete or mismatched responses instead of persisting a broken key."""
        if not isinstance(response, Mapping):
            raise CloudinaryStorageError("Cloudinary returned an invalid upload response.")

        returned_format = str(response.get("format", "")).lower()
        returned_format = _FORMAT_ALIASES.get(returned_format, returned_format)
        if (
            response.get("public_id") != identity.public_id
            or response.get("resource_type") != identity.resource_type
            or returned_format != identity.format
            or not str(response.get("secure_url", "")).startswith("https://")
        ):
            raise CloudinaryStorageError(
                "Cloudinary upload response did not match the requested asset identity."
            )
        return response

    def _save(self, name: str, content: Any) -> str:
        """Validate then upload one privacy-normalized source asset to Cloudinary."""
        identity = self.asset_identity(name)
        try:
            if identity.resource_type == "image":
                # Django model validators run in admin forms, but storage is
                # also reachable through programmatic Model.save(). Enforce
                # validation at this final pre-persistence boundary too.
                from backend.apps.common.media import prepare_secure_image_upload

                content = prepare_secure_image_upload(content)
            content.seek(0)
            response = cloudinary.uploader.upload(
                content,
                public_id=identity.public_id,
                resource_type=identity.resource_type,
                type="upload",
                overwrite=False,
                unique_filename=False,
                use_filename=False,
            )
            self._validate_upload_response(response, identity)
        except ImproperlyConfigured:
            raise
        except Exception:
            # Do not translate transport/API failures into image-corruption
            # errors. The caller and Railway logs retain the storage failure.
            raise
        return identity.storage_name

    # ``Storage.open()`` intentionally remains unsupported. Application image
    # validation and responsive delivery use incoming streams and Cloudinary
    # transformation URLs, so a remote CDN download is never part of upload.

    def delete(self, name: str) -> None:
        if not name:
            return

        identity = self.asset_identity(name)
        try:
            response = cloudinary.uploader.destroy(
                identity.public_id,
                resource_type=identity.resource_type,
                type="upload",
                invalidate=True,
            )
        except Exception:
            logger.exception(
                "Cloudinary deletion failed for public_id=%s resource_type=%s",
                identity.public_id,
                identity.resource_type,
            )
            raise

        result = response.get("result") if isinstance(response, Mapping) else None
        if result not in {"ok", "not found"}:
            raise CloudinaryStorageError(
                f"Cloudinary did not confirm deletion for '{identity.storage_name}'."
            )

    def exists(self, name: str) -> bool:
        if not name:
            return False
        identity = self.asset_identity(name)
        try:
            cloudinary.api.resource(
                identity.public_id,
                resource_type=identity.resource_type,
                type="upload",
            )
        except NotFound:
            return False
        return True

    def url(self, name: str) -> str:
        identity = self.asset_identity(name)
        url, _ = cloudinary.utils.cloudinary_url(
            identity.public_id,
            resource_type=identity.resource_type,
            type="upload",
            secure=True,
            format=identity.format,
            force_version=False,
        )
        return url

    def size(self, name: str) -> int:
        identity = self.asset_identity(name)
        try:
            resource = cloudinary.api.resource(
                identity.public_id,
                resource_type=identity.resource_type,
                type="upload",
            )
        except NotFound:
            raise FileNotFoundError(identity.storage_name) from None

        try:
            return int(resource["bytes"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CloudinaryStorageError(
                f"Cloudinary returned no valid size for '{identity.storage_name}'."
            ) from exc

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """Names are UUID-generated by upload_to, so collision renaming is unsafe."""
        return self.asset_identity(name).storage_name

    def get_modified_time(self, name: str):  # type: ignore[no-untyped-def]
        raise NotImplementedError("Cloudinary media does not expose filesystem timestamps.")

    def path(self, name: str) -> str:
        raise NotImplementedError("Cloudinary media has no local filesystem path.")


def cloudinary_transformed_url(name: str, width: int) -> str:
    """Return one of the fixed, CDN-cached responsive image delivery URLs."""
    identity = cloudinary_asset_identity(name)
    if identity.resource_type != "image":
        raise ValueError("Responsive image transformations cannot be applied to video assets.")
    url, _ = cloudinary.utils.cloudinary_url(
        identity.public_id,
        resource_type="image",
        type="upload",
        secure=True,
        format=identity.format,
        force_version=False,
        width=width,
        crop="limit",
        fetch_format="auto",
        quality="auto",
    )
    return url
