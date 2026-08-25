from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import WorkerModel
from cryton.hive.utility import exceptions as core_exceptions
from cryton.hive.models.worker import Worker


@extend_schema_view(
    list=extend_schema(description="List Workers.", parameters=[serializers.ListSerializer]),
    retrieve=extend_schema(description="Get existing Worker."),
    destroy=extend_schema(description="Delete Worker."),
)
class WorkerViewSet(util.InstanceFullViewSet):
    """
    Worker ViewSet.
    """

    queryset = WorkerModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.WorkerSerializer

    def _destroy(self, model_id: int):
        """
        Delete Worker.
        :param model_id: ID of the desired object
        :return: None
        """
        Worker(model_id).delete()

    @extend_schema(
        description="Create new Worker.",
        request=serializers.WorkerCreateSerializer,
        responses={
            201: serializers.CreateDetailSerializer,
            400: serializers.DetailStringSerializer,
        },
    )
    def create(self, request: Request):
        try:
            name = request.data.get("name", "")
            description = request.data.get("description", "")
            force = request.data.get("force", False)
        except core_exceptions.WrongParameterError as ex:
            raise exceptions.ParseError(ex)

        if not name:
            raise exceptions.ValidationError("Parameter `name` must be defined")

        if not force and WorkerModel.objects.filter(name=name).exists():
            raise exceptions.ValidationError(f"Worker `{name}` already exists")

        worker_obj_id = Worker.create_model(name, description).id

        msg = {"id": worker_obj_id, "detail": "Worker created."}
        return Response(msg, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Check if Worker is responding.",
        request=None,
        responses={
            200: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["post"], detail=True)
    def healthcheck(self, _, **kwargs):
        worker_id = kwargs.get("pk")
        try:
            worker_obj = Worker(worker_id)
        except core_exceptions.WorkerObjectDoesNotExist:
            raise exceptions.NotFound()
        worker_obj.healthcheck()

        msg = {"detail": f"Worker with ID {worker_id} is {worker_obj.state}."}
        return Response(msg, status=status.HTTP_200_OK)
