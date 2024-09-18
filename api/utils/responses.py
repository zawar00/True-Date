from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Returns a standardized success response
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
        "status_code": status_code,
    }
    return Response(response, status=status_code)

def error_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standardized error response
    """
    response = {
        "success": False,
        "message": message,
        "errors": errors,
        "status_code": status_code,
    }
    return Response(response, status=status_code)