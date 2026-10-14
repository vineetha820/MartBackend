from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, viewsets

from .models import Product
from .permissions import ProductAdminPermission
from .productFilter import ProductFilter
from .serializers.ProductSerializer import ProductSerializer


class ProductPagination(pagination.PageNumberPagination):
    page_size = 2


class productViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('seller', 'created_by').all()
    serializer_class = ProductSerializer
    permission_classes = [ProductAdminPermission]
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = ProductPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
