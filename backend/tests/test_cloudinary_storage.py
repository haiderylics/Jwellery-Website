"""Unit coverage for the official Cloudinary-backed production storage."""

from io import BytesIO
from pathlib import Path, PurePosixPath
from unittest.mock import Mock, patch

import cloudinary.api
import cloudinary.uploader
import pytest
from cloudinary.exceptions import NotFound
from django.contrib.auth import get_user_model
from django.core.checks import run_checks
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage, storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.test import Client, override_settings
from PIL import Image

from backend.apps.catalog.api.serializers import ProductImageSerializer
from backend.apps.catalog.models import Category, Product, ProductImage
from backend.apps.common.cloudinary_storage import (
    CloudinaryMediaStorage,
    CloudinaryStorageError,
    cloudinary_asset_identity,
    cloudinary_transformed_url,
)


def _image_upload(name: str = "ring.png", *, valid: bool = True) -> SimpleUploadedFile:
    if not valid:
        return SimpleUploadedFile(name, b"not an image", content_type="image/png")

    image_buffer = BytesIO()
    Image.new("RGB", (20, 20), color="gold").save(image_buffer, format="PNG")
    return SimpleUploadedFile(name, image_buffer.getvalue(), content_type="image/png")


def _successful_upload_response(file_obj, **options):
    asset_format = Path(file_obj.name).suffix.lower().lstrip(".")
    if asset_format == "jpeg":
        asset_format = "jpg"
    return {
        "public_id": options["public_id"],
        "resource_type": options["resource_type"],
        "format": asset_format,
        "secure_url": (
            f"https://res.cloudinary.com/test-cloud/{options['resource_type']}/upload/"
            f"{options['public_id']}.{asset_format}"
        ),
    }


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
    upload = Mock(side_effect=_successful_upload_response)
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

    with patch("cloudinary.uploader.upload", side_effect=_successful_upload_response) as upload:
        name = storage._save("products/images/2026/08/uuid.png", content)
        url = storage.url(name)

    assert name == "products/images/2026/08/uuid.png"
    upload.assert_called_once()
    assert upload.call_args.kwargs["resource_type"] == "image"
    assert upload.call_args.kwargs["type"] == "upload"
    assert upload.call_args.kwargs["public_id"] == "catalog/products/photos/2026/08/uuid"
    assert PurePosixPath(upload.call_args.kwargs["public_id"]).suffix == ""
    assert url == (
        "https://res.cloudinary.com/test-cloud/image/upload/"
        "catalog/products/photos/2026/08/uuid.png"
    )
    assert ".png.png" not in url
    assert "/v1/" not in url


def test_cloudinary_asset_identity_is_posix_extensionless_and_format_aware() -> None:
    image = cloudinary_asset_identity(r"products\images\2026\08\abc.jpeg")
    video = cloudinary_asset_identity("products/videos/2026/08/demo.mp4")
    future_image = cloudinary_asset_identity("catalog/products/photos/2026/08/future.webp")
    future_video = cloudinary_asset_identity("catalog/products/clips/2026/08/future.webm")

    assert image.storage_name == "products/images/2026/08/abc.jpeg"
    assert image.public_id == "catalog/products/photos/2026/08/abc"
    assert image.format == "jpg"
    assert image.resource_type == "image"
    assert image.legacy_extensionful_public_id == "products/images/2026/08/abc.jpeg"
    assert image.legacy_reserved_namespace_public_id == "products/images/2026/08/abc"
    assert video.public_id == "catalog/products/clips/2026/08/demo"
    assert video.format == "mp4"
    assert video.resource_type == "video"
    assert video.legacy_reserved_namespace_public_id == "products/videos/2026/08/demo"
    assert future_image.public_id == "catalog/products/photos/2026/08/future"
    assert future_image.legacy_reserved_namespace_public_id is None
    assert future_video.public_id == "catalog/products/clips/2026/08/future"
    assert future_video.resource_type == "video"
    for identity in (image, video, future_image, future_video):
        assert "images" not in PurePosixPath(identity.public_id).parts
        assert "videos" not in PurePosixPath(identity.public_id).parts
        assert PurePosixPath(identity.public_id).suffix == ""


@pytest.mark.parametrize(
    "name, message",
    [
        ("campaign/images/2026/08/abc.png", "reserved"),
        ("campaign/videos/2026/08/abc.mp4", "reserved"),
        ("catalog/v123/photos/abc.png", "version-like"),
        ("ab_variant/photos/abc.png", "transformation-like"),
    ],
)
def test_cloudinary_asset_identity_rejects_unsafe_future_paths(name: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        cloudinary_asset_identity(name)


def test_cloudinary_transformed_urls_share_canonical_public_id() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    name = "products/images/2026/08/abc.png"

    original = storage.url(name)
    transformed = cloudinary_transformed_url(name, 1600)

    assert original.endswith("/catalog/products/photos/2026/08/abc.png")
    assert transformed.endswith("/catalog/products/photos/2026/08/abc.png")
    assert "c_limit,f_auto,q_auto,w_1600" in transformed
    assert ".png.png" not in original + transformed
    assert "/v1/" not in original + transformed

    with pytest.raises(ValueError, match="cannot be applied to video"):
        cloudinary_transformed_url("products/videos/2026/08/demo.mp4", 800)


def test_cloudinary_upload_rejects_mismatched_response_identity() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )

    with (
        patch(
            "cloudinary.uploader.upload",
            return_value={
                "public_id": "wrong/id",
                "resource_type": "image",
                "format": "png",
                "secure_url": "https://res.cloudinary.com/test-cloud/image/upload/wrong.png",
            },
        ),
        pytest.raises(CloudinaryStorageError, match="did not match"),
    ):
        storage._save("products/images/2026/08/abc.png", _image_upload())


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

    with patch("cloudinary.uploader.destroy", return_value={"result": "ok"}) as destroy:
        storage.delete(name)

    destroy.assert_called_once_with(
        "catalog/products/clips/2026/08/uuid",
        resource_type="video",
        type="upload",
        invalidate=True,
    )


def test_cloudinary_video_upload_uses_extensionless_public_id_once() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    content = SimpleUploadedFile("demo.mp4", b"\x00\x00\x00 ftypisom", content_type="video/mp4")

    with patch("cloudinary.uploader.upload", side_effect=_successful_upload_response) as upload:
        name = storage._save("products/videos/2026/08/uuid.mp4", content)

    assert name == "products/videos/2026/08/uuid.mp4"
    upload.assert_called_once()
    assert upload.call_args.kwargs["public_id"] == "catalog/products/clips/2026/08/uuid"
    assert PurePosixPath(upload.call_args.kwargs["public_id"]).suffix == ""
    assert upload.call_args.kwargs["resource_type"] == "video"
    assert upload.call_args.kwargs["type"] == "upload"


def test_cloudinary_delete_not_found_is_idempotent() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    with patch("cloudinary.uploader.destroy", return_value={"result": "not found"}) as destroy:
        storage.delete("products/images/2026/08/missing.png")

    destroy.assert_called_once_with(
        "catalog/products/photos/2026/08/missing",
        resource_type="image",
        type="upload",
        invalidate=True,
    )


def test_cloudinary_delete_surfaces_unconfirmed_response() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    with (
        patch("cloudinary.uploader.destroy", return_value={"result": "error"}),
        pytest.raises(CloudinaryStorageError, match="did not confirm deletion"),
    ):
        storage.delete("products/images/2026/08/abc.png")


def test_cloudinary_exists_and_size_lookup_extensionless_identity() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    name = "products/images/2026/08/abc.png"

    with patch("cloudinary.api.resource", return_value={"bytes": 321}) as resource:
        assert storage.exists(name) is True
        assert storage.size(name) == 321

    assert resource.call_count == 2
    resource.assert_called_with(
        "catalog/products/photos/2026/08/abc",
        resource_type="image",
        type="upload",
    )


def test_cloudinary_exists_and_size_handle_not_found_without_leaking_sdk_error() -> None:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    name = "products/images/2026/08/missing.png"

    with patch("cloudinary.api.resource", side_effect=NotFound("remote detail")):
        assert storage.exists(name) is False
        with pytest.raises(FileNotFoundError, match="products/images/2026/08/missing.png"):
            storage.size(name)


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
        patch(
            "cloudinary.uploader.upload", side_effect=_successful_upload_response
        ) as cloudinary_upload,
        patch("cloudinary.api.resource") as cloudinary_resource,
        patch("backend.apps.common.signals.generate_image_variants") as generate_variants,
        patch.object(
            CloudinaryMediaStorage,
            "open",
            side_effect=AssertionError("Cloudinary media must not be reopened after upload"),
        ),
    ):
        product_image = ProductImage.objects.create(product=product, image=upload_file)
        payload = ProductImageSerializer(product_image).data

    assert product_image.image.name.startswith("products/images/")
    assert cloudinary_upload.call_count == 1
    cloudinary_resource.assert_not_called()
    generate_variants.assert_not_called()
    assert payload["image_url"].startswith("https://res.cloudinary.com/")
    assert payload["thumbnail_url"].startswith("https://res.cloudinary.com/")
    assert payload["medium_url"].startswith("https://res.cloudinary.com/")
    assert payload["large_url"].startswith("https://res.cloudinary.com/")
    assert "c_limit,f_auto,q_auto,w_300" in payload["thumbnail_url"]
    assert "c_limit,f_auto,q_auto,w_800" in payload["medium_url"]
    assert "c_limit,f_auto,q_auto,w_1600" in payload["large_url"]
    for url in (
        payload["image_url"],
        payload["thumbnail_url"],
        payload["medium_url"],
        payload["large_url"],
    ):
        assert "/catalog/products/photos/" in url
        assert "/images/" not in url
        assert "/videos/" not in url
        assert ".jpg.jpg" not in url
        assert "/v1/" not in url
        assert "/media/" not in url
        assert url.startswith("https://")
    assert "test-key" not in str(payload)
    assert "test-secret" not in str(payload)


@pytest.mark.django_db
def test_product_admin_retains_existing_cloudinary_image_without_reopening(
    cloudinary_admin_product: tuple[Client, Product, ProductImage, CloudinaryMediaStorage, Mock],
) -> None:
    client, product, product_image, storage, upload = cloudinary_admin_product
    url = f"/admin/catalog/product/{product.pk}/change/"

    with (
        patch.object(
            storage,
            "open",
            side_effect=AssertionError("An unchanged Cloudinary image must not be reopened"),
        ) as storage_open,
        patch.object(
            storage,
            "size",
            side_effect=AssertionError("An unchanged Cloudinary image must not fetch size"),
        ) as storage_size,
        patch("cloudinary.api.resource") as resource,
    ):
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
    storage_size.assert_not_called()
    resource.assert_not_called()
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
        patch("cloudinary.uploader.destroy", return_value={"result": "ok"}) as destroy,
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
    old_identity = cloudinary_asset_identity(old_name)
    destroy.assert_called_once_with(
        old_identity.public_id,
        resource_type="image",
        type="upload",
        invalidate=True,
    )


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


@pytest.mark.django_db(transaction=True)
def test_product_image_replacement_rollback_never_deletes_old_cloudinary_asset(
    cloudinary_admin_product: tuple[Client, Product, ProductImage, CloudinaryMediaStorage, Mock],
) -> None:
    _client, _product, product_image, _storage, upload = cloudinary_admin_product
    old_name = product_image.image.name

    with (
        patch("cloudinary.uploader.destroy", return_value={"result": "ok"}) as destroy,
        pytest.raises(RuntimeError, match="force rollback"),
    ):
        with transaction.atomic():
            product_image.image = _image_upload("replacement.png")
            product_image.save()
            raise RuntimeError("force rollback")

    product_image.refresh_from_db()
    assert product_image.image.name == old_name
    upload.assert_called_once()
    destroy.assert_not_called()
