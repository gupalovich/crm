from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from crm.companies.models import Customer, Deal, Product

from ..permissions import validate_customer_company_membership, validate_user_company_membership


class DealValidationMixin:
    def validate_manager(self, value):
        manager = self.initial_data.get("manager")
        if value is None and manager is None:
            raise serializers.ValidationError(_("Это поле не может быть пустым."))
        return value

    def validate_customer(self, value):
        customer = self.initial_data.get("customer")
        if value is None and customer is None:
            raise serializers.ValidationError(_("Это поле не может быть пустым."))
        return value

    def validate_product(self, value):
        request = self.context.get("request")
        validate_user_company_membership(request, value.company)
        return value


class DealListSerializer(DealValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ["manager", "product", "customer", "company"]

    class CustomerSerializer(serializers.ModelSerializer):
        class Meta:
            model = Customer
            fields = ["first_name", "middle_name", "last_name", "email", "phone_number"]

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.select_related("company"))
    manager = serializers.ReadOnlyField(source="manager.username")
    customer = CustomerSerializer()
    company = serializers.ReadOnlyField(source="product.company.id")

    def create(self, validated_data):
        validated_data["manager"] = self.context["request"].user
        customer_data = validated_data.pop("customer")
        product = validated_data.pop("product")
        customer = Customer.objects.create(company=product.company, **customer_data)
        deal = Deal.objects.create(customer=customer, product=product, **validated_data)
        return deal


class DealDetailSerializer(DealValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ["id", "details", "manager", "customer", "product", "company", "updated_at", "created_at"]

    details = serializers.HyperlinkedIdentityField(view_name="api:deal-detail")
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.select_related("company"))
    manager = serializers.ReadOnlyField(source="manager.username", default=None)
    company = serializers.ReadOnlyField(source="product.company.id")

    def validate_customer(self, value):
        super().validate_customer(value)
        validate_customer_company_membership(self.context["request"], value)
        return value

    def update(self, instance, validated_data):
        validated_data["manager"] = self.context["request"].user
        return super().update(instance, validated_data)
