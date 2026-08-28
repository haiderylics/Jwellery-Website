# Jewellery Website — Architecture

**Architecture principle:** Keep the system simple, modular, secure and replaceable.

---

## 1. System Architecture

```text
Browser
  │
  ├── Static Frontend (HTML/CSS/JS)
  │        │
  │        └── HTTPS JSON API
  │                  │
  │                  ▼
  │             Django 6.x
  │             ├── API
  │             ├── Domain/services
  │             ├── Django Admin
  │             └── Security middleware
  │                  │
  │                  ├── PostgreSQL
  │                  └── Media/Object Storage
  │
  └── WhatsApp handoff
```

The frontend is static/deployable independently. Django is the authoritative application/data layer.

Production media is stored through the official Cloudinary Python SDK, configured as Django's
default storage with server-only Railway credentials. WhiteNoise serves only collected Django
static files. Cloudinary's CDN provides the fixed responsive image delivery variants; the
application does not persist duplicate thumbnail files in production.

### Canonical Cloudinary Media Identity

- Django keeps its backward-compatible extension-bearing keys, such as
  `products/images/2026/08/<uuid>.png` and `products/videos/2026/08/<uuid>.mp4`; no field or data
  migration is required.
- The identity mapper rewrites those keys to Cloudinary-safe public IDs:
  `catalog/products/photos/2026/08/<uuid>` for images and
  `catalog/products/clips/2026/08/<uuid>` for videos. The format remains separate. Exact
  `images`/`videos` path elements, version-like `v<digits>` folders, and transformation-like
  short underscore prefixes are not allowed in generated public-ID paths.
- Upload, original URL, responsive URL, lookup, size, delete, replacement cleanup, and audit
  tooling all use the same canonical mapping. Backslashes never enter a Cloudinary public ID.
- Delivery URLs come from the official SDK with secure `upload` delivery. UUID asset names omit
  invented versions; 300/800/1600 variants use bounded `c_limit`, `q_auto`, and `f_auto`
  transformations and are generated on demand rather than stored eagerly.
- The frontend consumes backend-provided URLs without reconstructing Cloudinary paths.
- Replacement and deletion remain post-commit operations and always target the one safe canonical
  public ID; runtime deletion never probes or destroys speculative legacy IDs.
- The dry-run-by-default `normalize_cloudinary_media` command checks only database-referenced
  assets. It reports `CANONICAL`, `LEGACY_EXTENSIONFUL`, `LEGACY_RESERVED_NAMESPACE`, `MISSING`,
  or `CONFLICT`. A conflict is never overwritten and exits for manual review; only explicit
  `--apply` can rename a single unambiguous legacy source.

---

## 2. Recommended Stack

### Backend

- Python 3.12+ / currently supported version
- Django 6.x current supported patch release
- Django REST Framework only if API complexity justifies it
- PostgreSQL in production
- SQLite acceptable only for local development if useful
- Pillow for safe image processing where required

Django 6.0 supports Python 3.12–3.14. Production should use a supported Django patch release. source: Django 6.0 release notes

### Frontend

Choose one of these only after implementation-plan verification:

Preferred:
- Vite
- TypeScript
- React only if interaction complexity requires it

Alternative for a truly lightweight site:
- Vite + TypeScript
- Semantic HTML
- CSS modules or organized CSS
- Small reusable vanilla/TypeScript components

Do not add React merely because it is popular. The objective is lower complexity and fast delivery.

### API

Use versioned API namespace:

`/api/v1/`

Public endpoints are read-heavy.

Admin mutations happen through Django Admin.

Do not expose Django Admin through a public API.

---

## 3. Repository Layout

Recommended:

```text
project/
├── backend/
│   ├── config/
│   ├── apps/
│   │   ├── catalog/
│   │   ├── content/
│   │   ├── promotions/
│   │   ├── settings/
│   │   └── common/
│   ├── manage.py
│   ├── requirements/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── features/
│   │   ├── services/
│   │   ├── state/
│   │   ├── styles/
│   │   └── types/
│   ├── public/
│   └── package.json
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── README.md
└── security/
```

Names may be adjusted during the implementation plan.

---

## 4. Django App Boundaries

### catalog

Owns:

- Category
- Product
- ProductAttribute
- ProductVariant
- ProductImage
- ProductVideo
- inventory/availability fields

### content

Owns:

- Reviews
- Gallery
- About content
- contact content

### promotions

Owns:

- Promotion
- Popup
- announcement bar

### settings

Owns:

- Site settings
- delivery rules
- WhatsApp destination
- social URLs
- public configuration

### common

Owns only truly shared abstractions/utilities.

Avoid a giant `utils.py`.

---

## 5. Domain Model

```text
Category
  └── Product
        ├── ProductImage (1..10)
        ├── ProductVideo (0..1 or configurable)
        └── ProductVariant (0..n)

Product <-> ProductAttribute

Review
GalleryItem

Promotion
Popup

DeliverySettings
SiteSettings
SocialLink
```

Use explicit foreign keys and many-to-many relationships where they communicate domain intent.

---

## 6. Data Integrity

Use database constraints for:

- unique slugs
- non-negative prices
- non-negative stock
- valid thresholds
- unique priority where appropriate
- valid relationships

Do not rely only on frontend validation.

Every API serializer/form must validate independently.

---

## 7. API Design

Public examples:

```text
GET /api/v1/products/
GET /api/v1/products/{slug}/
GET /api/v1/categories/
GET /api/v1/attributes/
GET /api/v1/reviews/
GET /api/v1/gallery/
GET /api/v1/home/
GET /api/v1/site-settings/
GET /api/v1/promotions/active/
```

Possible query parameters:

```text
?category=rings
?attribute=stainless-steel
?featured=true
?new_arrival=true
?q=gold
?page=2
```

API must implement:

- pagination
- max page size
- deterministic ordering
- validation
- safe filtering
- controlled fields
- no accidental model serialization
- no secret/admin fields

---

## 8. API Serialization

Never serialize model `__dict__` wholesale.

Use explicit serializers/schemas.

Public product response should expose only what the storefront needs:

```json
{
  "id": "...",
  "name": "...",
  "slug": "...",
  "description": "...",
  "price": "5500.00",
  "compare_at_price": null,
  "availability": "in_stock",
  "is_custom_order": true,
  "category": {...},
  "attributes": [...],
  "variants": [...],
  "images": [...],
  "video": null
}
```

Do not expose internal notes, audit fields, storage paths, private customer metadata or admin-only flags.

---

## 9. Cart Authority Model

Client-side cart is convenience only.

When preparing an order:

1. Client sends product/variant identifiers and quantities to backend.
2. Backend re-fetches authoritative records.
3. Backend validates published/available state.
4. Backend validates quantity.
5. Backend calculates prices.
6. Backend calculates delivery rule.
7. Backend returns a normalized order summary.
8. Frontend generates WhatsApp message from server-confirmed values.

No client-provided `total`, `price`, `discount`, `shipping` is trusted.

No actual order record is required in MVP.

---

## 10. WhatsApp Integration

Use a normal HTTPS WhatsApp URL generated from controlled settings.

Rules:

- Normalize phone number in backend configuration.
- URL-encode message.
- Limit message size.
- Do not include sensitive information unnecessarily.
- Do not pass arbitrary user-controlled URLs to the WhatsApp destination.
- Product links must be generated from trusted canonical base URL + known slug.

---

## 11. Authentication & Admin

Django Admin is the only authenticated operational interface in MVP.

Controls:

- non-obvious admin URL may be used as defense-in-depth, not as security
- strict HTTPS
- secure session cookies
- CSRF protection
- strong staff passwords
- least privilege groups
- no shared admin password
- superuser used only when necessary
- staff account for day-to-day management
- MFA recommended
- login throttling/protection
- audit-friendly logs

If future custom dashboard is added, use explicit permissions for every mutation.

DRF permission classes are evaluated before view logic; authorization must never depend solely on URL obfuscation or UI restrictions. source: DRF permissions

---

## 12. Security Architecture

### Browser boundary

- Strict CSP
- Referrer-Policy
- Permissions-Policy
- X-Content-Type-Options
- X-Frame-Options/frame-ancestors as appropriate
- HTTPS
- HSTS after validation
- secure cookies
- SameSite

### API boundary

- CORS allowlist
- method restrictions
- request-size limits
- pagination limits
- throttling
- validation
- safe serializers
- predictable status codes
- generic errors

### Database boundary

- PostgreSQL
- least-privileged DB user
- no public DB exposure
- TLS where provider/setup supports it
- backups
- migrations under version control
- no raw SQL with user strings
- encrypted/secret credentials

### Media boundary

Uploads are untrusted.

Controls:

- strict allowlist
- MIME + extension checks
- content verification where practical
- file-size limit
- image dimension limit
- video size limit
- random server-side filenames
- no executable extensions
- public media served as media, never executed
- isolate media storage from application code if possible
- remove/avoid unsafe metadata when practical
- backup media
- optionally malware scan uploads if infrastructure supports it

OWASP specifically recommends treating uploads as hostile input, controlling file types/sizes, isolating storage and preventing execution. source: OWASP File Upload Cheat Sheet

---

## 13. Security Headers

Baseline production policy should include:

```text
Content-Security-Policy
Referrer-Policy
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Permissions-Policy
Strict-Transport-Security
```

CSP must be designed around actual frontend needs rather than disabling security to make third-party scripts work.

Avoid inline scripts and unsafe-eval wherever possible.

---

## 14. CORS

Allow only the actual production frontend origin(s).

Example conceptually:

```text
https://www.example.com
https://example.com
```

Do not use:

```text
*
```

with credentials.

Development origins must be environment-specific.

---

## 15. CSRF

If cookie/session authentication is used for admin/API mutations:

- keep CSRF enabled
- correctly configure trusted origins
- do not replace CSRF with origin checks alone
- test state-changing requests

Django's security documentation explicitly covers CSRF, secure cookies, HTTPS and HSTS requirements. source: Django 6.0 security documentation

---

## 16. Secrets

Never commit:

- SECRET_KEY
- DB passwords
- cloud credentials
- MCP credentials
- API keys
- WhatsApp/API credentials if later introduced
- Sentry DSN if considered sensitive in the chosen setup
- deployment tokens

Use:

- `.env` locally
- platform secret manager in production
- `.env.example` with placeholders

Run secret scanning before push.

---

## 17. Logging & Monitoring

Log:

- authentication failures
- admin authentication events where feasible
- permission failures
- unexpected 4xx/5xx patterns
- suspicious input failures
- upload validation failures
- security exceptions

Never log:

- passwords
- session secrets
- access tokens
- full sensitive personal data
- private customer conversations

Use structured JSON logs in production when practical.

---

## 18. Error Handling

Public users see:

- friendly 404
- friendly 500
- no stack traces
- no SQL errors
- no environment details

Developers/admins get detailed logs securely.

Never catch every exception and silently continue.

---

## 19. Dependency & Supply Chain

Use:

- pinned/locked dependencies where practical
- Dependabot/Renovate or equivalent
- vulnerability scanning
- license review when needed
- minimal dependency count
- no package added "just because"
- verify package names before installation
- remove unused packages

OWASP Top 10:2025 includes Software Supply Chain Failures as A03. source: OWASP Top 10:2025

---

## 20. Caching

Cache only public/read-only data.

Safe candidates:

- categories
- public site settings
- home sections
- active promotions
- catalog pages where invalidation is defined

Do not publicly cache:

- admin responses
- authenticated responses
- user-specific checkout data

Invalidate relevant cache when admin content changes.

"Immediately reflect frontend" means API freshness/invalidation, not a browser with stale cache.

---

## 21. Database and API Performance

Use:

- `select_related`
- `prefetch_related`
- indexed fields
- pagination
- bounded querysets
- N+1 detection
- query profiling during testing

Do not optimize blindly.

---

## 22. Deployment Shape

Preferred production topology:

```text
CDN / Reverse Proxy
        │
        ├── Static frontend
        │
        └── HTTPS
             │
             ▼
        Django ASGI/WSGI
             │
             ├── PostgreSQL
             └── Media/object storage
```

Do not use Django `runserver` in production.

Django's deployment checklist explicitly recommends a production WSGI/ASGI server and running `manage.py check --deploy`. source: Django deployment checklist

---

## 23. Environment Separation

Required:

```text
development
staging (recommended)
production
```

Never share production secrets with development.

Use separate databases.

---

## 24. Backup / Recovery

At minimum:

- scheduled PostgreSQL backups
- media backups
- documented restore procedure
- test a restore before declaring production ready

A backup that has never been restored is not a verified recovery strategy.

---

## 25. Testing Architecture

### Backend

- model tests
- serializer/API tests
- permission tests
- validation tests
- security tests
- upload tests
- delivery calculation tests
- cart verification tests

### Frontend

- component tests where useful
- API integration tests
- end-to-end smoke tests
- mobile viewport tests

### Security

- dependency scan
- secret scan
- Django deploy checks
- header checks
- auth abuse tests
- XSS payload tests
- SQL injection probes at validation boundaries
- path traversal upload probes
- oversized upload tests
- unauthorized mutation tests

---

## 26. References

- Django 6.0 security: https://docs.djangoproject.com/en/6.0/topics/security/
- Django deployment checklist: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/
- Django 6.0 release notes: https://docs.djangoproject.com/en/6.0/releases/6.0/
- OWASP Top 10:2025: https://owasp.org/Top10/
- OWASP File Upload Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- DRF permissions: https://www.django-rest-framework.org/api-guide/permissions/
- DRF throttling: https://www.django-rest-framework.org/api-guide/throttling/
