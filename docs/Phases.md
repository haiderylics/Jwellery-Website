# Jewellery Website — Implementation Phases

This document controls execution order.

**Absolute workflow rule:** Antigravity MUST read all six project docs before touching code.

Required order:

1. Read docs.
2. Analyze requirements.
3. Produce phase implementation plan.
4. Present plan for human verification.
5. Do not implement until plan is approved.
6. Implement only the approved phase.
7. Run tests/checks.
8. Summarize changed files, tests and risks.
9. Update project memory if an architectural decision changed.

---

# Phase 0 — Requirements & Feasibility Lock

## Objective

Convert PRD into an implementation-ready checklist.

## Tasks

- Resolve ambiguity.
- Verify assumptions.
- Identify dependencies.
- Identify fields needed by admin.
- Identify API contracts.
- Identify frontend routes.
- Create acceptance criteria.
- Create threat model.
- Confirm exact project scope.

## Deliverables

- implementation plan
- ERD/domain model proposal
- route map
- API map
- security checklist
- test strategy

## Gate

Human approval required.

No production code.

---

# Phase 1 — Repository & Tooling Foundation

## Objective

Create maintainable project skeleton.

## Tasks

- Git initialization
- README
- `.gitignore`
- environment variables
- backend project
- frontend project
- formatting/linting
- pre-commit configuration where justified
- dependency lock/management
- CI baseline
- local development instructions
- test commands

## Security

- no secrets
- secret scanning
- dependency audit baseline
- secure environment handling

## Gate

- project installs from clean checkout
- tests run
- linters run
- no secrets committed

---

# Phase 2 — Database & Domain Models

## Objective

Implement the core data model.

## Tasks

- Category
- Product
- ProductAttribute
- ProductVariant
- ProductImage
- ProductVideo
- Review
- GalleryItem
- Promotion
- Popup
- DeliverySettings
- SiteSettings
- SocialLink if needed

## Requirements

- useful indexes
- constraints
- slug generation
- safe deletion behaviour
- ordering
- timestamps

## Tests

- constraints
- relationships
- invalid prices
- invalid stock
- duplicate slugs
- variant behaviour

## Gate

Model tests pass and migrations are clean.

---

# Phase 3 — Django Admin / Operations Console

## Objective

Make the owner fully independent for normal content operations.

## Tasks

- grouped admin navigation
- list display
- filtering
- search
- pagination
- inline product images
- variant editing
- media validation
- preview links
- bulk actions where useful
- sensible fieldsets
- help text

## UX rules

The admin is for a non-technical owner.

Avoid exposing unnecessary Django internals.

Use business terminology.

## Security

- staff permissions
- no public admin access
- CSRF
- secure cookies
- authentication protections
- audit logging as practical

## Gate

Owner can create/update/delete/publish core content without source-code changes.

---

# Phase 4 — API Layer

## Objective

Provide stable, minimal public API.

## Tasks

- `/api/v1/`
- catalog endpoints
- product detail
- categories
- attributes
- reviews
- gallery
- promotions
- site settings
- homepage data

## Rules

- explicit serializers
- pagination
- filtering
- bounded page size
- cache headers where safe
- no secret leakage
- deterministic ordering

## Security

- CORS allowlist
- rate limits
- validation
- no mutation endpoints unless required
- public responses contain only public fields

## Gate

OpenAPI/API documentation exists if API complexity warrants it.

---

# Phase 5 — Frontend Foundation

## Objective

Build the premium visual system before page-by-page implementation.

## Tasks

- typography
- color tokens
- spacing scale
- container system
- buttons
- product cards
- inputs
- modal
- badges
- navigation
- footer
- responsive breakpoints
- loading states
- empty states
- error states

## Gate

Design system approved visually before cloning it across pages.

---

# Phase 6 — Home Page

Sections:

1. Announcement bar
2. Header/navigation
3. Hero
4. Category discovery
5. Featured products
6. New arrivals
7. Brand story
8. Reviews
9. Exhibition/seminar gallery
10. WhatsApp CTA
11. Footer

## Acceptance

- mobile first
- premium
- no template feel
- fast load
- content API-driven

---

# Phase 7 — Catalog / Search / Filters

## Tasks

- Shop page
- category pages
- search
- attribute filters
- sort
- pagination/infinite scroll only if justified
- empty states
- stock states

## Acceptance

- filters compose correctly
- URL can represent meaningful search/filter state
- no N+1 API calls
- product cards have consistent visual hierarchy

---

# Phase 8 — Product Detail

## Tasks

- gallery
- variants
- price
- custom order
- stock
- video
- related products
- add to cart
- WhatsApp CTA
- social/share metadata where appropriate

## Security

- server-authoritative pricing
- validated variant identifiers
- no client-trusted stock

---

# Phase 9 — Cart & WhatsApp Checkout

## Tasks

- cart state
- quantity
- remove/update
- customer form
- delivery options
- server recalculation
- WhatsApp message
- product links
- multi-product summary

## Acceptance

Invalid/modified client prices cannot influence final message calculations.

---

# Phase 10 — Promotions, Events & Popup

## Tasks

- top announcement bar
- sale/event section
- popup
- date scheduling
- active state
- priority
- mobile behaviour
- frequency controls

## Acceptance

Admin update becomes visible without source-code changes.

---

# Phase 11 — Content, SEO & Trust

## Tasks

- About
- Reviews
- Gallery
- Contact
- metadata
- OG tags
- sitemap
- robots
- schema
- canonical URLs

## Trust principle

Never manufacture:

- reviews
- ratings
- certifications
- customer counts
- years of experience
- exhibition claims

Only use verified business information.

---

# Phase 12 — Security Hardening

This phase is mandatory.

## Backend

- DEBUG=False
- secret management
- ALLOWED_HOSTS
- CSRF
- secure cookies
- HTTPS
- HSTS
- CSP
- CORS
- X-Content-Type-Options
- frame protection
- permission checks
- throttling
- secure admin
- error handling
- upload restrictions
- validation
- dependency scanning

## Frontend

- no secrets
- safe rendering
- output escaping
- URL sanitization
- no arbitrary HTML
- safe third-party assets
- CSP-compatible code

## Testing

Attempt:

- XSS
- CSRF
- SQLi boundaries
- broken authorization
- IDOR
- path traversal
- malicious uploads
- oversized inputs
- method abuse
- rate-limit bypass
- stale cart price manipulation

---

# Phase 13 — Performance & Accessibility

## Performance

- image optimization
- lazy loading
- preloading only where justified
- bundle optimization
- caching
- API optimization
- query optimization

## Accessibility

- keyboard
- focus
- headings
- labels
- alt text
- contrast
- reduced motion
- screen-reader smoke checks

---

# Phase 14 — End-to-End Verification

## Functional scenarios

1. Browse home.
2. Browse category.
3. Search product.
4. Filter by category + attribute.
5. Open product.
6. Select variant.
7. Add to cart.
8. Change quantity.
9. Checkout.
10. Delivery threshold calculation.
11. WhatsApp message generation.
12. Admin changes product.
13. Frontend reflects change.
14. Admin activates promotion.
15. Popup activates.
16. Admin publishes review.
17. Admin changes social links.

---

# Phase 15 — Production Readiness

## Required

- current supported framework patch
- production env
- PostgreSQL
- media strategy
- static strategy
- HTTPS
- DNS
- backups
- health check
- logging
- deployment server
- CI checks
- deploy check
- smoke test

Run:

```bash
python manage.py check --deploy
```

Do not use:

```bash
python manage.py runserver
```

for production.

---

# Phase 16 — Launch & Handover

## Deliverables

- source repository
- deployment information
- `.env.example`
- admin usage guide
- content entry guide
- backup notes
- recovery notes
- known limitations
- future backlog

## Owner training

Teach only:

- login
- products
- images
- prices
- stock
- variants
- featured/new
- reviews
- gallery
- popup
- promotions
- delivery
- WhatsApp/settings

---

# Phase Management Rule

If a phase is incomplete, do not silently start the next phase.

Any scope expansion creates:

- a new requirement
- impact assessment
- phase assignment
- estimate adjustment
- explicit approval

