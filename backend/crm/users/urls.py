from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .auth.views import CustomTokenObtainPairView, LogoutView

app_name = "users"

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/logout/", LogoutView.as_view(), name="token_blacklist"),
]
