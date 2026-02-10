from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Display in list view
    list_display = ("email", "Role", "is_staff", "is_active")
    list_filter = ("Role", "is_staff", "is_active")

    # Field layout in edit page
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {
            "fields": (
                "Role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields when creating a user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "Role",
                "is_staff",
                "is_active",
            ),
        }),
    )

    search_fields = ("email",)
    ordering = ("email",)

    # Remove username completely
    filter_horizontal = ("groups", "user_permissions")
