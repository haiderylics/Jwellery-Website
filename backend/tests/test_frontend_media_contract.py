"""Static cross-stack guard for backend-authoritative media delivery URLs."""

from pathlib import Path

FRONTEND_SOURCE = Path(__file__).resolve().parents[2] / "frontend" / "src"


def test_frontend_does_not_construct_cloudinary_asset_urls() -> None:
    offenders = []
    for source_path in FRONTEND_SOURCE.rglob("*.ts*"):
        source = source_path.read_text(encoding="utf-8").lower()
        if "res.cloudinary.com" in source or "cloudinary_url" in source:
            offenders.append(source_path.relative_to(FRONTEND_SOURCE).as_posix())

    assert offenders == []


def test_responsive_image_consumes_backend_urls_without_identity_rewrites() -> None:
    source = (FRONTEND_SOURCE / "components" / "ui" / "ResponsiveImage.tsx").read_text(
        encoding="utf-8"
    )

    assert "const mainSrc = src || image?.image_url;" in source
    assert "const thumbSrc = image?.thumbnail_url;" in source
    assert "const medSrc = image?.medium_url;" in source
    assert "const lrgSrc = image?.large_url;" in source
    assert "src={medSrc || mainSrc}" in source
    assert "srcSet={srcSet}" in source
    assert '".png"' not in source
    assert '"/v1/"' not in source
