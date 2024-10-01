from rest_framework.permissions import BasePermission

class IsSuperAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SuperAdmin'
    
# Permission for Admin users only
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()

# Permission for Regular Users (non-admin)
class IsRegularUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_regular_user()
