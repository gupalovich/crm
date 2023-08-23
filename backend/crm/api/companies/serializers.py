from rest_framework import serializers

from crm.companies.models import Company
from crm.companies.services import company_create, company_render_business_card
from crm.core.validators import validate_image_size

from ..permissions import validate_user_company_type


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

    details = serializers.HyperlinkedIdentityField(view_name="api:company-detail")
    price_template = serializers.ChoiceField(choices=Company.PriceListTemplates, read_only=True)
    offer_template = serializers.ChoiceField(choices=Company.CommercialOfferTemplates, read_only=True)

    def validate_company_type(self, value):
        validate_user_company_type(self.context.get("request"), value)
        return value

    def validate_logo_image(self, value):
        validate_image_size(value, max_size_kb=2000)
        return value

    def validate_signature_image(self, value):
        validate_image_size(value, max_size_kb=2000)
        return value

    def validate_name(self, value):
        if self.instance and self.instance.name == value:
            return value
        if Company.objects.filter(name=value).exists():
            raise serializers.ValidationError("Компания с таким именем уже существует")
        return value

    def update_business_card(self, request, validated_data):
        validated_data["business_card"] = company_render_business_card(
            user=request.user, bc=validated_data["business_card"]
        )
        return validated_data

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data = self.update_business_card(request, validated_data)
        company = company_create(user=request.user, company_data=validated_data)
        return company

    def update(self, instance, validated_data):
        validated_data = self.update_business_card(self.context.get("request"), validated_data)
        return super().update(instance, validated_data)
