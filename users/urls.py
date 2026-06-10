from django.urls import path
from rest_framework.permissions import AllowAny
from users.apps import UsersConfig
from users.views import (
    ProfilesListAPIView,
    ProfileViewingAPIView,
    ProfileCreateAPIView,
    ProfileUpdateAPIView,
    ProfileDestroyAPIView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


app_name = UsersConfig.name

urlpatterns = [
    path("", ProfilesListAPIView.as_view(), name="profiles"),
    path("profile/<int:pk>/", ProfileViewingAPIView.as_view(), name="profile"),
    path("registration/", ProfileCreateAPIView.as_view(), name="registration"),
    path("profile/<int:pk>/update/", ProfileUpdateAPIView.as_view(), name="update_profile"),
    path("profile/<int:pk>/delete/", ProfileDestroyAPIView.as_view(), name="delete_profile"),
    path("authorization/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="authorization"),
    path("refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
]
