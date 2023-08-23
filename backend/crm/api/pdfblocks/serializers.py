from rest_framework import serializers

from crm.core.validators import validate_image_size
from crm.documents.models import PDFBlock

from ..permissions import validate_user_company_membership


class PDFBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFBlock
        fields = "__all__"

    details = serializers.HyperlinkedIdentityField(view_name="api:pdfblock-detail", lookup_field="pk")

    def validate_image(self, value):
        validate_image_size(value, max_size_kb=2000)
        return value

    def validate_company(self, value):
        request = self.context.get("request")
        validate_user_company_membership(request, value)
        return value
