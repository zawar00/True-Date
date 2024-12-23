# utils/response_helper.py

from rest_framework.response import Response
from rest_framework import status

from rest_framework.response import Response

def successResponse(data=None, message="Request was successful", code=200, pagination=None):
    """
    Helper function for creating a standardized success response.
    
    :param data: The data to include in the response (default: None)
    :param message: A message describing the success (default: "Request was successful")
    :param code: The HTTP status code (default: 200 OK)
    :param pagination: A dictionary containing pagination metadata (default: None)
    :return: A Response object with a standardized format
    """
    response_data = {
        "status": "success",
        "message": message,
        "data": data,
        "code": code
    }
    
    # Include pagination metadata if available
    if pagination:
        response_data["pagination"] = {
            "count": pagination.get('count', 0),  # Total number of records
            "current_page_count": pagination.get('current_page_count', len(data) if data else 0),  # Records on the current page
            "next": pagination.get('next', None),  # URL for the next page
            "previous": pagination.get('previous', None)  # URL for the previous page
        }

    return Response(response_data, status=code)



def errorResponse(message="An error occurred", details=None, code=status.HTTP_400_BAD_REQUEST):
    """
    Helper function for creating a standardized error response.
    
    :param message: A message describing the error (default: "An error occurred")
    :param details: Detailed information about the error (default: None)
    :param code: The HTTP status code (default: 400 Bad Request)
    :return: A Response object with a standardized format
    """
    response_data = {
        "status": "error",
        "message": message,
        "details": details,
        "code": code
    }
    return Response(response_data, status=code)
