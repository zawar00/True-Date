import logging
from rest_framework import serializers
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler to get the standard response
    response = drf_exception_handler(exc, context)

    # If DRF's exception handler generated a response
    if response is not None:
        # Handle cases where response.data is a dict or list
        details = response.data if isinstance(response.data, (dict, list)) else {"detail": str(response.data)}
        message = details.get("detail", "An error occurred.") if isinstance(details, dict) else "An error occurred."

        # Log the exception with context
        logger.error(f"Exception occurred: {exc}. Context: {context}")

        # Return a structured error response
        return Response({
            "status": "error",
            "message": message,
            "details": details,
            "code": response.status_code
        }, status=response.status_code)

    # Handle cases not caught by DRF's exception handler
    if isinstance(exc, serializers.ValidationError):
        # Handle validation errors explicitly
        logger.warning(f"Validation error: {exc}. Context: {context}")
        return Response({
            "status": "error",
            "message": "Validation error occurred.",
            "details": exc.detail,  # exc.detail can be a dict or list
            "code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    # Catch-all for unknown errors
    logger.critical(f"Unhandled exception: {exc}. Context: {context}", exc_info=True)
    return Response({
        "status": "error",
        "message": "A server error occurred.",
        "details": str(exc),
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
