from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from cryton_core.cryton_app import util, serializers, exceptions
from cryton_core.cryton_app.models import ExecutionVariableModel, PlanExecutionModel


@extend_schema_view(
    list=extend_schema(description="List execution variables.",
                       parameters=[serializers.ExecutionVariableListSerializer]),
    retrieve=extend_schema(description="Get existing execution variable."),
    destroy=extend_schema(description="Delete execution variable.")
)
class ExecutionVariableViewSet(util.InstanceFullViewSet):
    """
    ExecutionVariable ViewSet.
    """
    queryset = ExecutionVariableModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.ExecutionVariableSerializer

    def _destroy(self, model_id: int):
        """
        Delete execution variable.
        :param model_id: ID of the desired object
        :return: None
        """
        ExecutionVariableModel.objects.get(id=model_id).delete()

    @extend_schema(
        description="Load all uploaded files (there is no limit or naming convention) and create "
                    "execution variables from them.",
        request=serializers.ExecutionVariableCreateSerializer,
        examples=[
            OpenApiExample(
                "Multiple files upload",
                description="Uploading multiple files containing execution variables.",
                value={
                    'plan_execution_id': 1,
                    'file1': "file content in bytes format",
                    'file2': "file content in bytes format",
                },
                request_only=True
            )
        ],
        responses={
            201: serializers.CreateMultipleDetailSerializer,
            400: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
            500: serializers.DetailStringSerializer,
        }
    )
    def create(self, request: Request):
        # Get PlanExecution ID for the execution Variables
        try:
            plan_execution_id = int(request.data['plan_execution_id'])
        except (KeyError, ValueError, TypeError) as ex:
            raise exceptions.ValidationError(ex)

        try:
            PlanExecutionModel.objects.get(id=plan_execution_id)
        except PlanExecutionModel.DoesNotExist:
            raise exceptions.NotFound(f"Nonexistent plan_execution_id: {plan_execution_id}.")

        execution_variables = util.get_inventory_variables_from_files(request.FILES)
        created_exec_vars = []
        for name, value in execution_variables.items():
            params = {'plan_execution_id': plan_execution_id, 'name': name, 'value': value}
            exec_var_model = ExecutionVariableModel.objects.create(**params)
            created_exec_vars.append(exec_var_model.id)

        msg = {'ids': created_exec_vars, 'detail': 'Execution variables created.'}
        return Response(msg, status=status.HTTP_201_CREATED)
