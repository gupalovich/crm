from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from crm.companies.models import (
    Company,
    CompanyProductLink,
    CompanyType,
    Customer,
    Deal,
    Product,
    ProductImage,
    ProductTranslation,
)
from crm.documents.models import Document, PDFBlock

User = get_user_model()


class Command(BaseCommand):
    help = "Create predefined user groups with permissions"

    PERMISSIONS_MAP = {
        "Superuser": [
            "add_user",
            "change_user",
            "delete_user",
            # customer
            "add_customer",
            "change_customer",
            "delete_customer",
            # company
            "add_company",
            "change_company",
            "delete_company",
            # companytype
            "add_companytype",
            "change_companytype",
            "delete_companytype",
            # companyproductlink
            "add_companyproductlink",
            "change_companyproductlink",
            "delete_companyproductlink",
            # deal
            "add_deal",
            "change_deal",
            "delete_deal",
            # product
            "add_product",
            "change_product",
            "delete_product",
            # product image
            "add_productimage",
            "change_productimage",
            "delete_productimage",
            # product image
            "add_producttranslation",
            "change_producttranslation",
            "delete_producttranslation",
            # pdfblock
            "add_pdfblock",
            "change_pdfblock",
            "delete_pdfblock",
            # document
            "add_document",
            "change_document",
            "delete_document",
        ],
        "Admin": [
            "add_user",
            "change_user",
            "delete_user",
            # customer
            "add_customer",
            "change_customer",
            "delete_customer",
            # company
            "change_company",
            # companyproductlink
            "change_companyproductlink",
            # deal
            "add_deal",
            "change_deal",
            "delete_deal",
            # product
            "change_product",
            # product image
            "change_productimage",
            # pdfblock
            "add_pdfblock",
            "change_pdfblock",
            "delete_pdfblock",
            # document
            "add_document",
            "change_document",
            "delete_document",
        ],
        "Manager": [
            "add_customer",
            "change_customer",
            # deal
            "add_deal",
            "change_deal",
            # document
            "add_document",
        ],
    }

    PERMISSION_CONTENT_TYPE_MAP = {  # !!! order for company is important - can cause DoesNotExist error
        "user": ContentType.objects.get_for_model(User),
        "companyproductlink": ContentType.objects.get_for_model(CompanyProductLink),
        "companytype": ContentType.objects.get_for_model(CompanyType),
        "company": ContentType.objects.get_for_model(Company),
        "customer": ContentType.objects.get_for_model(Customer),
        "deal": ContentType.objects.get_for_model(Deal),
        "productimage": ContentType.objects.get_for_model(ProductImage),
        "producttranslation": ContentType.objects.get_for_model(ProductTranslation),
        "product": ContentType.objects.get_for_model(Product),
        "pdfblock": ContentType.objects.get_for_model(PDFBlock),
        "document": ContentType.objects.get_for_model(Document),
    }

    def handle(self, *args, **options):
        for role, permission_codenames in self.PERMISSIONS_MAP.items():
            permissions = []

            for codename in permission_codenames:
                content_type = self.get_content_type(codename)
                permission = Permission.objects.get(codename=codename, content_type=content_type)
                permissions.append(permission)

            group, _ = Group.objects.get_or_create(name=role)
            group.permissions.set(permissions)
        # self.stdout.write(self.style.SUCCESS("User groups created successfully."))

    def get_content_type(self, codename):
        for key, value in self.PERMISSION_CONTENT_TYPE_MAP.items():
            if key in codename:
                return value
        return None
