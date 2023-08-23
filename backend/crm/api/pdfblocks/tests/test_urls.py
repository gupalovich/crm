from django.urls import resolve, reverse

from crm.documents.models import PDFBlock


def test_pdf_block_list():
    assert reverse("api:pdfblock-list") == "/api/v1/pdf-blocks/"
    assert resolve("/api/v1/pdf-blocks/").view_name == "api:pdfblock-list"


def test_pdf_block_detail(pdf_block: PDFBlock):
    assert reverse("api:pdfblock-detail", args=[pdf_block.id]) == f"/api/v1/pdf-blocks/{pdf_block.id}/"
    assert resolve(f"/api/v1/pdf-blocks/{pdf_block.id}/").view_name == "api:pdfblock-detail"


def test_pdf_block_add():
    assert reverse("api:pdfblock-add") == "/api/v1/pdf-blocks/add/"
    assert resolve("/api/v1/pdf-blocks/add/").view_name == "api:pdfblock-add"


def test_pdf_block_ids():
    assert reverse("api:pdfblock-ids") == "/api/v1/pdf-blocks/ids/"
    assert resolve("/api/v1/pdf-blocks/ids/").view_name == "api:pdfblock-ids"
