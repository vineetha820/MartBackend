from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


def can_manage_products(user):
    return bool(
        user and user.is_authenticated and user.is_active and user.is_staff
        and user.pk == settings.PRODUCT_ADMIN_USER_ID
    )


class ProductAdminPermission(BasePermission):
    """Anyone can browse; only the designated mart admin can change products."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or can_manage_products(request.user)

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or can_manage_products(request.user)
