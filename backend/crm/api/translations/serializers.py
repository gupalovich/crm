from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from crm.companies.models import ProductTranslation


class ProductTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTranslation
        fields = "__all__"

    key = serializers.CharField(validators=[UniqueValidator(queryset=ProductTranslation.objects.all())])
    details = serializers.HyperlinkedIdentityField(view_name="api:translation-detail", lookup_field="pk")


class ProductTranslationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTranslation
        fields = "__all__"

    key = serializers.CharField(validators=[UniqueValidator(queryset=ProductTranslation.objects.all())])
