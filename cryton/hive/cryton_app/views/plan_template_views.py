from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from cryton.hive.cryton_app import util, serializers, exceptions
from cryton.hive.cryton_app.models import PlanTemplateModel


@extend_schema_view(
    list=extend_schema(description="List templates.", parameters=[serializers.ListSerializer]),
    create=extend_schema(
        description="Create new template.",
        examples=[
            OpenApiExample(
                "File upload",
                description="Upload template file.",
                value={
                    "file": "file content in bytes format",
                },
                request_only=True,
            )
        ],
    ),
    retrieve=extend_schema(description="Get existing template."),
    destroy=extend_schema(description="Delete template."),
)
class PlanTemplateViewSet(util.InstanceFullViewSet):
    """
    Plan's template ViewSet.
    """

    queryset = PlanTemplateModel.objects.all()
    http_method_names = ["get", "post", "delete"]
    serializer_class = serializers.PlanTemplateSerializer

    def _destroy(self, model_id: int):
        """
        Delete template.
        :param model_id: ID of the desired object
        :return: None
        """
        PlanTemplateModel.objects.get(id=model_id).delete()

    @extend_schema(
        description="Get template (its YAML).",
        responses={
            200: serializers.DetailStringSerializer,
            404: serializers.DetailStringSerializer,
            500: serializers.DetailStringSerializer,
        },
    )
    @action(methods=["get"], detail=True)
    def get_template(self, _, **kwargs):
        template_id = kwargs.get("pk")
        try:
            plan_template_obj = PlanTemplateModel.objects.get(id=template_id)
        except PlanTemplateModel.DoesNotExist:
            raise exceptions.NotFound(detail=f"Template with ID {template_id} does not exist.")

        try:
            with open(str(plan_template_obj.file.path)) as template_file:
                plan_template = template_file.read()
        except IOError:
            raise exceptions.APIException("Couldn't read the template file.")

        msg = {"detail": plan_template}
        return Response(msg, status=status.HTTP_200_OK)
