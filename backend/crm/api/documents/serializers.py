from rest_framework import serializers

from crm.documents.models import Document, Product


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

    details = serializers.HyperlinkedIdentityField(view_name="api:document-detail")
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.select_related("company"))


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["product", "url"]
