"""Unit coverage for the official Cloudinary-backed production storage."""

from io import BytesIO
from unittest.mock import patch

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
