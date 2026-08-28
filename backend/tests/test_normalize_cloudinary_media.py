"""Regression coverage for DB-bounded legacy Cloudinary identity normalization."""

import io
from unittest.mock import patch

import pytest
from cloudinary.exceptions import NotFound
from django.core.files.storage import default_storage, storages
from django.core.management import call_command
from django.core.management.base import CommandError

from backend.apps.catalog.models import Category, Product, ProductImage, ProductVideo
from backend.apps.common.cloudinary_storage import CloudinaryMediaStorage


@pytest.fixture
def cloudinary_storage(monkeypatch: pytest.MonkeyPatch) -> CloudinaryMediaStorage:
    storage = CloudinaryMediaStorage(
        cloud_name="test-cloud", api_key="test-key", api_secret="test-secret"
    )
    monkeypatch.setitem(storages._storages, "default", storage)
    monkeypatch.setattr(default_storage, "_wrapped", storage)
    return storage


@pytest.fixture
def product(cloudinary_storage: CloudinaryMediaStorage) -> Product:
    category = Category.objects.create(name="Legacy Media", slug="legacy-media")
    return Product.objects.create(
        name="Legacy Ring",
        slug="legacy-ring",
        category=category,
        base_price=1000,
    )


@pytest.fixture
def referenced_product_image(product: Product) -> ProductImage:
    return ProductImage.objects.create(
        product=product,
        image="products/images/2026/08/abc.png",
    )


def _resource(public_id: str, resource_type: str, asset_format: str) -> dict[str, str]:
    return {
        "public_id": public_id,
        "format": asset_format,
        "resource_type": resource_type,
    }


@pytest.mark.django_db
def test_normalize_cloudinary_media_dry_run_reports_extensionful_legacy(
    referenced_product_image: ProductImage,
) -> None:
    def lookup(public_id: str, **_options):
        if public_id == "products/images/2026/08/abc.png":
            return _resource(public_id, "image", "png")
        raise NotFound("missing")

    output = io.StringIO()
    with (
        patch("cloudinary.api.resource", side_effect=lookup) as resource,
        patch("cloudinary.uploader.rename") as rename,
        patch("cloudinary.api.resources") as account_enumeration,
    ):
        call_command("normalize_cloudinary_media", stdout=output)

    text = output.getvalue()
    assert "DRY RUN" in text
    assert (
        "LEGACY_EXTENSIONFUL products/images/2026/08/abc.png -> catalog/products/photos/2026/08/abc"
    ) in text
    assert "legacy_extensionful=1" in text
    assert resource.call_count == 3
    rename.assert_not_called()
    account_enumeration.assert_not_called()


@pytest.mark.django_db
def test_normalize_cloudinary_media_apply_is_idempotent(
    referenced_product_image: ProductImage,
) -> None:
    source = "products/images/2026/08/abc.png"
    target = "catalog/products/photos/2026/08/abc"
    remote_assets = {source}

    def lookup(public_id: str, **_options):
        if public_id in remote_assets:
            return _resource(public_id, "image", "png")
        raise NotFound("missing")

    def rename_asset(from_public_id: str, to_public_id: str, **_options):
        remote_assets.remove(from_public_id)
        remote_assets.add(to_public_id)
        return _resource(to_public_id, "image", "png")

    first_output = io.StringIO()
    second_output = io.StringIO()
    with (
        patch("cloudinary.api.resource", side_effect=lookup),
        patch("cloudinary.uploader.rename", side_effect=rename_asset) as rename,
    ):
        call_command("normalize_cloudinary_media", "--apply", stdout=first_output)
        call_command("normalize_cloudinary_media", "--apply", stdout=second_output)

    rename.assert_called_once_with(
        source,
        target,
        resource_type="image",
        type="upload",
        overwrite=False,
        invalidate=True,
    )
    assert "renamed=1" in first_output.getvalue()
    assert f"CANONICAL products/images/2026/08/abc.png -> {target}" in second_output.getvalue()
    assert "renamed=0" in second_output.getvalue()
    referenced_product_image.refresh_from_db()
    assert referenced_product_image.image.name == source


@pytest.mark.django_db
def test_normalize_cloudinary_media_reports_target_conflict_without_overwrite(
    referenced_product_image: ProductImage,
) -> None:
    existing = {
        "products/images/2026/08/abc.png",
        "catalog/products/photos/2026/08/abc",
    }

    def lookup(public_id: str, **_options):
        if public_id in existing:
            return _resource(public_id, "image", "png")
        raise NotFound("missing")

    output = io.StringIO()
    with (
        patch("cloudinary.api.resource", side_effect=lookup),
        patch("cloudinary.uploader.rename") as rename,
        pytest.raises(CommandError, match="manual review"),
    ):
        call_command("normalize_cloudinary_media", "--apply", stdout=output)

    text = output.getvalue()
    assert "CONFLICT products/images/2026/08/abc.png" in text
    assert "target=catalog/products/photos/2026/08/abc" in text
    assert "conflict=1" in text
    rename.assert_not_called()


@pytest.mark.django_db
def test_normalize_cloudinary_media_reports_missing_reference(
    referenced_product_image: ProductImage,
) -> None:
    output = io.StringIO()
    with (
        patch("cloudinary.api.resource", side_effect=NotFound("missing")),
        patch("cloudinary.uploader.rename") as rename,
    ):
        call_command("normalize_cloudinary_media", "--dry-run", stdout=output)

    assert (
        "MISSING products/images/2026/08/abc.png -> catalog/products/photos/2026/08/abc"
        in output.getvalue()
    )
    assert "missing=1" in output.getvalue()
    rename.assert_not_called()


@pytest.mark.django_db
def test_normalize_cloudinary_media_renames_reserved_video_namespace(product: Product) -> None:
    ProductVideo.objects.create(
        product=product,
        video_file="products/videos/2026/08/demo.mp4",
    )
    source = "products/videos/2026/08/demo"
    target = "catalog/products/clips/2026/08/demo"

    def lookup(public_id: str, **_options):
        if public_id == source:
            return _resource(public_id, "video", "mp4")
        raise NotFound("missing")

    output = io.StringIO()
    with (
        patch("cloudinary.api.resource", side_effect=lookup),
        patch(
            "cloudinary.uploader.rename",
            return_value=_resource(target, "video", "mp4"),
        ) as rename,
    ):
        call_command("normalize_cloudinary_media", "--apply", stdout=output)

    rename.assert_called_once_with(
        source,
        target,
        resource_type="video",
        type="upload",
        overwrite=False,
        invalidate=True,
    )
    assert f"RENAMED LEGACY_RESERVED_NAMESPACE {source} -> {target}" in output.getvalue()
    assert "legacy_reserved_namespace=1" in output.getvalue()
