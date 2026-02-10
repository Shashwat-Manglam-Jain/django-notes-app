from django.contrib import admin
from .models import NotesModel


@admin.register(NotesModel)
class NotesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "note_type",
        "isActiveReq",
        "validateDeleteManager",
        "validateDeleteSuperAdmin",
        "created_at",
    )

    list_filter = (
        "note_type",
        "isActiveReq",
        "validateDeleteManager",
        "validateDeleteSuperAdmin",
    )

    search_fields = ("description",)

    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)
