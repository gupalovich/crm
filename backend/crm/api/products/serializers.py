from rest_framework import serializers

from crm.companies.models import Product

from ..permissions import validate_user_company_membership


class ImagesField(serializers.RelatedField):
    def to_representation(self, value):
        return value.url


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["pid", "images"]

    details = serializers.HyperlinkedIdentityField(view_name="api:product-detail")
    images = ImagesField(many=True, read_only=True)

    def validate_company(self, value):
        request = self.context.get("request")
        validate_user_company_membership(request, value)
        return value


class OfferSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    pdf_blocks = serializers.ListField(child=serializers.IntegerField(), required=False)
