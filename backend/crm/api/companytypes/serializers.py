from rest_framework import serializers

from crm.companies.models import CompanyType


class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = [
            "id",
            "details",
            "name",
            "updated_at",
            "created_at",
        ]

    details = serializers.HyperlinkedIdentityField(view_name="api:companytype-detail")

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().update(instance, validated_data)
