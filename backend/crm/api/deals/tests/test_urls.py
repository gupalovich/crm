from django.urls import resolve, reverse

from ..serializers import Deal


def test_deal_list():
    assert reverse("api:deal-list") == "/api/v1/deals/"
    assert resolve("/api/v1/deals/").view_name == "api:deal-list"


def test_deal_detail(deal: Deal):
    assert reverse("api:deal-detail", kwargs={"pk": deal.pk}) == f"/api/v1/deals/{deal.pk}/"
    assert resolve(f"/api/v1/deals/{deal.pk}/").view_name == "api:deal-detail"


def test_deal_add():
    assert reverse("api:deal-add") == "/api/v1/deals/add/"
    assert resolve("/api/v1/deals/add/").view_name == "api:deal-add"


def test_deal_ids():
    assert reverse("api:deal-ids") == "/api/v1/deals/ids/"
    assert resolve("/api/v1/deals/ids/").view_name == "api:deal-ids"
