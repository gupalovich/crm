from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from crm.core.pagination import PageNumberPagination

from ..mixins import CreateInfoMixin, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsSuperPermission
from .serializers import ProductTranslation, ProductTranslationDetailSerializer, ProductTranslationSerializer


class ProductTranslationViewset(CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    queryset = ProductTranslation.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions, IsSuperPermission]
    pagination_class = Pagination

    def get_serializer_class(self):
        list_serializer = ProductTranslationSerializer
        detail_serializer = ProductTranslationDetailSerializer
        serializer_classes = {
            "create": list_serializer,
            "retrieve": detail_serializer,
            "update": detail_serializer,
            "partial_update": detail_serializer,
            "destroy": detail_serializer,
            "add": list_serializer,
            "ids": DeleteMultipleSerializer,
        }
        return serializer_classes.get(self.action, list_serializer)
