from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import User

from .models import MenuItem
from .permissions import MenuReadOrVendorStaffWrite
from .serializers import MenuItemSerializer


class MenuItemViewSet(ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [MenuReadOrVendorStaffWrite]

    def get_queryset(self):
        qs = MenuItem.objects.select_related("vendor").all().order_by("name")
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.is_superuser:
            return qs
        role = getattr(user, "role", User.Role.STUDENT)
        if role == User.Role.VENDOR:
            return qs.filter(vendor__manager=user)
        if role in (User.Role.ADMIN, User.Role.SUPERADMIN):
            return qs
        if role == User.Role.STUDENT:
            return qs
        return qs.none()
