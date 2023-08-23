from django.urls import resolve, reverse

from crm.documents.models import Document


def test_document_list():
    assert reverse("api:document-list") == "/api/v1/documents/"
    assert resolve("/api/v1/documents/").view_name == "api:document-list"


def test_document_detail(document: Document):
    assert reverse("api:document-detail", args=[document.id]) == f"/api/v1/documents/{document.id}/"
    assert resolve(f"/api/v1/documents/{document.id}/").view_name == "api:document-detail"


def test_document_ids():
    assert reverse("api:document-ids") == "/api/v1/documents/ids/"
    assert resolve("/api/v1/documents/ids/").view_name == "api:document-ids"
