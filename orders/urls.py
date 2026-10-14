from django.urls import path

from .views import OrdercreateView

urlpatterns = [
    path('', OrdercreateView.as_view(), name='order-list-create'),
]
