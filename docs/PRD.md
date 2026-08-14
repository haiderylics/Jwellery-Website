# Jewellery E-Commerce Website — Product Requirements Document (PRD)

**Status:** Baseline requirements / implementation source of truth  
**Project type:** Premium jewellery catalog + cart + WhatsApp-assisted ordering  
**Primary stack:** Django 6.x backend, PostgreSQL production database, modern static frontend consuming JSON API  
**Target delivery:** 1 week for MVP production candidate, subject to scope freeze  
**Languages:** English  
**Visual direction:** Premium, editorial, understated black + gold; must not look AI-generated or template-heavy

---

## 1. Product Goal

Build a premium jewellery website that converts social-media visitors into qualified WhatsApp orders.

The website is **not** a full traditional e-commerce checkout at this stage. It is a product catalog with:

1. Rich product discovery.
2. Search and filtering.
3. Product variants.
4. Cart.
5. Delivery-rule calculation.
6. Customer details collection.
7. WhatsApp-assisted order handoff.
8. Admin-controlled content and merchandising.
9. Promotions/events and popup messaging.
10. Strong security, performance, accessibility and maintainability.

The site should create trust for a jewellery business that already sells through exhibitions/seminars but currently receives few/no online orders.

---

## 2. Business Context

The business sells multiple jewellery categories and variants, attends exhibitions and seminars, has existing WhatsApp customer reviews, and plans future seminar/exhibition photography.

The owner is non-technical and will depend on the Django admin for content operations.

The owner must be able to update commercial/content data without changing source code.

---

## 3. Explicit Scope

### 3.1 Customer-facing features

- Home page
- Product catalog/shop
- Category browsing
- Secondary product type/material/attribute filtering
- Search
- Product detail page
- Product image gallery
- Optional product video
- Product variants
- Quantity selection
- Stock state
- Custom-order indication
- Price display
- Cart
- Order summary
- Delivery-rule display
- Customer name/contact/city/address fields where required for WhatsApp handoff
- WhatsApp order redirect
- Product URL in WhatsApp message
- Multi-product cart message
- About section
- Customer reviews/testimonials
- Exhibition/seminar gallery
- Featured Products
- New Arrivals
- Promotional/event banner at the top
- Promotional/event section
- Optional promotional popup
- Contact section
- Social links
- Responsive mobile-first design
- SEO basics
- Accessibility basics
- Error states / empty states / loading states

### 3.2 Admin features

Use Django Admin unless a custom admin interface becomes necessary after implementation.

Admin must manage:

- Products
- Product categories
- Product types/materials/attributes
- Product variants
- Product images
- Product videos
- Product price
- Compare-at/original price when needed
- Stock quantity/status
- Custom-order flag
- Featured status
- New-arrival status
- Product ordering/sort priority
- Reviews
- Gallery items
- About Us content
- Promotions/events
- Top announcement bar
- Popup
- Delivery settings
- International-delivery visibility
- Free-delivery threshold
- Delivery charges
- WhatsApp number
- Social links
- General site settings
- Basic SEO/meta content

### 3.3 Intentionally out of scope for this release

Do NOT add unless explicitly approved later:

- Customer accounts
- Customer login/register
- Online payment gateway
- Stored orders/order history
- Loyalty program
- Coupons engine
- Wishlists
- Multi-vendor marketplace
- Blog CMS
- Advanced analytics dashboard
- Inventory ERP
- Automated courier API integrations
- Multi-language UI
- Custom page builder
- Theme editor
- Drag-and-drop website builder

---

## 4. Product Taxonomy

Use a two-axis taxonomy rather than forcing every descriptor into a single category.

### Primary category

Examples:

- Rings
- Earrings
- Necklaces
- Bangles
- Bracelets
- Sets
- Bridal
- Other categories as needed

### Secondary type/material/attribute

Examples:

- 1 Carat
- Stainless Steel
- Gold Plated
- Silver
- Custom
- Other business-specific attributes

Model these independently so one product can belong to one primary category and multiple secondary attributes.

---

## 5. Product Requirements

Each product supports:

- Name
- Slug
- Short description
- Full description
- Primary category
- Secondary attributes
- Base price
- Optional compare-at price
- Stock quantity/status
- Published/unpublished state
- Custom-order available
- Featured flag
- New-arrival flag
- Sort priority
- SEO title
- SEO description
- Created/updated timestamps

### Media

- Minimum 1 product image
- Maximum 10 product images
- One primary image
- Explicit image ordering
- Optional product video
- If no image is available, frontend uses a controlled "Coming Soon" placeholder
- Do not require dummy media to be stored in the database

### Variants

Products may have:

- Color
- Size
- Design
- Other future business-specific variants

Do not build a Shopify-scale variant engine. MVP variants must be simple, explicit and maintainable.

Each variant may optionally override:

- Price
- Stock
- Display label
- Availability

---

## 6. Stock Behaviour

Product states:

- Available
- Low stock
- Out of stock
- Coming soon

If a product is out of stock:

- Do not present it as purchasable.
- Allow configurable "Contact on WhatsApp" behaviour if business wants inquiries.
- Prevent invalid quantity selection.

Stock displayed on frontend should be a business-safe state, not necessarily exact warehouse quantity unless explicitly desired.

---

## 7. Custom Orders

Products can have `is_custom_order = true`.

Display a clear label such as:

> Customizable

The product page should explain that final customization details and pricing may be confirmed through WhatsApp.

Do not pretend that custom products have a deterministic online checkout price if they do not.

---

## 8. Cart

Cart is client-side state with server API support only where needed.

Requirements:

- Add product
- Add variant
- Change quantity
- Remove item
- Clear cart
- Persist cart locally for convenience
- Validate current product/variant state before WhatsApp handoff
- Prevent invalid/stale prices from being trusted
- Recalculate totals from authoritative backend data

The client must never be the source of truth for price or stock.

---

## 9. WhatsApp Ordering

No payment gateway in MVP.

Customer journey:

`Product → Add to Cart → Cart → Proceed → Customer details → Delivery summary → Open WhatsApp`

Generated message should contain:

- Greeting
- Product name
- Selected variant
- Quantity
- Current backend-validated price
- Cart subtotal
- Delivery rule/estimated charge where applicable
- Total
- Customer name
- Phone/WhatsApp number if collected
- City
- Address if collected
- Product URL(s)
- Optional custom-order note

The message must be URL-encoded safely.

Use a configured business WhatsApp number from admin/site settings.

Never hard-code the number in frontend source.

---

## 10. Delivery

Business requirements:

- Pakistan-wide delivery
- International delivery may be enabled/disabled by admin
- Free delivery threshold default: PKR 5,000
- Threshold editable from admin
- Pakistan delivery charge editable from admin
- International delivery may use "contact on WhatsApp" until a deterministic rate table exists
- Courier currently includes Leopards and TCS
- Do not hard-code courier names into pricing logic

Suggested configuration:

- Pakistan delivery enabled
- International delivery enabled
- Free shipping threshold
- Pakistan delivery charge
- International delivery mode:
  - WhatsApp quote
  - Fixed
  - Disabled

---

## 11. Promotions & Events

Admin-controlled promotion entity.

Fields should support:

- Title
- Subtitle/message
- Image/banner
- CTA label
- CTA URL
- Active state
- Start date/time
- End date/time
- Display priority

Examples:

- Eid Sale
- Independence Day Sale
- Limited Time Offer
- Exhibition Announcement

### Top announcement bar

Must appear above main navigation when an active promotion is configured.

### Popup

Popup is configurable and should support:

- Title
- Message
- Image
- CTA
- Schedule
- Active/inactive
- Frequency/once-per-session behaviour

Do not make popup aggressive or unusable on mobile.

---

## 12. Featured Products & New Arrivals

Both sections must be admin-controlled.

Recommended selection model:

- `is_featured`
- `is_new_arrival`
- `sort_priority`

Avoid manually entering product IDs into frontend code.

---

## 13. Reviews

Admin can create/publish reviews from WhatsApp-provided evidence.

Fields:

- Customer display name
- Review text
- Optional image
- Verified/internal note
- Published state
- Sort priority

Do not expose private customer phone numbers or private WhatsApp screenshots unless the owner has deliberately approved their public use.

---

## 14. Gallery

Admin-managed gallery for:

- Exhibitions
- Seminars
- Brand moments
- Future event photography

Current requirement:

- Seed one controlled placeholder/dummy item.
- Replace later through admin.

Do not fake testimonials or event participation.

---

## 15. About Us

Initial placeholder copy may be used during development, but production copy should be owner-approved.

Draft positioning:

> We create jewellery designed to bring elegance into everyday moments and special occasions alike. From timeless classics to statement pieces, our collection is curated with a focus on refined design, quality and wearability. Our journey has grown through direct relationships with customers at exhibitions, seminars and personal recommendations. We are now bringing that same personal shopping experience online, making it easier to discover our latest pieces and connect with us directly. Whether you are looking for something elegant for yourself or a meaningful piece for someone special, we are here to help you find the right choice.

This text must remain editable in admin.

---

## 16. SEO

MVP SEO:

- Unique page title
- Meta description
- Canonical URL
- Clean slugs
- Open Graph metadata
- Twitter/X card metadata
- Product structured data where data is authoritative
- Organization/brand structured data where appropriate
- XML sitemap
- robots.txt
- Proper heading hierarchy
- Descriptive image alt text

Never generate false review markup, fake ratings or fake availability.

---

## 17. Accessibility

Target WCAG 2.2 AA principles where practical:

- Keyboard navigation
- Visible focus
- Semantic HTML
- Accessible forms
- Alt text
- Sufficient contrast
- Reduced-motion support
- No critical information conveyed by color alone
- Mobile tap targets
- Meaningful labels

---

## 18. Performance

Targets:

- Fast initial render on mobile
- Responsive image sizing
- Lazy-load below-fold imagery
- Prefer AVIF/WebP where supported
- Avoid huge hero images
- Minimize JS
- Avoid unnecessary client-side state
- Cache public GET API responses where safe
- Never cache personalized/admin responses publicly

Performance work must not compromise security.

---

## 19. Security Requirements

Security objective: defense-in-depth aligned with OWASP Top 10:2025 and Django security guidance.

Required controls include:

- Current supported Django version
- DEBUG disabled in production
- Strong random SECRET_KEY from environment/secret manager
- Strict ALLOWED_HOSTS
- HTTPS only in production
- Secure cookies
- HttpOnly cookies where applicable
- SameSite protection
- CSRF protection for state-changing requests
- HSTS after HTTPS is verified
- Clickjacking protection
- Content-Type sniffing protection
- Content Security Policy where compatible with the frontend
- Strict input validation
- ORM parameterization; no raw SQL from user input
- Output escaping
- Safe HTML policy; no raw user HTML rendering
- Rate limiting
- Authentication on admin
- Least privilege
- Strong admin passwords
- Optional MFA if operationally feasible
- Brute-force protection / login rate limiting
- Security logging
- Generic public error messages
- Detailed errors only in protected logs
- Dependency scanning
- Regular dependency updates
- Secure headers
- CORS limited to exact frontend origin(s)
- No wildcard credentialed CORS
- Server-side authorization for every mutation
- No trust in client-submitted price/stock
- Upload validation
- Uploaded-file size limits
- Image/video type allowlist
- Filename normalization
- Randomized server-side file names
- Storage isolation
- Do not execute uploads as code
- EXIF/metadata considerations for public media
- Backup strategy
- Secret scanning
- No secrets committed to Git
- Production secrets separated by environment

Django's production guidance explicitly requires proper SECRET_KEY handling, DEBUG=False, ALLOWED_HOSTS, static/media configuration, HTTPS and deployment checks. Django 6.0.6 also contains security fixes released in June 2026, so the project must remain on a current supported patch release rather than pinning an old version. See references in Architecture.md. 

---

## 20. Security Reality

No web application can honestly be guaranteed "unhackable."

The project requirement is:

> Make compromise difficult, minimize attack surface, follow secure defaults, detect failures, limit blast radius, and continuously verify security.

Never claim absolute security.

---

## 21. Definition of Done

A phase is complete only when:

- Requirement implemented
- Tests pass
- Security checks pass
- No secrets in repository
- No unreviewed TODO blocking production
- Responsive behaviour verified
- API errors handled
- Admin workflow tested
- Accessibility smoke test completed
- Performance regressions checked
- Documentation updated
- Code review/agent self-review completed

