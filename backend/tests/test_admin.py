"""Tests for Django Admin operations, permissions, custom forms, actions, and security validation."""

from decimal import Decimal

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, RequestFactory

from backend.apps.catalog.admin import CategoryAdmin, ProductAdmin
from backend.apps.catalog.models import Category, Product
from backend.apps.common.validators import validate_safe_url
from backend.apps.content.admin import ReviewAdmin
from backend.apps.content.models import Review
from backend.apps.promotions.admin import PromotionAdminForm
from backend.apps.settings.admin import (
    DeliverySettingsAdmin,
    SiteSettingsAdmin,
    SocialLinkAdminForm,
)
from backend.apps.settings.models import DeliverySettings, SiteSettings

User = get_user_model()


class MockSuperUser:
    """Mock user object for admin unit tests."""

    is_active = True
    is_staff = True
    is_superuser = True

    def has_perm(self, perm: str, obj=None) -> bool:
        return True


@pytest.fixture
def staff_user() -> User:
    """Create and return an active staff user."""
    return User.objects.create_user(
        username="staff_editor",
        password="StaffPassword123!",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def non_staff_user() -> User:
    """Create and return an active non-staff user."""
    return User.objects.create_user(
        username="regular_customer",
        password="CustomerPassword123!",
        is_staff=False,
    )


@pytest.mark.django_db
class TestAdminAuthenticationAndAccess:
    """Test suite for Admin authentication gates and permission boundaries."""

    def test_anonymous_user_redirected_to_login(self, client: Client) -> None:
        """Verify unauthenticated requests to admin are redirected to login."""
        response = client.get("/admin/catalog/product/")
        assert response.status_code == 302
        assert "/admin/login/" in response.headers["Location"]

    def test_non_staff_user_forbidden(self, client: Client, non_staff_user: User) -> None:
        """Verify non-staff authenticated users cannot access admin changelist."""
        client.force_login(non_staff_user)
        response = client.get("/admin/catalog/product/")
        assert response.status_code in (302, 403)

    def test_staff_user_can_access_admin_changelists(
        self, client: Client, staff_user: User
    ) -> None:
        """Verify staff users with permissions can access all domain model changelists."""
        client.force_login(staff_user)

        endpoints = [
            "/admin/catalog/product/",
            "/admin/catalog/category/",
            "/admin/catalog/productattributetype/",
            "/admin/content/review/",
            "/admin/content/galleryitem/",
            "/admin/content/aboutsection/",
            "/admin/promotions/promotion/",
            "/admin/promotions/popup/",
            "/admin/settings/sitesettings/",
            "/admin/settings/deliverysettings/",
            "/admin/settings/sociallink/",
        ]

        for url in endpoints:
            response = client.get(url)
            assert response.status_code == 200, f"Failed to access {url}"


@pytest.mark.django_db
class TestSingletonAdminProtection:
    """Test suite for singleton settings admin permissions."""

    def test_sitesettings_admin_prevents_duplicate_and_delete(self) -> None:
        """Verify SiteSettingsAdmin prevents adding a second row and prevents deletion."""
        site = AdminSite()
        admin_obj = SiteSettingsAdmin(SiteSettings, site)
        rf = RequestFactory()
        request = rf.get("/admin/")
        request.user = MockSuperUser()

        # Before any instance exists, add is allowed
        assert admin_obj.has_add_permission(request) is True

        # Create singleton instance
        SiteSettings.get_solo()

        # Once singleton exists, add is blocked
        assert admin_obj.has_add_permission(request) is False

        # Deletion is always blocked
        assert admin_obj.has_delete_permission(request) is False

    def test_deliverysettings_admin_prevents_duplicate_and_delete(self) -> None:
        """Verify DeliverySettingsAdmin prevents adding a second row and prevents deletion."""
        site = AdminSite()
        admin_obj = DeliverySettingsAdmin(DeliverySettings, site)
        rf = RequestFactory()
        request = rf.get("/admin/")
        request.user = MockSuperUser()

        # Before any instance exists, add is allowed
        assert admin_obj.has_add_permission(request) is True

        # Create singleton instance
        DeliverySettings.get_solo()

        # Once singleton exists, add is blocked
        assert admin_obj.has_add_permission(request) is False

        # Deletion is always blocked
        assert admin_obj.has_delete_permission(request) is False


@pytest.mark.django_db
class TestAdminActions:
    """Test suite for custom safe ModelAdmin bulk actions."""

    def test_product_admin_bulk_actions(self) -> None:
        """Verify ProductAdmin publication and merchandising actions."""
        cat = Category.objects.create(name="Rings", slug="rings")
        p1 = Product.objects.create(
            name="Ring A",
            slug="ring-a",
            category=cat,
            base_price=Decimal("1000"),
            is_published=False,
        )
        p2 = Product.objects.create(
            name="Ring B",
            slug="ring-b",
            category=cat,
            base_price=Decimal("2000"),
            is_published=False,
        )

        site = AdminSite()
        admin_obj = ProductAdmin(Product, site)
        rf = RequestFactory()
        request = rf.post("/admin/")
        request.user = MockSuperUser()
        # Add messages middleware support for request
        from django.contrib.messages.storage.fallback import FallbackStorage

        request.session = {}
        request._messages = FallbackStorage(request)

        # Test make_published
        admin_obj.make_published(request, Product.objects.filter(pk__in=[p1.pk, p2.pk]))
        p1.refresh_from_db()
        p2.refresh_from_db()
        assert p1.is_published is True
        assert p2.is_published is True

        # Test make_unpublished
        admin_obj.make_unpublished(request, Product.objects.filter(pk__in=[p1.pk, p2.pk]))
        p1.refresh_from_db()
        assert p1.is_published is False

        # Test mark_featured & unmark_featured
        admin_obj.mark_featured(request, Product.objects.filter(pk=p1.pk))
        p1.refresh_from_db()
        assert p1.is_featured is True

        admin_obj.unmark_featured(request, Product.objects.filter(pk=p1.pk))
        p1.refresh_from_db()
        assert p1.is_featured is False

    def test_review_admin_bulk_actions(self) -> None:
        """Verify ReviewAdmin publish and verification actions."""
        r1 = Review.objects.create(
            customer_name="Amina", review_text="Loved it!", rating=5, is_published=False
        )

        site = AdminSite()
        admin_obj = ReviewAdmin(Review, site)
        rf = RequestFactory()
        request = rf.post("/admin/")
        request.user = MockSuperUser()
        from django.contrib.messages.storage.fallback import FallbackStorage

        request.session = {}
        request._messages = FallbackStorage(request)

        admin_obj.publish_reviews(request, Review.objects.filter(pk=r1.pk))
        r1.refresh_from_db()
        assert r1.is_published is True

        admin_obj.mark_verified(request, Review.objects.filter(pk=r1.pk))
        r1.refresh_from_db()
        assert r1.is_verified is True


@pytest.mark.django_db
class TestSafeURLValidation:
    """Test suite for URL validation and security against pseudo-protocols."""

    def test_valid_https_urls(self) -> None:
        """Verify standard HTTPS URLs and relative paths pass validation."""
        valid_urls = [
            "https://instagram.com/jewellerybrand",
            "https://facebook.com/jewellerybrand",
            "https://api.whatsapp.com/send?phone=923001234567",
            "/shop/necklaces/",
            "/collections/bridal/",
            "#contact",
        ]
        for url in valid_urls:
            validate_safe_url(url)  # Should not raise

    def test_invalid_dangerous_urls_rejected(self) -> None:
        """Verify javascript:, data:, file:, and unsafe schemes raise ValidationError."""
        dangerous_urls = [
            "javascript:alert(1)",
            "javascript:void(0)",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "file:///C:/Windows/System32/cmd.exe",
            "vbscript:msgbox(1)",
            "http://insecure-site.com",  # External links must be HTTPS
        ]
        for url in dangerous_urls:
            with pytest.raises(ValidationError):
                validate_safe_url(url)

    def test_social_link_form_validation(self) -> None:
        """Verify SocialLinkAdminForm validates url field."""
        form_bad = SocialLinkAdminForm(
            data={
                "platform": "Instagram",
                "url": "javascript:alert(1)",
                "is_active": True,
                "sort_order": 0,
            }
        )
        assert form_bad.is_valid() is False
        assert "url" in form_bad.errors

        form_good = SocialLinkAdminForm(
            data={
                "platform": "Instagram",
                "url": "https://instagram.com/mybrand",
                "is_active": True,
                "sort_order": 0,
            }
        )
        assert form_good.is_valid() is True

    def test_promotion_form_url_validation(self) -> None:
        """Verify PromotionAdminForm validates cta_url."""
        form_bad = PromotionAdminForm(
            data={
                "title": "Sale",
                "cta_url": "data:text/plain,hello",
                "is_active": True,
                "priority": 0,
            }
        )
        assert form_bad.is_valid() is False
        assert "cta_url" in form_bad.errors


@pytest.mark.django_db
class TestAdminQueryOptimizations:
    """Verify admin querysets avoid N+1 query explosions."""

    def test_category_admin_annotates_product_count(self) -> None:
        """Verify CategoryAdmin annotates product count in queryset."""
        cat = Category.objects.create(name="Sets", slug="sets")
        Product.objects.create(name="Set 1", slug="set-1", category=cat, base_price=Decimal("1000"))
        Product.objects.create(name="Set 2", slug="set-2", category=cat, base_price=Decimal("2000"))

        site = AdminSite()
        admin_obj = CategoryAdmin(Category, site)
        rf = RequestFactory()
        request = rf.get("/admin/catalog/category/")
        request.user = MockSuperUser()

        qs = admin_obj.get_queryset(request)
        item = qs.get(pk=cat.pk)
        assert admin_obj.product_count_display(item) == 2
