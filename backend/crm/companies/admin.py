from django.contrib import admin

from .models import (
    Company,
    CompanyMember,
    CompanyProductLink,
    CompanyType,
    Customer,
    Deal,
    Product,
    ProductImage,
    ProductTranslation,
)


@admin.register(CompanyType)
class CompanyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "id", "created_at", "updated_at")
    search_fields = ["user__username", "name"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "company_type", "id", "created_at", "updated_at")
    search_fields = ["name"]


@admin.register(CompanyProductLink)
class CompanyProductLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "id", "is_valid", "created_at", "updated_at")
    search_fields = ["name", "company__name"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "company")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "id", "pid", "is_active", "created_at", "updated_at")
    search_fields = ["name", "company__name", "pid"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "created_at", "updated_at")
    search_fields = ["product__pid", "product__name", "product__company__name"]


@admin.register(ProductTranslation)
class ProductTranslationAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "created_at", "updated_at")
    search_fields = ["key", "value"]


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("manager", "customer", "product")


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "id", "company", "created_at", "updated_at"]
    search_fields = ["company__name", "user__username"]
