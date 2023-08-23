from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from crm.companies.models import CompanyType
from crm.companies.selectors import company_type_list
from crm.core.pagination import PageNumberPagination

from ..mixins import CreateInfoMixin, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsAdminPermission, IsSuperPermission
from .serializers import CompanyTypeSerializer


class CompanyTypeViewset(CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    queryset = CompanyType.objects.none()
    pagination_class = Pagination

    def get_queryset(self):
        company_types = company_type_list(self.request.user)
        if self.action != "ids":  # hack to fix DeleteMultipleMixin deletion
            company_types = company_types.distinct()
        return company_types

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ["add"]:
            permission_classes += [DjangoModelPermissions, IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        serializer_classes = {
            "create": CompanyTypeSerializer,
            "retrieve": CompanyTypeSerializer,
            "update": CompanyTypeSerializer,
            "partial_update": CompanyTypeSerializer,
            "destroy": CompanyTypeSerializer,
            "add": CompanyTypeSerializer,
            "ids": DeleteMultipleSerializer,
        }
        return serializer_classes.get(self.action, CompanyTypeSerializer)
