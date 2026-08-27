"""Secure media pipeline, validators, and image variant generator.

Features:
- Strict MIME & magic byte validation
- Decompression bomb & dimension limits protection
- EXIF metadata stripping for privacy (GPS, camera tags)
- Safe randomized UUID path generator
- WebP responsive variants generation (thumb, medium, large)
- Safe media file cleanup helpers
"""

import io
import logging
import uuid
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from PIL import Image, ImageOps

from backend.apps.common.security_events import log_security_event

logger = logging.getLogger(__name__)

# Constants
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "AVIF"}

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}

MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
MAX_IMAGE_PIXELS = 16_000_000  # 16 Megapixels

# Explicitly set Pillow's global decompression bomb limit
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

# Variant size specifications (max bounding box width x height)
IMAGE_VARIANTS = {
    "thumb": (300, 300),
    "medium": (800, 800),
    "large": (1600, 1600),
}


def validate_secure_image(file_obj: Any) -> None:
    """Validate uploaded image file for size, format, dimensions, and decompression safety."""
    if not file_obj:
        return

    filename = getattr(file_obj, "name", "unknown")
    size = getattr(file_obj, "size", 0)

    # 1. File size check
    if hasattr(file_obj, "size") and file_obj.size > MAX_IMAGE_SIZE_BYTES:
        log_security_event(
            "security.upload_rejected",
            reason="file_size_exceeded",
            filename=Path(filename).name,
            size_bytes=size,
            max_bytes=MAX_IMAGE_SIZE_BYTES,
        )
        raise ValidationError(
            f"Image file size exceeds the 10 MB limit (got {file_obj.size / (1024 * 1024):.1f} MB)."
        )

    # 2. Extension check
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        log_security_event(
            "security.upload_rejected",
            reason="unsupported_extension",
            filename=Path(filename).name,
            extension=ext,
        )
        raise ValidationError(
            f"Unsupported image extension '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}."
        )

    # 3. Content inspection & verification via Pillow
    try:
        # Seek to beginning
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        img = Image.open(file_obj)
        img_format = img.format

        if not img_format or img_format.upper() not in ALLOWED_IMAGE_FORMATS:
            log_security_event(
                "security.upload_rejected",
                reason="invalid_mime_content",
                filename=Path(filename).name,
                detected_format=str(img_format),
            )
            raise ValidationError(
                f"Invalid or corrupted image content. Detected format: '{img_format}' is not permitted."
            )

        width, height = img.size
        if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
            log_security_event(
                "security.upload_rejected",
                reason="excessive_dimensions",
                filename=Path(filename).name,
                width=width,
                height=height,
            )
            raise ValidationError(
                f"Image dimensions ({width}x{height}) exceed maximum allowed {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}px."
            )

        if (width * height) > MAX_IMAGE_PIXELS:
            log_security_event(
                "security.upload_rejected",
                reason="decompression_bomb_pixel_cap",
                filename=Path(filename).name,
                pixels=width * height,
            )
            raise ValidationError(
                f"Image pixel count ({width * height:,}) exceeds maximum permitted {MAX_IMAGE_PIXELS:,} pixels."
            )

        # Integrity verification
        img.verify()

        # Reset pointer for subsequent reads
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

    except ValidationError:
        raise
    except Exception as exc:
        log_security_event(
            "security.upload_rejected",
            reason="corrupted_image_parse_failure",
            filename=Path(filename).name,
            error=str(exc),
        )
        raise ValidationError(f"Corrupted or malicious image file rejected: {exc}") from exc


def prepare_secure_image_upload(file_obj: Any) -> ContentFile:
    """Validate and privacy-normalize an incoming image before it reaches remote storage.

    This deliberately operates on the uploaded stream, never on a stored
    ``FieldFile``.  It corrects EXIF orientation and re-encodes the image
    without EXIF metadata, including GPS/camera information.
    """
    validate_secure_image(file_obj)
    filename = Path(getattr(file_obj, "name", "upload.jpg")).name

    try:
        file_obj.seek(0)
        with Image.open(file_obj) as source:
            image = ImageOps.exif_transpose(source)
            image_format = source.format.upper() if source.format else "JPEG"

            # Preserve alpha where the source format supports it.
            if image_format == "JPEG":
                image = image.convert("RGB")
            elif image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")

            output = io.BytesIO()
            save_kwargs: dict[str, Any] = {}
            if image_format in {"JPEG", "WEBP"}:
                save_kwargs["quality"] = 90
            image.save(output, format=image_format, **save_kwargs)
    except Exception as exc:
        # This is a processing failure on the incoming stream, not a storage
        # error. Do not let callers misclassify backend failures as corruption.
        log_security_event(
            "security.upload_rejected",
            reason="image_normalization_failure",
            filename=filename,
            error=str(exc),
        )
        raise ValidationError("Image could not be safely normalized.") from exc
    finally:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

    return ContentFile(output.getvalue(), name=filename)


def validate_secure_video(file_obj: Any) -> None:
    """Validate uploaded video file for size and extension allowlist."""
    if not file_obj:
        return

    filename = getattr(file_obj, "name", "unknown")
    size = getattr(file_obj, "size", 0)

    if hasattr(file_obj, "size") and file_obj.size > MAX_VIDEO_SIZE_BYTES:
        log_security_event(
            "security.upload_rejected",
            reason="video_size_exceeded",
            filename=Path(filename).name,
            size_bytes=size,
            max_bytes=MAX_VIDEO_SIZE_BYTES,
        )
        raise ValidationError(
            f"Video file size exceeds the 50 MB limit (got {file_obj.size / (1024 * 1024):.1f} MB)."
        )

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        log_security_event(
            "security.upload_rejected",
            reason="unsupported_video_extension",
            filename=Path(filename).name,
            extension=ext,
        )
        raise ValidationError(
            f"Unsupported video extension '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}."
        )


@deconstructible
class SecureUploadPath:
    """Deconstructible upload path generator creating randomized UUID filenames under a controlled prefix."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, instance: Any, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if not ext or ext not in (ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS):
            ext = ".jpg"

        now = timezone.now()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return f"{self.prefix}/{now.year:04d}/{now.month:02d}/{unique_name}"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SecureUploadPath) and self.prefix == other.prefix


# Backward-compatible alias
secure_upload_path = SecureUploadPath


def get_variant_path(original_path: str, variant_name: str) -> str:
    """Derive deterministic variant path from original media path."""
    p = Path(original_path)
    return str(p.parent / f"{p.stem}_{variant_name}.webp").replace("\\", "/")


def generate_image_variants(storage_file_path: str) -> dict[str, str]:
    """Generate optimized WebP responsive variants (thumb, medium, large) and strip EXIF metadata.

    Returns a dict mapping variant name to storage path.
    """
    if getattr(default_storage, "is_cloudinary_storage", False):
        # Cloudinary serves the fixed responsive URLs below on demand and caches
        # them at the CDN, avoiding three duplicate stored files per upload.
        return {}

    if not default_storage.exists(storage_file_path):
        return {}

    generated_variants: dict[str, str] = {}

    try:
        with default_storage.open(storage_file_path, "rb") as f:
            raw_bytes = f.read()

        with Image.open(io.BytesIO(raw_bytes)) as img:
            # 1. Normalize orientation from EXIF before stripping metadata
            img = ImageOps.exif_transpose(img)

            # Convert to RGB if in CMYK or palette mode with alpha handling
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img_rgb = img.convert("RGBA")
            else:
                img_rgb = img.convert("RGB")

            orig_w, orig_h = img_rgb.size

            for variant_name, (max_w, max_h) in IMAGE_VARIANTS.items():
                variant_path = get_variant_path(storage_file_path, variant_name)

                # Resize preserving aspect ratio (shrink only)
                var_img = img_rgb.copy()
                var_img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

                # Save as optimized WebP without EXIF
                out_buffer = io.BytesIO()
                var_img.save(
                    out_buffer,
                    format="WEBP",
                    quality=85 if variant_name == "large" else 80,
                    method=4,
                )
                out_buffer.seek(0)

                # Save to Django storage
                if default_storage.exists(variant_path):
                    default_storage.delete(variant_path)
                default_storage.save(variant_path, ContentFile(out_buffer.getvalue()))
                generated_variants[variant_name] = variant_path

    except Exception as exc:
        log_security_event(
            "media.processing_failed",
            severity="ERROR",
            file_path=storage_file_path,
            error=str(exc),
        )
        logger.warning(
            "Failed to generate responsive variants for '%s': %s",
            storage_file_path,
            exc,
            exc_info=True,
        )

    return generated_variants


def cleanup_storage_media(storage_file_path: str) -> None:
    """Safely delete original media file and all generated responsive variants."""
    if not storage_file_path:
        return

    try:
        if getattr(default_storage, "is_cloudinary_storage", False):
            default_storage.delete(storage_file_path)
            return

        # Delete variants
        for variant_name in IMAGE_VARIANTS.keys():
            var_path = get_variant_path(storage_file_path, variant_name)
            if default_storage.exists(var_path):
                default_storage.delete(var_path)

        # Delete original
        if default_storage.exists(storage_file_path):
            default_storage.delete(storage_file_path)
    except Exception as exc:
        logger.warning("Error cleaning up media file '%s': %s", storage_file_path, exc)


def get_variant_url(image_field: Any, variant_name: str, request: Any = None) -> str | None:
    """Get absolute or relative URL for a specific image variant, falling back to original if variant is missing."""
    if not image_field or not getattr(image_field, "name", None):
        return None

    if getattr(default_storage, "is_cloudinary_storage", False):
        from backend.apps.common.cloudinary_storage import cloudinary_transformed_url

        return cloudinary_transformed_url(image_field.name, IMAGE_VARIANTS[variant_name][0])

    variant_path = get_variant_path(image_field.name, variant_name)
    if default_storage.exists(variant_path):
        url = default_storage.url(variant_path)
    else:
        url = image_field.url

    if request:
        return request.build_absolute_uri(url)
    return url
