"""Deterministic demo and QA data seeder for local & staging environments.

Creates a complete, realistic, and beautifully structured luxury jewellery catalog
for manual QA, responsive testing, and end-to-end verification.

Never runs automatically in production.
"""

import io
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from PIL import Image

from backend.apps.catalog.models import (
    Category,
    Product,
    ProductAttributeType,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
)
from backend.apps.common.media import generate_image_variants
from backend.apps.content.models import AboutSection, GalleryItem, Review
from backend.apps.promotions.models import Popup, Promotion
from backend.apps.settings.models import DeliverySettings, SiteSettings, SocialLink


def create_demo_image_content(
    name: str, color: tuple[int, int, int] = (180, 140, 60)
) -> ContentFile:
    """Generate a clean RGB test image with an elegant solid swatch."""
    buf = io.BytesIO()
    img = Image.new("RGB", (800, 800), color=color)
    img.save(buf, format="JPEG", quality=85)
    return ContentFile(buf.getvalue(), name=name)


class Command(BaseCommand):
    help = "Seed deterministic QA & demo data for local and staging manual verification."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Bypass safety checks when running in non-production environments.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Production Safety Check
        settings_module = str(getattr(settings, "SETTINGS_MODULE", "") or "")
        if "production" in settings_module and not options["force"]:
            raise CommandError(
                "Refusing to seed demo data in production environment without explicit --force flag. "
                "This command is strictly for development and QA staging."
            )

        self.stdout.write(
            self.style.MIGRATE_HEADING("\n=== Seeding Deterministic QA / Demo Catalog ===")
        )

        now = timezone.now()

        # 1. Site Settings
        self.stdout.write("1. Initializing Store & Business Settings...")
        site_settings = SiteSettings.get_solo()
        site_settings.brand_name = "Zirconia Fine Jewels"
        site_settings.tagline = "Bespoke Haute Joaillerie & Timeless Gold Craftsmanship"
        site_settings.contact_email = "concierge@zirconiajewels.demo"
        site_settings.whatsapp_number = "+923001234567"
        site_settings.phone_number = "+924235789000"
        site_settings.address = "Suite 402, Luxury Galleria, Gulberg III, Lahore, Pakistan"
        site_settings.currency_code = "PKR"
        site_settings.currency_symbol = "PKR "
        site_settings.save()

        # Social links
        SocialLink.objects.all().delete()
        SocialLink.objects.create(
            platform="Instagram",
            url="https://instagram.com/zirconiafinejewels.demo",
            is_active=True,
            sort_order=1,
        )
        SocialLink.objects.create(
            platform="Facebook",
            url="https://facebook.com/zirconiafinejewels.demo",
            is_active=True,
            sort_order=2,
        )

        # 2. Delivery Settings
        self.stdout.write("2. Initializing Pakistan & International Delivery Rules...")
        delivery = DeliverySettings.get_solo()
        delivery.free_delivery_threshold = Decimal("5000.00")
        delivery.pakistan_delivery_charge = Decimal("250.00")
        delivery.pakistan_delivery_enabled = True
        delivery.international_delivery_enabled = True
        delivery.international_delivery_note = (
            "International insured courier dispatch available upon consultation."
        )
        delivery.estimated_delivery_days = (
            "2 to 4 business days for Lahore & Karachi, 3 to 5 business days nationwide."
        )
        delivery.save()

        # 3. Attributes
        self.stdout.write("3. Creating Jewellery Specification Attributes...")
        metal_attr, _ = ProductAttributeType.objects.get_or_create(
            slug="metal-purity",
            defaults={"name": "Metal & Purity", "sort_order": 1},
        )
        gem_attr, _ = ProductAttributeType.objects.get_or_create(
            slug="gemstone",
            defaults={"name": "Gemstone", "sort_order": 2},
        )

        m_22k, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=metal_attr,
            slug="22k-gold",
            defaults={"value": "22K Yellow Gold", "sort_order": 1},
        )
        m_18k, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=metal_attr,
            slug="18k-gold",
            defaults={"value": "18K White Gold", "sort_order": 2},
        )
        m_plat, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=metal_attr,
            slug="platinum-950",
            defaults={"value": "Platinum 950", "sort_order": 3},
        )

        g_dia, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=gem_attr,
            slug="solitaire-diamond",
            defaults={"value": "Solitaire Diamond", "sort_order": 1},
        )
        g_eme, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=gem_attr,
            slug="zambian-emerald",
            defaults={"value": "Zambian Emerald", "sort_order": 2},
        )
        g_rub, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=gem_attr,
            slug="burmese-ruby",
            defaults={"value": "Burmese Ruby", "sort_order": 3},
        )
        g_pea, _ = ProductAttributeValue.objects.get_or_create(
            attribute_type=gem_attr,
            slug="south-sea-pearl",
            defaults={"value": "South Sea Pearl", "sort_order": 4},
        )

        # 4. Categories
        self.stdout.write("4. Creating Product Categories...")
        categories_data = [
            ("Rings", "rings", "Engagement solitaires, bespoke bands, and cocktail rings.", 1),
            (
                "Necklaces & Chokers",
                "necklaces",
                "Rivière diamond necklaces and handcrafted gold chokers.",
                2,
            ),
            ("Earrings", "earrings", "Chandelier drops, diamond studs, and polki jhumkas.", 3),
            (
                "Bangles & Bracelets",
                "bangles-bracelets",
                "Traditional kadas and modern diamond tennis bracelets.",
                4,
            ),
            (
                "Bridal Sets",
                "bridal-sets",
                "Comprehensive heirloom bridal collections for weddings.",
                5,
            ),
        ]

        created_categories = {}
        for name, slug, desc, order in categories_data:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "sort_order": order,
                    "is_active": True,
                },
            )
            created_categories[slug] = cat

        # 5. Products & Variants
        self.stdout.write("5. Seeding Demo Jewellery Products & Variants...")

        demo_products = [
            {
                "name": "The Royal Solitaire Diamond Ring",
                "slug": "royal-solitaire-diamond-ring",
                "category": created_categories["rings"],
                "short_description": "Exquisite 1.50ct round brilliant solitaire diamond set in a 6-prong 18K white gold cathedral band.",
                "description": "Crafted with impeccable symmetry, the Royal Solitaire features an independently certified center stone flanked by micro-pave diamonds along the shank. Every piece is hand-finished in our Lahore atelier.",
                "base_price": Decimal("185000.00"),
                "compare_at_price": Decimal("210000.00"),
                "stock_quantity": 10,
                "availability_status": "in_stock",
                "is_featured": True,
                "is_new_arrival": True,
                "is_custom_order": True,
                "color": (220, 200, 160),
                "attributes": [m_18k, g_dia],
                "variants": [
                    ("Size 6 (US)", "RSR-06", Decimal("185000.00"), 5),
                    ("Size 7 (US)", "RSR-07", Decimal("185000.00"), 3),
                    ("Size 8 (US)", "RSR-08", Decimal("190000.00"), 2),
                ],
            },
            {
                "name": "Zambian Emerald & Diamond Choker",
                "slug": "zambian-emerald-diamond-choker",
                "category": created_categories["necklaces"],
                "short_description": "Heirloom 22K yellow gold choker featuring vivid green emerald cabochons and brilliant-cut diamonds.",
                "description": "Inspired by traditional Mughal royal jewelry, this choker showcases natural Zambian emeralds framed by round brilliant diamonds on a handcrafted 22K gold openwork lattice.",
                "base_price": Decimal("420000.00"),
                "compare_at_price": None,
                "stock_quantity": 3,
                "availability_status": "in_stock",
                "is_featured": True,
                "is_new_arrival": False,
                "is_custom_order": True,
                "color": (160, 190, 140),
                "attributes": [m_22k, g_eme],
                "variants": [
                    ("Standard 16-inch Choker", "ZEC-STD", None, 2),
                    ("Extended 18-inch Fit", "ZEC-EXT", Decimal("450000.00"), 1),
                ],
            },
            {
                "name": "South Sea Pearl Drop Earrings",
                "slug": "south-sea-pearl-drop-earrings",
                "category": created_categories["earrings"],
                "short_description": "Lustrous 12mm South Sea cultured pearls suspended from pave diamond leaf motifs in 18K white gold.",
                "description": "Perfect for evening galas and bridal occasions, these drops combine deep organic pearl luster with glittering diamond sparkle.",
                "base_price": Decimal("95000.00"),
                "compare_at_price": Decimal("110000.00"),
                "stock_quantity": 5,
                "availability_status": "in_stock",
                "is_featured": True,
                "is_new_arrival": True,
                "is_custom_order": False,
                "color": (230, 230, 220),
                "attributes": [m_18k, g_pea],
                "variants": [],
            },
            {
                "name": "Heritage 22K Gold Filigree Bangle",
                "slug": "heritage-22k-gold-filigree-bangle",
                "category": created_categories["bangles-bracelets"],
                "short_description": "Substantial 22K handcrafted gold kada featuring intricate pierced floral filigree and screw closure.",
                "description": "Weighing 32 grams of pure hallmarked gold, each filigree petal is shaped individually by master goldsmiths.",
                "base_price": Decimal("295000.00"),
                "compare_at_price": None,
                "stock_quantity": 8,
                "availability_status": "in_stock",
                "is_featured": False,
                "is_new_arrival": True,
                "is_custom_order": True,
                "color": (210, 170, 70),
                "attributes": [m_22k],
                "variants": [
                    ("Size 2.4", "HGB-24", None, 3),
                    ("Size 2.6", "HGB-26", None, 4),
                    ("Size 2.8", "HGB-28", Decimal("315000.00"), 1),
                ],
            },
            {
                "name": "Noor-ul-Ain Royal Bridal Set",
                "slug": "noor-ul-ain-royal-bridal-set",
                "category": created_categories["bridal-sets"],
                "short_description": "Grand multi-tier bridal set including heavy choker, chandelier jhumkas, teeka, and matha patti.",
                "description": "The quintessential Pakistani bridal statement. Handcrafted over 180 atelier hours in 22K hallmarked gold with uncut polki diamonds and Burmese ruby drops.",
                "base_price": Decimal("1250000.00"),
                "compare_at_price": Decimal("1400000.00"),
                "stock_quantity": 2,
                "availability_status": "in_stock",
                "is_featured": True,
                "is_new_arrival": False,
                "is_custom_order": True,
                "color": (190, 120, 100),
                "attributes": [m_22k, g_rub],
                "variants": [],
            },
            {
                "name": "Archival Platinum Eternity Band [Out of Stock Demo]",
                "slug": "archival-platinum-eternity-band",
                "category": created_categories["rings"],
                "short_description": "Continuous channel of calibrated baguette diamonds in 950 Platinum.",
                "description": "Continuous sparkle for anniversaries and bespoke stacking.",
                "base_price": Decimal("240000.00"),
                "compare_at_price": None,
                "stock_quantity": 0,
                "availability_status": "out_of_stock",
                "is_featured": False,
                "is_new_arrival": False,
                "is_custom_order": True,
                "color": (180, 180, 190),
                "attributes": [m_plat, g_dia],
                "variants": [],
            },
        ]

        # Clean up any legacy or untracked development test products
        demo_slugs = [p["slug"] for p in demo_products]
        Product.objects.exclude(slug__in=demo_slugs).delete()

        for p_data in demo_products:
            prod, created = Product.objects.update_or_create(
                slug=p_data["slug"],
                defaults={
                    "name": p_data["name"],
                    "category": p_data["category"],
                    "short_description": p_data["short_description"],
                    "description": p_data["description"],
                    "base_price": p_data["base_price"],
                    "compare_at_price": p_data["compare_at_price"],
                    "stock_quantity": p_data["stock_quantity"],
                    "availability_status": p_data["availability_status"],
                    "is_published": True,
                    "is_featured": p_data["is_featured"],
                    "is_new_arrival": p_data["is_new_arrival"],
                    "is_custom_order": p_data["is_custom_order"],
                },
            )

            # Assign Attributes
            prod.attributes.set(p_data["attributes"])

            # Assign Variants
            ProductVariant.objects.filter(product=prod).delete()
            for v_name, sku, price_override, stock_qty in p_data["variants"]:
                ProductVariant.objects.create(
                    product=prod,
                    name=v_name,
                    sku=sku,
                    price_override=price_override,
                    stock_quantity=stock_qty,
                    is_available=(stock_qty > 0),
                )

            # Primary Image
            ProductImage.objects.filter(product=prod).delete()
            img_file = create_demo_image_content(f"{prod.slug}_primary.jpg", p_data["color"])
            prod_img = ProductImage.objects.create(
                product=prod,
                image=img_file,
                alt_text=f"{prod.name} showcase in atelier",
                is_primary=True,
                sort_order=1,
            )
            generate_image_variants(prod_img.image.name)

        # 6. Promotions & Popups
        self.stdout.write("6. Seeding Promotions & Popups...")
        Promotion.objects.all().delete()
        promo_img = create_demo_image_content("eid_festive_banner.jpg", (190, 150, 70))
        promo = Promotion.objects.create(
            title="Eid Festive Fine Jewellery Showcase",
            subtitle="Complimentary insured delivery across Pakistan on all bridal and festive orders.",
            announcement_text="✨ Complimentary Insured Shipping Across Pakistan on Orders Over PKR 5,000",
            image=promo_img,
            cta_label="Explore Collection",
            cta_url="/shop?category=bridal-sets",
            start_datetime=now - timezone.timedelta(days=2),
            end_datetime=now + timezone.timedelta(days=30),
            is_active=True,
            priority=1,
        )
        generate_image_variants(promo.image.name)

        Popup.objects.all().delete()
        popup_img = create_demo_image_content("popup_atelier.jpg", (200, 170, 90))
        popup = Popup.objects.create(
            title="Welcome to Zirconia Fine Jewels",
            message="Schedule a private viewing session for bridal sets, customized ring sizing, and authentic gold hallmarks in our Lahore atelier.",
            image=popup_img,
            cta_label="Explore Collection",
            cta_url="/shop",
            is_active=True,
            delay_seconds=3,
        )
        generate_image_variants(popup.image.name)

        # 7. Reviews & Content
        self.stdout.write("7. Seeding Verified Client Reviews & Atelier Moments...")
        Review.objects.all().delete()
        rev1_img = create_demo_image_content("review_amina.jpg", (180, 140, 100))
        rev1 = Review.objects.create(
            customer_name="Amina Farooq (Demo Test)",
            review_text="The Royal Solitaire ring exceeded all our expectations. The diamond clarity and gold weight are breathtaking. Thank you for the swift WhatsApp consultation!",
            rating=5,
            image=rev1_img,
            is_published=True,
            is_verified=True,
            sort_priority=1,
        )
        generate_image_variants(rev1.image.name)

        Review.objects.create(
            customer_name="Dr. Salman Qureshi (Demo Test)",
            review_text="Ordered the South Sea pearl drops for my wife's anniversary. Exceptional presentation box, hallmarked certificates, and flawless dispatch to Islamabad.",
            rating=5,
            is_published=True,
            is_verified=True,
            sort_priority=2,
        )

        AboutSection.objects.all().delete()
        about_img = create_demo_image_content("about_atelier.jpg", (170, 130, 80))
        about = AboutSection.objects.create(
            title="A Legacy of Timeless Goldsmithing",
            subtitle="Artisanal Haute Joaillerie crafted in our private Lahore atelier.",
            story_text="Founded with a passion for architectural purity and traditional heritage, Zirconia Fine Jewels creates bespoke pieces in hallmarked 22K/18K gold and certified gemstones. Every piece represents hours of dedicated mastercraft in our private atelier.",
            image=about_img,
            is_active=True,
        )
        generate_image_variants(about.image.name)

        # 8. Gallery
        GalleryItem.objects.all().delete()
        for idx, title in enumerate(
            ["Bridal Atelier Showcase", "Solitaire Ring Crafting", "Polki Setting Detail"], 1
        ):
            g_img = create_demo_image_content(f"gallery_moment_{idx}.jpg", (190, 160, 110))
            g_item = GalleryItem.objects.create(
                title=f"{title} [DEMO]",
                image=g_img,
                caption="Behind the scenes in our Lahore jewellery atelier.",
                item_type="brand",
                is_published=True,
                sort_priority=idx,
            )
            generate_image_variants(g_item.image.name)

        self.stdout.write(
            self.style.SUCCESS("\n[OK] Deterministic QA / Demo Catalog seeded successfully!")
        )
        self.stdout.write("Summary:")
        self.stdout.write(f"  - Categories: {Category.objects.count()}")
        self.stdout.write(f"  - Products: {Product.objects.count()}")
        self.stdout.write(f"  - Product Variants: {ProductVariant.objects.count()}")
        self.stdout.write(f"  - Product Images: {ProductImage.objects.count()}")
        self.stdout.write(f"  - Promotions: {Promotion.objects.count()}")
        self.stdout.write(f"  - Reviews: {Review.objects.count()}")
        self.stdout.write(f"  - Gallery Items: {GalleryItem.objects.count()}\n")
