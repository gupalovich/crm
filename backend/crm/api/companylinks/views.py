import django_filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from crm.companies.models import CompanyProductLink
from crm.companies.selectors import company_product_link_list
from crm.companies.tasks import parse_product_task
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, CreateInfoMixin, DeleteMultipleMixin, DeleteMultipleSerializer
from ..permissions import IsAdminPermission, IsSuperPermission, validate_company_product_link
from .serializers import CompanyProductLinkSerializer, ParseSerializer


class CompanyProductLinkViewset(CreateInfoMixin, DeleteMultipleMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = CompanyProductLink
            fields = []

        company = django_filters.CharFilter(field_name="company__id")

    queryset = CompanyProductLink.objects.none()
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self):
        company_links = company_product_link_list(self.request.user)
        return company_links

    def get_serializer_class(self):
        list_serializer = CompanyProductLinkSerializer
        serializer_classes = {
            "create": list_serializer,
            "retrieve": list_serializer,
            "update": list_serializer,
            "partial_update": list_serializer,
            "destroy": list_serializer,
            "add": list_serializer,
            "ids": DeleteMultipleSerializer,
            "parse": ParseSerializer,
        }
        return serializer_classes.get(self.action, list_serializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ["add"]:
            permission_classes += [DjangoModelPermissions, IsSuperPermission | IsAdminPermission]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post", "get"])
    def parse(self, request, pk=None):
        company_product_link = self.get_object()
        validate_company_product_link(company_product_link)
        task_result = parse_product_task.delay(company_product_link.pk)
        task_absolute_url = request.build_absolute_uri(f"/api/tasks/{task_result.id}/")
        response = {"task_id": task_result.id, "task_url": task_absolute_url}
        return Response(response, status=status.HTTP_200_OK)
