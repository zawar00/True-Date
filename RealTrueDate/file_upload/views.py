from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from utils.uploadFiles import upload_file_to_s3
from rest_framework.permissions import AllowAny
from utils.response_helper import successResponse, errorResponse  # Import the response helpers



class FileUploadAPIView(APIView):
    permission_classes = [AllowAny]

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return errorResponse(message="No file provided", details={}, code=status.HTTP_400_BAD_REQUEST)

        try:
            # Call the helper function
            file_url = upload_file_to_s3(file)
            return successResponse(data={ "file_url": file_url}, message="File uploaded successfully.", code=status.HTTP_201_CREATED)
        except Exception as e:
            return errorResponse(message="error", details=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)
