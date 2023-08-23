from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker

from crm.core.models import BaseModel, BaseUser

User = get_user_model()


class CompanyType(BaseModel):
    class Meta:
        verbose_name_plural = "Company Types"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="company_types", verbose_name=_("Пользователь")
    )
    # fields
    name = models.CharField(_("Название"), max_length=50)

    def __str__(self):
        return str(self.name)


class Company(BaseModel):
    class Meta:
        verbose_name_plural = _("Companies")

    class PriceListTemplates(models.TextChoices):
        TEMPLATE_1 = "price-lists/1.html", "Шаблон прайс-листа #1"

    class CommercialOfferTemplates(models.TextChoices):
        TEMPLATE_1 = "commercial-offers/1.html", "Шаблон коммерческого предложения #1"

    company_type = models.ForeignKey(
        CompanyType, on_delete=models.SET_NULL, null=True, verbose_name=_("Тип Компании")
    )
    # fields
    name = models.CharField(_("Название Компании"), max_length=150)
    executive_name = models.CharField(_("ФИО исполняющего лица"), max_length=150)
    executive_position = models.CharField(_("Должность исполняющего лица"), max_length=150)
    address = models.CharField(_("Адрес"), max_length=150)
    logo_image = models.ImageField(_("Логотип"), upload_to="company-logos/")
    signature_image = models.ImageField(_("Подпись"), upload_to="company-signatures/", blank=True)
    business_card = RichTextField(_("Визитка"), blank=True)
    price_template = models.CharField(
        _("Шаблон для прайс-листа"),
        max_length=150,
        choices=PriceListTemplates.choices,
        default=PriceListTemplates.TEMPLATE_1,
    )
    offer_template = models.CharField(
        _("Шаблон для коммерческого предложения"),
        max_length=150,
        choices=CommercialOfferTemplates.choices,
        default=CommercialOfferTemplates.TEMPLATE_1,
    )

    def __str__(self):
        return str(self.name)


class CompanyMember(BaseModel):
    class Meta:
        verbose_name_plural = "Company Members"
        unique_together = ("user", "company")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="memberships", verbose_name=_("Пользователь")
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="members", verbose_name=_("Компания")
    )

    def __str__(self):
        return f"{self.user} - {self.company}"


class CompanyProductLink(BaseModel):
    class Meta:
        verbose_name_plural = "Company Product Links"
        unique_together = ("company", "url")

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="links", verbose_name=_("Компания")
    )
    # fields
    name = models.CharField(_("Название"), max_length=150)
    url = models.URLField(_("Ссылка"))
    is_valid = models.BooleanField(_("Функционирующий"), default=True)
    # tracker
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.company} - {self.name} - {self.url}"

    def save(self, *args, **kwargs):
        if self.url != self.tracker.previous("url"):
            self.is_valid = True
        super().save(*args, **kwargs)


class Customer(BaseUser):
    class Meta:
        verbose_name_plural = "Customers"

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="customers", verbose_name=_("Компания")
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Product(BaseModel):
    class Meta:
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=["pid"]),
        ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="products", verbose_name=_("Компания")
    )
    # fields
    pid = models.CharField(_("Product ID"), max_length=50)
    name = models.CharField(_("Название"), max_length=150)
    data = models.JSONField(_("Параметры"))
    data_options = models.JSONField(_("Дополнительные параметры"), null=True, blank=True)
    price = models.PositiveIntegerField(_("Цена розничная"), null=True, blank=True)
    price_special = models.PositiveIntegerField(_("Цена специальная"), null=True, blank=True)
    url = models.URLField(_("Ссылка"))
    is_active = models.BooleanField(_("Активен"), default=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class ProductImage(BaseModel):
    class Meta:
        verbose_name_plural = "Product Images"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("Товар")
    )
    # fields
    url = models.URLField(_("Ссылка"))

    def __str__(self):
        return f"{self.url}"


class ProductTranslation(BaseModel):
    class Meta:
        verbose_name_plural = "Product Translations"

    key = models.CharField(_("Ключ"), max_length=70)
    value = models.CharField(_("Значение"), max_length=70)

    def __str__(self):
        return f"{self.key} - {self.value}"


class Deal(BaseModel):
    class Meta:
        verbose_name_plural = "Deals"

    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="deals", verbose_name=_("Менеджер")
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, related_name="deals", verbose_name=_("Клиент")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="deals", verbose_name=_("Товар")
    )

    def __str__(self):
        return f"{self.customer} - {self.product}"
