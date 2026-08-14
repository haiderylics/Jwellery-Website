"""Shared validation utilities for Jewellery Website."""

import re
import urllib.parse

from django.core.exceptions import ValidationError

from backend.apps.common.security_events import log_security_event

SAFE_EXTERNAL_SCHEMES = ("https",)
SAFE_INTERNAL_PREFIXES = ("/", "#")
DISALLOWED_SCHEMES = ("javascript", "data", "file", "vbscript", "blob", "about")


def validate_safe_url(value: str) -> None:
    """Validate that a URL uses a safe scheme (https) or is a relative path.

    Rejects dangerous pseudo-protocols like javascript:, data:, file:, vbscript:
    including URL-encoded, case-mixed, and whitespace-injected variations.
    """
    if not value:
        return

    # Strip whitespace and null bytes
    cleaned = value.strip().replace("\x00", "")

    # Decode percent-encodings to catch java%73cript: or %00
    try:
        decoded = urllib.parse.unquote(cleaned)
    except Exception:
        decoded = cleaned

    # Remove all internal whitespace to catch 'j a v a s c r i p t :'
    squashed = re.sub(r"\s+", "", decoded).lower()

    for scheme in DISALLOWED_SCHEMES:
        if squashed.startswith(f"{scheme}:") or f"{scheme}:" in squashed:
            log_security_event(
                "security.url_rejected",
                reason="dangerous_scheme_detected",
                attempted_scheme=scheme,
            )
            raise ValidationError(f"Unsafe URL scheme '{scheme}:' is strictly prohibited.")

    # Allow relative URLs (e.g. /collections/rings/ or #contact)
    if any(cleaned.startswith(prefix) for prefix in SAFE_INTERNAL_PREFIXES):
        if cleaned.startswith("//"):
            # Protocol-relative URL attempt (e.g. //evil.com)
            log_security_event(
                "security.url_rejected",
                reason="protocol_relative_url_rejected",
            )
            raise ValidationError("Protocol-relative URLs starting with '//' are not permitted.")
        return

    parsed = urllib.parse.urlparse(cleaned)
    if not parsed.scheme:
        raise ValidationError("URL must start with https:// or a relative path (e.g. /shop/).")

    if parsed.scheme.lower() not in SAFE_EXTERNAL_SCHEMES:
        log_security_event(
            "security.url_rejected",
            reason="unsupported_scheme",
            attempted_scheme=parsed.scheme,
        )
        raise ValidationError(
            f"Unsafe URL protocol '{parsed.scheme}:'. Only secure HTTPS URLs (https://) are permitted."
        )

    if not parsed.netloc:
        raise ValidationError("Invalid URL structure: missing domain name.")
