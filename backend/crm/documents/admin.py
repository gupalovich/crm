from django.contrib import admin

from .models import Document, PDFBlock


@admin.register(PDFBlock)
class PDFBlockAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "company", "created_at", "updated_at"]
    search_fields = ["name", "company__name"]
    list_filter = ["company"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "product", "created_at", "updated_at"]
    search_fields = ["name", "product__name"]
    raw_id_fields = ["product"]
