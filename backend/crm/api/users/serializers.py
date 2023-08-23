from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from crm.companies.models import Company
from crm.companies.services import user_create

from ..permissions import validate_user_company_membership

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["details", "username", "role"]

    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        return self.context.get("request").build_absolute_uri(
            reverse("api:user-detail", kwargs={"username": obj.username})
        )


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role", "is_active"]


class BaseUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "company",
        ]

    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)

    def validate_company(self, value):
        if not value:
            raise ValidationError("ID Компании не задан")
        validate_user_company_membership(self.context.get("request"), value)
        return value

    def validate(self, data):
        if "company" not in data:
            raise serializers.ValidationError("ID Компании не задан")
        return data

    def create(self, validated_data):
        new_user = user_create(user_data=validated_data)
        new_user.password = validated_data["password"]
        return new_user


class UserCreateForSuperUserSerializer(BaseUserCreateSerializer):
    role = serializers.ChoiceField(choices=[User.Roles.ADMIN, User.Roles.MANAGER])


class UserCreateForAdminSerializer(BaseUserCreateSerializer):
    role = serializers.ChoiceField(choices=[User.Roles.MANAGER], initial=User.Roles.MANAGER)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "is_active",
        ]
        read_only_fields = ["role"]
