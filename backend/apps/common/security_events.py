"""Structured security and operational event logging.

Provides standardized event emission for auditing and intrusion detection
without leaking sensitive PII, passwords, or secrets.
"""

import json
import logging
from typing import Any

logger = logging.getLogger("backend.security")


def log_security_event(event_type: str, severity: str = "WARNING", **details: Any) -> None:
    """Emit a structured JSON security or operational event log."""
    # Sanitize detail values: avoid printing long payloads or sensitive tokens
    safe_details = {}
    for k, v in details.items():
        if k in ("password", "token", "secret", "session", "whatsapp_message", "address", "phone"):
            safe_details[k] = "[REDACTED]"
        elif isinstance(v, (str, int, float, bool)) or v is None:
            safe_details[k] = v
        else:
            safe_details[k] = str(v)

    log_entry = {
        "event_type": event_type,
        "severity": severity,
        **safe_details,
    }

    msg = f"SECURITY_EVENT {json.dumps(log_entry)}"
    if severity == "ERROR":
        logger.error(msg)
    elif severity == "INFO":
        logger.info(msg)
    else:
        logger.warning(msg)
