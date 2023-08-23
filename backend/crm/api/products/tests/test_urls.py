from django.urls import resolve, reverse

from crm.companies.models import Product


def test_product_list():
    assert reverse("api:product-list") == "/api/v1/products/"
    assert resolve("/api/v1/products/").view_name == "api:product-list"


def test_product_detail(product: Product):
    assert reverse("api:product-detail", args=[product.id]) == f"/api/v1/products/{product.id}/"
    assert resolve(f"/api/v1/products/{product.id}/").view_name == "api:product-detail"


def test_product_price_list(product: Product):
    assert reverse("api:product-price", args=[product.id]) == f"/api/v1/products/{product.id}/price/"
    assert resolve(f"/api/v1/products/{product.id}/price/").view_name == "api:product-price"


def test_product_commercial_offer(product: Product):
    assert reverse("api:product-offer", args=[product.id]) == f"/api/v1/products/{product.id}/offer/"
    assert resolve(f"/api/v1/products/{product.id}/offer/").view_name == "api:product-offer"


def test_product_add():
    assert reverse("api:product-add") == "/api/v1/products/add/"
    assert resolve("/api/v1/products/add/").view_name == "api:product-add"


def test_product_ids():
    assert reverse("api:product-ids") == "/api/v1/products/ids/"
    assert resolve("/api/v1/products/ids/").view_name == "api:product-ids"
