import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.query import QuerySet
from requests.exceptions import ConnectionError, HTTPError, InvalidJSONError, JSONDecodeError

from crm.documents.models import Document

from .models import Company, CompanyMember, CompanyProductLink, Product, ProductImage, ProductTranslation

User = get_user_model()


def document_create(*, document_data: dict) -> Document:
    """
    Create document instance with a file attached.
    Example:
        document_data = {
            "pdf_file": {"content": pdf_file, "name": "test_file_name.pdf"},
            "name": "test document",
            "product": product,
        }
    """
    pdf_file_object = ContentFile(**document_data.pop("pdf_file"))
    document = Document(**document_data, url=pdf_file_object)
    document.full_clean()
    document.save()
    return document


@transaction.atomic
def user_create(*, user_data: dict) -> User:
    """Atomic transaction. Create user and associated company membership"""
    company = user_data.pop("company", None)
    user = User.objects.create_user(**user_data)
    CompanyMember.objects.create(user=user, company=company)
    return user


@transaction.atomic
def company_create(*, user: User, company_data: dict) -> Company:
    """Atomic transaction. Create company and associated company membership"""
    company = Company.objects.create(**company_data)
    CompanyMember.objects.create(user=user, company=company)
    return company


def company_render_business_card(*, user: User, bc: str) -> str:
    variables = {
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "email": user.email,
    }

    rendered_card = bc
    for variable, value in variables.items():
        rendered_card = rendered_card.replace(f"{{{variable}}}", value)

    return rendered_card


def product_translation_filter_by_keys(*, keys: list[str]) -> QuerySet[ProductTranslation]:
    return ProductTranslation.objects.filter(key__in=keys)


def translate_dict_keys(
    *, data: dict[str, str], translations: QuerySet[ProductTranslation]
) -> dict[str, str]:
    for trans in translations:
        old_key = trans.key
        new_key = trans.value
        if old_key in data:
            data[new_key] = data.pop(old_key)
    return data


def product_translate(*, product: Product, hard_save=False) -> Product:
    translations = product_translation_filter_by_keys(keys=product.data.keys())
    product.data = translate_dict_keys(data=product.data, translations=translations)
    product.full_clean()
    if hard_save:
        product.save()
    return product


def product_image_create(*, product: Product, url: str, hard_save=False) -> ProductImage:
    product_image = ProductImage(product=product, url=url)
    product_image.full_clean()
    if hard_save:
        product_image.save()
    return product_image


def product_images_replace(*, product: Product, images: list[str]) -> QuerySet[ProductImage]:
    # Get all existing image URLs for the product
    current_images = set(product.images.values_list("url", flat=True))
    # Find images to be removed (existing images not in the new list)
    images_to_remove = current_images - set(images)
    if images_to_remove:
        product.images.filter(url__in=images_to_remove).delete()
    # Find new images to be created (new images not in the current list)
    images_to_create = set(images) - current_images
    if images_to_create:
        new_images = [product_image_create(product=product, url=url) for url in images_to_create]
        ProductImage.objects.bulk_create(new_images)
    return product.images.all()


def product_create_update(*, product_data: dict) -> Product:
    """Create-update product based on [pid] field if product.is_active"""
    try:
        product = Product.objects.get(company=product_data["company"], pid=product_data["pid"])

        if not product.is_active:
            return product

        for key, value in product_data.items():
            setattr(product, key, value)
    except Product.DoesNotExist:
        product = Product(**product_data)

    product.full_clean()
    product.save()
    return product


class ProductIntegrationService:
    def __init__(self, company_product_link: CompanyProductLink):
        self.company_product_link = company_product_link
        self.raw_products = []
        self.products = []

    def _invalidate(self):
        self.company_product_link.is_valid = False
        self.company_product_link.save(update_fields=["is_valid"])

    def fetch_products(self, max_attempts=3):
        attempts = 0
        while attempts < max_attempts:
            try:
                response = requests.get(self.company_product_link.url, timeout=3)
                response.raise_for_status()  # Raise an exception for non-200 status codes
                self.raw_products = response.json()
                break
            except (JSONDecodeError, InvalidJSONError, HTTPError, ConnectionError):
                attempts += 1
                if attempts >= max_attempts:
                    self._invalidate()
            except Exception as e:
                raise e

    def build_products(self):
        self.products = [
            {
                "company": self.company_product_link.company,
                "pid": product_data["id"],
                "name": "default",
                "price": int(product_data.get("price", 0)),
                "price_special": int(product_data.get("special", 0)),
                "url": product_data.get("url", ""),
                "data": product_data.get("data", {}),
                "data_options": product_data.get("data_options", {}),
                "images": product_data.get("images", []),
            }
            for product_data in self.raw_products
        ]

    def save_products(self):
        for product_data in self.products:
            images = product_data.pop("images", [])
            product = product_create_update(product_data=product_data)
            product_images_replace(product=product, images=images)
