from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import User


class VendorReadOrStaffWrite(BasePermission):
    """List/retrieve for any authenticated user (kiosk). Mutations for vendor/staff only."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if getattr(request.user, "is_superuser", False):
            return True
        role = getattr(request.user, "role", User.Role.STUDENT)
        return role in (User.Role.VENDOR, User.Role.ADMIN, User.Role.SUPERADMIN)
