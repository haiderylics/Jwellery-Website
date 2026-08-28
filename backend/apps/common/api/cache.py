"""Conservative HTTP and server-cache helpers for anonymous public APIs."""

import hashlib
import json
from datetime import timedelta
from math import ceil
from typing import Any

from django.db.models import Min, Q
from django.http import HttpRequest
from django.utils import timezone
from django.utils.cache import patch_cache_control
from django.utils.http import parse_etags, quote_etag
from rest_framework.response import Response

from backend.apps.common.cache_utils import bounded_schedule_timeout

SCHEDULED_CACHE_MARKER = "_ahs_scheduled_cache_v1"


def public_response(
    request: HttpRequest,
    payload: Any,
    *,
    max_age: int,
    status_code: int = 200,
) -> Response:
    """Return a cacheable anonymous GET response with conditional-GET support."""
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    etag = quote_etag(hashlib.sha256(serialized.encode("utf-8")).hexdigest())
    headers = {"ETag": etag}
    if etag in parse_etags(request.headers.get("If-None-Match", "")):
        response = Response(status=304, headers=headers)
    else:
        response = Response(payload, status=status_code, headers=headers)
    patch_cache_control(response, public=True, max_age=max_age, must_revalidate=True)
    return response


def schedule_cache_timeout(*model_classes: type, configured_timeout: int) -> int:
    """Bound a scheduled payload's TTL by the nearest enabled start/end boundary."""
    now = timezone.now()
    boundaries = []
    for model_class in model_classes:
        boundary = model_class.objects.filter(is_active=True).aggregate(
            next_start=Min("start_datetime", filter=Q(start_datetime__gt=now)),
            next_end=Min("end_datetime", filter=Q(end_datetime__gt=now)),
        )
        boundaries.extend((boundary["next_start"], boundary["next_end"]))
    return bounded_schedule_timeout(configured_timeout, boundaries, now=now)


def scheduled_cache_entry(payload: Any, timeout: int) -> dict[str, Any]:
    """Store schedule expiry alongside a payload for DB-free cache hits."""
    return {
        SCHEDULED_CACHE_MARKER: True,
        "payload": payload,
        "expires_at": timezone.now() + timedelta(seconds=timeout),
    }


def unpack_scheduled_cache_entry(entry: dict[str, Any], *, browser_max_age: int) -> tuple[Any, int]:
    """Cap browser freshness by the cached schedule entry's remaining lifetime."""
    remaining = max(0, ceil((entry["expires_at"] - timezone.now()).total_seconds()))
    return entry["payload"], min(browser_max_age, remaining)


class PublicCacheControlMixin:
    """Apply short browser caching only to successful anonymous GET/HEAD responses."""

    cache_control_max_age = 30

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if request.method in {"GET", "HEAD"} and 200 <= response.status_code < 300:
            patch_cache_control(
                response,
                public=True,
                max_age=self.cache_control_max_age,
                must_revalidate=True,
            )
        return response
