"""Verification tests for Custom Django Admin UX, branding, and QA seeder."""

import io

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, override_settings

from backend.apps.catalog.models import Category, Product
from backend.apps.common.templatetags.admin_dashboard_tags import get_operational_metrics

User = get_user_model()


@pytest.mark.django_db
class TestAdminBrandingAndDashboard:
    """Verify luxury Django Admin template overrides and dashboard metrics."""

    @pytest.fixture(autouse=True)
    def setup_staff(self):
        self.client = Client()
        self.staff_user = User.objects.create_superuser(
            username="admin_qa",
            email="admin_qa@zirconiajewels.demo",
            password="secure_admin_password_123",
        )

    def test_admin_login_page_renders_branded_templates(self):
        res = self.client.get("/admin/login/")
        assert res.status_code == 200
        content = res.content.decode("utf-8")
        assert "ZIRCONIA FINE JEWELS" in content
        assert "brand-monogram" in content
        assert "custom_admin.css" in content

    def test_admin_index_dashboard_renders_kpis_and_shortcuts(self):
        self.client.force_login(self.staff_user)
        res = self.client.get("/admin/")
        assert res.status_code == 200
        content = res.content.decode("utf-8")
        assert "admin-kpi-grid" in content
        assert "Total Catalog Pieces" in content
        assert "Quick Merchandising Actions" in content
        assert "View Live Storefront" in content

    def test_admin_promotions_and_popups_changelist_render_cleanly(self):
        from backend.apps.promotions.models import Popup, Promotion

        Promotion.objects.create(title="Promo Test", announcement_text="Test", is_active=True)
        Popup.objects.create(title="Popup Test", message="Test Msg", is_active=True)

        self.client.force_login(self.staff_user)

        res_promo = self.client.get("/admin/promotions/promotion/")
        assert res_promo.status_code == 200

        res_popup = self.client.get("/admin/promotions/popup/")
        assert res_popup.status_code == 200

    def test_operational_metrics_template_tag(self):
        category = Category.objects.create(name="Rings QA", slug="rings-qa")
        Product.objects.create(
            name="Solitaire QA",
            slug="solitaire-qa",
            category=category,
            base_price=100000,
            is_published=True,
        )
        Product.objects.create(
            name="Out of Stock QA",
            slug="oos-qa",
            category=category,
            base_price=120000,
            is_published=True,
            availability_status="out_of_stock",
        )

        metrics = get_operational_metrics()
        assert metrics["total_products"] >= 2
        assert metrics["published_products"] >= 2
        assert metrics["out_of_stock"] >= 1


@pytest.mark.django_db
class TestDemoDataSeeder:
    """Verify seed_demo_data command behavior, idempotence, and safety boundaries."""

    def test_seed_demo_data_executes_idempotently(self):
        out = io.StringIO()
        call_command("seed_demo_data", stdout=out)
        output = out.getvalue()
        assert "Deterministic QA / Demo Catalog seeded successfully!" in output

        # Re-running must be idempotent without primary key collision errors
        out2 = io.StringIO()
        call_command("seed_demo_data", stdout=out2)
        assert "Deterministic QA / Demo Catalog seeded successfully!" in out2.getvalue()

    def test_seed_demo_data_refuses_in_production_without_force(self):
        with override_settings(SETTINGS_MODULE="backend.config.settings.production"):
            with pytest.raises(
                CommandError, match="Refusing to seed demo data in production environment"
            ):
                call_command("seed_demo_data")
