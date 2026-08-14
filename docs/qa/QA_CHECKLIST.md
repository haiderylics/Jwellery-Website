# Pre-Production Manual QA Execution Checklist

**Tester Name**: __________________________  
**Execution Date**: __________________________  
**Target Environment**: Local (`http://localhost:5173`) / Staging  
**Overall Status**: `[ ] READY FOR PRODUCTION CANDIDATE` &nbsp;&nbsp; `[ ] BLOCKED (Open P0/P1 Defects)`

---

## Execution Results Summary

| Section | Total Cases | PASS | FAIL | BLOCKED | N/A |
|---|---|---|---|---|---|
| 1. Environment & Startup | 4 | [ ] | [ ] | [ ] | [ ] |
| 2. Admin Authentication & UI | 5 | [ ] | [ ] | [ ] | [ ] |
| 3. Permissions & Role Boundaries | 3 | [ ] | [ ] | [ ] | [ ] |
| 4. Catalog Management | 6 | [ ] | [ ] | [ ] | [ ] |
| 5. Variants & Pricing | 4 | [ ] | [ ] | [ ] | [ ] |
| 6. Media Pipeline & Storage | 5 | [ ] | [ ] | [ ] | [ ] |
| 7. Reviews, Gallery & Brand Story | 4 | [ ] | [ ] | [ ] | [ ] |
| 8. Delivery & Site Settings | 4 | [ ] | [ ] | [ ] | [ ] |
| 9. Promotions & Popups | 4 | [ ] | [ ] | [ ] | [ ] |
| 10. Public Read-Only API | 5 | [ ] | [ ] | [ ] | [ ] |
| 11. Storefront Home & Navigation | 4 | [ ] | [ ] | [ ] | [ ] |
| 12. Storefront Shop & Filtering | 5 | [ ] | [ ] | [ ] | [ ] |
| 13. Product Detail & Variant Selector | 5 | [ ] | [ ] | [ ] | [ ] |
| 14. Shopping Cart & Calculations | 5 | [ ] | [ ] | [ ] | [ ] |
| 15. Checkout Form & WhatsApp Handoff | 5 | [ ] | [ ] | [ ] | [ ] |
| 16. Responsive Viewport Matrix | 4 | [ ] | [ ] | [ ] | [ ] |
| 17. Accessibility & Keyboard Flow | 3 | [ ] | [ ] | [ ] | [ ] |
| 18. Security & Abuse Resistance | 5 | [ ] | [ ] | [ ] | [ ] |
| 19. Error Recovery & Resilience | 3 | [ ] | [ ] | [ ] | [ ] |
| 20. Data Consistency & Cache Freshness | 3 | [ ] | [ ] | [ ] | [ ] |
| **TOTAL** | **82** | **[ ]** | **[ ]** | **[ ]** | **[ ]** |

---

## Detailed Checklist by Area

### 1. Environment & Startup
- [ ] `TC-ENV-01`: Backend server starts cleanly with `uv run .\manage.py runserver` (Port 8000).
- [ ] `TC-ENV-02`: Frontend dev server starts cleanly with `npm run dev` (Port 5173).
- [ ] `TC-ENV-03`: Liveness probe `/health/live/` returns `{"status": "ok"}` (HTTP 200).
- [ ] `TC-ENV-04`: Readiness probe `/health/ready/` verifies database connectivity (HTTP 200).

### 2. Admin Authentication & UI
- [ ] `TC-AUTH-01`: Admin login page displays luxury ZIRCONIA branding and monogram.
- [ ] `TC-AUTH-02`: Valid staff credentials log in and redirect to branded dashboard.
- [ ] `TC-AUTH-03`: Invalid credentials display user-friendly error without leaking system internals.
- [ ] `TC-AUTH-04`: Admin logout clears session and redirects cleanly to login form.
- [ ] `TC-AUTH-05`: KPI metric cards display accurate product counts and operational shortcuts.

### 3. Permissions & Role Boundaries
- [ ] `TC-PERM-01`: Non-staff user attempting `/admin/` access is strictly blocked.
- [ ] `TC-PERM-02`: Singleton models (`SiteSettings`, `DeliverySettings`) block duplicate creation.
- [ ] `TC-PERM-03`: Object deletion confirmation displays dependent records safely.

### 4. Catalog Management
- [ ] `TC-CAT-01`: Create new category; verify correct slug generation and sorting order.
- [ ] `TC-PROD-01`: Create product with title, description, category, and base price.
- [ ] `TC-PROD-02`: Negative price or invalid stock quantity is blocked with validation error.
- [ ] `TC-PROD-03`: Compare-at price strike-through renders properly on storefront.
- [ ] `TC-PROD-04`: Uncheck `is_published`; verify product disappears from storefront immediately.
- [ ] `TC-PROD-05`: Check `is_custom_order`; verify bespoke inquiry button renders on PDP.

### 5. Variants & Pricing
- [ ] `TC-VAR-01`: Add multiple ring size variants (e.g. Size 6, Size 7, Size 8).
- [ ] `TC-VAR-02`: Apply price override on specific variant; verify dynamic price update on selection.
- [ ] `TC-VAR-03`: Set variant stock to 0; verify marked out-of-stock in selector.
- [ ] `TC-VAR-04`: Product without variants uses base product price and stock cleanly.

### 6. Media Pipeline & Storage
- [ ] `TC-MED-01`: Upload 3000x3000px high-resolution JPEG; verify `thumb`, `medium`, `large` WebP variants generated in storage.
- [ ] `TC-MED-02`: Upload non-image (`.exe` / `.txt` disguised as `.jpg`); verify rejection with security log.
- [ ] `TC-MED-03`: Upload oversized file (>10MB); verify rejection.
- [ ] `TC-MED-04`: Replace product image in Admin; verify old image file and variants safely cleaned up.
- [ ] `TC-MED-05`: Run `python manage.py audit_media --dry-run`; verify 0 missing files or unmanaged orphans.

### 7. Reviews, Gallery & Brand Story
- [ ] `TC-REV-01`: Publish 5-star customer review; verify display in testimonials carousel.
- [ ] `TC-REV-02`: Unpublish review; verify immediate removal from public API and storefront.
- [ ] `TC-GAL-01`: Upload atelier gallery moment; verify thumbnail rendering on `/gallery`.
- [ ] `TC-ABT-01`: Update About section narrative; verify immediate update on storefront Story section.

### 8. Delivery & Site Settings
- [ ] `TC-DEL-01`: Set Free Shipping Threshold: PKR 5,000, Delivery Charge: PKR 250.
- [ ] `TC-DEL-02`: Cart subtotal below PKR 5,000 includes PKR 250 delivery fee.
- [ ] `TC-DEL-03`: Cart subtotal >= PKR 5,000 calculates Free Shipping.
- [ ] `TC-SET-01`: Update business WhatsApp number; verify all CTA links update instantly.

### 9. Promotions & Popups
- [ ] `TC-PRM-01`: Active promotion displays announcement bar across top of storefront.
- [ ] `TC-PRM-02`: Expired promotion disappears automatically based on datetime schedule.
- [ ] `TC-POP-01`: Active popup modal triggers after specified delay (3s).
- [ ] `TC-POP-02`: Dismissing popup with close button or `Escape` key closes modal cleanly.

### 10. Public Read-Only API
- [ ] `TC-API-01`: `POST /api/v1/products/` returns `HTTP 405 Method Not Allowed`.
- [ ] `TC-API-02`: `PUT /api/v1/site-settings/` returns `HTTP 405 Method Not Allowed`.
- [ ] `TC-API-03`: `DELETE /api/v1/categories/` returns `HTTP 405 Method Not Allowed`.
- [ ] `TC-API-04`: `GET /api/v1/products/` supports pagination, search, and category filtering.
- [ ] `TC-API-05`: `GET /api/v1/home/` returns aggregated homepage sections in a single roundtrip.

### 11. Storefront Home & Navigation
- [ ] `TC-HOME-01`: Header displays brand monogram, navigation links, and cart badge.
- [ ] `TC-HOME-02`: Hero section renders luxury gold visuals and primary CTA button.
- [ ] `TC-HOME-03`: Category cards navigate directly to filtered shop collection.
- [ ] `TC-HOME-04`: Footer displays contact information, address, and social links.

### 12. Storefront Shop & Filtering
- [ ] `TC-SHOP-01`: Search bar filters products by name and description in real-time.
- [ ] `TC-SHOP-02`: Category chips filter product grid and update URL query parameters.
- [ ] `TC-SHOP-03`: Attribute filters (Metal, Gemstone) narrow product catalog accurately.
- [ ] `TC-SHOP-04`: Sort dropdown (Price Low-to-High, High-to-Low, Newest) updates product order.
- [ ] `TC-SHOP-05`: Clear all filters button resets catalog and URL query parameters.

### 13. Product Detail & Variant Selector
- [ ] `TC-PDP-01`: Primary image display supports click-to-zoom or high-res inspection.
- [ ] `TC-PDP-02`: Thumbnail strip switches active hero image on click/tap.
- [ ] `TC-PDP-03`: Variant selector updates price and stock status dynamically.
- [ ] `TC-PDP-04`: Specifications table lists metal purity, gemstone, and hallmarking details.
- [ ] `TC-PDP-05`: "Add to Cart" button adds selected variant and updates header counter badge.

### 14. Shopping Cart & Calculations
- [ ] `TC-CART-01`: Adding multiple products calculates accurate subtotal and line items.
- [ ] `TC-CART-02`: Quantity increment `+` and decrement `-` buttons update line totals in real-time.
- [ ] `TC-CART-03`: Decrementing quantity from 1 or clicking "Remove" removes item from cart.
- [ ] `TC-CART-04`: Refreshing browser preserves cart state from `localStorage`.
- [ ] `TC-CART-05`: "Clear Cart" button empties all items and resets totals to PKR 0.

### 15. Checkout Form & WhatsApp Handoff
- [ ] `TC-CHK-01`: Form validates required fields (Full Name, Phone, City, Delivery Address).
- [ ] `TC-CHK-02`: Inline validation error highlights missing required fields.
- [ ] `TC-WA-01`: "Order via WhatsApp" button opens structured `https://wa.me/...` URL.
- [ ] `TC-WA-02`: WhatsApp message contains customer details, items, variants, prices, and grand total.
- [ ] `TC-WA-03`: WhatsApp URL is properly encoded without broken characters or truncation.

### 16. Responsive Viewport Matrix
- [ ] `TC-RESP-01`: Mobile (390px / iPhone): Hamburger menu, single-column product grid, sticky CTA bar.
- [ ] `TC-RESP-02`: Tablet (768px / iPad): 2-column product grid, accessible filter bar.
- [ ] `TC-RESP-03`: Desktop (1440px): 3-column product grid, expanded navigation, full hero layout.
- [ ] `TC-RESP-04`: Zero horizontal overflow or clipped buttons across all tested viewports.

### 17. Accessibility & Keyboard Flow
- [ ] `TC-A11Y-01`: Entire storefront navigable using only `Tab`, `Shift+Tab`, `Enter`, and `Space`.
- [ ] `TC-A11Y-02`: All interactive elements display visible gold focus outlines.
- [ ] `TC-A11Y-03`: Modal popups trap focus and close on `Escape` key.

### 18. Security & Abuse Resistance
- [ ] `TC-SEC-01`: Entering `<script>alert(1)</script>` in text fields is escaped as plain text.
- [ ] `TC-SEC-02`: Unsafe URLs (`javascript:`, `data:`, `file:`) in Admin are rejected with validation errors.
- [ ] `TC-SEC-03`: Tampering with `localStorage` quantities (e.g. `quantity: -10`) is sanitized to 1.
- [ ] `TC-SEC-04`: Direct API mutations (`POST`, `PUT`, `DELETE`) are blocked with HTTP 405.
- [ ] `TC-SEC-05`: Security events log rejections without exposing customer PII or system paths.

### 19. Error Recovery & Resilience
- [ ] `TC-ERR-01`: Simulated API failure displays elegant luxury error state with retry button.
- [ ] `TC-ERR-02`: Missing or 404 image falls back to elegant branded jewelry placeholder.
- [ ] `TC-ERR-03`: Navigating to non-existent route displays custom 404 page with return-to-shop link.

### 20. Data Consistency & Cache Freshness
- [ ] `TC-SYNC-01`: Changing product price in Admin updates storefront upon immediate refresh.
- [ ] `TC-SYNC-02`: Adding new promotion in Admin updates homepage announcement bar immediately.
- [ ] `TC-SYNC-03`: Zero stale cache locks across API, Admin, and Storefront.

---

## Sign-Off Block

- **Lead QA Engineer**: __________________________________ &nbsp;&nbsp;&nbsp;&nbsp; **Date**: _______________
- **Technical Lead**: ______________________________________ &nbsp;&nbsp;&nbsp;&nbsp; **Date**: _______________
- **Overall Verdict**: `[ ] APPROVED FOR PRODUCTION CANDIDATE` &nbsp;&nbsp; `[ ] REJECTED`
