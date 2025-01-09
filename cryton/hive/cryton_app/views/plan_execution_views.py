from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import PlanExecutionModel
from cryton.hive.utility import exceptions as core_exceptions
from cryton.hive.models.plan import PlanExecution


@extend_schema_view(
    list=extend_schema(description="List Plan executions.", parameters=[serializers.PlanExecutionListSerializer]),
    retrieve=extend_schema(description="Get existing Plan execution."),
    destroy=extend_schema(description="Delete Plan execution."),
)
class PlanExecutionViewSet(util.ExecutionViewSet):
    """
    PlanExecution ViewSet.
    """

    queryset = PlanExecutionModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.PlanExecutionSerializer

    def _destroy(self, model_id: int):
        """
        Delete Plan execution.
        :param model_id: ID of the desired object
        :return: None
        """
        PlanExecution(model_id).delete()

    @extend_schema(
        description="Generate Plan execution report.",
        responses={
            200: serializers.DetailDictionarySerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["get"], detail=True)
    def report(self, _, **kwargs):
        plan_ex_id = kwargs.get("pk")
        try:
            plan_ex_obj = PlanExecution(plan_ex_id)
        except core_exceptions.PlanExecutionDoesNotExist:
            raise exceptions.NotFound()
        report = plan_ex_obj.report()

        msg = {"detail": report}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Pause Plan execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def pause(self, _, **kwargs):
        plan_ex_id = kwargs.get("pk")
        try:
            plan_ex_obj = PlanExecution(plan_ex_id)
            plan_ex_obj.pause()
        except core_exceptions.PlanExecutionDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": f"Plan execution {plan_ex_id} is paused."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Resume Plan execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def resume(self, _, **kwargs):
        plan_ex_id = kwargs.get("pk")
        try:
            plan_ex_obj = PlanExecution(plan_ex_id)
            plan_ex_obj.resume()
        except core_exceptions.PlanExecutionDoesNotExist as ex:
            raise exceptions.NotFound(ex)
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": f"Plan execution {plan_ex_id} resumed."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Validate modules in Plan execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
            500: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def validate_modules(self, _, **kwargs):
        plan_ex_id = kwargs.get("pk")
        try:
            plan_ex_obj = PlanExecution(plan_ex_id)
        except core_exceptions.PlanExecutionDoesNotExist:
            raise exceptions.NotFound()

        try:
            all_valid = plan_ex_obj.validate_modules()
        except core_exceptions.RpcTimeoutError:
            raise exceptions.RpcTimeout("Module's validation failed due to RPC timeout.")

        if not all_valid:
            msg = {"detail": "Plan execution's modules are not valid."}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        msg = {"detail": "Plan execution's modules were validated."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Stop Plan execution.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def stop(self, _, **kwargs):
        plan_ex_id = kwargs.get("pk")
        try:
            plan_ex_obj = PlanExecution(plan_ex_id)
            plan_ex_obj.stop()
        except core_exceptions.PlanExecutionDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": f"Plan execution {plan_ex_id} is stopped."}
        return Response(msg, status=status.HTTP_200_OK)
