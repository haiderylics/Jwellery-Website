# Skill: Backend Django Engineering

Build a modular, secure Django backend using the current supported Django/Python versions.

Rules:
- Prefer Django built-ins before dependencies.
- Use domain-based apps: catalog, content, promotions, settings, common.
- Keep views thin and serializers explicit.
- Centralize business rules.
- Enforce important invariants at both validation and database layers.
- Use transactions for atomic multi-write operations.
- Avoid giant models/views/utils modules.

API:
- Version public endpoints under /api/v1/.
- Explicit serializers only.
- Paginate and bound list responses.
- Never expose internal/admin fields.
- Use deterministic ordering.
- Allow only controlled filters.
- Cache public read-only data only.

Backend-authoritative values:
- prices
- stock/availability
- variants
- delivery rules
- promotions
- canonical product URLs

Cart verification:
1. Receive product/variant IDs and quantities.
2. Fetch authoritative records.
3. Validate publication, variant, stock and quantity.
4. Calculate price/delivery server-side.
5. Return normalized summary.
6. Frontend creates WhatsApp message from that summary.

Admin:
- Django Admin for MVP.
- Business terminology.
- Search/filter/pagination.
- Inline product images.
- Least-privilege staff permissions.

Security:
- Review DEBUG, SECRET_KEY, ALLOWED_HOSTS, CSRF, secure cookies, HTTPS, HSTS, CSP, CORS, clickjacking, content-sniffing and error handling.

Performance:
- select_related/prefetch_related where justified.
- indexes based on real queries.
- test for N+1.
- paginate.

Do not introduce Celery/Redis/microservices unless a real requirement appears.
