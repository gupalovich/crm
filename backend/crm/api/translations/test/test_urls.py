from django.urls import resolve, reverse

from ..serializers import ProductTranslation


def test_translation_list():
    assert reverse("api:translation-list") == "/api/v1/translations/"
    assert resolve("/api/v1/translations/").view_name == "api:translation-list"


def test_translation_detail(translation: ProductTranslation):
    assert (
        reverse("api:translation-detail", kwargs={"pk": translation.pk})
        == f"/api/v1/translations/{translation.pk}/"
    )
    assert resolve(f"/api/v1/translations/{translation.pk}/").view_name == "api:translation-detail"


def test_translation_add():
    assert reverse("api:translation-add") == "/api/v1/translations/add/"
    assert resolve("/api/v1/translations/add/").view_name == "api:translation-add"


def test_translation_ids():
    assert reverse("api:translation-ids") == "/api/v1/translations/ids/"
    assert resolve("/api/v1/translations/ids/").view_name == "api:translation-ids"
