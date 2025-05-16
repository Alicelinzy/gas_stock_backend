from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.profile.role == 'admin'
        )

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.profile.role in ['admin', 'manager']
        )

class IsDeliveryStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.profile.role in ['admin', 'manager', 'delivery']
        )

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.profile.role == 'customer'
        )