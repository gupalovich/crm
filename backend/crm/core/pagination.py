import math
from collections import OrderedDict
from typing import Any

from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination as _PageNumberPagination
from rest_framework.response import Response


def get_paginated_response(*, pagination_class, serializer_class, queryset, request, view):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(data=serializer.data)


class PageNumberPagination(_PageNumberPagination):
    page_size = 20
    max_page_size = 50

    def get_page_size(self, request):
        if "itemsPerPage" in request.query_params:
            page_size = int(request.query_params["itemsPerPage"])
            return min(page_size, self.max_page_size)
        return self.page_size

    def get_paginated_response(self, data: Any) -> Response:
        page_size = self.get_page_size(self.request)

        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("countPages", math.ceil(self.page.paginator.count / page_size)),
                    ("page", int(self.request.query_params.get(self.page_query_param, 1))),
                    ("itemsPerPage", page_size),
                    ("items", data),
                ]
            )
        )


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
