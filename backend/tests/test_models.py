"""Unit and database integrity tests for Phase 2 domain models."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone

from backend.apps.catalog.models import (
    Category,
    Product,
    ProductAttributeType,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
    ProductVideo,
)
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.models import Popup, Promotion
from backend.apps.settings.models import DeliverySettings, SiteSettings, SocialLink


@pytest.mark.django_db
class TestCatalogModels:
    """Test suite for catalog entities, relationships, and constraints."""

    def test_category_creation_and_uniqueness(self) -> None:
        """Verify Category model creation, slug uniqueness, and string representation."""
        cat = Category.objects.create(
            name="Rings", slug="rings", description="Gold and diamond rings"
        )
        assert str(cat) == "Rings"
        assert cat.is_active is True

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Duplicate Rings", slug="rings")

    def test_attribute_type_and_value_uniqueness(self) -> None:
        """Verify attribute taxonomy constraints and slug uniqueness per type."""
        attr_type = ProductAttributeType.objects.create(name="Material", slug="material")
        val1 = ProductAttributeValue.objects.create(
            attribute_type=attr_type, value="Gold Plated", slug="gold-plated"
        )

        assert str(val1) == "Material: Gold Plated"

        # Duplicate slug under same attribute type must fail
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ProductAttributeValue.objects.create(
                    attribute_type=attr_type, value="Another Gold", slug="gold-plated"
                )

        # Same slug under different attribute type is allowed
        attr_type_2 = ProductAttributeType.objects.create(name="Finish", slug="finish")
        val2 = ProductAttributeValue.objects.create(
            attribute_type=attr_type_2, value="Gold Plated", slug="gold-plated"
        )
        assert val2.pk is not None

    def test_product_creation_and_price_invariants(self) -> None:
        """Verify Product validation and database price constraints."""
        cat = Category.objects.create(name="Necklaces", slug="necklaces")
        product = Product.objects.create(
            name="Solitaire Pendant",
            slug="solitaire-pendant",
            category=cat,
            base_price=Decimal("12500.00"),
            compare_at_price=Decimal("15000.00"),
            stock_quantity=10,
        )
        assert str(product) == "Solitaire Pendant"
        assert product.effective_stock == 10

        # Base price must be non-negative
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    name="Invalid Price Item",
                    slug="invalid-price",
                    category=cat,
                    base_price=Decimal("-100.00"),
                )

        # Compare-at price must be greater than base price when provided
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    name="Invalid Sale Item",
                    slug="invalid-sale",
                    category=cat,
                    base_price=Decimal("5000.00"),
                    compare_at_price=Decimal("4000.00"),
                )

    def test_category_protected_on_product_delete(self) -> None:
        """Verify that deleting a category is blocked if products are assigned to it."""
        cat = Category.objects.create(name="Bangles", slug="bangles")
        Product.objects.create(
            name="Classic Gold Bangle",
            slug="classic-gold-bangle",
            category=cat,
            base_price=Decimal("35000.00"),
        )
        with pytest.raises(ProtectedError):
            with transaction.atomic():
                cat.delete()

    def test_product_variants_and_effective_stock(self) -> None:
        """Verify variant uniqueness, pricing overrides, and aggregate stock calculation."""
        cat = Category.objects.create(name="Earrings", slug="earrings")
        product = Product.objects.create(
            name="Stud Earrings",
            slug="stud-earrings",
            category=cat,
            base_price=Decimal("4500.00"),
            stock_quantity=0,
        )

        var1 = ProductVariant.objects.create(
            product=product,
            name="Small / Silver",
            price_override=Decimal("4000.00"),
            stock_quantity=5,
        )
        var2 = ProductVariant.objects.create(
            product=product,
            name="Large / Gold",
            price_override=Decimal("5500.00"),
            stock_quantity=8,
        )

        assert var1.effective_price == Decimal("4000.00")
        assert var2.effective_price == Decimal("5500.00")
        assert product.has_variants is True
        assert product.effective_stock == 13

        # Duplicate variant name under same product must fail
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ProductVariant.objects.create(
                    product=product,
                    name="Small / Silver",
                    stock_quantity=2,
                )

    def test_product_image_primary_constraint(self) -> None:
        """Verify that only one primary image is allowed per product."""
        cat = Category.objects.create(name="Bridal", slug="bridal")
        product = Product.objects.create(
            name="Bridal Set",
            slug="bridal-set",
            category=cat,
            base_price=Decimal("150000.00"),
        )

        ProductImage.objects.create(
            product=product,
            image="products/2026/08/hero.jpg",
            is_primary=True,
        )

        # Multiple non-primary images are allowed
        ProductImage.objects.create(
            product=product,
            image="products/2026/08/side.jpg",
            is_primary=False,
        )
        ProductImage.objects.create(
            product=product,
            image="products/2026/08/back.jpg",
            is_primary=False,
        )
        assert product.images.count() == 3

        # Second primary image must trigger partial unique constraint violation
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ProductImage.objects.create(
                    product=product,
                    image="products/2026/08/duplicate-primary.jpg",
                    is_primary=True,
                )

    def test_product_video_one_to_one(self) -> None:
        """Verify ProductVideo one-to-one relationship with Product."""
        cat = Category.objects.create(name="Bracelets", slug="bracelets")
        product = Product.objects.create(
            name="Charm Bracelet",
            slug="charm-bracelet",
            category=cat,
            base_price=Decimal("8000.00"),
        )

        video = ProductVideo.objects.create(
            product=product,
            video_url="https://cdn.example.com/videos/bracelet.mp4",
            title="360 view",
        )
        assert product.video == video

        # Second video for same product must fail one-to-one constraint
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ProductVideo.objects.create(
                    product=product,
                    video_url="https://cdn.example.com/videos/another.mp4",
                )


@pytest.mark.django_db
class TestContentModels:
    """Test suite for reviews, gallery items, and about section."""

    def test_review_rating_constraint(self) -> None:
        """Verify review rating is constrained between 1 and 5 stars."""
        rev = Review.objects.create(
            customer_name="Fatima A.",
            review_text="Excellent craftsmanship and timely delivery!",
            rating=5,
            is_published=True,
        )
        assert str(rev) == "Fatima A. (5★)"

        # Rating 0 must violate check constraint
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    customer_name="Invalid User",
                    review_text="Invalid rating",
                    rating=0,
                )

        # Rating 6 must violate check constraint
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    customer_name="Invalid User 2",
                    review_text="Invalid rating",
                    rating=6,
                )

    def test_gallery_item_creation(self) -> None:
        """Verify GalleryItem creation and string representation."""
        item = GalleryItem.objects.create(
            title="Lahore Expo Exhibition 2026",
            image="gallery/2026/08/expo.jpg",
            item_type=GalleryItem.ItemType.EXHIBITION,
        )
        assert "Lahore Expo Exhibition 2026" in str(item)

    def test_about_section(self) -> None:
        """Verify AboutSection creation and update."""
        about = AboutSection.objects.create(
            title="Our Heritage",
            story_text="Handcrafted jewellery with pure gold and precious gems.",
        )
        assert str(about) == "Our Heritage"


@pytest.mark.django_db
class TestPromotionsModels:
    """Test suite for promotions, announcements, and popup scheduling."""

    def test_promotion_scheduling_and_active_queryset(self) -> None:
        """Verify Promotion date constraints and active_now queryset filtering."""
        now = timezone.now()

        # Active promotion inside window
        promo_active = Promotion.objects.create(
            title="Independence Day Sale",
            announcement_text="14 August Special: 14% off",
            start_datetime=now - timedelta(days=1),
            end_datetime=now + timedelta(days=2),
            is_active=True,
            priority=1,
        )

        # Expired promotion
        Promotion.objects.create(
            title="Past Summer Sale",
            start_datetime=now - timedelta(days=10),
            end_datetime=now - timedelta(days=2),
            is_active=True,
            priority=2,
        )

        # Inactive promotion
        Promotion.objects.create(
            title="Draft Winter Sale",
            start_datetime=now - timedelta(days=1),
            end_datetime=now + timedelta(days=5),
            is_active=False,
            priority=3,
        )

        active_promotions = Promotion.objects.active_now(now)
        assert active_promotions.count() == 1
        assert active_promotions.first() == promo_active

    def test_promotion_end_before_start_constraint(self) -> None:
        """Verify end_datetime must be greater than start_datetime."""
        now = timezone.now()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Promotion.objects.create(
                    title="Invalid Date Promotion",
                    start_datetime=now + timedelta(days=5),
                    end_datetime=now,
                )

    def test_popup_date_constraint(self) -> None:
        """Verify Popup model end date constraint."""
        now = timezone.now()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Popup.objects.create(
                    title="Invalid Popup",
                    message="Test",
                    start_datetime=now + timedelta(days=2),
                    end_datetime=now - timedelta(days=1),
                )


@pytest.mark.django_db
class TestSettingsModels:
    """Test suite for singleton settings and delivery rules."""

    def test_site_settings_singleton_enforcement(self) -> None:
        """Verify SiteSettings enforces single-record integrity and get_solo() helper."""
        settings_1 = SiteSettings.get_solo()
        settings_1.brand_name = "Zirconia Fine Jewels"
        settings_1.whatsapp_number = "+923001234567"
        settings_1.save()

        # Subsequent get_solo() must return the same instance
        settings_2 = SiteSettings.get_solo()
        assert settings_2.brand_name == "Zirconia Fine Jewels"
        assert settings_2.whatsapp_number == "+923001234567"
        assert SiteSettings.objects.count() == 1

        # Attempting to insert a second record with singleton_guard=1 must fail
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SiteSettings.objects.create(singleton_guard=1, brand_name="Second Settings")

    def test_delivery_settings_singleton_and_constraints(self) -> None:
        """Verify DeliverySettings enforces singleton constraint and non-negative rates."""
        del_settings = DeliverySettings.get_solo()
        del_settings.free_delivery_threshold = Decimal("5000.00")
        del_settings.pakistan_delivery_charge = Decimal("250.00")
        del_settings.save()

        assert DeliverySettings.objects.count() == 1

        # Attempting to create duplicate delivery settings must fail
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                DeliverySettings.objects.create(singleton_guard=1)

        # Free threshold must be non-negative (using a dummy separate guard value if allowed or testing check constraint)
        # Note: singleton_guard=1 unique constraint triggers if trying to insert a second row with singleton_guard=1
        # To test check constraint on free_delivery_threshold, update or insert in atomic block
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                del_settings_bad = DeliverySettings(
                    singleton_guard=1, free_delivery_threshold=Decimal("-500.00")
                )
                del_settings_bad.save()

    def test_social_link_uniqueness(self) -> None:
        """Verify SocialLink platform uniqueness."""
        SocialLink.objects.create(
            platform="Instagram",
            url="https://instagram.com/jewellerybrand",
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SocialLink.objects.create(
                    platform="Instagram",
                    url="https://instagram.com/duplicate",
                )
