from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserDetailView,
    UserListCreateView,
    ChangePasswordView,
    ForgotPasswordView,
    PasswordResetView,
    MyTokenObtainPairView,
    DepartmentViewSet,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")

urlpatterns = [
    # User URLs
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:id>/", UserDetailView.as_view(), name="user-detail"),
    # JWT URLs
    path("auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # Password
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", PasswordResetView.as_view(), name="reset-password"),
    # Include router URLs
    path("", include(router.urls)),
]
