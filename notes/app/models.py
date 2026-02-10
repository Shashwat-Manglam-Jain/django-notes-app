from django.db import models
from accounts.models import CustomUser

class NotesModel(models.Model):
    Choice = (
        ("personal", "Personal"),
        ("work", "Work"),
    )

    note_type = models.CharField(max_length=10, choices=Choice)
    description = models.TextField()

    validateDeleteManager = models.BooleanField(default=False)
    validateDeleteSuperAdmin = models.BooleanField(default=False)
    isActiveReq = models.BooleanField(default=False)

    viewDetails = models.JSONField(default=list, blank=True)

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notes"   
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.note_type}"
