from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _

from crm.companies.models import Company, Product
from crm.core.models import BaseModel


class PDFBlock(BaseModel):
    class Meta:
        verbose_name_plural = "PDF Blocks"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_("Компания"))
    name = models.CharField(_("Наименования"), max_length=150)
    image = models.ImageField(_("Картинка"), upload_to="text-blocks/", null=True, blank=True)
    text = RichTextField(_("Текст"))

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Document(BaseModel):
    class Meta:
        verbose_name_plural = "Documents"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Товар"))
    name = models.CharField(_("Название"), max_length=150)
    url = models.FileField(_("Ссылка"), upload_to="documents/")

    def __str__(self):
        return self.name
