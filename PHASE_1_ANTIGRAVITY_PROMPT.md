You are the lead engineering agent for this jewellery e-commerce project.

We are starting PHASE 1 ONLY.

Before any implementation, completely read:
1. docs/PRD.md
2. docs/Architecture.md
3. docs/Phases.md
4. docs/rules.md
5. docs/design.md
6. docs/memory.md
7. docs/skills/README.md
8. docs/skills/backend-django.md
9. docs/skills/frontend-premium.md
10. docs/skills/security.md
11. docs/skills/testing.md
12. docs/skills/database.md
13. docs/skills/media.md
14. docs/skills/uv-tooling.md
15. docs/skills/mcp-agent.md

Then inspect the existing repository and Git state.

CRITICAL PYTHON CONSTRAINT:
My system already has Python 3.10 and other projects depend on it.
DO NOT uninstall, replace, upgrade, or globally modify Python 3.10.

This project MUST use a project-local uv-managed Python 3.12 environment.
Use uv for Python, dependency management and reproducible commands.
Prefer `uv run ...` rather than manual environment activation.

Target baseline:
- Python 3.12
- current supported Django 6.x patch release
- PostgreSQL in production
- pyproject.toml + uv.lock
- .python-version = 3.12
- .venv excluded from Git

Check the currently installed uv version and, if appropriate, use the official uv update command. Do not blindly trust stale package versions; verify current compatibility from official docs.

MCP:
Use current/trusted MCPs when useful:
- Google Developer Knowledge
- GitHub
- Playwright/browser
- PostgreSQL/database
- trusted official documentation MCPs
- observability MCP only if already configured

Use least privilege and read-only by default. Do not expose secrets or touch production.

PHASE 1 OBJECTIVE:
Establish the project/repository/tooling foundation ONLY.

Inspect:
- Git state
- existing pyproject.toml
- uv.lock
- .python-version
- .venv
- backend/frontend directories
- CI config
- Docker files
- env files
- existing app code
- existing documentation
- existing MCP configuration if safely inspectable

Determine:
- final repo layout
- Python/uv setup
- Django version
- dependency strategy
- frontend tooling
- linting/formatting
- type checking
- test framework
- pre-commit strategy if useful
- CI baseline
- environment variable strategy
- .gitignore
- secret scanning
- dependency vulnerability scanning
- baseline security checks
- local developer commands
- reproducibility strategy
- MCP usage plan

MANDATORY WORKFLOW:
Do NOT write application features yet.
Do NOT create models.
Do NOT create APIs.
Do NOT create admin features.
Do NOT create product pages.
Do NOT deploy.
Do NOT touch production credentials.
Do NOT modify unrelated projects.
Do NOT install unnecessary packages.

FIRST produce an implementation plan and STOP for human verification.

Your Phase 1 plan must contain:
1. Repository findings
2. Existing-state conflicts
3. Architectural/tooling decisions
4. Python 3.10 isolation strategy
5. Exact uv commands to be used
6. Dependency strategy
7. MCP plan and permissions
8. Files to create/change
9. Security baseline
10. Testing baseline
11. CI plan
12. Acceptance criteria
13. Risks/tradeoffs

QUALITY BAR:
The result must be modular, maintainable, reproducible, production-grade, secure by default, minimal in unnecessary dependencies, aligned with OWASP Top 10:2025, aligned with current Django security guidance, and appropriate for a premium small-business storefront without overengineering.

Return only the requested Phase 1 plan and STOP.
