from django.urls import resolve, reverse

from crm.companies.models import Company


def test_company_list():
    assert reverse("api:company-list") == "/api/v1/companies/"
    assert resolve("/api/v1/companies/").view_name == "api:company-list"


def test_company_detail(company: Company):
    assert reverse("api:company-detail", args=[company.id]) == f"/api/v1/companies/{company.id}/"
    assert resolve(f"/api/v1/companies/{company.id}/").view_name == "api:company-detail"


def test_company_add():
    assert reverse("api:company-add") == "/api/v1/companies/add/"
    assert resolve("/api/v1/companies/add/").view_name == "api:company-add"
