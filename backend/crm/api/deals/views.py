import django_filters
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from crm.companies.selectors import deal_list
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, CreateInfoMixin, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsAdminPermission, IsSuperPermission
from .serializers import Deal, DealDetailSerializer, DealListSerializer


class DealViewset(CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = Deal
            fields = []

        manager = django_filters.CharFilter(field_name="manager__username")
        customer = django_filters.CharFilter(field_name="customer__id")
        product = django_filters.CharFilter(field_name="product__id")
        company = django_filters.CharFilter(field_name="product__company__id", label="Компания ID")

    queryset = Deal.objects.none()
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self):
        deals = deal_list(self.request.user)
        return deals

    def get_serializer_class(self):
        list_serializer = DealListSerializer
        detail_serializer = DealDetailSerializer
        serializer_classes = {
            "create": list_serializer,
            "retrieve": detail_serializer,
            "update": detail_serializer,
            "partial_update": detail_serializer,
            "destroy": detail_serializer,
            "add": list_serializer,
            "ids": DeleteMultipleSerializer,
        }
        return serializer_classes.get(self.action, detail_serializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, DjangoModelPermissions]
        if self.action == "ids":
            permission_classes += [IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]
