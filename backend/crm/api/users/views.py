import django_filters
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from crm.companies.selectors import user_list
from crm.core.pagination import PageNumberPagination

from ..mixins import BaseFilter, CreateInfoMixin
from ..permissions import CanModifyUserPermission, IsAdminPermission, IsSuperPermission
from .serializers import (
    MeSerializer,
    UserCreateForAdminSerializer,
    UserCreateForSuperUserSerializer,
    UserDetailSerializer,
    UserListSerializer,
)

User = get_user_model()


class UserViewset(CreateInfoMixin, ModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10

    class Filter(BaseFilter):
        class Meta:
            model = User
            fields = []

        company = django_filters.CharFilter(field_name="memberships__company__id", label="Компания ID")

    queryset = User.objects.all()
    lookup_field = "username"
    pagination_class = Pagination
    filterset_class = Filter

    def get_queryset(self, *args, **kwargs):
        users = user_list(self.request.user)
        return users

    def get_serializer_class(self):
        is_superuser = self.request.user.is_crm_superuser
        create_serializer = UserCreateForSuperUserSerializer if is_superuser else UserCreateForAdminSerializer
        detail_serializer = UserDetailSerializer
        serializer_classes = {
            "create": create_serializer,
            "retrieve": detail_serializer,
            "update": detail_serializer,
            "partial_update": detail_serializer,
            "destroy": detail_serializer,
            "me": MeSerializer,
            "add": create_serializer,
        }

        return serializer_classes.get(self.action, UserListSerializer)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ["me", "add"]:
            permission_classes += [
                DjangoModelPermissions,
                CanModifyUserPermission,
                IsSuperPermission | IsAdminPermission,
            ]
        return [permission() for permission in permission_classes]

    @action(detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
