from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.query import QuerySet

from crm.documents.models import Document, PDFBlock

from .models import Company, CompanyProductLink, CompanyType, Customer, Deal, Product

User = get_user_model()


def user_get_company_ids(user: User) -> QuerySet[int]:
    """Return a queryset of company IDs that the user is a member of."""
    return user.memberships.values_list("company_id", flat=True)


def user_list(user: User) -> QuerySet[User]:
    """Return a queryset of users who are members of the same companies as the user."""
    company_ids = user_get_company_ids(user)
    users = User.objects.filter(memberships__company_id__in=company_ids).distinct()
    return users


def pdf_block_list(user: User) -> QuerySet[PDFBlock]:
    """Return a queryset of PDF blocks associated with the companies the user is a member of."""
    company_ids = user_get_company_ids(user)
    pdf_blocks = PDFBlock.objects.filter(company__in=company_ids)
    return pdf_blocks


def pdf_block_list_filter_by_ids(user: User, ids: list[int]):
    """Return a queryset of filtered PDF blocks associated with the companies the user is a member of."""
    pdf_blocks = pdf_block_list(user).filter(pk__in=ids).select_related("company")
    return pdf_blocks


def document_list(user: User) -> QuerySet[Document]:
    """Return a queryset of documents associated with companies that the user is a member of."""
    company_ids = user_get_company_ids(user)
    documents = Document.objects.filter(product__company__in=company_ids)
    return documents


def company_list(user: User) -> QuerySet[Company]:
    """Return a queryset of companies that the user is a member of."""
    company_ids = user_get_company_ids(user)
    companies = Company.objects.filter(id__in=company_ids)
    return companies


def company_type_list(user: User) -> QuerySet[CompanyType]:
    """Return a queryset of company types associated with the user or companies."""
    company_ids = user_get_company_ids(user)
    company_types = CompanyType.objects.filter(Q(user=user) | Q(company__id__in=company_ids))
    return company_types


def company_product_link_list(user: User) -> QuerySet[CompanyProductLink]:
    """Return a queryset of links for product parsing for companies that the user is a member of."""
    company_ids = user_get_company_ids(user)
    company_product_links = CompanyProductLink.objects.filter(company__in=company_ids)
    return company_product_links


def customer_list(user: User) -> QuerySet[Customer]:
    """Return a queryset of customers associated with companies that the user is a member of."""
    company_ids = user_get_company_ids(user)
    customers = Customer.objects.filter(company__in=company_ids)
    return customers


def product_list(user: User) -> QuerySet[Product]:
    """Return a queryset of products associated with companies that the user is a member of."""
    company_ids = user_get_company_ids(user)
    products = Product.objects.filter(company__in=company_ids).prefetch_related("images")
    return products


def deal_list(user: User) -> QuerySet[Company]:
    """Return a queryset of deals associated with company products that the user is a member of."""
    company_ids = user_get_company_ids(user)
    deals = Deal.objects.filter(product__company__in=company_ids).select_related(
        "manager", "product__company"
    )
    return deals
