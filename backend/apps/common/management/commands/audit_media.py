"""Management command to audit media consistency, detect orphans, and safely clean stale files.

Features:
- Scans database references across catalog, content, and promotions models.
- Audits filesystem storage against known managed namespaces.
- Identifies missing referenced files, unreferenced orphan files, and stale variants.
- Dry-run by default with `--clean-orphans` option.
- Safety protection: `--older-than-hours` threshold to avoid deleting in-flight uploads.
- Structured security/operational event logging.
"""

import os
import time
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from backend.apps.catalog.models import ProductImage, ProductVideo
from backend.apps.common.media import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    IMAGE_VARIANTS,
    cleanup_storage_media,
    get_variant_path,
)
from backend.apps.common.security_events import log_security_event
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.models import Popup, Promotion

MANAGED_NAMESPACES = {
    "products/images",
    "products/videos",
    "gallery",
    "reviews",
    "about",
    "promotions",
    "popups",
}


class Command(BaseCommand):
    help = (
        "Audit media storage integrity, find missing referenced files, and detect orphan artifacts."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--clean-orphans",
            action="store_true",
            default=False,
            help="Perform actual deletion of unreferenced orphan files (default is dry-run).",
        )
        parser.add_argument(
            "--older-than-hours",
            type=float,
            default=24.0,
            help="Minimum age in hours for an orphan file before it is eligible for cleanup (default: 24.0).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Explicitly simulate audit without modifying storage.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        clean_orphans = options["clean_orphans"]
        older_than_hours = options["older_than_hours"]
        is_dry_run = options["dry_run"] or not clean_orphans

        self.stdout.write(self.style.MIGRATE_HEADING("=== Media Integrity & Orphan Audit ==="))
        self.stdout.write(
            f"Mode: {'DRY RUN (No files modified)' if is_dry_run else 'ACTIVE CLEANUP'}"
        )
        self.stdout.write(f"Orphan Age Threshold: {older_than_hours:.1f} hours\n")

        # 1. Collect all DB media references and expected variant paths
        referenced_files: set[str] = set()
        expected_variants: set[str] = set()
        missing_db_files: list[dict[str, Any]] = []

        models_to_scan = [
            (ProductImage, "image", "products/images"),
            (ProductVideo, "video_file", "products/videos"),
            (GalleryItem, "image", "gallery"),
            (Review, "image", "reviews"),
            (AboutSection, "image", "about"),
            (Promotion, "image", "promotions"),
            (Popup, "image", "popups"),
        ]

        total_db_records = 0

        for model, field_name, _namespace in models_to_scan:
            records = model.objects.exclude(**{f"{field_name}__isnull": True}).exclude(
                **{f"{field_name}": ""}
            )
            count = records.count()
            total_db_records += count

            for obj in records:
                file_field = getattr(obj, field_name, None)
                if not file_field or not file_field.name:
                    continue

                file_path = file_field.name.replace("\\", "/")
                referenced_files.add(file_path)

                # Check if original exists in storage
                if default_storage.exists(file_path):
                    # For images, calculate expected variant paths
                    if field_name == "image":
                        for var_name in IMAGE_VARIANTS.keys():
                            expected_variants.add(get_variant_path(file_path, var_name))
                else:
                    missing_info = {
                        "model": model.__name__,
                        "pk": obj.pk,
                        "field": field_name,
                        "file_path": file_path,
                    }
                    missing_db_files.append(missing_info)
                    log_security_event(
                        "media.audit_missing_reference",
                        severity="ERROR",
                        **missing_info,
                    )

        # 2. Walk storage directories under MEDIA_ROOT
        media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
        actual_files: list[dict[str, Any]] = []

        if media_root.exists():
            for root, _, filenames in os.walk(media_root):
                for fname in filenames:
                    abs_path = Path(root) / fname
                    rel_path = str(abs_path.relative_to(media_root)).replace("\\", "/")
                    try:
                        stat = abs_path.stat()
                        file_age_hours = (time.time() - stat.st_mtime) / 3600.0
                        file_size = stat.st_size
                    except OSError:
                        file_age_hours = 0
                        file_size = 0

                    actual_files.append(
                        {
                            "path": rel_path,
                            "size": file_size,
                            "age_hours": file_age_hours,
                            "extension": Path(fname).suffix.lower(),
                        }
                    )

        # 3. Categorize storage files
        orphans: list[dict[str, Any]] = []
        suspicious_files: list[dict[str, Any]] = []
        stale_variants: list[dict[str, Any]] = []
        allowed_all_extensions = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

        for file_info in actual_files:
            p = file_info["path"]
            ext = file_info["extension"]

            # Check if file is in managed namespace
            in_managed_ns = any(p.startswith(ns) for ns in MANAGED_NAMESPACES)

            if not in_managed_ns or ext not in allowed_all_extensions:
                suspicious_files.append(file_info)
                continue

            # Check if it is a referenced original or an expected active variant
            if p in referenced_files or p in expected_variants:
                continue

            # It is not directly referenced: check if it's an unreferenced variant or orphan original
            if any(p.endswith(f"_{v}.webp") for v in IMAGE_VARIANTS.keys()):
                stale_variants.append(file_info)
            else:
                orphans.append(file_info)
                log_security_event(
                    "media.audit_orphan_detected",
                    file_path=p,
                    size_bytes=file_info["size"],
                    age_hours=round(file_info["age_hours"], 2),
                )

        # 4. Print structured summary report
        self.stdout.write(self.style.SUCCESS(f"Total DB Records with Media: {total_db_records}"))
        self.stdout.write(f"Total Unique Referenced Files: {len(referenced_files)}")
        self.stdout.write(f"Total Files in Storage: {len(actual_files)}")
        self.stdout.write(f"Expected Active Variants: {len(expected_variants)}")

        if missing_db_files:
            self.stdout.write(
                self.style.ERROR(f"\n[!] Missing Referenced Files ({len(missing_db_files)}):")
            )
            for item in missing_db_files:
                self.stdout.write(f"  - {item['model']} (ID: {item['pk']}): {item['file_path']}")
        else:
            self.stdout.write(self.style.SUCCESS("\n[OK] No missing DB referenced files."))

        if suspicious_files:
            self.stdout.write(
                self.style.WARNING(f"\n[!] Suspicious / Unmanaged Files ({len(suspicious_files)}):")
            )
            for item in suspicious_files:
                self.stdout.write(
                    f"  - {item['path']} ({item['size']} bytes, ext: {item['extension']})"
                )

        all_cleanup_candidates = orphans + stale_variants
        eligible_for_deletion = [
            c for c in all_cleanup_candidates if c["age_hours"] >= older_than_hours
        ]

        self.stdout.write(
            f"\nUnreferenced Orphans: {len(orphans)} | Stale Variants: {len(stale_variants)} | Eligible for cleanup: {len(eligible_for_deletion)}"
        )

        # 5. Perform cleanup if explicitly requested and safe
        if clean_orphans and not options.get("dry_run", False):
            deleted_count = 0
            for item in eligible_for_deletion:
                p = item["path"]
                # Safety checks: Never delete referenced files or outside managed namespaces
                if p in referenced_files or not any(p.startswith(ns) for ns in MANAGED_NAMESPACES):
                    continue

                try:
                    cleanup_storage_media(p)
                    deleted_count += 1
                    self.stdout.write(f"  Deleted orphan: {p}")
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"  Failed to delete {p}: {exc}"))

            self.stdout.write(
                self.style.SUCCESS(f"\n[OK] Safely cleaned {deleted_count} orphan/stale files.")
            )
        else:
            if eligible_for_deletion:
                self.stdout.write(self.style.WARNING("\nCandidates for deletion (Dry-run mode):"))
                for c in eligible_for_deletion[:20]:
                    self.stdout.write(
                        f"  - {c['path']} (Age: {c['age_hours']:.1f}h, Size: {c['size']} bytes)"
                    )
                if len(eligible_for_deletion) > 20:
                    self.stdout.write(f"  ... and {len(eligible_for_deletion) - 20} more.")
                self.stdout.write(
                    "\nTo delete eligible orphans, run with: python manage.py audit_media --clean-orphans --no-dry-run"
                )
