# Jewellery Website — Persistent Project Memory

This file records durable facts, decisions, constraints, and unresolved items.

Agents MUST read this file before implementation.

---

# 1. Business Facts

- Business is a jewellery seller.
- Current sales come through physical exhibitions/seminars and direct customer relationships.
- Online social pages exist.
- Professional Instagram/Facebook/TikTok profiles have been configured.
- Branding/logo/bio/contact links have already been improved.
- Customer wants online leads/sales.
- Owner is non-technical.
- Owner will use Django Admin.
- Owner may later give admin access to another person.
- Business operates in Pakistan.
- International ordering/delivery is also desired.
- Current couriers include Leopards and TCS.
- Existing customer reviews are available from WhatsApp.
- Future seminar/exhibition photography will be collected.
- Current gallery may use a controlled placeholder until real imagery exists.

---

# 2. Business Information Already Available Outside This File

The developer already has:

- business name
- contact numbers
- tagline
- email
- social URLs
- brand/logo assets where available

Do not ask the owner for these again unless the source data is missing or changed.

---

# 3. Locked Product Requirements

## Product categories

Owner sells all major jewellery types.

Primary examples:

- Rings
- Earrings
- Necklaces
- Bangles
- Additional categories as required

## Secondary taxonomy

A second axis is required for product type/material/attribute.

Examples:

- 1 Carat
- Stainless Steel
- other business-specific attributes

---

# 4. Media Rules

- Product images: minimum 1, maximum 10
- Product may have optional video
- Existing videos are simple camera videos
- If no real image is available, frontend may show a Coming Soon placeholder
- Do not require fake product images
- Gallery placeholder can be used until real exhibition/seminar photos exist

---

# 5. Pricing

- Product price must be visible on frontend.
- Owner must control price through admin.
- Client-side price must never be trusted.
- No payment gateway in MVP.

---

# 6. Custom Orders

- Custom jewellery is offered.
- Custom products must be clearly marked on frontend.
- Final customization details can be handled through WhatsApp.
- Do not promise automatic custom-order pricing if human discussion is required.

---

# 7. Delivery

- Pakistan-wide delivery.
- International delivery available by configuration.
- Admin can enable:
  - Pakistan only
  - International only where appropriate
  - both
- Default free-delivery threshold: PKR 5,000.
- Admin can change threshold.
- Admin can change Pakistan delivery charge.
- International delivery may initially be quote-on-WhatsApp rather than automatic.
- Couriers include Leopards and TCS.
- Do not hard-code courier pricing.

---

# 8. Ordering

MVP flow:

`Browse → Product → Cart → Proceed → Customer Details → WhatsApp`

WhatsApp message should contain:

- product
- variant
- quantity
- price
- product link
- customer details
- delivery information
- cart summary

Multiple products in one cart must be supported.

---

# 9. Promotions

Top-of-site promotion/event section required.

Examples:

- Eid
- Independence Day
- sale
- campaign
- exhibition

Promotion must be admin-controlled.

Popup must also be admin-controlled and schedulable.

---

# 10. Merchandising

Admin-controlled:

- Featured Products
- New Arrivals
- Product order/priority
- Promotions

---

# 11. Content

Reviews:

- existing WhatsApp reviews can be added
- only publish approved/public-safe content

Gallery:

- current placeholder acceptable
- future real photos replace it via admin

About Us:

- initial draft can be supplied
- final owner approval required before production

---

# 12. Language

English only for MVP.

---

# 13. Visual Direction

Locked:

- Black + Gold
- Premium
- Modern
- Editorial
- Minimal
- Real product photography
- No obvious AI-generated template appearance

The exact design tokens live in `design.md`.

---

# 14. Architecture Decision

Locked:

- Static frontend
- Django backend
- PostgreSQL production database
- Django Admin
- JSON API
- WhatsApp-assisted checkout
- No online payment gateway in MVP
- No customer accounts in MVP

---

# 15. Admin Philosophy

Admin should control business content and merchandising.

Admin should NOT be a full website/page builder.

Admin can manage:

- products
- prices
- stock
- images
- video
- categories
- attributes
- variants
- custom-order status
- featured/new-arrivals
- reviews
- gallery
- promotions
- popup
- delivery
- WhatsApp/social settings
- editable business content
- SEO basics

Admin should NOT manage:

- CSS
- layout
- component architecture
- breakpoints
- raw JavaScript
- page code

---

# 16. Security Decisions

Security is a first-class requirement.

Absolute "unhackable" security is impossible and must never be claimed.

Security target:

- current Django
- defense-in-depth
- least privilege
- strict validation
- secure browser headers
- HTTPS
- secure cookies
- CSRF
- CORS allowlist
- rate limiting
- upload isolation
- dependency scanning
- secret management
- logging
- backups
- safe errors
- server-authoritative business calculations

Relevant standards:

- OWASP Top 10:2025
- Django 6.0 security guidance
- OWASP File Upload Cheat Sheet
- DRF permissions/throttling guidance

---

# 17. Current Technical Baseline

As of project planning date:

- Django 6.0 exists and supports Python 3.12–3.14.
- Django 6.0.6 was released June 3, 2026 and included security fixes.
- Therefore do not pin an obsolete Django version without a documented reason.
- Always verify the latest supported patch release before deployment.

Reference:
https://docs.djangoproject.com/en/6.0/releases/6.0/

---

# 18. Antigravity Workflow Decision

The coding agent must:

1. Read all project docs.
2. Inspect repository.
3. Analyze current phase.
4. Propose implementation plan.
5. Wait for human verification.
6. Implement approved scope.
7. Run tests/checks.
8. Report changed files and validation.
9. Update memory for durable decisions.

Never skip plan approval.

---

# 19. MCP Decisions

Candidate MCPs:

- Google Developer Knowledge MCP
- GitHub MCP
- Playwright/browser MCP
- PostgreSQL/database MCP
- Trusted documentation/context MCP
- Sentry/observability MCP if observability is configured

MCPs are optional.

Only trusted, necessary MCPs should be enabled.

Default preference:

- read-only
- development/staging
- least privilege
- no production secrets
- no arbitrary production mutations

---

# 20. Deployment Decision

Deployment will be decided after the site is production-ready.

Priority:

1. Security
2. Reliability
3. Cost
4. Simplicity

Do not choose hosting before the actual resource requirements are known.

---

# 21. Scope Freeze

MVP excludes:

- payments
- customer accounts
- order history
- wishlists
- advanced coupons
- loyalty
- multi-vendor
- ERP
- courier APIs
- custom page builder
- multi-language

Any new feature must go through change assessment.

---

# 22. Open Decisions

These should be resolved before affected implementation:

- exact frontend framework choice: React/TypeScript vs lightweight Vite/TypeScript
- exact product variant representation
- exact international delivery behaviour
- exact WhatsApp message fields
- exact admin content structure
- production hosting
- media/object storage
- monitoring provider
- final owner-approved About Us copy
- legal pages required for production

---

# 23. Working Assumptions

Until changed:

- Free delivery threshold starts at PKR 5,000.
- International shipping is quote-on-WhatsApp initially.
- Product prices are public.
- Cart supports multiple products.
- Product image max is 10.
- Product video is optional.
- Gallery placeholder is temporary.
- English only.
- Black/gold visual language.
- Django Admin is sufficient for operational management.

---

# 24. Decision Log

Format:

```text
DATE:
DECISION:
REASON:
IMPACT:
APPROVED BY:
```

```text
DATE: 2026-08-14
DECISION: Adopt user-local Astral uv with isolated Python 3.12.13 and `.venv`
REASON: System Python 3.10 is used by other projects and must remain untouched; Django 6.x requires Python 3.12+.
IMPACT: All developer and CI commands use `uv run ...`. Global Python environment is never modified.
APPROVED BY: Project Owner / Phase 1 Execution Authorization

DATE: 2026-08-14
DECISION: Minimalist Phase 1 dependency baseline locked via uv.lock (Django 6.0.8, Ruff, Pytest, Bandit, Pip-Audit)
REASON: Avoid premature dependencies (Pillow, django-environ, etc.) until required by active code in future phases.
IMPACT: Fast, secure, minimal attack surface; deterministic reproducibility via `uv sync --frozen`.
APPROVED BY: Project Owner / Phase 1 Execution Authorization

DATE: 2026-08-14
DECISION: Node.js 20 LTS pinned for frontend toolchain (.node-version + engines in package.json)
REASON: Predictable, deterministic build toolchain across local development and GitHub Actions CI.
IMPACT: Frontend baseline uses Vite + TypeScript with strict type checking and standard design tokens.
APPROVED BY: Project Owner / Phase 1 Execution Authorization

DATE: 2026-08-14
DECISION: Relational 2-Axis Taxonomy (Category + ProductAttributeType / ProductAttributeValue)
REASON: Provides strict relational normalization, clean admin/API filtering, and avoids fragile JSONField / text blob parsing.
IMPACT: Products belong to one Category and can have multiple normalized attribute values (e.g. Material, Purity).
APPROVED BY: Project Owner / Phase 2 Execution Authorization

DATE: 2026-08-14
DECISION: Database-Level Integrity Constraints (DecimalField pricing, unique variant combinations, partial unique primary image, singleton settings)
REASON: Defense-in-depth data integrity preventing impossible state combinations regardless of caller.
IMPACT: Primary images enforced uniquely per product; site/delivery settings guarded as singletons; variant stock aggregated cleanly.
APPROVED BY: Project Owner / Phase 2 Execution Authorization

DATE: 2026-08-14
DECISION: Django Admin Operations Console with Non-Technical Owner UX & URL Scheme Validation
REASON: Empowers non-technical owner to operate catalog, content, promotions, and settings without code edits; prevents malicious URL pseudo-protocols (`javascript:`, `data:`).
IMPACT: Custom ModelAdmins across all domain apps with query optimization (`select_related`, `prefetch_related`), singleton protection, safe bulk actions, and safe URL validators.
APPROVED BY: Project Owner / Phase 3 Execution Authorization

DATE: 2026-08-14
DECISION: Psycopg 3 PostgreSQL Driver Baseline (`psycopg-binary==3.3.4`)
REASON: Required for Django 6.0 production deployments to PostgreSQL and verified via `manage.py check --deploy`.
IMPACT: Production settings cleanly load and pass strict deploy checks against PostgreSQL.
APPROVED BY: Project Owner / Phase 3 Execution Authorization

DATE: 2026-08-14
DECISION: Read-Only Public API Contract under `/api/v1/` with DRF 3.18 & django-cors-headers
REASON: Provides clean, standard, strictly read-only storefront data contracts without public mutation attack surface.
IMPACT: All storefront endpoints explicitly reject POST/PUT/PATCH/DELETE (405); querysets enforce `is_published=True` / active schedules at the DB layer; bounded pagination (max 50) and allowlisted sorting.
APPROVED BY: Project Owner / Phase 4 Execution Authorization

DATE: 2026-08-14
DECISION: Aggregated Storefront Homepage (`/api/v1/home/`) with Signal-Based Invalidation
REASON: Consolidates 8 landing sections into a single fast payload, eliminating waterfall requests while maintaining fresh data via automatic cache invalidation on admin saves.
IMPACT: Instantaneous page load performance with zero stale data risks.
APPROVED BY: Project Owner / Phase 4 Execution Authorization

DATE: 2026-08-14
DECISION: React 18 + TypeScript 5.7 + Vite 6 + Vanilla CSS Luxury Editorial Storefront Architecture
REASON: Meets requirements for rich reactive filtering, search, cart, variant selection, modals, and mobile-first responsive interactions while maintaining a lightweight 64 kB gzipped bundle footprint.
IMPACT: Complete storefront page suite (Home, Shop, Product Detail, Cart, About, Reviews, Gallery, Contact, 404), zero framework bloat, strict TypeScript types matching `/api/v1/` response contracts.
APPROVED BY: Project Owner / Phase 5 Execution Authorization

DATE: 2026-08-14
DECISION: Untrusted Client-Side Cart Storage & Authoritative Backend Price Resolution
REASON: Guarantees client-side tampering (modifying localStorage price/stock/discounts) cannot affect order accuracy.
IMPACT: LocalStorage strictly stores `{ productSlug, variantId, quantity }`; the Cart and WhatsApp order builder resolve live, authoritative pricing and stock from the API upon checkout.
APPROVED BY: Project Owner / Phase 5 Execution Authorization

DATE: 2026-08-14
DECISION: Secure Media Pipeline with EXIF Stripping, Decompression Bomb Defense & WebP Variants
REASON: Protects backend from malicious uploads, path traversals, and resource exhaustion while optimizing public delivery with responsive WebP variants.
IMPACT: Strict validation (10 MB image, 50 MB video, 4096px / 16M pixel bounds), randomized UUID storage paths (`SecureUploadPath`), auto-generated WebP variants (`thumb`, `medium`, `large`), and safe orphan cleanup on model deletion.
APPROVED BY: Project Owner / Phase 6 Execution Authorization

DATE: 2026-08-14
DECISION: Post-Commit Media Processing, Change Detection & Safe Replacement Architecture
REASON: Guarantees media generation and storage cleanup only execute after database transactions commit, prevents redundant processing on non-media saves, and ensures old media is not deleted prematurely during replacements or rollbacks.
IMPACT: `signals.py` uses `pre_save` comparison to track file changes and `transaction.on_commit` for variant creation and replacement cleanup.
APPROVED BY: Project Owner / Phase 7 Execution Authorization

DATE: 2026-08-14
DECISION: Bounded Orphan Media Audit & Consistency Command (`audit_media`)
REASON: Provides operational observability to detect unreferenced storage files, missing database references, and stale variants without risking accidental data loss.
IMPACT: `audit_media` defaults to dry-run, audits 7 model types against physical files, and requires explicit `--clean-orphans` with `--older-than-hours` age thresholds.
APPROVED BY: Project Owner / Phase 7 Execution Authorization

DATE: 2026-08-14
DECISION: Multi-Layer Request Body & Upload Boundary Policy
REASON: Prevents upload Denial-of-Service at infrastructure, application framework, and validator layers.
IMPACT: Web-server reverse proxy must enforce `client_max_body_size 60M;`, Django controls memory buffer (`FILE_UPLOAD_MAX_MEMORY_SIZE = 5MB`), and application validators enforce strict 10MB image / 50MB video caps.
APPROVED BY: Project Owner / Phase 7 Execution Authorization

DATE: 2026-08-14
DECISION: Custom Branded Django Admin Visual Redesign & Operational Dashboard
REASON: Unifies Django Admin with the brand's luxury obsidian/gold aesthetic while preserving 100% of Django's native authentication, permissions, CSRF, and ModelAdmin security.
IMPACT: Added `admin/login.html`, `admin/base_site.html`, `admin/index.html` with operational KPI metrics (product counts, low/out-of-stock count, active campaigns, client reviews), and `custom_admin.css`.
APPROVED BY: Project Owner / Pre-Production QA & Admin UX Pass

DATE: 2026-08-14
DECISION: Deterministic Pre-Production QA Seeder & Human-Executable E2E QA Documentation Suite
REASON: Guarantees deterministic, reproducible manual QA testing across all storefront and admin business flows without creating fake PII or touching production environments.
IMPACT: Built `seed_demo_data` command and comprehensive `docs/qa/` documentation (`E2E_MANUAL_TEST_GUIDE.md`, `TEST_CASE_MATRIX.md`, `BUG_REPORT_TEMPLATE.md`, `TEST_DATA_GUIDE.md`, `QA_CHECKLIST.md`).
APPROVED BY: Project Owner / Pre-Production QA & Admin UX Pass
```

---

# 25. Known Risks

1. One-week timeline is tight for a highly polished production candidate.
2. "Every small thing editable from admin" can turn into a page-builder project; keep it limited to business/content data.
3. Media upload is a security boundary.
4. WhatsApp handoff is not a payment/order management system.
5. International delivery pricing is not yet deterministic.
6. Real exhibition/seminar imagery is not yet available.
7. Owner may request scope expansion after seeing the first version.

---

# 26. Project Principle

Build less, but build it properly.

A smaller secure, fast and maintainable product that looks premium is better than a feature-heavy codebase that is rushed, fragile or insecure.
# Production media and static deployment

- Railway serves Django static files with WhiteNoise after the build-time `collectstatic` step.
- Production Django media uses Cloudinary via the official Python SDK and requires the three
  `CLOUDINARY_*` Railway variables. Development continues to use local filesystem media.
- Product, gallery, review, about, promotion, popup, and product-video fields retain their
  existing Django field schema; no production data migration is needed.
