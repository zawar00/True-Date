from rest_framework.views import exception_handler
from .responses import error_response

def custom_exception_handler(exc, context):
    """
    Custom exception handler to return a structured error response
    """
    # Call REST framework's default exception handler first to get the standard error response
    response = exception_handler(exc, context)

    # Now add the custom error response format
    if response is not None:
        errors = response.data
        message = errors.pop('detail', 'An error occurred') if 'detail' in errors else 'Validation errors'
        return error_response(message=message, errors=errors, status_code=response.status_code)

    # If no response is generated, return a generic error response
    return error_response(message="An unexpected error occurred", status_code=500)
from rest_framework.views import exception_handler
from .responses import error_response

def custom_exception_handler(exc, context):
    """
    Custom exception handler to return a structured error response
    """
    # Call REST framework's default exception handler first to get the standard error response
    response = exception_handler(exc, context)

    # Now add the custom error response format
    if response is not None:
        errors = response.data
        message = errors.pop('detail', 'An error occurred') if 'detail' in errors else 'Validation errors'
        return error_response(message=message, errors=errors, status_code=response.status_code)

    # If no response is generated, return a generic error response
    return error_response(message="An unexpected error occurred", status_code=500)
