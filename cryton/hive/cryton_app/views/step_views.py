from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import StepModel
from cryton.hive.utility import exceptions as core_exceptions, creator, states
from cryton.hive.models.step import Step, StepExecution, StepExecutionType
from cryton.hive.models.stage import Stage, StageExecution


@extend_schema_view(
    list=extend_schema(description="List Steps.", parameters=[serializers.ListSerializer]),
    retrieve=extend_schema(description="Get existing Step."),
    destroy=extend_schema(description="Delete Step."),
)
class StepViewSet(util.InstanceFullViewSet):
    """
    Step ViewSet.
    """

    queryset = StepModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.StepSerializer

    def _destroy(self, model_id: int):
        """
        Delete Step.
        :param model_id: ID of the desired object
        :return: None
        """
        Step(step_model_id=model_id).delete()

    @extend_schema(
        description="Create Step under Stage. There is no limit or naming convention for inventory files.",
        request=serializers.StepCreateSerializer,
        responses={
            200: serializers.CreateDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    def create(self, request: Request, *args, **kwargs):
        try:  # Get Stage ID and check if the Stage exists
            stage_id: int = request.data["stage_id"]
            stage_obj = Stage(stage_model_id=stage_id)
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)
        except core_exceptions.StageObjectDoesNotExist:
            raise exceptions.NotFound()

        # Check if the Plan is dynamic
        plan_model_obj = stage_obj.model.plan_model
        if not plan_model_obj.dynamic:
            raise exceptions.ValidationError("Creating objects under non dynamic Plan is not supported.")

        step_data = util.parse_object_from_files(request.FILES)

        # Check if the name is unique
        step_name = step_data.get("name")
        if StepModel.objects.filter(stage_model__plan_model_id=plan_model_obj.id, name=step_name).exists():
            raise exceptions.ValidationError(f"Step with the name `{step_name}` already exists.")

        # Validate Step
        try:
            Step.validate(step_data)
        except core_exceptions.ValidationError as ex:
            raise exceptions.ValidationError(ex)

        # Create a Step
        parent_step_model = stage_obj.model.steps.last()
        step_id = creator.create_step(step_data, stage_id)
        step_obj = Step(step_model_id=step_id)

        # Mark the new Step as a successor
        if not step_obj.is_init and parent_step_model is not None:
            parent_step = Step(step_model_id=parent_step_model.id)
            creator.create_successor(parent_step, stage_id, step_name, "any", "")

        msg = {"id": step_id, "detail": "Step successfully created."}
        return Response(msg, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Validate Step YAML. There is no limit or naming convention for inventory files.",
        request=serializers.CreateWithFilesSerializer,
        responses={200: serializers.DetailStringSerializer, 400: serializers.DetailStringSerializer},
    )
    @action(methods=["post"], detail=False)
    def validate(self, request: Request):
        step_data = util.parse_object_from_files(request.FILES)

        try:
            Step.validate(step_data)
        except (core_exceptions.ValidationError, core_exceptions.StepTypeDoesNotExist) as ex:
            raise exceptions.ValidationError(f"Step is not valid. Original error: {ex}")

        msg = {"detail": "Step is valid."}
        return Response(msg, status=status.HTTP_200_OK)

    @extend_schema(
        description="Execute Step under Stage execution.",
        request=serializers.StepExecuteSerializer,
        responses={
            200: serializers.ExecutionCreateDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def execute(self, request: Request, **kwargs):
        step_id = kwargs.get("pk")

        try:  # Check if the Step exists
            step_obj = Step(step_model_id=step_id)
        except core_exceptions.StepObjectDoesNotExist:
            raise exceptions.NotFound()

        # Check if the Plan is dynamic
        if not step_obj.model.stage_model.plan_model.dynamic:
            raise exceptions.ValidationError("Manually executing objects under non dynamic Plan is not supported.")

        try:  # Check if the Stage execution exists
            stage_ex_id: int = request.data["stage_execution_id"]
            stage_ex = StageExecution(stage_execution_id=stage_ex_id)
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)
        except core_exceptions.StageExecutionObjectDoesNotExist:
            raise exceptions.NotFound()

        if step_obj.model.stage_model.id != stage_ex.model.stage_model.id:
            raise exceptions.ValidationError(
                f"Incorrect Stage execution. Step's Stage ID ({step_obj.model.stage_model.id}) and Stage execution's "
                f"Stage ID ({stage_ex.model.stage_model.id}) must match."
            )

        if stage_ex.model.step_executions.filter(step_model=step_obj.model).exists():
            raise exceptions.ValidationError(
                "Multiple instances of the same Step can't run under the same Stage " "execution."
            )

        if stage_ex.state not in states.STEP_STAGE_EXECUTE_STATES:
            raise exceptions.ApiWrongObjectState(
                f"Stage execution's state must be " f"{', or'.join(states.STEP_STAGE_EXECUTE_STATES)}."
            )

        # Create and start Step execution
        step_ex_obj = StepExecution(step_model_id=step_id, stage_execution_id=stage_ex_id)
        step_ex_obj_typed = StepExecutionType[step_ex_obj.model.step_model.step_type].value(
            step_execution_id=step_ex_obj.model.id
        )
        step_ex_obj_typed.execute()

        msg = {"detail": "Started Step execution.", "execution_id": step_ex_obj.model.id}
        return Response(msg, status=status.HTTP_200_OK)
