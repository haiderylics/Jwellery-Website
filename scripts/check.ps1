# ==============================================================================
# Comprehensive Local Quality & Security Check Script
# Runs formatting, linting, static security analysis, dependency audits,
# Django system checks, and the Pytest test suite.
# ==============================================================================
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "`n[1/6] Running Ruff linter..." -ForegroundColor Cyan
uv run ruff check .

Write-Host "`n[2/6] Running Ruff format check..." -ForegroundColor Cyan
uv run ruff format --check .

Write-Host "`n[3/6] Running Bandit static security analysis..." -ForegroundColor Cyan
uv run bandit -r backend/ -x backend/tests

Write-Host "`n[4/6] Running pip-audit dependency vulnerability scan..." -ForegroundColor Cyan
uv run pip-audit

Write-Host "`n[5/6] Running Django system checks..." -ForegroundColor Cyan
uv run python backend/manage.py check

Write-Host "`n[6/6] Running Pytest test suite..." -ForegroundColor Cyan
uv run pytest

Write-Host "`nAll Phase 1 quality and security checks passed successfully!`n" -ForegroundColor Green
