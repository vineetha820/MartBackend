
from django.urls import include, path
from .views import productViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', productViewSet, basename='product')
urlpatterns = [
    path('', include(router.urls)),
]
   