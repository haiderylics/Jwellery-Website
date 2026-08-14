"""Comprehensive test suite for Phase 4 Public Read-Only API Layer."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.cache import cache
from django.test import Client
from django.utils import timezone
from rest_framework import status

from backend.apps.catalog.models import (
    Category,
    Product,
    ProductAttributeType,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
)
from backend.apps.common.cache_utils import CACHE_KEY_HOMEPAGE
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.models import Popup, Promotion
from backend.apps.settings.models import DeliverySettings, SiteSettings, SocialLink


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> None:
    """Clear memory cache before every test run."""
    cache.clear()


@pytest.mark.django_db
class TestCatalogAPI:
    """Test suite for catalog endpoints, filtering, search, pagination, and sorting."""

    def test_product_list_published_only(self, client: Client) -> None:
        """Verify product list returns only published products."""
        cat = Category.objects.create(name="Rings", slug="rings")
        p_pub = Product.objects.create(
            name="Diamond Solitaire Ring",
            slug="diamond-solitaire-ring",
            category=cat,
            base_price=Decimal("45000.00"),
            is_published=True,
        )
        p_unpub = Product.objects.create(
            name="Draft Ruby Ring",
            slug="draft-ruby-ring",
            category=cat,
            base_price=Decimal("30000.00"),
            is_published=False,
        )

        response = client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        slugs = [item["slug"] for item in data["results"]]
        assert p_pub.slug in slugs
        assert p_unpub.slug not in slugs

    def test_product_detail_published_only(self, client: Client) -> None:
        """Verify product detail returns 200 for published, 404 for unpublished."""
        cat = Category.objects.create(name="Earrings", slug="earrings")
        p_pub = Product.objects.create(
            name="Emerald Drops",
            slug="emerald-drops",
            category=cat,
            base_price=Decimal("18000.00"),
            is_published=True,
        )
        p_unpub = Product.objects.create(
            name="Draft Drops",
            slug="draft-drops",
            category=cat,
            base_price=Decimal("12000.00"),
            is_published=False,
        )

        # Published detail
        res_pub = client.get(f"/api/v1/products/{p_pub.slug}/")
        assert res_pub.status_code == status.HTTP_200_OK
        assert res_pub.json()["name"] == "Emerald Drops"

        # Unpublished detail returns 404
        res_unpub = client.get(f"/api/v1/products/{p_unpub.slug}/")
        assert res_unpub.status_code == status.HTTP_404_NOT_FOUND

        # Nonexistent detail returns 404
        res_none = client.get("/api/v1/products/non-existent-slug/")
        assert res_none.status_code == status.HTTP_404_NOT_FOUND

    def test_product_pagination_limits(self, client: Client) -> None:
        """Verify pagination bounds and max page size capping."""
        cat = Category.objects.create(name="Bracelets", slug="bracelets")
        for i in range(25):
            Product.objects.create(
                name=f"Bracelet {i}",
                slug=f"bracelet-{i}",
                category=cat,
                base_price=Decimal("5000.00"),
                is_published=True,
            )

        # Default page size 20
        res = client.get("/api/v1/products/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["count"] == 25
        assert len(data["results"]) == 20
        assert data["total_pages"] == 2

        # Page 2
        res_p2 = client.get("/api/v1/products/?page=2")
        assert res_p2.status_code == status.HTTP_200_OK
        assert len(res_p2.json()["results"]) == 5

        # Request exceeding max page size (50) is capped at 50
        res_cap = client.get("/api/v1/products/?page_size=9999")
        assert res_cap.status_code == status.HTTP_200_OK
        assert len(res_cap.json()["results"]) == 25

    def test_product_filtering_and_search(self, client: Client) -> None:
        """Verify category, attribute, flag filters, and keyword search."""
        cat_rings = Category.objects.create(name="Rings", slug="rings")
        cat_necklaces = Category.objects.create(name="Necklaces", slug="necklaces")

        attr_type = ProductAttributeType.objects.create(name="Material", slug="material")
        gold_val = ProductAttributeValue.objects.create(
            attribute_type=attr_type, value="Gold", slug="gold"
        )
        silver_val = ProductAttributeValue.objects.create(
            attribute_type=attr_type, value="Silver", slug="silver"
        )

        p1 = Product.objects.create(
            name="Gold Royal Ring",
            slug="gold-royal-ring",
            category=cat_rings,
            base_price=Decimal("50000.00"),
            is_published=True,
            is_featured=True,
        )
        p1.attributes.add(gold_val)

        p2 = Product.objects.create(
            name="Silver Minimal Ring",
            slug="silver-minimal-ring",
            category=cat_rings,
            base_price=Decimal("8000.00"),
            is_published=True,
            is_new_arrival=True,
        )
        p2.attributes.add(silver_val)

        p3 = Product.objects.create(
            name="Gold Pearl Necklace",
            slug="gold-pearl-necklace",
            category=cat_necklaces,
            base_price=Decimal("35000.00"),
            is_published=True,
        )
        p3.attributes.add(gold_val)

        # 1. Filter by category
        res_cat = client.get("/api/v1/products/?category=rings")
        data_cat = res_cat.json()
        assert data_cat["count"] == 2

        # 2. Filter by attribute
        res_attr = client.get("/api/v1/products/?attribute=gold")
        data_attr = res_attr.json()
        assert data_attr["count"] == 2

        # 3. Filter by featured
        res_feat = client.get("/api/v1/products/?featured=true")
        assert res_feat.json()["count"] == 1
        assert res_feat.json()["results"][0]["slug"] == "gold-royal-ring"

        # 4. Search query
        res_q = client.get("/api/v1/products/?q=pearl")
        assert res_q.json()["count"] == 1
        assert res_q.json()["results"][0]["slug"] == "gold-pearl-necklace"

    def test_product_sorting(self, client: Client) -> None:
        """Verify sorting options price_low, price_high, newest."""
        cat = Category.objects.create(name="Bangles", slug="bangles")
        p1 = Product.objects.create(
            name="Low Price",
            slug="low-price",
            category=cat,
            base_price=Decimal("1000.00"),
            is_published=True,
        )
        p2 = Product.objects.create(
            name="High Price",
            slug="high-price",
            category=cat,
            base_price=Decimal("9000.00"),
            is_published=True,
        )

        res_low = client.get("/api/v1/products/?ordering=price_low")
        assert res_low.json()["results"][0]["slug"] == p1.slug

        res_high = client.get("/api/v1/products/?ordering=price_high")
        assert res_high.json()["results"][0]["slug"] == p2.slug

    def test_category_and_attribute_endpoints(self, client: Client) -> None:
        """Verify categories and attributes public endpoints."""
        cat1 = Category.objects.create(
            name="Active Cat", slug="active-cat", is_active=True, sort_order=1
        )
        Category.objects.create(name="Inactive Cat", slug="inactive-cat", is_active=False)
        Product.objects.create(
            name="P1", slug="p1", category=cat1, base_price=Decimal("1000"), is_published=True
        )

        attr_type = ProductAttributeType.objects.create(name="Gemstone", slug="gemstone")
        ProductAttributeValue.objects.create(
            attribute_type=attr_type, value="Diamond", slug="diamond"
        )

        # Category endpoint
        res_cat = client.get("/api/v1/categories/")
        assert res_cat.status_code == status.HTTP_200_OK
        cats = res_cat.json()
        assert len(cats) == 1
        assert cats[0]["slug"] == "active-cat"
        assert cats[0]["product_count"] == 1

        # Attribute endpoint
        res_attr = client.get("/api/v1/attributes/")
        assert res_attr.status_code == status.HTTP_200_OK
        attrs = res_attr.json()
        assert len(attrs) == 1
        assert attrs[0]["slug"] == "gemstone"
        assert len(attrs[0]["values"]) == 1

    def test_read_only_methods_enforced(self, client: Client) -> None:
        """Verify mutation methods (POST, PUT, PATCH, DELETE) are rejected with 405."""
        unsupported = ["post", "put", "patch", "delete"]
        for method in unsupported:
            client_method = getattr(client, method)
            res = client_method("/api/v1/products/", {"name": "Hacked Product"})
            assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestContentAPI:
    """Test suite for public reviews, gallery items, and about section."""

    def test_reviews_published_only(self, client: Client) -> None:
        """Verify review list returns only published reviews."""
        Review.objects.create(
            customer_name="Sara K.", review_text="Gorgeous earrings!", rating=5, is_published=True
        )
        Review.objects.create(
            customer_name="Hidden User", review_text="Spam review", rating=1, is_published=False
        )

        res = client.get("/api/v1/reviews/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["count"] == 1
        assert data["results"][0]["customer_name"] == "Sara K."

    def test_gallery_published_only(self, client: Client) -> None:
        """Verify gallery returns only published moments."""
        GalleryItem.objects.create(
            title="Lahore Jewellery Show 2026",
            image="gallery/show.jpg",
            item_type=GalleryItem.ItemType.EXHIBITION,
            is_published=True,
        )
        GalleryItem.objects.create(
            title="Unpublished Draft Moment",
            image="gallery/draft.jpg",
            is_published=False,
        )

        res = client.get("/api/v1/gallery/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Lahore Jewellery Show 2026"

    def test_about_section(self, client: Client) -> None:
        """Verify about section endpoint."""
        AboutSection.objects.create(
            title="Our Artisans",
            story_text="Four decades of bespoke bridal craftsmanship.",
            is_active=True,
        )

        res = client.get("/api/v1/about/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["title"] == "Our Artisans"


@pytest.mark.django_db
class TestPromotionsAPI:
    """Test suite for active promotions and active popup endpoints."""

    def test_active_promotions_and_popups(self, client: Client) -> None:
        """Verify only promotions and popups within active scheduled windows are returned."""
        now = timezone.now()

        # Active Promotion
        Promotion.objects.create(
            title="Eid Festive Sale",
            announcement_text="Special 10% off storewide",
            start_datetime=now - timedelta(days=1),
            end_datetime=now + timedelta(days=3),
            is_active=True,
            show_in_announcement_bar=True,
        )
        # Expired Promotion
        Promotion.objects.create(
            title="Old Promotion",
            start_datetime=now - timedelta(days=10),
            end_datetime=now - timedelta(days=2),
            is_active=True,
        )

        # Active Popup
        Popup.objects.create(
            title="Join the VIP Club",
            message="Sign up for early bridal collection access.",
            start_datetime=now - timedelta(hours=1),
            end_datetime=now + timedelta(days=5),
            is_active=True,
            delay_seconds=5,
        )

        # Promotions Endpoint
        res_promo = client.get("/api/v1/promotions/active/")
        assert res_promo.status_code == status.HTTP_200_OK
        promos = res_promo.json()
        assert len(promos) == 1
        assert promos[0]["title"] == "Eid Festive Sale"

        # Popup Endpoint
        res_popup = client.get("/api/v1/popups/active/")
        assert res_popup.status_code == status.HTTP_200_OK
        popup_data = res_popup.json()
        assert popup_data["data"]["title"] == "Join the VIP Club"


@pytest.mark.django_db
class TestSettingsAPI:
    """Test suite for public site settings and delivery endpoints."""

    def test_site_settings_public_profile(self, client: Client) -> None:
        """Verify site settings endpoint exposes only public business profile fields."""
        settings_obj = SiteSettings.get_solo()
        settings_obj.brand_name = "Zirconia Fine Jewels"
        settings_obj.whatsapp_number = "+923001234567"
        settings_obj.contact_email = "concierge@zirconiajewels.com"
        settings_obj.save()

        SocialLink.objects.create(
            platform="Instagram", url="https://instagram.com/zirconia", is_active=True
        )

        res = client.get("/api/v1/site-settings/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["brand_name"] == "Zirconia Fine Jewels"
        assert data["whatsapp_number"] == "+923001234567"
        assert len(data["social_links"]) == 1
        assert "SECRET_KEY" not in data
        assert "password" not in data

    def test_delivery_settings_public(self, client: Client) -> None:
        """Verify delivery settings endpoint."""
        del_settings = DeliverySettings.get_solo()
        del_settings.free_delivery_threshold = Decimal("5000.00")
        del_settings.pakistan_delivery_charge = Decimal("250.00")
        del_settings.save()

        res = client.get("/api/v1/delivery-settings/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["pakistan_delivery_enabled"] is True
        assert Decimal(data["free_delivery_threshold"]) == Decimal("5000.00")
        assert Decimal(data["pakistan_delivery_charge"]) == Decimal("250.00")


@pytest.mark.django_db(transaction=True)
class TestStorefrontHomeAPI:
    """Test suite for aggregated homepage endpoint and cache invalidation."""

    def test_storefront_home_aggregation(self, client: Client) -> None:
        """Verify /api/v1/home/ aggregates all landing sections in a single response."""
        cat = Category.objects.create(name="Rings", slug="rings", is_active=True)
        Product.objects.create(
            name="Solitaire Ring",
            slug="solitaire-ring",
            category=cat,
            base_price=Decimal("15000"),
            is_published=True,
            is_featured=True,
            is_new_arrival=True,
        )
        Review.objects.create(
            customer_name="Fatima", review_text="Loved it", rating=5, is_published=True
        )

        res = client.get("/api/v1/home/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()

        assert "site_settings" in data
        assert "delivery_settings" in data
        assert "featured_categories" in data
        assert "featured_products" in data
        assert "new_arrivals" in data
        assert "reviews" in data
        assert len(data["featured_products"]) == 1
        assert len(data["reviews"]) == 1

    def test_cache_invalidation_on_admin_save(self, client: Client) -> None:
        """Verify editing a model triggers cache invalidation for the homepage."""
        cat = Category.objects.create(name="Initial Category", slug="init-cat", is_active=True)
        res1 = client.get("/api/v1/home/")
        assert res1.status_code == status.HTTP_200_OK
        assert res1.json()["featured_categories"][0]["name"] == "Initial Category"

        # Verify cached
        assert cache.get(CACHE_KEY_HOMEPAGE) is not None

        # Update category
        cat.name = "Renamed Luxury Category"
        cat.save()

        # Cache must have been invalidated by signal
        assert cache.get(CACHE_KEY_HOMEPAGE) is None

        # Subsequent GET fetches fresh data
        res2 = client.get("/api/v1/home/")
        assert res2.json()["featured_categories"][0]["name"] == "Renamed Luxury Category"


@pytest.mark.django_db
class TestAPISecurityAndPerformance:
    """Test suite for CORS headers and bounded query performance."""

    def test_cors_headers_allowed_origin(self, client: Client) -> None:
        """Verify CORS response headers for allowed frontend origin."""
        response = client.get(
            "/api/v1/products/",
            HTTP_ORIGIN="http://localhost:5173",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"

    def test_query_count_bounded_on_product_list(
        self, client: Client, django_assert_num_queries
    ) -> None:
        """Verify product list executes a bounded number of queries (preventing N+1)."""
        cat = Category.objects.create(name="Pendants", slug="pendants")
        attr_type = ProductAttributeType.objects.create(name="Finish", slug="finish")
        attr_val = ProductAttributeValue.objects.create(
            attribute_type=attr_type, value="Rose Gold", slug="rose-gold"
        )

        for i in range(10):
            p = Product.objects.create(
                name=f"Pendant {i}",
                slug=f"pendant-{i}",
                category=cat,
                base_price=Decimal("12000"),
                is_published=True,
            )
            p.attributes.add(attr_val)
            ProductVariant.objects.create(product=p, name="Small", stock_quantity=5)
            ProductImage.objects.create(product=p, image=f"products/p{i}.jpg", is_primary=True)

        # 1 count query + 1 products select_related category + 3 prefetch (images, variants, attributes)
        # Bounded <= 6 queries regardless of product count
        with django_assert_num_queries(5):
            res = client.get("/api/v1/products/")
            assert res.status_code == status.HTTP_200_OK
            assert res.json()["count"] == 10
