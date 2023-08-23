import django_filters
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from crm.api.documents.serializers import DocumentSerializer
from crm.companies.selectors import User, pdf_block_list_filter_by_ids, product_list
from crm.companies.services import document_create, product_translate
from crm.core.pagination import PageNumberPagination
from crm.core.utils import convert_img_to_base64, generate_qr_code, html_to_pdf

from ..mixins import (
    BaseFilter,
    CreateInfoMixin,
    DeleteMultipleMixin,
    DeleteMultipleSerializer,
    VectorSearchMixin,
)
from ..permissions import validate_product
from .serializers import OfferSerializer, Product, ProductSerializer


class ProductViewset(VectorSearchMixin, CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = Product
            fields = []

        company = django_filters.CharFilter(field_name="company__id")

    queryset = Product.objects.none()
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self):
        products = product_list(self.request.user)
        products = self.search(products, search_fields=["data"])
        return products

    def get_serializer_class(self):
        list_serializer = ProductSerializer
        serializer_classes = {
            "create": list_serializer,
            "retrieve": list_serializer,
            "update": list_serializer,
            "partial_update": list_serializer,
            "destroy": list_serializer,
            "add": list_serializer,
            "ids": DeleteMultipleSerializer,
            "offer": OfferSerializer,
        }
        return serializer_classes.get(self.action, list_serializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    def generate_pdf_context(self, user: User, product: Product, pdf_blocks: list[int] = []) -> dict:
        validate_product(product)
        context = {
            "user": user,
            "company": product.company,
            "product": product_translate(product=product),
            "pdf_blocks": pdf_block_list_filter_by_ids(user, pdf_blocks),
            "qr_code": convert_img_to_base64(generate_qr_code(product.url)),
            "file_name": f"{user.username}-{product.id}.pdf",
        }
        return context

    def generate_pdf_response(self, file, file_name, disposition="inline") -> HttpResponse:
        response = HttpResponse(file, content_type="application/pdf")
        response["Content-Disposition"] = f"{disposition}; filename={file_name}"
        return response

    @action(detail=True, methods=["get"])
    def price(self, request, pk=None):
        context = self.generate_pdf_context(request.user, self.get_object())
        template = context["company"].price_template
        pdf_file = html_to_pdf(request, template, context)
        response = self.generate_pdf_response(pdf_file, context["file_name"])
        return response

    @action(detail=True, methods=["post"])
    def offer(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance_name = serializer.validated_data["name"]
        pdf_blocks = serializer.validated_data.get("pdf_blocks", [])

        context = self.generate_pdf_context(request.user, self.get_object(), pdf_blocks=pdf_blocks)
        template = context["company"].offer_template
        pdf_file = html_to_pdf(request, template, context, "css/pdf.css")

        document = document_create(
            document_data={
                "pdf_file": {"content": pdf_file, "name": context["file_name"]},
                "name": instance_name,
                "product": context["product"],
            }
        )
        document = DocumentSerializer(document, context={"request": request})

        return Response(document.data, status=status.HTTP_201_CREATED)
