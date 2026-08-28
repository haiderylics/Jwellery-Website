"""Normalize DB-referenced Cloudinary assets to safe canonical public IDs."""

from collections.abc import Iterator, Mapping
from typing import Any

import cloudinary.api
import cloudinary.uploader
from cloudinary.exceptions import NotFound
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from backend.apps.catalog.models import ProductImage, ProductVideo
from backend.apps.common.cloudinary_storage import (
    CloudinaryAssetIdentity,
    cloudinary_asset_identity,
)
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.models import Popup, Promotion

MEDIA_FIELDS = (
    (ProductImage, "image"),
    (ProductVideo, "video_file"),
    (GalleryItem, "image"),
    (Review, "image"),
    (AboutSection, "image"),
    (Promotion, "image"),
    (Popup, "image"),
)


class Command(BaseCommand):
    help = (
        "Find DB-referenced Cloudinary assets using extensionful or reserved-namespace "
        "public IDs and optionally rename them to the safe canonical identity."
    )

    def add_arguments(self, parser: Any) -> None:
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument(
            "--apply",
            action="store_true",
            help="Apply DB-bounded Cloudinary renames. Without this flag the command is dry-run.",
        )
        mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Explicitly report candidates without changing Cloudinary (the default).",
        )

    @staticmethod
    def _referenced_assets() -> Iterator[CloudinaryAssetIdentity]:
        seen: set[tuple[str, str]] = set()
        for model, field_name in MEDIA_FIELDS:
            names = (
                model.objects.exclude(**{f"{field_name}__isnull": True})
                .exclude(**{field_name: ""})
                .values_list(field_name, flat=True)
            )
            for name in names.iterator():
                identity = cloudinary_asset_identity(str(name))
                key = (identity.resource_type, identity.storage_name)
                if key not in seen:
                    seen.add(key)
                    yield identity

    @staticmethod
    def _lookup(public_id: str, resource_type: str) -> Mapping[str, Any] | None:
        try:
            return cloudinary.api.resource(
                public_id,
                resource_type=resource_type,
                type="upload",
            )
        except NotFound:
            return None

    def handle(self, *args: Any, **options: Any) -> None:
        if not getattr(default_storage, "is_cloudinary_storage", False):
            raise CommandError("normalize_cloudinary_media requires Cloudinary default storage.")

        apply_changes = bool(options["apply"])
        counts = {
            "referenced": 0,
            "canonical": 0,
            "legacy_extensionful": 0,
            "legacy_reserved_namespace": 0,
            "missing": 0,
            "conflict": 0,
            "renamed": 0,
            "errors": 0,
        }
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Cloudinary media identity normalization: "
                + ("APPLY" if apply_changes else "DRY RUN")
            )
        )

        for identity in self._referenced_assets():
            counts["referenced"] += 1
            try:
                canonical = self._lookup(identity.public_id, identity.resource_type)
                candidates = [
                    (
                        "LEGACY_EXTENSIONFUL",
                        identity.legacy_extensionful_public_id,
                    )
                ]
                if identity.legacy_reserved_namespace_public_id is not None:
                    candidates.append(
                        (
                            "LEGACY_RESERVED_NAMESPACE",
                            identity.legacy_reserved_namespace_public_id,
                        )
                    )

                legacy_assets = [
                    (category, public_id)
                    for category, public_id in candidates
                    if self._lookup(public_id, identity.resource_type) is not None
                ]

                if canonical is not None and not legacy_assets:
                    counts["canonical"] += 1
                    self.stdout.write(f"CANONICAL {identity.storage_name} -> {identity.public_id}")
                    continue

                if canonical is not None or len(legacy_assets) > 1:
                    counts["conflict"] += 1
                    sources = ", ".join(public_id for _, public_id in legacy_assets)
                    self.stdout.write(
                        self.style.ERROR(
                            f"CONFLICT {identity.storage_name}: target={identity.public_id}; "
                            f"legacy={sources or 'none'}"
                        )
                    )
                    continue

                if not legacy_assets:
                    counts["missing"] += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"MISSING {identity.storage_name} -> {identity.public_id}"
                        )
                    )
                    continue

                category, source_public_id = legacy_assets[0]
                count_key = category.lower()
                counts[count_key] += 1
                if not apply_changes:
                    self.stdout.write(
                        self.style.WARNING(f"{category} {source_public_id} -> {identity.public_id}")
                    )
                    continue

                response = cloudinary.uploader.rename(
                    source_public_id,
                    identity.public_id,
                    resource_type=identity.resource_type,
                    type="upload",
                    overwrite=False,
                    invalidate=True,
                )
                if (
                    not isinstance(response, Mapping)
                    or response.get("public_id") != identity.public_id
                    or response.get("resource_type") != identity.resource_type
                    or str(response.get("format", "")).lower() != identity.format
                ):
                    raise RuntimeError("Cloudinary did not confirm the canonical asset identity.")
                counts["renamed"] += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"RENAMED {category} {source_public_id} -> {identity.public_id}"
                    )
                )
            except Exception:
                counts["errors"] += 1
                self.stderr.write(
                    self.style.ERROR(f"ERROR {identity.storage_name}: Cloudinary operation failed")
                )

        self.stdout.write(
            "Summary: " + ", ".join(f"{key}={value}" for key, value in counts.items())
        )
        if counts["errors"]:
            raise CommandError(
                f"Normalization completed with {counts['errors']} Cloudinary operation error(s)."
            )
        if counts["conflict"]:
            raise CommandError(
                f"Normalization found {counts['conflict']} conflict(s); manual review is required."
            )
