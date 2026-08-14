# Skill: Application Security

Target defense-in-depth aligned with OWASP Top 10:2025 and current Django security guidance.

Never claim the application is unhackable.

Threat-model:
- admin accounts
- customer data
- media
- database
- secrets
- deployment
- public API
- uploads
- external integrations

Review OWASP 2025:
A01 Broken Access Control
A02 Security Misconfiguration
A03 Software Supply Chain Failures
A04 Cryptographic Failures
A05 Injection
A06 Insecure Design
A07 Authentication Failures
A08 Software/Data Integrity Failures
A09 Security Logging/Alerting Failures
A10 Mishandling Exceptional Conditions

Non-negotiables:
- no committed secrets
- server-side authorization
- CSRF
- strict CORS allowlist
- HTTPS and secure cookies
- HSTS after HTTPS validation
- CSP
- secure headers
- rate limiting where useful
- generic public errors
- structured safe logs
- dependency/security scans

Uploads are hostile:
- allowlisted extensions
- MIME/content validation
- file-size and dimension/duration limits
- randomized filenames
- no executable uploads
- path traversal prevention
- isolated media storage
- safe delivery

Do not trust client totals, hidden fields, localStorage prices, or UI-only permissions.

Test:
- IDOR
- privilege escalation
- XSS
- CSRF
- injection boundaries
- upload attacks
- oversized inputs
- rate-limit abuse
- information leakage
