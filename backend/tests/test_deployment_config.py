"""Deployment routing assertions that protect the external admin entry point."""

from pathlib import Path


def test_netlify_admin_redirects_precede_spa_fallback() -> None:
    redirect_file = Path("frontend/public/_redirects")
    rules = [
        line.strip()
        for line in redirect_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert rules[0] == ("/admin https://jwellery-website-production.up.railway.app/admin/ 302")
    assert rules[1] == (
        "/admin/* https://jwellery-website-production.up.railway.app/admin/:splat 302"
    )
    assert rules[-1] == "/* /index.html 200"
