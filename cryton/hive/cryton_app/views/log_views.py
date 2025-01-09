from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from cryton.hive.cryton_app import util, exceptions, serializers
from cryton.hive.utility import util as core_util


class LogViewSet(util.BaseViewSet):
    """
    Log ViewSet.
    """

    http_method_names = ["get"]
    serializer_class = serializers.LogSerializer

    @extend_schema(
        description="Get Cryton Hive app logs.",
        parameters=[
            OpenApiParameter("offset", OpenApiTypes.NUMBER, OpenApiParameter.QUERY),
            OpenApiParameter("limit", OpenApiTypes.NUMBER, OpenApiParameter.QUERY),
            OpenApiParameter(
                "any", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter results using `any` key."
            ),
            OpenApiParameter("page", exclude=True),
        ],
        responses={
            200: serializers.LogSerializer,  # 'next'/'previous' parameters are inherited by default
            500: serializers.DetailStringSerializer,
        },
    )
    def list(self, request: Request):
        query_params = request.query_params.copy()
        try:
            offset = int(query_params.pop("offset", 0)[0])
            limit = int(query_params.pop("limit", 0)[0])

            if offset < 0:
                raise ValueError("The `offset` parameter must be a positive number.")

            if limit < 0:
                raise ValueError("The `limit` parameter must be a positive number.")
        except ValueError as ex:
            raise exceptions.ValidationError(ex)

        logs = core_util.get_logs(offset, limit, query_params)

        msg = {"count": len(logs), "results": logs, "next": "", "previous": ""}
        return Response(msg, status=status.HTTP_200_OK)
