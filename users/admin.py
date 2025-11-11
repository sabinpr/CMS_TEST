from django.contrib import admin
from .models import CustomUser, Department
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "full_name", "role", "department", "status", "is_staff")
    list_filter = ("role", "status", "is_staff", "is_superuser", "department")

    # Make non-editable fields readonly
    readonly_fields = ("created_at", "last_active", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", "department", "role", "status")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "last_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "role",
                    "department",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email", "full_name")
    ordering = ("email",)


admin.site.register(Department)
