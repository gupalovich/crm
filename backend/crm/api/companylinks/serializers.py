from rest_framework import serializers

from crm.companies.models import CompanyProductLink

from ..permissions import validate_user_company_membership


class CompanyProductLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProductLink
        fields = "__all__"
        read_only_fields = ["is_valid"]

    details = serializers.HyperlinkedIdentityField(view_name="api:companyproductlink-detail")

    def validate_company(self, value):
        request = self.context.get("request")
        validate_user_company_membership(request, value)
        return value


class ParseSerializer(serializers.Serializer):
    pass
