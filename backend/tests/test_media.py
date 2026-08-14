"""Comprehensive tests for media pipeline, upload security, variants, and lifecycle."""

import io
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from backend.apps.catalog.api.serializers import ProductImageSerializer
from backend.apps.catalog.models import Category, Product, ProductImage
from backend.apps.common.media import (
    MAX_IMAGE_SIZE_BYTES,
    MAX_VIDEO_SIZE_BYTES,
    SecureUploadPath,
    get_variant_path,
    validate_secure_image,
    validate_secure_video,
)
from backend.apps.content.models import GalleryItem


def create_test_image_file(
    name="test.jpg",
    size=(200, 200),
    format="JPEG",
    color=(200, 150, 50),
) -> SimpleUploadedFile:
    """Helper creating an in-memory valid image uploaded file."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    buf.seek(0)
    return SimpleUploadedFile(name, buf.getvalue(), content_type=f"image/{format.lower()}")


@pytest.mark.django_db
class TestImageValidation:
    """Verify security validation, format allowlisting, and dimension bounds."""

    def test_valid_jpeg_png_webp_accepted(self):
        for fmt, ext in [("JPEG", "jpg"), ("PNG", "png"), ("WEBP", "webp")]:
            upload = create_test_image_file(name=f"valid.{ext}", format=fmt)
            # Should not raise
            validate_secure_image(upload)

    def test_disallowed_extension_rejected(self):
        upload = SimpleUploadedFile(
            "evil.svg", b"<svg>alert(1)</svg>", content_type="image/svg+xml"
        )
        with pytest.raises(ValidationError) as exc:
            validate_secure_image(upload)
        assert "Unsupported image extension" in str(exc.value)

    def test_executable_extension_rejected(self):
        upload = SimpleUploadedFile(
            "script.php", b"<?php phpinfo(); ?>", content_type="application/x-php"
        )
        with pytest.raises(ValidationError) as exc:
            validate_secure_image(upload)
        assert "Unsupported image extension" in str(exc.value)

    def test_corrupt_image_content_rejected(self):
        # Named .jpg but containing random corrupt binary data
        upload = SimpleUploadedFile(
            "fake.jpg", b"NOT_A_REAL_IMAGE_DATA_12345", content_type="image/jpeg"
        )
        with pytest.raises(ValidationError) as exc:
            validate_secure_image(upload)
        assert "Corrupted or malicious image" in str(exc.value)

    def test_oversized_image_rejected(self):
        # Fake file with size exceeding 10 MB
        class FakeHugeFile:
            name = "huge.jpg"
            size = MAX_IMAGE_SIZE_BYTES + 1024

        with pytest.raises(ValidationError) as exc:
            validate_secure_image(FakeHugeFile())
        assert "exceeds the 10 MB limit" in str(exc.value)

    def test_excessive_dimensions_rejected(self):
        # Image exceeding 4096px dimension limit
        upload = create_test_image_file(name="bomb.jpg", size=(5000, 100))
        with pytest.raises(ValidationError) as exc:
            validate_secure_image(upload)
        assert "exceed maximum allowed" in str(exc.value)


@pytest.mark.django_db
class TestVideoValidation:
    """Verify video format allowlist and file size constraints."""

    def test_valid_mp4_video_accepted(self):
        upload = SimpleUploadedFile("demo.mp4", b"\x00\x00\x00 ftypisom", content_type="video/mp4")
        validate_secure_video(upload)

    def test_disallowed_video_extension_rejected(self):
        upload = SimpleUploadedFile("demo.avi", b"RIFF....AVI ", content_type="video/x-msvideo")
        with pytest.raises(ValidationError) as exc:
            validate_secure_video(upload)
        assert "Unsupported video extension" in str(exc.value)

    def test_oversized_video_rejected(self):
        class FakeHugeVideo:
            name = "huge.mp4"
            size = MAX_VIDEO_SIZE_BYTES + 1024

        with pytest.raises(ValidationError) as exc:
            validate_secure_video(FakeHugeVideo())
        assert "exceeds the 50 MB limit" in str(exc.value)


@pytest.mark.django_db
class TestSecureUploadPath:
    """Verify randomized UUID path generation and directory namespace isolation."""

    def test_path_randomization_ignores_dangerous_filename(self):
        generator = SecureUploadPath("products/images")
        result = generator(None, "../../../etc/passwd.jpg")

        assert "../" not in result
        assert result.startswith("products/images/")
        assert result.endswith(".jpg")
        # UUID length hex is 32 chars
        filename = Path(result).name
        assert len(filename.split(".")[0]) == 32


@pytest.mark.django_db(transaction=True)
class TestVariantGenerationAndSignals:
    """Verify WebP variant creation, EXIF stripping, and signal-driven cleanup."""

    @pytest.fixture(autouse=True)
    def setup_catalog(self):
        self.category = Category.objects.create(
            name="Rings",
            slug="rings",
        )
        self.product = Product.objects.create(
            name="Emerald Gold Ring",
            slug="emerald-gold-ring",
            category=self.category,
            base_price=Decimal("45000.00"),
        )

    def test_product_image_post_save_generates_webp_variants(self):
        upload = create_test_image_file(name="atelier_ring.jpg", size=(1200, 1200))
        prod_img = ProductImage.objects.create(
            product=self.product,
            image=upload,
            is_primary=True,
        )

        assert prod_img.image.name is not None
        storage_path = prod_img.image.name

        thumb_path = get_variant_path(storage_path, "thumb")
        med_path = get_variant_path(storage_path, "medium")
        lrg_path = get_variant_path(storage_path, "large")

        assert default_storage.exists(thumb_path)
        assert default_storage.exists(med_path)
        assert default_storage.exists(lrg_path)

        # Inspect generated thumbnail dimensions
        with default_storage.open(thumb_path, "rb") as f:
            with Image.open(f) as v_img:
                assert v_img.format == "WEBP"
                assert v_img.width <= 300
                assert v_img.height <= 300

        # Verify cleanup on deletion
        prod_img.delete()
        assert not default_storage.exists(storage_path)
        assert not default_storage.exists(thumb_path)
        assert not default_storage.exists(med_path)
        assert not default_storage.exists(lrg_path)

    def test_gallery_item_variant_generation_and_cleanup(self):
        upload = create_test_image_file(name="expo_lahore.png", size=(800, 600), format="PNG")
        gallery = GalleryItem.objects.create(
            title="Lahore Expo 2026",
            image=upload,
            item_type=GalleryItem.ItemType.EXHIBITION,
        )

        storage_path = gallery.image.name
        thumb_path = get_variant_path(storage_path, "thumb")
        assert default_storage.exists(thumb_path)

        gallery.delete()
        assert not default_storage.exists(storage_path)
        assert not default_storage.exists(thumb_path)

    def test_serializer_exposes_responsive_variant_urls(self):
        upload = create_test_image_file(name="bridal_piece.jpg", size=(600, 600))
        prod_img = ProductImage.objects.create(
            product=self.product,
            image=upload,
            is_primary=True,
            alt_text="Bridal Emerald Ring",
        )

        serializer = ProductImageSerializer(prod_img)
        data = serializer.data

        assert "image_url" in data
        assert "thumbnail_url" in data
        assert "medium_url" in data
        assert "large_url" in data
        assert data["thumbnail_url"].endswith("_thumb.webp")
        assert data["medium_url"].endswith("_medium.webp")
        assert data["large_url"].endswith("_large.webp")

        prod_img.delete()
