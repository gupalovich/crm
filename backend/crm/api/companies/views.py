import django_filters
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from crm.companies.selectors import company_list
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, CreateInfoMixin
from ..permissions import IsAdminPermission, IsSuperPermission
from .serializers import Company, CompanySerializer


class CompanyViewset(CreateInfoMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = Company
            fields = []

        company_type = django_filters.CharFilter(field_name="company_type__name", lookup_expr="iexact")

    queryset = Company.objects.none()
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self):
        companies = company_list(self.request.user)
        return companies

    def get_serializer_class(self):
        list_serializer = CompanySerializer
        serializer_classes = {
            "create": list_serializer,
            "retrieve": list_serializer,
            "update": list_serializer,
            "partial_update": list_serializer,
            "destroy": list_serializer,
            "add": list_serializer,
        }
        return serializer_classes.get(self.action, list_serializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ["add"]:
            permission_classes += [DjangoModelPermissions, IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]
