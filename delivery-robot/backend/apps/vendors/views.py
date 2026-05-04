from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import User

from .models import Vendor
from .permissions import VendorReadOrStaffWrite
from .serializers import VendorSerializer


class VendorViewSet(ModelViewSet):
    serializer_class = VendorSerializer
    permission_classes = [VendorReadOrStaffWrite]

    def get_queryset(self):
        qs = Vendor.objects.all().order_by("name")
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.is_superuser:
            return qs
        role = getattr(user, "role", User.Role.STUDENT)
        if role == User.Role.VENDOR:
            return qs.filter(manager=user)
        if role in (User.Role.ADMIN, User.Role.SUPERADMIN):
            return qs
        if role == User.Role.STUDENT:
            return qs
        return qs.none()
