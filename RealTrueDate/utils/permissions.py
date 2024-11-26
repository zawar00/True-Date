from rest_framework.permissions import BasePermission

from rest_framework.permissions import BasePermission

class IsRegularUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'user'

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == 'admin'

class IsUserOrAdmin(BasePermission):
    """
    Allows access to users with either 'user' or 'admin' roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role in ['user', 'admin']
