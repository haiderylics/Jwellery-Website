# Engineering, Security & Antigravity Rules

These rules are mandatory project constraints.

---

## 1. Agent Operating Protocol

Before any implementation:

1. Read:
   - PRD.md
   - Architecture.md
   - Phases.md
   - rules.md
   - design.md
   - memory.md
2. Inspect repository.
3. Identify existing code.
4. Reconcile requirements with current state.
5. Produce a concise implementation plan for the requested phase.
6. Stop and wait for human verification.

Do not write implementation code before plan approval.

---

## 2. Phase Isolation

Work only on the approved phase.

Do not:

- refactor unrelated modules
- change architecture without approval
- install unrelated libraries
- redesign completed pages
- create speculative abstractions

If another issue is discovered, record it under backlog/memory and continue only if it blocks the current phase.

---

## 3. No Fake Completion

Never say a feature is complete if:

- tests do not pass
- it works only in one browser without qualification
- data is hard-coded where requirements require admin control
- security checks were skipped
- integration is mocked but presented as real
- deployment was not tested where production readiness is claimed

---

## 4. Source of Truth

Priority:

1. Approved human instruction for current scope
2. PRD.md
3. Architecture.md
4. Phases.md
5. design.md
6. memory.md
7. code comments

If documents conflict, stop and report the conflict.

---

## 5. Code Quality

Required:

- small cohesive modules
- explicit naming
- type hints where valuable
- docstrings for non-obvious public APIs
- no giant functions
- no giant components
- no god classes
- no duplicated business logic
- domain rules centralized
- deterministic behaviour
- tests for business-critical logic

Avoid:

- premature abstractions
- generic `utils.py` dumping ground
- magic numbers
- magic strings
- deeply nested conditionals
- unnecessary inheritance
- copy-paste CRUD
- dead code

---

## 6. Dependency Policy

Before adding a dependency:

- verify maintained status
- inspect package purpose
- check security history
- check compatibility with current Python/Django
- confirm it solves a real requirement
- prefer stdlib/Django functionality when sufficient

Never install a package merely because an AI suggested it.

---

## 7. Security Non-Negotiables

### Secrets

Never hard-code secrets.

Never commit:

- `.env`
- API keys
- passwords
- tokens
- cloud credentials
- MCP credentials

### Input

Treat all external input as untrusted:

- query strings
- path params
- POST data
- JSON
- uploaded files
- HTTP headers
- cookies
- third-party responses

### Output

Escape output by default.

Do not render raw HTML unless explicitly sanitized with a vetted, justified sanitizer.

### SQL

Never concatenate user input into SQL.

Prefer Django ORM.

### Authorization

Every mutation needs server-side authorization.

UI hiding is not authorization.

### Admin

Django Admin must not be exposed as a public API.

---

## 8. Upload Security

All uploaded images/videos are hostile by default.

Required:

- allowlist extensions
- allowlist MIME types
- verify actual file content where practical
- file-size limits
- dimension/duration limits
- randomized filenames
- safe storage location
- no executable file types
- prevent path traversal
- no client-controlled storage path
- no direct template execution
- safe Content-Type
- consider stripping unsafe metadata

No SVG upload unless it is explicitly treated/sanitized as potentially active content.

---

## 9. Frontend Security

Never trust:

- localStorage price
- localStorage stock
- hidden form values
- cart totals
- client-side discount
- client-side delivery calculations

Frontend is a presentation client.

Backend is authoritative.

---

## 10. API Security

Every endpoint must answer:

- Who can call it?
- What can they see?
- What can they modify?
- How much data can they request?
- What is the maximum input size?
- How is abuse limited?
- What is logged?

Use pagination for lists.

Avoid returning entire database tables.

---

## 11. Rate Limiting

Use endpoint-specific limits for:

- admin login
- public search
- expensive catalog queries
- contact-like future endpoints
- any future write endpoint

Framework throttling is a policy/control, not a complete DDoS defense. Network/CDN protection may still be required. DRF documents this limitation explicitly. source: DRF throttling

---

## 12. Error Handling

Never leak:

- stack traces
- SQL queries
- filesystem paths
- environment variables
- secret values
- internal IDs that are not needed
- dependency versions unless intentionally public

Public error:

```text
Something went wrong. Please try again.
```

Detailed error goes to secure logs.

---

## 13. Logging

Logs must be useful but non-sensitive.

Never log:

- passwords
- raw session cookies
- API tokens
- full credit-card data
- private WhatsApp content
- unnecessary PII

Use structured logs when practical.

---

## 14. Database Rules

- All schema changes via migrations.
- Never edit production DB manually without a documented emergency procedure.
- Add indexes based on actual query patterns.
- Add constraints where business rules matter.
- Avoid cascade deletes when they can destroy meaningful business content unexpectedly.
- Use soft deletion only where it provides real value; do not add it everywhere.

---

## 15. Admin Rules

Owner-facing admin should:

- use understandable labels
- provide useful help text
- default safe states
- validate before save
- support search/filter
- avoid exposing technical fields unless needed

Do not give the owner a giant settings table with cryptic fields.

---

## 16. API/Frontend Contract

API changes must update:

- types
- serializers
- tests
- frontend consumer
- documentation if public contract changed

Avoid silently changing response shapes.

---

## 17. Git Rules

Commit messages should be meaningful.

Prefer:

```text
feat(catalog): add product variants
fix(cart): validate server-side totals
security(upload): restrict media types
```

Do not commit:

```text
update
fix stuff
final
new final
final2
```

Never rewrite shared history casually.

---

## 18. Testing Rules

Each bug fixed must have a regression test if practical.

Critical logic requires tests:

- pricing
- delivery
- stock
- variant selection
- permissions
- uploads
- API validation
- promotions
- cart normalization

Before claiming completion:

```bash
python manage.py test
```

plus frontend tests/lint/build as applicable.

---

## 19. Agent Self-Review

Before phase completion, agent must inspect:

- changed files
- unused imports
- dead code
- duplicate logic
- security regressions
- accessibility
- responsive layout
- API error paths
- loading/empty/error states
- secret leakage
- dependency additions
- query count/performance risks

---

## 20. No Overengineering

The target is a premium small-business e-commerce catalog.

Do not build:

- microservices
- event buses
- GraphQL
- Kubernetes
- CQRS
- complex service meshes
- custom identity systems

unless a real requirement appears.

Simple architecture is a security feature.

---

## 21. UI Quality Gate

Reject:

- generic AI gradients
- excessive glassmorphism
- random rounded cards
- giant centered headings everywhere
- over-animated sections
- fake 3D jewellery
- stock-template copy
- dense visual clutter
- inconsistent icon styles
- 20 different button styles

The page must look intentionally designed.

---

## 22. MCP Rules

MCP tools are assistants, not authorities.

Before using an MCP:

- identify the data it can access
- minimize permissions
- prefer read-only where possible
- use only trusted servers
- inspect configuration
- avoid passing secrets unless required
- never expose production credentials to an unnecessary MCP
- do not let an MCP mutate production infrastructure without explicit approval

Antigravity supports local and remote MCP servers and configures them through its MCP configuration mechanism. source: Google Antigravity Codelab

---

## 23. Recommended MCP Categories

Use only what materially helps.

### 1. Google Developer Knowledge MCP

Useful for:

- official Google docs
- current APIs
- Google tooling
- eliminating stale documentation assumptions

### 2. GitHub MCP

Useful for:

- repository inspection
- issues
- pull requests
- diffs
- code navigation

Scope it to the project repository if possible.

### 3. Playwright/browser MCP

Useful for:

- browser automation
- screenshots
- responsive checks
- UI interaction
- regression tests

Must not receive production secrets.

### 4. PostgreSQL/database MCP

Useful for:

- schema inspection
- query analysis
- controlled development DB exploration

Use against development/staging DB by default, not production.

### 5. Context/documentation MCP

A trusted documentation MCP can be useful for framework/library docs.

Never rely on an untrusted documentation mirror when official docs are available.

### 6. Sentry/observability MCP

Useful only if observability is actually configured.

Do not add it merely for appearance.

---

## 24. MCP Security

Assume MCP tools are privileged integrations.

Rules:

- least privilege
- read-only default
- staging before production
- no credential dumping
- no arbitrary shell execution through an MCP
- audit changes
- disconnect unused servers

OWASP's 2025 Non-Human Identity guidance highlights secret leakage, overprivileged non-human identities, vulnerable third-party identities and long-lived secrets as material risks. source: OWASP NHI Top 10:2025

---

## 25. Browser Automation Rules

Automated browser agents must:

- use test accounts only
- use staging/local data
- never purchase anything
- never send real customer messages
- never publish to production
- never upload private customer data during tests

WhatsApp integration must be tested by generating a deterministic URL/message, not by accidentally contacting the business.

---

## 26. Accessibility Rules

Every interactive control must be:

- keyboard reachable
- visibly focused
- labelled
- operable on mobile

Images require useful alt text unless decorative.

---

## 27. Performance Rules

Do not ship:

- huge unoptimized original images
- blocking third-party scripts without justification
- unnecessary dependencies
- repeated API calls for the same data
- N+1 database access
- render-blocking code that can be deferred

---

## 28. Production Rule

Before production:

```text
DEBUG = False
manage.py check --deploy passes
HTTPS works
admin secure
database backups verified
media storage verified
secrets externalized
CORS restricted
CSP configured
error pages tested
logging works
health checks work
```

