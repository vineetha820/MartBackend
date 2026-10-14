from django.contrib import admin

# Register your models here.
from .models import Product
from django.core.exceptions import PermissionDenied
from .permissions import can_manage_products
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_by', 'created_at')
    readonly_fields = ('created_by',)

    def has_add_permission(self, request):
        return can_manage_products(request.user)

    def has_change_permission(self, request, obj=None):
        return can_manage_products(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_manage_products(request.user)

    def save_model(self, request, obj, form, change):
        if not can_manage_products(request.user):
            raise PermissionDenied
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
