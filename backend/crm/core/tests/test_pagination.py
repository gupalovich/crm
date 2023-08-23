from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from crm.users.tests.factories import UserFactory

from ..pagination import LimitOffsetPagination, get_paginated_response

User = get_user_model()


class ExampleListApi(APIView):
    permission_classes = [AllowAny]

    class Pagination(LimitOffsetPagination):
        default_limit = 1

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email")

    def get(self, request):
        queryset = User.objects.order_by("id")

        response = get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

        return response


class GetPaginatedResponseTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user1 = UserFactory(email="user1@email.ru")
        self.user2 = UserFactory(email="user2@email.ru")

    def test_response_is_paginated_correctly(self):
        first_page_request = self.factory.get("/some/path")
        first_page_response = ExampleListApi.as_view()(first_page_request)

        expected_first_page_response = OrderedDict(
            {
                "limit": 1,
                "offset": 0,
                "count": User.objects.count(),
                "next": "http://testserver/some/path?limit=1&offset=1",
                "previous": None,
                "results": [
                    OrderedDict(
                        {
                            "id": self.user1.id,
                            "email": self.user1.email,
                        }
                    )
                ],
            }
        )

        self.assertEqual(expected_first_page_response, first_page_response.data)

        next_page_request = self.factory.get("/some/path?limit=1&offset=1")
        next_page_response = ExampleListApi.as_view()(next_page_request)

        expected_next_page_response = OrderedDict(
            {
                "limit": 1,
                "offset": 1,
                "count": User.objects.count(),
                "next": None,
                "previous": "http://testserver/some/path?limit=1",
                "results": [
                    OrderedDict(
                        {
                            "id": self.user2.id,
                            "email": self.user2.email,
                        }
                    )
                ],
            }
        )

        self.assertEqual(expected_next_page_response, next_page_response.data)
