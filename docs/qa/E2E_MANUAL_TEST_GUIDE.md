# Pre-Production End-to-End Manual Testing Guide

This guide provides a human-executable, step-by-step verification protocol for the entire Jewellery Website platform.

Follow this guide sequentially before considering any production deployment. No source code inspection is required to execute these manual tests.

---

## Table of Contents
1. [Environment Startup & Health Verification](#1-environment-startup--health-verification)
2. [Admin Operations Console & Authentication](#2-admin-operations-console--authentication)
3. [Catalog & Merchandising Management](#3-catalog--merchandising-management)
4. [Media Upload & Responsive Image Validation](#4-media-upload--responsive-image-validation)
5. [Marketing, Promotions & Popups](#5-marketing-promotions--popups)
6. [Storefront Customer Experience (E2E)](#6-storefront-customer-experience-e2e)
7. [Shopping Cart & WhatsApp Checkout Protocol](#7-shopping-cart--whatsapp-checkout-protocol)
8. [Mobile & Tablet Responsive Verification](#8-mobile--tablet-responsive-verification)
9. [Keyboard Navigation & Accessibility](#9-keyboard-navigation--accessibility)
10. [Security Abuse & Edge Case Scenarios](#10-security-abuse--edge-case-scenarios)
11. [Data Consistency & Cache Invalidation](#11-data-consistency--cache-invalidation)
12. [Defect Reporting & Test Reset Protocol](#12-defect-reporting--test-reset-protocol)

---

## 1. Environment Startup & Health Verification

### Step 1.1: Start Local Servers
1. Open a terminal in the project root (`d:\Jwellery Website`) and start the backend:
   ```bash
   uv run .\manage.py runserver
   ```
   *Expected Output*: `Starting development server at http://127.0.0.1:8000/` with 0 errors.

2. Open a second terminal and start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```
   *Expected Output*: `VITE v6.4.3 ready in ... ms` -> Local: `http://localhost:5173/`.

### Step 1.2: Check System Health Endpoints
1. Open your browser and navigate to: `http://127.0.0.1:8000/health/live/`
   *Expected Result*: Returns `{"status": "ok"}` with HTTP status 200.
2. Navigate to: `http://127.0.0.1:8000/health/ready/`
   *Expected Result*: Returns `{"status": "ready"}` with HTTP status 200.
3. Verify that zero internal stack traces, system paths, or credentials appear in the responses.

---

## 2. Admin Operations Console & Authentication

### Step 2.1: Seed Deterministic QA Catalog
In your terminal, seed the clean baseline catalog:
```bash
uv run python backend/manage.py seed_demo_data
```
*Expected Result*: Success confirmation listing 5 categories, 9 products, 9 variants, 7 images, 1 promotion, 2 reviews, and 3 gallery items.

### Step 2.2: Staff Login Flow
1. Navigate to `http://127.0.0.1:8000/admin/`.
2. Verify the branded login interface:
   - Deep obsidian background with refined gold monogram badge (`Z`).
   - Clean typography with "ZIRCONIA FINE JEWELS" header.
3. Test invalid login:
   - Enter Username: `admin`, Password: `wrongpassword123`. Click **Log In**.
   - *Expected Result*: Displays "Please enter the correct username and password".
4. Test valid staff login:
   - Enter valid staff credentials and click **Log In**.
   - *Expected Result*: Redirects to dashboard showing:
     - Top KPI cards (Total Pieces, Live on Storefront, Out of Stock, Active Campaigns, Client Reviews).
     - Quick Merchandising Action buttons (+ Add Piece, + Create Promotion, Store Settings).
     - Link to **"View Live Storefront"** in the top navigation.

---

## 3. Catalog & Merchandising Management

### Step 3.1: Create a New Jewellery Piece
1. In Admin, click **"+ Add New Jewellery Piece"** or go to **Catalog -> Products -> Add Product**.
2. Enter the following details:
   - **Name**: `Bespoke Solitaire Diamond Ring [QA Test]`
   - **Slug**: Leave blank (auto-generates from name).
   - **Category**: Select `Rings`.
   - **Base Price**: `195000.00`
   - **Compare At Price**: `220000.00`
   - **Stock Quantity**: `4`
   - **Availability Status**: `In Stock`
   - **Is Published**: Checked
   - **Is Featured**: Checked
   - **Is Custom Order**: Checked
3. In the **Product Images inline**, upload a JPEG photo (e.g. `ring.jpg`), set Alt Text: `Bespoke Solitaire Ring Test`, check **Is Primary**, and click **Save**.
4. *Expected Result*:
   - Product saves successfully with message *"The Product was added successfully"*.
   - In storage, `_thumb.webp`, `_medium.webp`, and `_large.webp` variants are generated.

### Step 3.2: Configure Multi-Size Variants
1. Re-open the newly created product.
2. Scroll to **Product Variants inline** and add 2 rows:
   - Row 1: Name `Size 6 (US)`, SKU `BSR-06`, Stock `2`, Price Override: (blank).
   - Row 2: Name `Size 8 (US)`, SKU `BSR-08`, Stock `2`, Price Override: `205000.00`.
3. Click **Save**.
4. *Expected Result*: Variants save without error.

---

## 4. Media Upload & Responsive Image Validation

### Step 4.1: Valid High-Resolution Upload
1. Upload a large 2000x2000px high-resolution JPEG photo to a product or gallery item.
2. Save the record.
3. Inspect the storefront in browser DevTools Network tab:
   - Filter by `Img`.
   - Verify the browser downloads a modern `.webp` variant tailored to the viewport size.
   - Verify image dimensions fit within aspect-ratio containers without distortion or stretching.

### Step 4.2: Upload Security & Rejection Tests
1. Attempt to upload a `.txt` file renamed to `malicious.jpg`.
   *Expected Result*: Django Admin displays validation error *"Corrupted or invalid image file. Only JPEG, PNG, and WebP images are permitted."*
2. Attempt to upload an image exceeding 10 MB.
   *Expected Result*: Admin displays validation error *"Image file size exceeds maximum limit of 10.0 MB."*

---

## 5. Marketing, Promotions & Popups

### Step 5.1: Top Announcement Bar
1. Navigate to **Admin -> Promotions -> Promotions**.
2. Open `Eid Festive Fine Jewellery Showcase`.
3. Modify Announcement Text to: `✨ Festive Complimentary Shipping Nationwide on All Orders Above PKR 5,000`.
4. Click **Save**.
5. Switch to storefront tab (`http://localhost:5173/`) and refresh:
   *Expected Result*: Top announcement bar immediately reflects the updated wording.

### Step 5.2: Timed VIP Modal Popup
1. In Admin, go to **Promotions -> Popup Announcements**.
2. Ensure active popup is configured with `delay_seconds: 3`.
3. Open a new private/incognito window and navigate to `http://localhost:5173/`.
4. Wait 3 seconds:
   *Expected Result*:
   - Modal popup fades in with title "Welcome to Zirconia Fine Jewels".
   - Pressing the `Escape` key closes the modal instantly.
   - Background scroll is locked while popup is active.

---

## 6. Storefront Customer Experience (E2E)

### Step 6.1: Homepage Exploration
1. Load `http://localhost:5173/`.
2. Verify visual sections:
   - **Header**: Monogram, Navigation (`Shop All`, `Rings`, `Necklaces`, `Bridal`, `Our Story`), Cart Counter badge.
   - **Hero**: Atmospheric goldsmithing imagery, headline, and "Explore Collection" button.
   - **Category Showcase**: Clickable tiles for Rings, Necklaces, Earrings, Bangles, Bridal Sets.
   - **Featured Pieces**: Responsive product cards with image hover transitions, price display, and Quick View/Detail links.
   - **Client Testimonials**: Verified customer feedback cards.
   - **Atelier Gallery**: High-resolution workshop and exhibition moments.
   - **Footer**: Brand story, direct concierge phone/WhatsApp, address in Lahore, and social media links.

### Step 6.2: Shop Catalog & Faceted Search
1. Click **"Shop All"** in navigation (routes to `/shop`).
2. Test real-time search:
   - Type `solitaire` in the search bar.
   - *Expected Result*: Product grid instantly updates to show only matching solitaire items.
3. Test Category chips:
   - Click `Bridal Sets`.
   - *Expected Result*: URL updates to `/shop?category=bridal-sets` and displays the `Noor-ul-Ain Royal Bridal Set`.
4. Test Sort options:
   - Select `Price: High to Low` from the sort dropdown.
   - *Expected Result*: Grand bridal sets appear first, followed by chokers and rings.

---

## 7. Shopping Cart & WhatsApp Checkout Protocol

### Step 7.1: Product Selection & Variant Interaction
1. Open `The Royal Solitaire Diamond Ring` from the shop.
2. On the Product Detail Page (PDP):
   - Click each thumbnail in the gallery strip; verify the main photo changes smoothly.
   - Click the variant selector and choose `Size 8 (US)`.
   - *Expected Result*: The displayed price dynamically changes from `PKR 185,000` to `PKR 190,000` (price override).
3. Set Quantity to `1` and click **"Add to Bag"**.
   - *Expected Result*: Cart badge in header updates to `1`.

### Step 7.2: Cart Calculations & Delivery Threshold
1. Click the Cart icon in the header (opens `/cart`).
2. Verify line item breakdown:
   - Item: `The Royal Solitaire Diamond Ring (Size 8 (US))`
   - Price: `PKR 190,000`
   - Subtotal: `PKR 190,000`
   - Delivery: `FREE (Order over PKR 5,000)`
   - Grand Total: `PKR 190,000`
3. Click the `+` button to increase quantity to `2`.
   - *Expected Result*: Subtotal updates to `PKR 380,000`.

### Step 7.3: Customer Delivery Form & WhatsApp Order Generation
1. On the cart page, scroll to the **Delivery & Consultation Details** form.
2. Fill in the fields:
   - **Full Name**: `Sara Ahmed`
   - **WhatsApp Phone**: `03001234567`
   - **City**: `Lahore`
   - **Delivery Address**: `House 12, Street 4, DHA Phase 5, Lahore`
   - **Order Notes**: `Please include velvet gift box and hallmarked authenticity certificate.`
3. Click **"Order via WhatsApp"**.
4. **DO NOT send a real message.** Instead, inspect the opened URL:
   *Expected URL Structure*:
   ```text
   https://wa.me/923001234567?text=...
   ```
   *Decoded Message Verification*:
   - Business Phone: `923001234567`
   - Customer Name: `Sara Ahmed`
   - City & Address: `Lahore`, `House 12, Street 4, DHA Phase 5, Lahore`
   - Items: `1. The Royal Solitaire Diamond Ring (Size 8 (US)) - Qty: 2 × PKR 190,000 = PKR 380,000`
   - Direct Product Link: `http://localhost:5173/product/royal-solitaire-diamond-ring`
   - Subtotal: `PKR 380,000`
   - Shipping: `FREE (Order over PKR 5,000)`
   - Estimated Total: `PKR 380,000`

---

## 8. Mobile & Tablet Responsive Verification

### Step 8.1: Mobile Viewport (390px - iPhone 14)
1. Open Chrome DevTools (`F12`), toggle Device Toolbar, and select **iPhone 12/13/14 (390x844)**.
2. Navigate through `/`, `/shop`, `/product/...`, and `/cart`.
3. Verify:
   - Mobile navigation hamburger menu expands smoothly.
   - Product cards collapse cleanly into single or double column touch-friendly layout.
   - On PDP, sticky "Add to Bag / Consult" bottom bar is accessible.
   - Cart checkout form inputs fit viewport with zero horizontal scrolling.

### Step 8.2: Tablet Viewport (768px - iPad)
1. In DevTools, select **iPad Air (820x1180)**.
2. Verify:
   - Header navigation displays properly without colliding with brand title.
   - Product grid displays a balanced 2 or 3-column layout.

---

## 9. Keyboard Navigation & Accessibility

### Step 9.1: Full Keyboard Tab Order
1. Disconnect or stop using your mouse.
2. Use `Tab` to navigate forward, `Shift+Tab` to navigate backward, `Enter` to activate links, and `Space` to toggle buttons.
3. Verify:
   - Clear gold focus rings appear around every active interactive element.
   - Focus order proceeds logically from top header -> main content -> footer.
   - Skip to main content link allows bypassing header.

---

## 10. Security Abuse & Edge Case Scenarios

### Step 10.1: HTML / Script Injection (XSS)
1. In Admin, edit a product name or review to: `<script>alert('XSS')</script> Diamond Ring`.
2. Save and view on storefront.
3. *Expected Result*: Displays literal text `<script>alert('XSS')</script> Diamond Ring`. No JavaScript executes.

### Step 10.2: LocalStorage Tampering
1. In browser DevTools -> Application -> Local Storage, edit `zirconia_cart_v1` JSON to set `quantity: -99` or `quantity: 10000`.
2. Refresh the page.
3. *Expected Result*: Cart store automatically sanitizes the corrupted value and clamps quantity safely to valid bounds [1..99].

### Step 10.3: Direct API Mutation Block
1. In terminal or Postman, send a POST request:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/products/ -d "{\"name\":\"Hacked\"}"
   ```
2. *Expected Result*: Returns `HTTP 405 Method Not Allowed`.

---

## 11. Data Consistency & Cache Invalidation

### Step 11.1: Live Price Update Consistency
1. Open storefront in tab 1 (`http://localhost:5173/shop`). Note price of `The Royal Solitaire Diamond Ring` (`PKR 185,000`).
2. In Admin (tab 2), update Base Price to `PKR 199,000.00`. Click **Save**.
3. Return to tab 1 and refresh.
4. *Expected Result*: Storefront immediately displays `PKR 199,000`. Cache invalidation signal executed post-commit without stale delay.

---

## 12. Defect Reporting & Test Reset Protocol

### Logging Defects
If any step fails, document the exact issue using [docs/qa/BUG_REPORT_TEMPLATE.md](file:///d:/Jwellery%20Website/docs/qa/BUG_REPORT_TEMPLATE.md).

### Resetting Environment for Next QA Pass
To return the environment to a pristine state:
```bash
uv run python backend/manage.py flush --no-input
uv run python backend/manage.py migrate
uv run python backend/manage.py seed_demo_data
```
