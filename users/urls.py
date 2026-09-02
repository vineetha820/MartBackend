
from django.urls import include, path
from .views import LoginView, RegistrationView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
   path('register/', RegistrationView.as_view(), name='register'),
   path('login/', LoginView.as_view(), name='login'),
   path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
]   
