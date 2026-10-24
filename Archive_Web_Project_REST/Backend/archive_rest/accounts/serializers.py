from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .constants import DEPARTMENT, DESIGNATION
from .models import Profile


class UserSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    designation = serializers.CharField(source="profile.designation", default=None, read_only=True)
    dept = serializers.CharField(source="profile.dept", default=None, read_only=True)
    image = serializers.ImageField(source="profile.image", default=None, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "designation", "dept", "image"]

    def get_full_name(self, user):
        return user.get_full_name() or user.username


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "designation",
            "dept",
            "contact_number",
            "address",
            "image",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    designation = serializers.ChoiceField(choices=DESIGNATION)
    dept = serializers.ChoiceField(choices=DEPARTMENT, required=False, allow_null=True)
    contact_number = serializers.CharField(max_length=11, required=False, allow_blank=True)
    address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "designation",
            "dept",
            "contact_number",
            "address",
            "image",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        validate_password(data["password"])
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        profile_data = {
            "designation": validated_data.pop("designation"),
            "dept": validated_data.pop("dept", None),
            "contact_number": validated_data.pop("contact_number", None),
            "address": validated_data.pop("address", None),
            "image": validated_data.pop("image", None) or "",
        }
        user = User.objects.create_user(**validated_data, is_active=False)
        Profile.objects.create(user=user, **profile_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})
