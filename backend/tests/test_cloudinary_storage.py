"""Unit coverage for the official Cloudinary-backed production storage."""

from io import BytesIO
from unittest.mock import Mock, patch

import cloudinary.uploader
import pytest
from django.contrib.auth import get_user_model
from django.core.checks import run_checks
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage, storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from PIL import Image

from backend.apps.catalog.api.serializers import ProductImageSerializer
from backend.apps.catalog.models import Category, Product, ProductImage
from backend.apps.common.cloudinary_storage import CloudinaryMediaStorage


def _image_upload(name: str = "ring.png", *, valid: bool = True) -> SimpleUploadedFile:
    if not valid:
        return SimpleUploadedFile(name, b"not an image", content_type="image/png")

    image_buffer = BytesIO()
    Image.new("RGB", (20, 20), color="gold").save(image_buffer, format="PNG")
    return SimpleUploadedFile(name, image_buffer.getvalue(), content_type="image/png")


def _product_change_data(product: Product, product_image: ProductImage) -> dict[str, object]:
    """Return a complete Product admin payload retaining its existing image inline."""
    return {
        "name": product.name,
        "slug": product.slug,
        "short_description": product.short_description,
        "description": product.description,
        "category": str(product.category_id),
        "base_price": str(product.base_price),
        "compare_at_price": "",
        "stock_quantity": str(product.stock_quantity),
        "availability_status": product.availability_status,
        "is_published": "on",
        "sort_priority": str(product.sort_priority),
        "seo_title": product.seo_title,
        "seo_description": product.seo_description,
        "images-TOTAL_FORMS": "2",
        "images-INITIAL_FORMS": "1",
        "images-MIN_NUM_FORMS": "0",
        "images-MAX_NUM_FORMS": "1000",
        "images-0-id": str(product_image.pk),
        "images-0-product": str(product.pk),
        "images-0-alt_text": product_image.alt_text,
        "images-0-sort_order": str(product_image.sort_order),
        "images-1-alt_text": "",
        "images-1-sort_order": "0",
        "variants-TOTAL_FORMS": "0",
        "variants-INITIAL_FORMS": "0",
        "variants-MIN_NUM_FORMS": "0",
        "variants-MAX_NUM_FORMS": "1000",
        "video-TOTAL_FORMS": "0",
        "video-INITIAL_FORMS": "0",
        "video-MIN_NUM_FORMS": "0",
        "video-MAX_NUM_FORMS": "1",
        "_save": "Save",
    }


@pytest.fixture
def cloudinary_admin_product(
    monkeypatch: pytest.MonkeyPatch, client: Client
) -> tuple[Client, Product, ProductImage, CloudinaryMediaStorage, Mock]:
    """Create an admin-editable product whose existing image is in Cloudinary."""
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    monkeypatch.setitem(storages._storages, "default", storage)
    monkeypatch.setattr(default_storage, "_wrapped", storage)
    upload = Mock()
    monkeypatch.setattr(cloudinary.uploader, "upload", upload)

    category = Category.objects.create(name="Admin Rings", slug="admin-rings")
    product = Product.objects.create(
        name="Admin Cloudinary Ring",
        slug="admin-cloudinary-ring",
        category=category,
        base_price=1000,
    )
    product_image = ProductImage.objects.create(product=product, image=_image_upload())
    assert upload.call_count == 1
    upload.reset_mock()

    user = get_user_model().objects.create_superuser(
        username="cloudinary-admin",
        email="cloudinary-admin@example.test",
        password="test-password-not-used",
    )
    client.force_login(user)
    return client, product, product_image, storage, upload


def test_cloudinary_storage_uploads_server_generated_key_and_returns_https_url() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    image_buffer = BytesIO()
    Image.new("RGB", (20, 20), color="gold").save(image_buffer, format="PNG")
    content = SimpleUploadedFile("source.png", image_buffer.getvalue(), content_type="image/png")

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


def test_corrupt_image_is_rejected_before_cloudinary_upload() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )

    with (
        patch("cloudinary.uploader.upload") as upload,
        pytest.raises(Exception, match="Corrupted or malicious image"),
    ):
        storage._save(
            "products/images/2026/08/broken.jpg",
            SimpleUploadedFile("broken.jpg", b"not an image", content_type="image/jpeg"),
        )

    upload.assert_not_called()


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
    cloud_storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    monkeypatch.setitem(storages._storages, "default", cloud_storage)
    monkeypatch.setattr(default_storage, "_wrapped", cloud_storage)

    category = Category.objects.create(name="Rings", slug="rings")
    product = Product.objects.create(
        name="Cloudinary Ring", slug="cloudinary-ring", category=category, base_price=1000
    )
    with (
        patch("cloudinary.uploader.upload") as cloudinary_upload,
        patch("backend.apps.common.signals.generate_image_variants") as generate_variants,
        patch.object(
            CloudinaryMediaStorage,
            "open",
            side_effect=AssertionError("Cloudinary media must not be reopened after upload"),
        ),
        patch(
            "cloudinary.utils.cloudinary_url",
            return_value=("https://res.cloudinary.com/test-cloud/image/upload/ring.jpg", {}),
        ),
    ):
        product_image = ProductImage.objects.create(product=product, image=upload_file)
        payload = ProductImageSerializer(product_image).data

    assert product_image.image.name.startswith("products/images/")
    assert cloudinary_upload.call_count == 1
    generate_variants.assert_not_called()
    assert payload["image_url"].startswith("https://res.cloudinary.com/")
    assert payload["thumbnail_url"].startswith("https://res.cloudinary.com/")
    assert payload["medium_url"].startswith("https://res.cloudinary.com/")
    assert payload["large_url"].startswith("https://res.cloudinary.com/")
    assert "test-key" not in str(payload)
    assert "test-secret" not in str(payload)


@pytest.mark.django_db
def test_product_admin_retains_existing_cloudinary_image_without_reopening(
    cloudinary_admin_product: tuple[Client, Product, ProductImage, CloudinaryMediaStorage, Mock],
) -> None:
    client, product, product_image, storage, upload = cloudinary_admin_product
    url = f"/admin/catalog/product/{product.pk}/change/"

    with patch.object(
        storage,
        "open",
        side_effect=AssertionError("An unchanged Cloudinary image must not be reopened"),
    ) as storage_open:
        get_response = client.get(url)
        post_data = _product_change_data(product, product_image)
        post_data["name"] = "Admin Cloudinary Ring Updated"
        post_response = client.post(url, data=post_data)

    assert get_response.status_code == 200
    assert post_response.status_code == 302, (
        post_response.context_data["adminform"].form.errors,
        [inline.formset.errors for inline in post_response.context_data["inline_admin_formsets"]],
    )
    product.refresh_from_db()
    product_image.refresh_from_db()
    assert product.name == "Admin Cloudinary Ring Updated"
    assert product_image.image.name.startswith("products/images/")
    storage_open.assert_not_called()
    upload.assert_not_called()


@pytest.mark.django_db
def test_product_admin_replacement_validates_once_and_cleans_old_asset_after_commit(
    cloudinary_admin_product: tuple[Client, Product, ProductImage, CloudinaryMediaStorage, Mock],
    django_capture_on_commit_callbacks,
) -> None:
    client, product, product_image, storage, upload = cloudinary_admin_product
    old_name = product_image.image.name
    post_data = _product_change_data(product, product_image)
    post_data["images-0-image"] = _image_upload("replacement.png")

    with (
        patch.object(
            storage,
            "open",
            side_effect=AssertionError("A new upload must be validated from its incoming stream"),
        ) as storage_open,
        patch("cloudinary.uploader.destroy") as destroy,
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = client.post(
            f"/admin/catalog/product/{product.pk}/change/",
            data=post_data,
        )

    assert response.status_code == 302, (
        response.context_data["adminform"].form.errors,
        [inline.formset.errors for inline in response.context_data["inline_admin_formsets"]],
    )
    product_image.refresh_from_db()
    assert product_image.image.name != old_name
    assert product_image.image.name.startswith("products/images/")
    upload.assert_called_once()
    storage_open.assert_not_called()
    destroy.assert_called_once_with(old_name, resource_type="image", invalidate=True)


@pytest.mark.django_db
def test_product_admin_rejects_corrupt_replacement_before_cloudinary_upload(
    cloudinary_admin_product: tuple[Client, Product, ProductImage, CloudinaryMediaStorage, Mock],
) -> None:
    client, product, product_image, storage, upload = cloudinary_admin_product
    old_name = product_image.image.name
    post_data = _product_change_data(product, product_image)
    post_data["images-0-image"] = _image_upload("corrupt.png", valid=False)

    with patch.object(
        storage,
        "open",
        side_effect=AssertionError("Corrupt incoming bytes must not trigger a storage read"),
    ) as storage_open:
        response = client.post(
            f"/admin/catalog/product/{product.pk}/change/",
            data=post_data,
        )

    assert response.status_code == 200
    assert b"Upload a valid image" in response.content
    product_image.refresh_from_db()
    assert product_image.image.name == old_name
    upload.assert_not_called()
    storage_open.assert_not_called()
