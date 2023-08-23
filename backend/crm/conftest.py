import pytest

from crm.companies.tests.factories import (
    Company,
    CompanyFactory,
    CompanyProductLink,
    CompanyProductLinkFactory,
    CompanyType,
    CompanyTypeFactory,
    Customer,
    CustomerFactory,
    Deal,
    DealFactory,
    Product,
    ProductFactory,
    ProductTranslation,
    ProductTranslationFactory,
)
from crm.documents.tests.factories import Document, DocumentFactory, PDFBlock, PDFBlockFactory
from crm.users.tests.factories import User, UserFactory


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def companytype(db) -> CompanyType:
    return CompanyTypeFactory()


@pytest.fixture
def company(db) -> Company:
    return CompanyFactory()


@pytest.fixture
def companyproductlink(db) -> CompanyProductLink:
    return CompanyProductLinkFactory()


@pytest.fixture
def customer(db) -> Customer:
    return CustomerFactory()


@pytest.fixture
def product(db) -> Product:
    return ProductFactory()


@pytest.fixture
def translation(db) -> ProductTranslation:
    return ProductTranslationFactory()


@pytest.fixture
def deal(db) -> Deal:
    return DealFactory()


@pytest.fixture
def pdf_block(db) -> PDFBlock:
    return PDFBlockFactory()


@pytest.fixture
def document(db) -> Document:
    return DocumentFactory()
