from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from cryton_core.cryton_app import util, exceptions, serializers
from cryton_core.lib.util import util as core_util


class LogViewSet(util.BaseViewSet):
    """
    Log ViewSet.
    """
    http_method_names = ["get"]
    serializer_class = serializers.LogSerializer

    @extend_schema(
        description="Get Cryton Core app logs.",
        parameters=[
            OpenApiParameter("offset", OpenApiTypes.NUMBER, OpenApiParameter.QUERY),
            OpenApiParameter("limit", OpenApiTypes.NUMBER, OpenApiParameter.QUERY),
            OpenApiParameter("filter", OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="Filter results using substrings separated by `|`."),
            OpenApiParameter("page", exclude=True)
        ],
        responses={
            200: serializers.LogSerializer,  # 'next'/'previous' parameters are inherited by default
            500: serializers.DetailStringSerializer,
        }
    )
    def list(self, request: Request):
        raw_filter: str = request.query_params.get("filter", "")
        filter_params = [] if raw_filter == "" else raw_filter.split("|")

        try:
            offset = int(request.query_params.get("offset", 0))
            limit = int(request.query_params.get("limit", 0))

            if offset < 0:
                raise ValueError("The `offset` parameter must be a positive number.")

            if limit < 0:
                raise ValueError("The `limit` parameter must be a positive number.")
        except ValueError as ex:
            raise exceptions.ValidationError(ex)

        logs = core_util.get_logs(offset, limit, filter_params)

        msg = {"count": len(logs), "results": logs, "next": "", "previous": ""}
        return Response(msg, status=status.HTTP_200_OK)
