import django_filters
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from crm.companies.selectors import customer_list
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, CreateInfoMixin, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsAdminPermission, IsSuperPermission
from .serializers import Customer, CustomerSerializer


class CustomerViewset(CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = Customer
            fields = []

        company = django_filters.CharFilter(field_name="company__id")

    queryset = Customer.objects.none()
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self):
        customers = customer_list(self.request.user)
        return customers

    def get_serializer_class(self):
        list_serializer = CustomerSerializer
        serializer_classes = {
            "create": list_serializer,
            "retrieve": list_serializer,
            "update": list_serializer,
            "partial_update": list_serializer,
            "destroy": list_serializer,
            "add": list_serializer,
            "ids": DeleteMultipleSerializer,
        }
        return serializer_classes.get(self.action, list_serializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ["add"]:
            permission_classes += [DjangoModelPermissions]
        if self.action in ["ids"]:
            permission_classes += [IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]
