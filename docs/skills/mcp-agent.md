# Skill: MCP & Agent Tooling

Use MCP to improve accuracy and speed without expanding the attack surface.

Preferred MCP categories:
1. Google Developer Knowledge — official/current Google documentation.
2. GitHub — repo/issues/PRs/code review.
3. Playwright/browser — UI and responsive smoke tests.
4. PostgreSQL/database — development/staging inspection and query analysis.
5. Trusted official documentation MCPs.
6. Observability MCP only if actually configured.

Security:
- least privilege
- read-only by default
- local/staging first
- no secret dumping
- no unnecessary production access
- no arbitrary production mutations
- verify server provenance
- disconnect unused integrations

Agent may freely:
- inspect repo
- run safe local commands
- edit current project
- run tests

Approval required before:
- production deployment
- destructive DB operations
- credential rotation
- production data mutation
- installing untrusted MCPs
- external messages/actions

For technical questions:
inspect local project → official docs/MCP → verify installed versions → implement → test.

Never blindly copy MCP output into production code.
