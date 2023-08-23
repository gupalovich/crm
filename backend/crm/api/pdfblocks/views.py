import django_filters
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from crm.companies.selectors import pdf_block_list
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, CreateInfoMixin, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsAdminPermission, IsSuperPermission
from .serializers import PDFBlock, PDFBlockSerializer


class PDFBlockViewset(CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = PDFBlock
            fields = []

        company = django_filters.CharFilter(field_name="company__id")

    queryset = PDFBlock.objects.none()
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self):
        pdf_blocks = pdf_block_list(self.request.user)
        return pdf_blocks

    def get_serializer_class(self):
        serializer_classes = {
            "create": PDFBlockSerializer,
            "retrieve": PDFBlockSerializer,
            "update": PDFBlockSerializer,
            "partial_update": PDFBlockSerializer,
            "destroy": PDFBlockSerializer,
            "add": PDFBlockSerializer,
            "ids": DeleteMultipleSerializer,
        }
        return serializer_classes.get(self.action, PDFBlockSerializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ["add"]:
            permission_classes += [DjangoModelPermissions, IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]
