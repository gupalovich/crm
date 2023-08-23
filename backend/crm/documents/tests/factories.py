from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from crm.companies.tests.factories import CompanyFactory, ProductFactory

from ..models import Document, PDFBlock


class PDFBlockFactory(DjangoModelFactory):
    class Meta:
        model = PDFBlock

    company = SubFactory(CompanyFactory)
    name = Faker("sentence", nb_words=3, locale="ru_RU")
    text = Faker("paragraph", locale="ru_RU")


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    product = SubFactory(ProductFactory)
    name = Faker("sentence", nb_words=3, locale="ru_RU")
    url = Faker("url")
