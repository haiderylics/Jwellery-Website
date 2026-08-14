# Deterministic Test Data Strategy & Reference Guide

This document defines the structured test data baseline required for comprehensive, repeatable manual QA across all storefront and admin workflows.

All test entities are clearly identified as **QA / DEMO ONLY** to prevent confusion with real commercial inventory or customer communications.

---

## 1. Quick Setup: Automated Seeder

For local development and staging environments, populate the entire baseline in one command:

```bash
uv run python backend/manage.py seed_demo_data
```

> [!IMPORTANT]
> The seeder is idempotent and guarded: it refuses to execute in production environments (`DEBUG=False`) without an explicit `--force` override.

---

## 2. Taxonomy & Attribute Test Matrix

### Categories
| Name | Slug | Sort Order | Purpose / Boundary |
|---|---|---|---|
| **Rings** | `rings` | 1 | Standard items, high variant density (sizes 6, 7, 8), out-of-stock samples |
| **Necklaces & Chokers** | `necklaces` | 2 | High-ticket items (PKR 420,000+), price overrides on extended length |
| **Earrings** | `earrings` | 3 | Simple single-SKU products without variants |
| **Bangles & Bracelets** | `bangles-bracelets` | 4 | Traditional diameter sizing (2.4, 2.6, 2.8) |
| **Bridal Sets** | `bridal-sets` | 5 | Luxury multi-piece sets (PKR 1,250,000+), bespoke custom order flag |

### Product Attributes
| Attribute Type | Slug | Allowed Values | Filter Style |
|---|---|---|---|
| **Metal & Purity** | `metal-purity` | `22K Yellow Gold`, `18K White Gold`, `Platinum 950` | Button / Chip |
| **Gemstone** | `gemstone` | `Solitaire Diamond`, `Zambian Emerald`, `Burmese Ruby`, `South Sea Pearl` | Button / Chip |

---

## 3. Product Catalog Baseline

### Sample 1: Variant Heavy with Price Override
- **Name**: `The Royal Solitaire Diamond Ring`
- **Slug**: `royal-solitaire-diamond-ring`
- **Category**: `Rings`
- **Base Price**: `PKR 185,000.00`
- **Compare-At Price**: `PKR 210,000.00` (Discount strike-through test)
- **Variants**:
  - `Size 6 (US)` (SKU: `RSR-06`, Price: `PKR 185,000.00`, Stock: 5)
  - `Size 7 (US)` (SKU: `RSR-07`, Price: `PKR 185,000.00`, Stock: 3)
  - `Size 8 (US)` (SKU: `RSR-08`, Price: `PKR 190,000.00` [Override], Stock: 2)
- **Attributes**: `18K White Gold`, `Solitaire Diamond`
- **Flags**: `is_featured = True`, `is_new_arrival = True`, `is_custom_order = True`

### Sample 2: Out of Stock Edge Case
- **Name**: `Archival Platinum Eternity Band [Out of Stock Demo]`
- **Slug**: `archival-platinum-eternity-band`
- **Category**: `Rings`
- **Base Price**: `PKR 240,000.00`
- **Stock Quantity**: `0`
- **Availability Status**: `out_of_stock`
- **Flags**: `is_published = True`, `is_custom_order = True`
- **Expected UX**: "Out of Stock" badge displayed, standard Add to Cart disabled, "Inquire for Bespoke Sizing via WhatsApp" button active.

### Sample 3: High Ticket Bridal Piece
- **Name**: `Noor-ul-Ain Royal Bridal Set`
- **Slug**: `noor-ul-ain-royal-bridal-set`
- **Category**: `Bridal Sets`
- **Base Price**: `PKR 1,250,000.00`
- **Compare-At Price**: `PKR 1,400,000.00`
- **Attributes**: `22K Yellow Gold`, `Burmese Ruby`
- **Flags**: `is_featured = True`, `is_custom_order = True`

---

## 4. Delivery Boundary Matrix

| Scenario | Subtotal Value | Free Threshold | Standard Fee | Expected Shipping Display | Expected Total |
|---|---|---|---|---|---|
| **Below Threshold** | PKR 4,500 | PKR 5,000 | PKR 250 | `PKR 250` | `PKR 4,750` |
| **Exact Threshold** | PKR 5,000 | PKR 5,000 | PKR 250 | `FREE (Order over PKR 5,000)` | `PKR 5,000` |
| **Above Threshold** | PKR 185,000 | PKR 5,000 | PKR 250 | `FREE (Order over PKR 5,000)` | `PKR 185,000` |

---

## 5. Marketing & Content Baseline

### Active Campaign
- **Title**: `Eid Festive Fine Jewellery Showcase`
- **Announcement Bar**: `✨ Complimentary Insured Shipping Across Pakistan on Orders Over PKR 5,000`
- **CTA**: `/shop?category=bridal-sets` (`Explore Collection`)
- **Status**: `is_active = True`, Scheduled across current date.

### Modal Popup
- **Title**: `Welcome to Zirconia Fine Jewels`
- **Message**: `Schedule a private viewing session for bridal sets, customized ring sizing, and authentic gold hallmarks in our Lahore atelier.`
- **Delay**: `3 seconds`
- **Status**: `is_active = True`

---

## 6. Customer Checkout Form Edge Cases

| Field | Valid Input Sample | Edge Case / Abuse Input | Expected Handling |
|---|---|---|---|
| **Full Name** | `Syeda Fatima Shah` | `<script>alert(1)</script>` or 250 chars | Sanitized, rendered safely as text without script execution |
| **Phone** | `03001234567` / `+923001234567` | `abc-xyz` or empty | Form blocks submission with inline validation message |
| **City** | `Lahore` | `Karachi` / `Islamabad` | Validates required field |
| **Address** | `House 14-B, Sector F-7/2, Islamabad` | Very long address (500 chars) | Bounded, included in WhatsApp message |
| **Order Notes** | `Please call before delivery.` | Multi-line text with emojis 💎 | URL-encoded properly into `wa.me` message |

---

## 7. Data Reset & Cleanup Procedures

To reset the database to a clean testing state:

1. **Flush Database**:
   ```bash
   uv run python backend/manage.py flush --no-input
   ```
2. **Run Migrations**:
   ```bash
   uv run python backend/manage.py migrate
   ```
3. **Re-seed Deterministic Data**:
   ```bash
   uv run python backend/manage.py seed_demo_data
   ```
4. **Create QA Staff User**:
   ```bash
   uv run python backend/manage.py createsuperuser --username admin --email admin@zirconiajewels.demo
   ```
