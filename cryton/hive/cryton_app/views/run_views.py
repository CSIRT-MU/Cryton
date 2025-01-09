from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import RunModel, WorkerModel, PlanModel
from cryton.hive.utility import exceptions as core_exceptions, states
from cryton.hive.models.run import Run
from cryton.hive.models.plan import Plan


@extend_schema_view(
    list=extend_schema(description="List Runs.", parameters=[serializers.ListSerializer]),
    retrieve=extend_schema(description="Get existing Run."),
    destroy=extend_schema(description="Delete Run."),
)
class RunViewSet(util.ExecutionFullViewSet):
    """
    Run ViewSet.
    """

    queryset = RunModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.RunSerializer

    def _destroy(self, model_id: int):
        """
        Delete Run.
        :param model_id: ID of the desired object
        :return: None
        """
        Run(model_id).delete()

    @extend_schema(
        description="Create new Run.",
        request=serializers.RunCreateSerializer,
        responses={
            201: serializers.RunCreateDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    def create(self, request: Request, **kwargs):
        try:
            plan_id = int(request.data["plan_id"])
            worker_ids = request.data["worker_ids"]
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(str(ex))

        try:
            workers = WorkerModel.objects.filter(id__in=worker_ids)
        except (ValueError, TypeError):
            raise exceptions.ValidationError("Parameter 'worker_ids' is wrong.")

        if not workers.exists() or len(workers) != len(worker_ids):
            raise exceptions.ValidationError("Nonexistent Worker(s) specified.")

        if not PlanModel.objects.filter(id=plan_id).exists():
            raise exceptions.NotFound(f"Nonexistent Plan with ID {plan_id} specified.")

        run_obj = Run.prepare(plan_id, worker_ids)
        plan_execution_ids = run_obj.model.plan_executions.values_list("id", flat=True)

        msg = {"id": run_obj.model.id, "detail": "Run successfully created.", "plan_execution_ids": plan_execution_ids}
        return Response(msg, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Generate Run report.",
        responses={
            200: serializers.DetailDictionarySerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["get"], detail=True)
    def report(self, _, **kwargs):
        run_id = kwargs.get("pk")
        try:
            run_obj = Run(run_id)
            report = run_obj.report()
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        return Response({"detail": report}, status=status.HTTP_200_OK)

    @extend_schema(
        description="Pause Run.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def pause(self, _, **kwargs):
        run_id = kwargs.get("pk")

        try:
            run_obj = Run(run_id)
            run_obj.pause()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        msg = {"detail": f"Run {run_id} is paused."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Resume Run.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def resume(self, _, **kwargs):
        run_id = kwargs.get("pk")

        try:
            run_obj = Run(run_id)
            run_obj.resume()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        msg = {"detail": f"Run {run_id} is resumed."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Schedule Run.",
        request=serializers.RunScheduleSerializer(),
        examples=[
            OpenApiExample(
                "Schedule Run (seconds precision)",
                description="Schedule Run to year 1999, month 2, day 1, hour 13, minute 12, second 11.",
                value={
                    "start_time": "1999-2-1T13:12:11Z",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Schedule Run (milliseconds precision)",
                description="Schedule Run to year 1999, month 2, day 1, hour 13, minute 12, second 11, millisecond 1.",
                value={
                    "start_time": "1999-2-1T13:12:11.1Z",
                },
                request_only=True,
            ),
        ],
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def schedule(self, request: Request, **kwargs):
        run_id = kwargs.get("pk")
        start_time = util.get_start_time(request.data)

        try:
            run_obj = Run(run_id)
            run_obj.schedule(start_time)
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        msg = {"detail": f"Run {run_id} is scheduled for {start_time}."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Execute Run.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def execute(self, _, **kwargs):
        run_id = kwargs.get("pk")
        try:
            run_obj = Run(run_id)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        if run_obj.state not in states.RUN_EXECUTE_NOW_STATES:
            raise exceptions.ApiWrongObjectState(
                f"Run object in wrong state: {run_obj.state}, " f"must be in: {states.RUN_EXECUTE_NOW_STATES}"
            )

        try:
            run_obj.start()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)
        except core_exceptions.RpcTimeoutError as ex:
            raise exceptions.RpcTimeout(ex)

        msg = {"detail": f"Run {run_id} was executed."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Reschedule Run.",
        request=serializers.RunScheduleSerializer(),
        examples=[
            OpenApiExample(
                "Reschedule Run (seconds precision)",
                description="Reschedule Run to year 1999, month 2, day 1, hour 13, minute 12, second 11.",
                value={
                    "start_time": "1999-2-1T13:12:11Z",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Reschedule Run (milliseconds precision)",
                description="Reschedule Run to year 1999, month 2, day 1, hour 13, minute 1, second 2, millisecond 3.",
                value={
                    "start_time": "1999-2-1T13:1:2.3Z",
                },
                request_only=True,
            ),
        ],
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def reschedule(self, request: Request, **kwargs):
        run_id = kwargs.get("pk")
        start_time = util.get_start_time(request.data)

        try:
            run_obj = Run(run_id)
            run_obj.reschedule(start_time)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": f"Run {run_id} is rescheduled for {start_time}."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Unschedule Run.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def unschedule(self, _, **kwargs):
        run_id = kwargs.get("pk")
        try:
            run_obj = Run(run_id)
            run_obj.unschedule()
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": f"Run {run_id} is unscheduled."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Stop Run.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def stop(self, _, **kwargs):
        run_id = kwargs.get("pk")

        try:
            run_obj = Run(run_id)
            run_obj.stop()
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()
        except core_exceptions.InvalidStateError as ex:
            raise exceptions.ApiWrongObjectState(ex)

        msg = {"detail": f"Run {run_id} is stopped."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Check if Workers in Run are available.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
            500: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def healthcheck_workers(self, _, **kwargs):
        run_id = kwargs.get("pk")
        try:
            run_obj = Run(run_id)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        try:
            run_obj.healthcheck_workers()
        except ConnectionError as ex:
            raise exceptions.RpcTimeout(ex)

        msg = {"detail": "Run's Workers are available."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Validate modules in Run.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
            500: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def validate_modules(self, _, **kwargs):
        run_id = kwargs.get("pk")
        try:
            run_obj = Run(run_id)
        except core_exceptions.RunObjectDoesNotExist:
            raise exceptions.NotFound()

        try:
            all_valid = run_obj.validate_modules()
        except core_exceptions.RpcTimeoutError:
            raise exceptions.RpcTimeout("Module's validation failed due to RPC timeout.")

        if not all_valid:
            msg = {"detail": "Run's modules are not valid."}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        msg = {"detail": "Run's modules were validated."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Get Plan's YAML.",
        responses={200: serializers.DetailDictionarySerializer, 404: serializers.DetailStringSerializer},
    )
    @action(methods=["get"], detail=True)
    def get_plan(self, _, **kwargs):
        run_id = kwargs.get("pk")
        try:
            run_obj = RunModel.objects.get(id=run_id)
        except RunModel.DoesNotExist:
            raise exceptions.NotFound(f"Run with ID {run_id} does not exist.")

        plan_obj = Plan(run_obj.plan_id)

        msg = {"detail": plan_obj.generate_plan()}
        return Response(msg, status=status.HTTP_200_OK)
