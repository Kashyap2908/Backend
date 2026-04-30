import logging

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status

from common.exceptions import BaseAppException
from common.responses import error_response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Handle our own domain exceptions first
    if isinstance(exc, BaseAppException):
        logger.warning(
            "App exception [%s]: %s | details=%s",
            exc.error_code,
            exc.message,
            exc.details,
        )
        return error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            http_status=exc.http_status,
        )

    # Fall back to DRF's built-in handler (handles 405, 415, serializer errors, etc.)
    response = drf_exception_handler(exc, context)
    if response is not None:
        # Reshape DRF errors into our standard envelope
        original_data = response.data
        message = "Request failed"
        details = None

        if isinstance(original_data, dict):
            detail = original_data.get("detail")
            if detail:
                message = str(detail)
            else:
                details = original_data
        elif isinstance(original_data, list):
            details = original_data

        return error_response(
            message=message,
            error_code="REQUEST_ERROR",
            details=details,
            http_status=response.status_code,
        )

    # Truly unhandled — 500
    logger.error("Unhandled exception in view", exc_info=exc)
    return error_response(
        message="An unexpected error occurred. Please try again later.",
        error_code="INTERNAL_SERVER_ERROR",
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
