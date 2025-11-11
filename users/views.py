from rest_framework import generics, filters, permissions, status, viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser, Department
from .serializers import (
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
    DepartmentSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAdmin

User = get_user_model()


# -----------------------------
# Custom JWT Login with last_active
# -----------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Update last_active immediately after successful login
        self.user.last_active = timezone.now()
        self.user.save(update_fields=["last_active"])
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# -----------------------------
# User CRUD
# -----------------------------
class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["full_name", "email"]
    filterset_fields = ["role", "status"]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"
    permission_classes = [IsAdmin]


# -----------------------------
# Password Management
# -----------------------------
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully"})


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "If this email exists, a reset link will be sent."},
                status=status.HTTP_200_OK,
            )

        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{user.pk}/{token}/"

        send_mail(
            "Reset your password",
            f"Click here to reset your password: {reset_url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response(
            {"detail": "If this email exists, a reset link will be sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password reset successfully."}, status=status.HTTP_200_OK
        )


# -----------------------------
# Department List
# -----------------------------
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
