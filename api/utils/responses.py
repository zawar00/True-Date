from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional, Union, List

def success_response(
    data: Optional[Any] = None, 
    message: Optional[str] = "Success", 
    status_code: int = status.HTTP_200_OK
) -> Response:
    response_content: Dict[str, Union[bool, str, Any]] = {
        "success": True,
        "message": message,
        "data": data,
        "status_code": status_code,
    }
    
    return Response(response_content, status=status_code)

def error_response(
    message: Optional[str] = "An error occurred", 
    errors: Optional[List[Dict[str, Any]]] = None, 
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    response_content: Dict[str, Union[bool, str, List[Dict[str, Any]]]] = {
        "success": False,
        "message": message,
        "errors": errors or [],
        "status_code": status_code,
    }
    
    return Response(response_content, status=status_code)
