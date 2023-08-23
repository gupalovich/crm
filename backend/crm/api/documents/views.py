import django_filters
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from crm.companies.selectors import document_list
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsAdminPermission, IsSuperPermission
from .serializers import Document, DocumentDetailSerializer, DocumentSerializer


class DocumentViewset(
    DeleteMultipleMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = Document
            fields = []

        user = django_filters.CharFilter(field_name="url", lookup_expr="icontains")
        product = django_filters.CharFilter(field_name="product__id")
        company = django_filters.CharFilter(field_name="product__company__id")

    queryset = Document.objects.none()
    pagination_class = Pagination
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_class = Filter

    def get_queryset(self):
        documents = document_list(self.request.user)
        return documents

    def get_serializer_class(self):
        list_serializer = DocumentSerializer
        detail_serializer = DocumentDetailSerializer
        serializer_classes = {
            "retrieve": detail_serializer,
            "update": detail_serializer,
            "partial_update": detail_serializer,
            "destroy": detail_serializer,
            "ids": DeleteMultipleSerializer,
        }
        return serializer_classes.get(self.action, list_serializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, DjangoModelPermissions]
        if self.action == "ids":
            permission_classes += [IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]
