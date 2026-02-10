from rest_framework import serializers
from .models import NotesModel


class NotesSerializer(serializers.ModelSerializer):
    note_type = serializers.CharField()

    class Meta:
        model = NotesModel
        fields = (
            "id",
            "note_type",
            "description",
            "viewDetails",
            "isActiveReq",
            "validateDeleteManager",
            "validateDeleteSuperAdmin",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "isActiveReq",
            "validateDeleteManager",
            "validateDeleteSuperAdmin",
            "created_at",
            "updated_at",
        )

    
    def validate_note_type(self, value):
        normalized = str(value).strip().lower()
        if normalized not in {"personal", "work"}:
            raise serializers.ValidationError(
                "You have to select a proper note type (personal or work)."
            )
        return normalized

    
    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        validated_data["user"] = request.user
        return super().create(validated_data)
