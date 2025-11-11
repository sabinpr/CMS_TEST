from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


ROLE_CHOICES = (
    ("admin", "Admin"),
    ("procurement_officer", "Procurement Officer"),
    ("legal_reviewer", "Legal Reviewer"),
    ("department_head", "Department Head"),
    ("signatory", "Signatory"),
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    department = models.ForeignKey(
        "Department", on_delete=models.SET_NULL, null=True, blank=True
    )
    full_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "role"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name
