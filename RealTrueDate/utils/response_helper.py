# utils/response_helper.py

from rest_framework.response import Response
from rest_framework import status

def successResponse(data=None, message="Request was successful", code=status.HTTP_200_OK):
    """
    Helper function for creating a standardized success response.
    
    :param data: The data to include in the response (default: None)
    :param message: A message describing the success (default: "Request was successful")
    :param code: The HTTP status code (default: 200 OK)
    :return: A Response object with a standardized format
    """
    response_data = {
        "status": "success",
        "message": message,
        "data": data,
        "code": code
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
