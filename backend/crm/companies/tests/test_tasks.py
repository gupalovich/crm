import pytest
from celery.result import EagerResult

from ..tasks import parse_product_task, products_integration_task
from .factories import CompanyFactory, CompanyProductLinkFactory, Product


@pytest.mark.django_db
def test_parse_product_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    company_product_link = CompanyProductLinkFactory()
    result = parse_product_task.delay(company_product_link.pk)
    assert isinstance(result, EagerResult)
    assert Product.objects.count() >= 2


@pytest.mark.django_db
def test_products_integration_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    # create companies
    company = CompanyFactory()
    other_company = CompanyFactory()
    # create links
    CompanyProductLinkFactory(company=company)
    CompanyProductLinkFactory(company=other_company)
    link_invalid = CompanyProductLinkFactory(company=company, url="https://used.dealer-car.ru/")
    result = products_integration_task.delay()
    link_invalid.refresh_from_db()
    # test task result
    assert isinstance(result, EagerResult)
    assert Product.objects.count() == 4
    assert company.products.count() == 2
    assert other_company.products.count() == 2
    assert link_invalid.is_valid is False
