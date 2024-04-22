from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import StepExecutionModel
from cryton.hive.utility import exceptions as core_exceptions
from cryton.hive.models.step import StepExecution


@extend_schema_view(
    list=extend_schema(description="List Step executions.", parameters=[serializers.StepExecutionListSerializer]),
    retrieve=extend_schema(description="Get existing Step execution."),
    destroy=extend_schema(description="Delete Step execution."),
)
class StepExecutionViewSet(util.ExecutionViewSet):
    """
    StepExecution ViewSet.
    """

    queryset = StepExecutionModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.StepExecutionSerializer

    def _destroy(self, model_id: int):
        """
        Delete Step execution.
        :param model_id: ID of the desired object
        :return: None
        """
        StepExecution(step_execution_id=model_id).delete()

    @extend_schema(
        description="Generate Step execution report.",
        responses={
            200: serializers.DetailDictionarySerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["get"], detail=True)
    def report(self, _, **kwargs):
        step_execution_id = kwargs.get("pk")

        try:
            step_ex_obj = StepExecution(step_execution_id=step_execution_id)
        except core_exceptions.StepExecutionObjectDoesNotExist:
            raise exceptions.NotFound()
        report = step_ex_obj.report()

        return Response(report, status=status.HTTP_200_OK)

    @extend_schema(
        description="Kill Step execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def kill(self, _, **kwargs):
        step_execution_id = kwargs.get("pk")

        try:
            step_ex_obj = StepExecution(step_execution_id=step_execution_id)
            step_ex_obj.kill()
        except core_exceptions.StepExecutionObjectDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": "{}".format("Step execution {} is terminated.".format(step_execution_id))}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Re-execute Step execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def re_execute(self, _, **kwargs):
        step_execution_id = kwargs.get("pk")

        try:
            step_ex_obj = StepExecution(step_execution_id=step_execution_id)
            step_ex_obj.re_execute()
        except core_exceptions.StepExecutionObjectDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": "{}".format("Step execution {} re-executed.".format(step_execution_id))}
        return Response(msg, status=status.HTTP_200_OK)
