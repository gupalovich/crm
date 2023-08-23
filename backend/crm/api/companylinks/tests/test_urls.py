from django.urls import resolve, reverse

from crm.companies.models import CompanyProductLink


def test_companyproductlink_list():
    assert reverse("api:companyproductlink-list") == "/api/v1/company-links/"
    assert resolve("/api/v1/company-links/").view_name == "api:companyproductlink-list"


def test_companyproductlink_detail(companyproductlink: CompanyProductLink):
    link_id = companyproductlink.id
    assert reverse("api:companyproductlink-detail", args=[link_id]) == f"/api/v1/company-links/{link_id}/"
    assert resolve(f"/api/v1/company-links/{link_id}/").view_name == "api:companyproductlink-detail"


def test_companyproductlink_add():
    assert reverse("api:companyproductlink-add") == "/api/v1/company-links/add/"
    assert resolve("/api/v1/company-links/add/").view_name == "api:companyproductlink-add"


def test_companyproductlink_ids():
    assert reverse("api:companyproductlink-ids") == "/api/v1/company-links/ids/"
    assert resolve("/api/v1/company-links/ids/").view_name == "api:companyproductlink-ids"


def test_companyproductlink_parse(companyproductlink: CompanyProductLink):
    link_id = companyproductlink.id
    assert (
        reverse("api:companyproductlink-parse", args=[link_id]) == f"/api/v1/company-links/{link_id}/parse/"
    )
    assert resolve(f"/api/v1/company-links/{link_id}/parse/").view_name == "api:companyproductlink-parse"
