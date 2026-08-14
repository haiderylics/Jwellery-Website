"""Comprehensive Phase 7 Security Hardening, Transactional Safety, and Integration Tests."""

import io
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from PIL import Image

from backend.apps.catalog.models import Category, Product, ProductImage
from backend.apps.common.media import (
    generate_image_variants,
    get_variant_path,
)
from backend.apps.common.security_events import log_security_event
from backend.apps.common.validators import validate_safe_url


def create_in_memory_image(name="ring.jpg", size=(400, 400), format="JPEG") -> SimpleUploadedFile:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=(180, 140, 60))
    img.save(buf, format=format)
    buf.seek(0)
    return SimpleUploadedFile(name, buf.getvalue(), content_type=f"image/{format.lower()}")


@pytest.mark.django_db(transaction=True)
class TestMediaTransactionalWorkflowAndChangeDetection:
    """Verify post-commit execution, change detection, and replacement safety."""

    def test_media_change_detection_prevents_unnecessary_regeneration(self):
        category = Category.objects.create(name="Necklaces", slug="necklaces")
        product = Product.objects.create(
            name="Diamond Choker",
            slug="diamond-choker",
            category=category,
            base_price=Decimal("150000.00"),
        )
        upload = create_in_memory_image("choker.jpg")
        prod_img = ProductImage.objects.create(
            product=product, image=upload, alt_text="Choker Initial"
        )

        storage_path = prod_img.image.name
        assert default_storage.exists(storage_path)

        with patch("backend.apps.common.signals.generate_image_variants") as mock_gen:
            # Update non-media attribute (alt_text, sort_order)
            prod_img.alt_text = "Choker Updated Alt"
            prod_img.sort_order = 5
            prod_img.save()

            # Variant generation must NOT be called since image didn't change
            mock_gen.assert_not_called()

        prod_img.delete()

    def test_media_replacement_safety(self):
        category = Category.objects.create(name="Bangles", slug="bangles")
        product = Product.objects.create(
            name="Gold Bangle",
            slug="gold-bangle",
            category=category,
            base_price=Decimal("80000.00"),
        )
        upload_old = create_in_memory_image("old_bangle.jpg")
        prod_img = ProductImage.objects.create(product=product, image=upload_old)
        old_storage_path = prod_img.image.name

        assert default_storage.exists(old_storage_path)
        old_thumb = get_variant_path(old_storage_path, "thumb")
        generate_image_variants(old_storage_path)
        assert default_storage.exists(old_thumb)

        # Replace image with a new upload
        upload_new = create_in_memory_image("new_bangle.jpg")
        prod_img.image = upload_new
        prod_img.save()

        new_storage_path = prod_img.image.name
        assert new_storage_path != old_storage_path
        assert default_storage.exists(new_storage_path)

        # Old file and variants safely cleaned up
        assert not default_storage.exists(old_storage_path)
        assert not default_storage.exists(old_thumb)

        prod_img.delete()


@pytest.mark.django_db
class TestMediaAuditCommand:
    """Verify audit_media command in dry-run and cleanup modes."""

    def test_audit_media_dry_run_does_not_delete_files(self):
        category = Category.objects.create(name="Pendants", slug="pendants")
        product = Product.objects.create(
            name="Pearl Pendant",
            slug="pearl-pendant",
            category=category,
            base_price=Decimal("35000.00"),
        )
        upload = create_in_memory_image("pendant.jpg")
        prod_img = ProductImage.objects.create(product=product, image=upload)

        out = io.StringIO()
        call_command("audit_media", "--dry-run", stdout=out)
        output = out.getvalue()

        assert "Mode: DRY RUN" in output
        assert "Total DB Records with Media: 1" in output
        assert "[OK] No missing DB referenced files." in output

        # Storage file must still exist
        assert default_storage.exists(prod_img.image.name)
        prod_img.delete()

    def test_audit_media_cleans_only_eligible_unreferenced_orphans(self):
        # Create an intentional unreferenced orphan file
        orphan_path = "products/images/2026/08/00000000000000000000000000000099.jpg"
        default_storage.save(orphan_path, ContentFile(b"fake image data"))
        assert default_storage.exists(orphan_path)

        out = io.StringIO()
        # With threshold 0 hours and clean-orphans, it should clean the orphan
        call_command("audit_media", "--clean-orphans", "--older-than-hours", "0", stdout=out)
        output = out.getvalue()

        assert "Deleted orphan: " in output or "[OK] Safely cleaned" in output
        assert not default_storage.exists(orphan_path)


@pytest.mark.django_db
class TestURLSecurityAndInjectionPrevention:
    """Verify URL validation blocks dangerous schemes and encodings."""

    def test_safe_urls_accepted(self):
        valid_urls = [
            "https://www.zirconiajewels.com",
            "https://instagram.com/zirconiajewels",
            "/collections/bridal-rings/",
            "#contact",
        ]
        for url in valid_urls:
            validate_safe_url(url)

    def test_dangerous_schemes_rejected(self):
        dangerous_urls = [
            "javascript:alert(1)",
            "JAVASCRIPT:alert(1)",
            "java\x00script:alert(1)",
            "java%73cript:alert(1)",
            "j a v a s c r i p t :alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
            "vbscript:msgbox(1)",
            "blob:https://evil.com/123",
            "//evil.com/phishing",
            "http://insecure-site.com",  # plain HTTP external rejected
        ]
        for url in dangerous_urls:
            with pytest.raises(ValidationError):
                validate_safe_url(url)


@pytest.mark.django_db
class TestAPIReadOnlyAndSecurityBoundaries:
    """Verify public API read-only enforcement, pagination limits, and unpublished data isolation."""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.client = Client()
        self.category = Category.objects.create(name="Earrings", slug="earrings")
        self.published_product = Product.objects.create(
            name="Solitaire Studs",
            slug="solitaire-studs",
            category=self.category,
            base_price=Decimal("55000.00"),
            is_published=True,
        )
        self.draft_product = Product.objects.create(
            name="Secret Prototype Studs",
            slug="secret-prototype-studs",
            category=self.category,
            base_price=Decimal("990000.00"),
            is_published=False,
        )

    def test_mutations_rejected_with_405(self):
        for method in ("post", "put", "patch", "delete"):
            fn = getattr(self.client, method)
            res = fn(
                "/api/v1/products/",
                data={"name": "Hacked Product"},
                content_type="application/json",
            )
            assert res.status_code == 405

    def test_unpublished_products_never_leak_in_list_or_detail(self):
        # List endpoint
        res = self.client.get("/api/v1/products/")
        assert res.status_code == 200
        slugs = [item["slug"] for item in res.json()["results"]]
        assert "solitaire-studs" in slugs
        assert "secret-prototype-studs" not in slugs

        # Direct detail lookup on unpublished item
        detail_res = self.client.get("/api/v1/products/secret-prototype-studs/")
        assert detail_res.status_code == 404

    def test_pagination_bounds_enforced(self):
        res = self.client.get("/api/v1/products/?page_size=99999")
        assert res.status_code == 200
        # DRF max_page_size=100 limits excessive page_size abuse
        assert len(res.json()["results"]) <= 100


@pytest.mark.django_db
class TestHealthEndpoints:
    """Verify liveness and readiness probe security and responses."""

    def test_health_liveness_endpoint(self):
        client = Client()
        res = client.get("/health/live/")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

    def test_health_readiness_endpoint(self):
        client = Client()
        res = client.get("/health/ready/")
        assert res.status_code == 200
        assert res.json() == {"status": "ready"}


class TestSecurityLogging:
    """Verify security event logging does not leak credentials or PII."""

    def test_sensitive_fields_redacted(self):
        with patch("backend.apps.common.security_events.logger.warning") as mock_log:
            log_security_event(
                "security.test_event",
                password="super_secret_password",
                token="jwt_secret_token_xyz",
                phone="+923001234567",
                address="123 Luxury Avenue, Lahore",
                safe_id=42,
            )
            mock_log.assert_called_once()
            logged_str = mock_log.call_args[0][0]
            assert "[REDACTED]" in logged_str
            assert "super_secret_password" not in logged_str
            assert "jwt_secret_token_xyz" not in logged_str
            assert "+923001234567" not in logged_str
            assert "42" in logged_str
