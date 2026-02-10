from rest_framework import serializers
from .models import CustomUser


class AuthSerializer(serializers.ModelSerializer):
    Role = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "password", "Role")
        extra_kwargs = {
            "password": {"write_only": True},
            "Role": {"required": False},
        }

    # VALIDATE ROLE
    def validate_Role(self, value):
        normalized = str(value).strip().lower()

        if not normalized:
            return "user"

        if normalized in {"user", "manager"}:
            return normalized

        if normalized in {"superadmin", "super_admin", "super-admin"}:
            return "superAdmin"

        raise serializers.ValidationError(
            "You have to select a proper role (user / manager)."
        )

    # CREATE USER
    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.get("Role", "user")

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        user.Role = role
        user.save(update_fields=["Role"])

        return user



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "Role")