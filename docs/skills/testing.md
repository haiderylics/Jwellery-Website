# Skill: Testing & Verification

Use a practical test pyramid:
1. unit
2. integration/API
3. browser/E2E smoke tests

Backend:
- model constraints
- pricing
- stock
- variants
- delivery
- promotions
- serializers
- filters/search
- permissions
- uploads
- error paths

Cart:
- normal
- multiple products
- variants
- quantity
- stale product
- out-of-stock
- changed price
- delivery threshold
- international mode

Frontend:
- browse
- search/filter
- product detail
- cart
- checkout validation
- WhatsApp message generation
- popup
- responsive navigation

E2E can use Playwright/browser MCP.
Never use real customer data, real purchases or real customer WhatsApp sends in tests.

Before phase completion:
- tests pass
- lint/type checks pass where configured
- production frontend build passes
- migrations/checks pass
- no secrets
- no unexpected dependency changes

Report changed files, commands, tests, risks and deferred work.
