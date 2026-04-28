import logging
from rest_framework.views import exception_handler
from rest_framework import status
from utils.response import api_error

logger = logging.getLogger(__name__)


def global_exception_handler(exc, context):
    """
    Custom DRF exception handler.
    - Known DRF exceptions (400, 401, 403, 404, etc.) → structured api_error response.
    - Unhandled exceptions (500) → logged with traceback, returns generic api_error.
    """
    # Let DRF handle its own exceptions first (validation, auth, throttling, etc.)
    response = exception_handler(exc, context)

    if response is not None:
        # DRF already handled it — re-wrap into our api_error format
        message = response.data.get("detail", str(exc)) if isinstance(response.data, dict) else str(exc)
        return api_error(
            message=str(message),
            status_code=response.status_code,
            data=response.data if isinstance(response.data, dict) else None,
        )

    # Unhandled exception → 500
    view = context.get("view", None)
    view_name = view.__class__.__name__ if view else "Unknown"
    logger.exception(
        "[%s] Unhandled server error: %s",
        view_name,
        str(exc),
    )

    return api_error(
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
