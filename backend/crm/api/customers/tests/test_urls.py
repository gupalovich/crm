from django.urls import resolve, reverse

from ..serializers import Customer


def test_customer_list():
    assert reverse("api:customer-list") == "/api/v1/customers/"
    assert resolve("/api/v1/customers/").view_name == "api:customer-list"


def test_customer_detail(customer: Customer):
    assert reverse("api:customer-detail", kwargs={"pk": customer.pk}) == f"/api/v1/customers/{customer.pk}/"
    assert resolve(f"/api/v1/customers/{customer.pk}/").view_name == "api:customer-detail"


def test_customer_add():
    assert reverse("api:customer-add") == "/api/v1/customers/add/"
    assert resolve("/api/v1/customers/add/").view_name == "api:customer-add"


def test_customer_ids():
    assert reverse("api:customer-ids") == "/api/v1/customers/ids/"
    assert resolve("/api/v1/customers/ids/").view_name == "api:customer-ids"
