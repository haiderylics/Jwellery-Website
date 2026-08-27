# Jewellery E-Commerce Platform

A modern, secure, editorial jewellery catalog, shopping cart, and WhatsApp-assisted ordering platform.

---

## 1. Project Overview

- **Backend:** Django 6.x running on an isolated, project-local Python 3.12 environment managed by Astral `uv`.
- **Database:** PostgreSQL in production; SQLite enabled for local development convenience.
- **Frontend:** Modern static client designed to consume versioned backend JSON APIs (`/api/v1/`).
- **Checkout Model:** Client-side cart with server-authoritative pricing and inventory validation handoff to WhatsApp.
- **Administration:** Django Admin for business content, merchandising, and settings management.
- **Static files:** WhiteNoise serves collected Django static assets in Railway.
- **Media:** Cloudinary stores admin-uploaded images and videos in production.

---

## 2. Architecture & Directory Structure

```text
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
├── backend/
│   ├── apps/                  # Domain-driven modular Django apps
│   │   ├── catalog/           # Products, variants, attributes, categories
│   │   ├── content/           # Reviews, gallery, about, testimonials
│   │   ├── promotions/        # Banners, popup notifications, events
│   │   ├── settings/          # Store settings, WhatsApp configuration, delivery rules
│   │   └── common/            # Shared primitives and utilities
│   ├── config/                # Django project configuration
│   │   ├── settings/
│   │   │   ├── base.py        # Shared configuration & baseline security headers
│   │   │   ├── development.py # Development-only settings (DEBUG=True, SQLite)
│   │   │   └── production.py  # Production settings (DEBUG=False, strict HTTPS/HSTS/CORS)
│   │   ├── urls.py            # Root URLconf with /health/live/ probe
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── tests/                 # Integration, settings, and smoke test suite
│   └── manage.py
├── frontend/                  # Static frontend application
│   ├── src/                   # Component, style, and API consumer baseline
│   ├── package.json           # Frontend dependency manifest
│   └── .node-version          # Pinned Node.js LTS version (20.x)
├── docs/                      # PRD, Architecture, Rules, and Skill guides
├── scripts/                   # Local developer convenience scripts
├── .env.example               # Sanitized environment variable template
├── .gitignore                 # Strict ignore rules
├── .python-version            # Pinned Python version (3.12)
├── pyproject.toml             # uv project manifest and tool configurations
└── uv.lock                    # Deterministic dependency lockfile
```

---

## 3. Prerequisites & Environment Isolation

This project requires **Python 3.12**, managed via **Astral `uv`**.
The host system's global Python 3.10 is completely untouched and preserved for other projects.

### Installing `uv` (Standalone)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 4. Local Setup Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/haiderylics/Jwellery-Website.git
   cd "Jwellery Website"
   ```

2. **Initialize Python 3.12 and synchronize locked dependencies:**
   ```bash
   uv python install 3.12
   uv venv --python 3.12 .venv
   uv sync
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```

4. **Verify Django System Integrity:**
   ```bash
   uv run python backend/manage.py check
   ```

5. **Run the Test Suite:**
   ```bash
   uv run pytest
   ```

---

## 5. Developer Command Reference

Always use `uv run ...` to ensure commands execute inside the project-local Python 3.12 virtual environment:

| Task | Command |
| :--- | :--- |
| **Run Dev Server** | `uv run python backend/manage.py runserver` |
| **Run Tests** | `uv run pytest` |
| **Lint Code** | `uv run ruff check .` |
| **Format Code** | `uv run ruff format .` |
| **Check Formatting** | `uv run ruff format --check .` |
| **Static Security Scan** | `uv run bandit -r backend/` |
| **Dependency Audit** | `uv run pip-audit` |
| **Django System Check** | `uv run python backend/manage.py check` |
| **Deployment Check** | `uv run python backend/manage.py check --deploy --settings=backend.config.settings.production` |

---

## 6. Continuous Integration (CI)

The GitHub Actions workflow (`.github/workflows/ci.yml`) enforces the following gates on every pull request and push to `main`:

1. Strict dependency verification using `uv sync --frozen`
2. Ruff code formatting and linting
3. Bandit static security analysis
4. `pip-audit` vulnerability scanning
5. Django system and deployment checks
6. Pytest test suite execution
7. Frontend build and TypeScript validation

---

## 7. Phase Management

Implementation strictly follows the phased delivery roadmap in [`docs/Phases.md`](docs/Phases.md).
Phase 1 establishes the repository and tooling foundation. Subsequent phases implement domain models, admin capabilities, APIs, and frontend styling.
