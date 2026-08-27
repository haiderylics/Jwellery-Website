"""Unit coverage for the official Cloudinary-backed production storage."""

from io import BytesIO
from unittest.mock import patch

import pytest
from django.core.checks import run_checks
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage, storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from PIL import Image

from backend.apps.catalog.api.serializers import ProductImageSerializer
from backend.apps.catalog.models import Category, Product, ProductImage
from backend.apps.common.cloudinary_storage import CloudinaryMediaStorage


def test_cloudinary_storage_uploads_server_generated_key_and_returns_https_url() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    content = BytesIO(b"image bytes")

    with (
        patch("cloudinary.uploader.upload") as upload,
        patch(
            "cloudinary.utils.cloudinary_url",
            return_value=("https://res.cloudinary.com/test/image", {}),
        ),
    ):
        name = storage._save("products/images/2026/08/uuid.jpg", content)
        url = storage.url(name)

    assert name == "products/images/2026/08/uuid.jpg"
    assert upload.call_args.kwargs["resource_type"] == "image"
    assert upload.call_args.kwargs["public_id"] == name
    assert url.startswith("https://")


def test_cloudinary_storage_uses_video_resource_type_and_deletes_with_invalidation() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    name = "products/videos/2026/08/uuid.mp4"

    with patch("cloudinary.uploader.destroy") as destroy:
        storage.delete(name)

    assert destroy.call_args.kwargs == {
        "resource_type": "video",
        "invalidate": True,
    }


def test_cloudinary_storage_fails_without_credentials_instead_of_using_local_media() -> None:
    with pytest.raises(ImproperlyConfigured, match="Cloudinary media storage requires"):
        CloudinaryMediaStorage(cloud_name="", api_key="", api_secret="")


@override_settings(
    DEBUG=False,
    STORAGES={
        "default": {
            "BACKEND": "backend.apps.common.cloudinary_storage.CloudinaryMediaStorage",
            "OPTIONS": {"cloud_name": "", "api_key": "", "api_secret": ""},
        },
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    },
)
def test_missing_cloudinary_credentials_fail_deploy_check_and_readiness_safely() -> None:
    errors = run_checks(include_deployment_checks=True)
    assert any(error.id == "common.E001" for error in errors)

    response = Client().get("/health/ready/")
    assert response.status_code == 503
    assert response.json() == {"status": "unready"}


@pytest.mark.django_db
@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "backend.apps.common.cloudinary_storage.CloudinaryMediaStorage",
            "OPTIONS": {
                "cloud_name": "test-cloud",
                "api_key": "test-key",
                "api_secret": "test-secret",
            },
        },
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
)
def test_product_image_uses_django_default_storage_and_cloudinary_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image_buffer = BytesIO()
    Image.new("RGB", (20, 20), color="gold").save(image_buffer, format="JPEG")
    upload_file = SimpleUploadedFile("ring.jpg", image_buffer.getvalue(), content_type="image/jpeg")
    storages._storages.pop("default", None)
    monkeypatch.setattr(default_storage, "_wrapped", storages["default"])

    category = Category.objects.create(name="Rings", slug="rings")
    product = Product.objects.create(
        name="Cloudinary Ring", slug="cloudinary-ring", category=category, base_price=1000
    )
    with (
        patch("cloudinary.uploader.upload") as cloudinary_upload,
        patch(
            "cloudinary.utils.cloudinary_url",
            return_value=("https://res.cloudinary.com/test-cloud/image/upload/ring.jpg", {}),
        ),
    ):
        product_image = ProductImage.objects.create(product=product, image=upload_file)
        payload = ProductImageSerializer(product_image).data

    assert product_image.image.name.startswith("products/images/")
    assert cloudinary_upload.call_count == 1
    assert payload["image_url"].startswith("https://res.cloudinary.com/")
    assert "test-key" not in str(payload)
    assert "test-secret" not in str(payload)
