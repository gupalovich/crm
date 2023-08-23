from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from crm.companies.models import Company, CompanyProductLink, CompanyType, Customer, Product
from crm.companies.selectors import company_type_list, user_get_company_ids

User = get_user_model()


class IsSuperPermission(BasePermission):
    """Allow user access if user role is superuser"""

    def has_permission(self, request, view):
        user = request.user
        return user.is_active and user.is_crm_superuser


class IsAdminPermission(BasePermission):
    """Allow user access if user role is admin"""

    def has_permission(self, request, view):
        user = request.user
        return user.is_active and user.is_crm_admin


class IsManagerPermission(BasePermission):
    """Allow user access if user role is manager"""

    def has_permission(self, request, view):
        user = request.user
        return user.is_active and user.is_crm_manager


class CanModifyUserPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_crm_admin:
            # Admin can't delete self
            if obj == user and request.method in ["DELETE"]:
                return False
            # Admin can't modify/delete/update Superuser
            if obj.is_crm_superuser:
                return False
        return True


def validate_user_company_membership(request: Request, company: Company | None) -> None:
    """Check if user belongs to company"""
    user_companies = user_get_company_ids(request.user)
    if company and company.id not in user_companies:
        raise PermissionDenied()


def validate_user_company_type(request: Request, company_type: CompanyType) -> None:
    """Check if user belongs to company_type"""
    user_company_types = company_type_list(request.user)
    if company_type not in user_company_types:
        raise PermissionDenied()


def validate_customer_company_membership(request: Request, customer: Customer) -> None:
    """Check if customer belongs to company"""
    user_companies = user_get_company_ids(request.user)
    if customer and customer.company.id not in user_companies:
        raise PermissionDenied()


def validate_product(product: Product) -> None:
    """Check if product.is_active"""
    if not product.is_active:
        raise PermissionDenied({"is_active": f"Товар: [{product.name}] неактивен"})


def validate_company_product_link(company_product_link: CompanyProductLink) -> None:
    """Validate that company_product_link.is_valid"""
    if not company_product_link.is_valid:
        raise ValidationError({"is_valid": "Неверная ссылка"})
