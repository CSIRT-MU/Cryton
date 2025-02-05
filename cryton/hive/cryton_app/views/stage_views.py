from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import StageModel
from cryton.hive.utility import exceptions as core_exceptions, creator, states
from cryton.hive.models.stage import Stage, StageExecution
from cryton.hive.models.plan import Plan, PlanExecution
from cryton.hive.utility.validator import Validator


@extend_schema_view(
    list=extend_schema(description="List Stages.", parameters=[serializers.ListSerializer]),
    retrieve=extend_schema(description="Get existing Stage."),
    destroy=extend_schema(description="Delete Stage."),
)
class StageViewSet(util.InstanceFullViewSet):
    """
    Stage ViewSet.
    """

    queryset = StageModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.StageSerializer

    def _destroy(self, model_id: int):
        """
        Delete Stage.
        :param model_id: ID of the desired object
        :return: None
        """
        Stage(model_id).delete()

    @extend_schema(
        description="Create Stage under Plan. There is no limit or naming convention for inventory files.",
        request=serializers.StageCreateSerializer,
        responses={
            200: serializers.CreateDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    def create(self, request: Request, *args, **kwargs):
        try:  # Get Plan ID and check if the Plan exists
            plan_id: int = request.data["plan_id"]
            plan_obj = Plan(plan_id)
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)
        except core_exceptions.PlanObjectDoesNotExist:
            raise exceptions.NotFound()

        # Check if the Plan is dynamic
        if not plan_obj.dynamic:
            raise exceptions.ValidationError("Creating objects under non dynamic plan is not supported.")

        # Parse the stage definition
        stages = util.parse_object_from_files(request.FILES)
        stage_name, stage_data = next(iter(stages.items()))

        # Check the number of stages to be created
        if len(stages) != 1:
            raise exceptions.ValidationError("Create one stage at a time.")

        # Check validity of the new plan
        new_plan = plan_obj.generate_plan()
        if new_plan["stages"].get(stage_name):
            exceptions.ValidationError(f"Stage {stage_name} is already present in the plan.")
        new_plan["stages"][stage_name] = stage_data

        try:
            Validator(new_plan).validate()
        except core_exceptions.ValidationError as ex:
            raise exceptions.ValidationError(ex)

        # Create the stage
        stage_id = creator.create_stages(plan_obj.model, stages)
        msg = {"id": stage_id, "detail": "Stage successfully created."}

        return Response(msg, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Validate Stage YAML. There is no limit or naming convention for inventory files.",
        request=serializers.StageValidateSerializer,
        responses={200: serializers.DetailStringSerializer, 400: serializers.DetailStringSerializer},
    )
    @action(methods=["post"], detail=False)
    def validate(self, request: Request):
        try:  # Get Plan ID and check if the Plan exists
            plan_id: int = request.data["plan_id"]
            plan_obj = Plan(plan_id)
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)
        except core_exceptions.PlanObjectDoesNotExist:
            raise exceptions.NotFound()

        stage_data = util.parse_object_from_files(request.FILES)

        new_plan = plan_obj.generate_plan()
        for stage, stage_dict in stage_data.items():
            if new_plan["stages"].get(stage):
                raise exceptions.ValidationError(f"Stage {stage} is already present in the plan.")
            new_plan["stages"][stage] = stage_dict

        try:
            Validator(new_plan).validate()
        except core_exceptions.ValidationError as ex:
            raise exceptions.ValidationError(f"Adding the stage(s) would make the plan invalid.\n{ex}")

        msg = {"detail": "Stage is valid."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Start Stage's trigger under Plan execution.",
        request=serializers.StageStartTriggerSerializer,
        responses={
            200: serializers.ExecutionCreateDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def start_trigger(self, request: Request, **kwargs):
        stage_id = kwargs.get("pk")

        try:  # Check if the Stage exists
            stage_obj = Stage(stage_id)
        except core_exceptions.StageObjectDoesNotExist:
            raise exceptions.NotFound()

        # Check if the Plan is dynamic
        if not stage_obj.model.plan.dynamic:
            raise exceptions.ValidationError("Manually executing objects under non dynamic Plan is not supported.")

        try:  # Check if the Plan execution exists
            plan_ex_id: int = request.data["plan_execution_id"]
            plan_ex = PlanExecution(plan_ex_id)
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)
        except core_exceptions.PlanExecutionDoesNotExist:
            raise exceptions.NotFound()

        if stage_obj.model.plan.id != plan_ex.model.plan.id:
            raise exceptions.ValidationError(
                f"Incorrect Plan execution. Stage's Plan ID ({stage_obj.model.plan.id}) and Plan execution's "
                f"Plan ID ({plan_ex.model.plan.id}) must match."
            )

        if plan_ex.model.stage_executions.filter(stage=stage_obj.model).exists():
            raise exceptions.ValidationError(
                "Multiple instances of the same Stage can't run under the same Plan " "execution."
            )

        if plan_ex.state not in states.STAGE_PLAN_EXECUTE_STATES:
            raise exceptions.ApiWrongObjectState(
                f"Plan execution's state must be " f"{', or'.join(states.STAGE_PLAN_EXECUTE_STATES)}."
            )

        # Create and start Stage trigger
        stage_ex_obj = StageExecution.prepare(stage_id, plan_ex_id)
        stage_ex_obj.trigger.start()

        msg = {"detail": "Started Stage trigger.", "execution_id": stage_ex_obj.model.id}
        return Response(msg, status=status.HTTP_200_OK)
