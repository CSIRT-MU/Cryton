import yaml

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import PlanModel, PlanTemplateModel, RunModel, WorkerModel
from cryton.hive.utility import exceptions as core_exceptions, creator, states
from cryton.hive.models.plan import Plan, PlanExecution
from cryton.hive.models.run import Run
from cryton.hive.utility.validator import Validator


@extend_schema_view(
    list=extend_schema(description="List Plans.", parameters=[serializers.ListSerializer]),
    retrieve=extend_schema(description="Get existing Plan."),
    destroy=extend_schema(description="Delete Plan."),
)
class PlanViewSet(util.InstanceFullViewSet):
    """
    Plan ViewSet.
    """

    queryset = PlanModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.PlanSerializer

    def _destroy(self, model_id: int):
        """
        Delete Plan.
        :param model_id: ID of the desired object
        :return: None
        """
        Plan(model_id).delete()

    @extend_schema(
        description="Create new Plan. There is no limit or naming convention for inventory files.",
        request=serializers.PlanCreateSerializer,
        examples=[
            OpenApiExample(
                "Multiple files upload",
                description="Uploading multiple inventory files.",
                value={
                    "template_id": 1,
                    "file1": "file content in bytes format",
                    "file2": "file content in bytes format",
                },
                request_only=True,
            )
        ],
        responses={
            201: serializers.CreateDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
            500: serializers.DetailStringSerializer,
        },
    )
    def create(self, request: Request, **kwargs):
        # Get plan template ID from request
        try:
            template_id = int(request.data["template_id"])
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)

        # Read Plan template
        try:
            plan_template_obj = PlanTemplateModel.objects.get(id=template_id)
        except PlanTemplateModel.DoesNotExist:
            raise exceptions.NotFound(f"Nonexistent template_id: {template_id}.")

        try:
            with open(str(plan_template_obj.file.path)) as temp:
                plan_template = temp.read()
        except FileNotFoundError:
            raise exceptions.NotFound("The template was removed. Please upload a new one.")

        inventory_variables = util.get_inventory_variables_from_files(request.FILES)
        filled_plan_template = util.fill_template(inventory_variables, plan_template)

        try:
            plan_data = yaml.safe_load(filled_plan_template)
        except yaml.YAMLError as ex:
            raise exceptions.ValidationError(f"Couldn't load the plan. Original exception: {ex}")

        if not isinstance(plan_data, dict):
            raise exceptions.ValidationError("The plan is invalid. Make sure the template isn't empty.")

        try:
            Validator(plan_data).validate()
        except core_exceptions.ValidationError as ex:
            raise exceptions.ValidationError(str(ex))

        plan_obj_id = creator.create_plan(plan_data)

        msg = {"id": plan_obj_id, "detail": "Plan created."}
        return Response(msg, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Validate Plan YAML. There is no limit or naming convention for inventory files.",
        request=serializers.CreateWithFilesSerializer,
        responses={
            200: serializers.DetailStringSerializer,
            400: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=False)
    def validate(self, request: Request):
        plan_data = util.parse_object_from_files(request.FILES)
        try:
            Validator(plan_data).validate()
        except core_exceptions.ValidationError as ex:
            raise exceptions.ValidationError(f"Plan is not valid. Original error: {ex}")

        msg = {"detail": "Plan is valid."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Create new PlanExecution and execute it.",
        request=serializers.PlanExecuteSerializer,
        responses={200: serializers.DetailStringSerializer, 400: serializers.DetailStringSerializer},
    )
    @action(methods=["post"], detail=True)
    def execute(self, request: Request, **kwargs):
        try:
            plan_id = int(kwargs.get("pk"))
            run_id = int(request.data["run_id"])
            worker_id = int(request.data["worker_id"])
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(f"Wrong input. Original error: {ex}")

        if not PlanModel.objects.filter(id=plan_id).exists():
            raise exceptions.ValidationError(f"Plan with id {plan_id} doesn't exist.")
        if not WorkerModel.objects.filter(id=worker_id).exists():
            raise exceptions.ValidationError(f"Worker with id {worker_id} doesn't exist.")
        if not RunModel.objects.filter(id=run_id).exists():
            raise exceptions.ValidationError(f"Run with id {run_id} doesn't exist.")

        run_obj = Run(run_model_id=run_id)
        if plan_id != run_obj.model.plan.id:
            raise exceptions.ValidationError(
                f"Incorrect Run. Plan ID ({plan_id}) and Run's Plan ID ({run_obj.model.plan.id}) must match."
            )

        if run_obj.state not in states.PLAN_RUN_EXECUTE_STATES:
            raise exceptions.ApiWrongObjectState(
                f"Run's state must be " f"{', or'.join(states.PLAN_RUN_EXECUTE_STATES)}."
            )

        plan_exec = PlanExecution(plan_id=plan_id, worker_id=worker_id, run_id=run_id)
        plan_exec.execute()

        msg = {"detail": f"PlanExecution with ID {plan_exec.model.id} successfully created and executed."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Get Plan's YAML.",
        responses={200: serializers.DetailDictionarySerializer, 404: serializers.DetailStringSerializer},
    )
    @action(methods=["get"], detail=True)
    def get_plan(self, _, **kwargs):
        plan_id = kwargs.get("pk")
        try:
            plan_obj = Plan(plan_id)
        except core_exceptions.PlanObjectDoesNotExist:
            raise exceptions.NotFound(f"Plan with ID {plan_id} does not exist.")

        msg = {"detail": plan_obj.generate_plan()}
        return Response(msg, status=status.HTTP_200_OK)
