from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import StageExecutionModel
from cryton.hive.utility import exceptions as core_exceptions
from cryton.hive.models.stage import StageExecution


@extend_schema_view(
    list=extend_schema(description="List Stage executions.", parameters=[serializers.StageExecutionListSerializer]),
    retrieve=extend_schema(description="Get existing Stage execution."),
    destroy=extend_schema(description="Delete Stage execution."),
)
class StageExecutionViewSet(util.ExecutionViewSet):
    """
    StageExecution ViewSet.
    """

    queryset = StageExecutionModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.StageExecutionSerializer

    def _destroy(self, model_id: int):
        """
        Delete Stage execution.
        :param model_id: ID of the desired object
        :return: None
        """
        StageExecution(stage_execution_id=model_id).delete()

    @extend_schema(
        description="Generate Stage execution report.",
        responses={
            200: serializers.DetailDictionarySerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["get"], detail=True)
    def report(self, _, **kwargs):
        stage_execution_id = kwargs.get("pk")
        try:
            stage_ex_obj = StageExecution(stage_execution_id=stage_execution_id)
        except core_exceptions.StageExecutionObjectDoesNotExist:
            raise exceptions.NotFound()
        report = stage_ex_obj.report()

        return Response(report, status=status.HTTP_200_OK)

    @extend_schema(
        description="Kill Stage execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def kill(self, _, **kwargs):
        stage_execution_id = kwargs.get("pk")

        try:
            stage_ex_obj = StageExecution(stage_execution_id=stage_execution_id)
            stage_ex_obj.kill()
        except core_exceptions.StageExecutionObjectDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": "{}".format("Stage execution {} is terminated.".format(stage_execution_id))}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Re-execute Stage execution.",
        request=serializers.StageExecutionReExecuteSerializer,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def re_execute(self, request: Request, **kwargs):
        stage_execution_id = kwargs.get("pk")
        try:
            stage_ex_obj = StageExecution(stage_execution_id=stage_execution_id)
        except core_exceptions.StageExecutionObjectDoesNotExist:
            raise exceptions.NotFound()

        immediately = request.data.get("immediately", True)
        if not isinstance(immediately, bool):
            raise exceptions.ValidationError("Parameter 'immediately' must be of type 'bool'.")

        try:
            stage_ex_obj.re_execute(immediately)
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(str(ex))

        msg = {"detail": "{}".format("Stage execution {} re-executed.".format(stage_execution_id))}
        return Response(msg, status=status.HTTP_200_OK)
