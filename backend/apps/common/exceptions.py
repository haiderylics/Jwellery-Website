"""Custom DRF exception handling for consistent, non-leaking JSON error contracts."""

import logging
from typing import Any

from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("django.security")


def custom_api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Standardize error responses into a consistent JSON envelope.

    Prevents raw stack traces or internal secrets from leaking into public responses.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = "error"
        if isinstance(exc, exceptions.NotFound | Http404):
            error_code = "not_found"
            message = "The requested resource was not found."
        elif isinstance(exc, exceptions.MethodNotAllowed):
            error_code = "method_not_allowed"
            message = f"Method '{context.get('request').method}' is not allowed for this endpoint."
        elif isinstance(exc, exceptions.Throttled):
            error_code = "throttled"
            message = f"Request was throttled. Expected available in {exc.wait} seconds."
        elif isinstance(exc, exceptions.ValidationError):
            error_code = "validation_error"
            message = "Invalid request parameters."
        elif isinstance(exc, exceptions.PermissionDenied):
            error_code = "forbidden"
            message = "You do not have permission to perform this action."
        elif isinstance(exc, exceptions.NotAuthenticated):
            error_code = "unauthenticated"
            message = "Authentication credentials were not provided."
        else:
            message = "An error occurred while processing the request."

        payload = {
            "error": {
                "code": error_code,
                "message": message,
                "details": response.data,
            }
        }
        response.data = payload
        return response

    # Unhandled 500 exceptions
    logger.exception("Unhandled server exception in public API: %s", exc)
    return Response(
        {
            "error": {
                "code": "internal_error",
                "message": "A server error occurred. Please try again later.",
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
