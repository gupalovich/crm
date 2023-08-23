from rest_framework import serializers

from crm.companies.models import Customer

from ..permissions import validate_user_company_membership


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "details",
            "company",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "updated_at",
            "created_at",
        ]

    details = serializers.HyperlinkedIdentityField(view_name="api:customer-detail")

    def validate_company(self, value):
        request = self.context.get("request")
        validate_user_company_membership(request, value)
        return value
