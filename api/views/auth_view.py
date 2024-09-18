from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status, serializers
from api.utils.responses import success_response, error_response
from api.utils.validators import verify_required_params
from api.services.auth_service import register_user  # Import the new service
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers.auth_serializer import EmailTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]  # No authentication required for registration

    def post(self, request):
        # List of required fields for registration
        required_params = ['name', 'email', 'password', 'gender', 'bio', 'looking_for', 'zipcode', 'birthday', 'distance']

        try:
            # Verify required parameters
            verify_required_params(request.data, required_params)
            
            # Call the service to handle the registration logic
            user = register_user(request.data)

            # Return success response
            return success_response(message="Registration successful.", status_code=201)

        except ValidationError as e:
            return error_response(message=str(e), status_code=400)

        except Exception as e:
            return error_response(message="Something went wrong.", errors=str(e), status_code=500)


class EmailLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmailTokenObtainPairSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            token_data = serializer.validated_data

            return success_response(data=token_data, message="Login successful", status_code=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            return error_response(message="Validation errors", errors=e.detail, status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return error_response(message="An unexpected error occurred", errors=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)