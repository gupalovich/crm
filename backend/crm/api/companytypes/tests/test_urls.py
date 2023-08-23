from django.urls import resolve, reverse

from ..serializers import CompanyType


def test_companytype_list():
    assert reverse("api:companytype-list") == "/api/v1/company-types/"
    assert resolve("/api/v1/company-types/").view_name == "api:companytype-list"


def test_companytype_detail(companytype: CompanyType):
    assert (
        reverse("api:companytype-detail", kwargs={"pk": companytype.pk})
        == f"/api/v1/company-types/{companytype.pk}/"
    )
    assert resolve(f"/api/v1/company-types/{companytype.pk}/").view_name == "api:companytype-detail"


def test_companytype_add():
    assert reverse("api:companytype-add") == "/api/v1/company-types/add/"
    assert resolve("/api/v1/company-types/add/").view_name == "api:companytype-add"


def test_companytype_ids():
    assert reverse("api:companytype-ids") == "/api/v1/company-types/ids/"
    assert resolve("/api/v1/company-types/ids/").view_name == "api:companytype-ids"
