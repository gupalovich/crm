from factory import Faker, LazyFunction, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker import Faker as OriginalFaker

from crm.users.tests.factories import UserFactory

from ..models import (
    Company,
    CompanyMember,
    CompanyProductLink,
    CompanyType,
    Customer,
    Deal,
    Product,
    ProductImage,
    ProductTranslation,
)

fake = OriginalFaker()


class CompanyTypeFactory(DjangoModelFactory):
    class Meta:
        model = CompanyType

    user = SubFactory(UserFactory)
    name = Faker("word")


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    company_type = SubFactory(CompanyTypeFactory)
    name = Faker("company")
    executive_name = Faker("name")
    executive_position = Faker("job")
    address = Faker("address")
    logo_image = Faker("image_url")
    signature_image = Faker("image_url")


class CompanyProductLinkFactory(DjangoModelFactory):
    class Meta:
        model = CompanyProductLink

    company = SubFactory(CompanyFactory)
    name = Faker("word")
    url = "https://used.dealer-car.ru/test_json.json"
    is_valid = True


class CompanyMemberFactory(DjangoModelFactory):
    class Meta:
        model = CompanyMember

    user = SubFactory(UserFactory)
    company = SubFactory(CompanyFactory)


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    company = SubFactory(CompanyFactory)
    first_name = Faker("first_name")
    middle_name = Faker("last_name")
    last_name = Faker("last_name")
    email = Faker("email")
    phone_number = Faker("phone_number", locale="ru_RU")


def gen_product_data() -> dict:
    data = {
        "brand": fake.word(),
        "model": fake.word(),
        "year": fake.year(),
        "doors": fake.pyint(min_value=0, max_value=10),
        "color": fake.word(),
        "fuel_type": fake.word(),
        "engine_volume": fake.pyint(min_value=0, max_value=500),
        "power": fake.pyint(min_value=0, max_value=500),
        "interior": fake.sentence(nb_words=4),
        "max_speed": "100 км/ч",
    }
    return data


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    company = SubFactory(CompanyFactory)
    pid = Faker("uuid4")
    name = Faker("sentence", nb_words=3)
    data = LazyFunction(lambda: gen_product_data())
    price = Faker("pyint", min_value=1000000, max_value=1000000000)
    price_special = Faker("pyint", min_value=1000000, max_value=1000000000)
    url = Faker("url")
    is_active = True


def generate_product_image_url():
    base_url = "https://sales.mercedes-orenburg.ru/image/cache/catalog/cars/order_0152481574_uploaded"
    return f"{base_url}/16441416594210001-1200x900_resize.jpg"


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = SubFactory(ProductFactory)
    url = FuzzyChoice([generate_product_image_url() for _ in range(1, 3)])


class ProductTranslationFactory(DjangoModelFactory):
    class Meta:
        model = ProductTranslation

    key = Faker("word")
    value = Faker("sentence", nb_words=2, locale="ru_RU")


class DealFactory(DjangoModelFactory):
    class Meta:
        model = Deal

    manager = SubFactory(UserFactory)
    customer = SubFactory(CustomerFactory)
    product = SubFactory(ProductFactory)
