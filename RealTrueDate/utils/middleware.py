# utils/middleware.py

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based access for both regular users and admins.
    Allows configurable access restrictions per role and shared paths.
    """
    def process_request(self, request):
        # Skip if the user is not authenticated
        if not request.user.is_authenticated:
            return None  # Skip middleware for unauthenticated users

        # Define path access based on user role
        user_only_paths = [ '/profiles/']  # Paths for regular users
        admin_only_paths = ['/profile_review/', '/admin-dashboard/']  # Paths for admin users
        shared_paths = ['/shared-resource/', '/common-endpoint/']  # Accessible by both roles

        # Check if the path is restricted to regular users
        if any(request.path.startswith(path) for path in user_only_paths):
            if request.user.user_role != 'user':
                return JsonResponse({"message": "Access restricted to regular users only."}, status=403)

        # Check if the path is restricted to admin users
        elif any(request.path.startswith(path) for path in admin_only_paths):
            if request.user.user_role != 'admin':
                return JsonResponse({"message": "Access restricted to admin users only."}, status=403)

        # Check for shared paths accessible by both roles
        elif any(request.path.startswith(path) for path in shared_paths):
            if request.user.user_role not in ['user', 'admin']:
                return JsonResponse({"message": "Access restricted to authenticated users only."}, status=403)

        # If the path is not specified in any restricted lists, allow access by default
        return None
