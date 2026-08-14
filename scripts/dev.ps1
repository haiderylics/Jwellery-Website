# ==============================================================================
# Local Development Server Runner
# Runs Django development server inside project-local Python 3.12 environment
# ==============================================================================
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "Starting Django development server (Python 3.12 via uv)..." -ForegroundColor Cyan
uv run python backend/manage.py runserver
