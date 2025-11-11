from rest_framework import serializers
from .models import CustomUser, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        write_only=True,
        required=False,
    )
    password = serializers.CharField(write_only=True, required=True)  # NEW

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "role",
            "department",
            "department_id",
            "status",
            "last_active",
            "created_at",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)  # Hash if password is updated
            user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uid = serializers.IntegerField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
