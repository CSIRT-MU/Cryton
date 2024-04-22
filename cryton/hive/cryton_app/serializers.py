from rest_framework import serializers

from cryton.hive.cryton_app import models


class BaseSerializer(serializers.Serializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ListSerializer(BaseSerializer):
    order_by = serializers.CharField(required=False, help_text="The parameter used to sort the results.")
    any_returned_parameter = serializers.CharField(
        required=False, help_text="Filter the results using any returned parameter."
    )


class DetailStringSerializer(BaseSerializer):
    detail = serializers.CharField()


class DetailDictionarySerializer(BaseSerializer):
    detail = serializers.DictField()


class CreateDetailSerializer(DetailStringSerializer):
    id = serializers.IntegerField()


class ExecutionCreateDetailSerializer(DetailStringSerializer):
    execution_id = serializers.IntegerField()


class CreateWithFilesSerializer(BaseSerializer):
    file = serializers.FileField()
    inventory_file = serializers.FileField()


class CreateMultipleDetailSerializer(DetailStringSerializer):
    ids = serializers.ListField(child=serializers.IntegerField())


class LogListResponseSerializer(BaseSerializer):
    count = serializers.CharField()
    results = serializers.ListField()


class LogSerializer(BaseSerializer):
    detail = serializers.CharField()


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanModel
        exclude = []


class PlanCreateSerializer(BaseSerializer):
    template_id = serializers.IntegerField()
    file = serializers.FileField()


class PlanExecuteSerializer(BaseSerializer):
    run_id = serializers.IntegerField()
    worker_id = serializers.IntegerField()


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StageModel
        exclude = []


class StageCreateSerializer(CreateWithFilesSerializer):
    plan_id = serializers.IntegerField()


class StageValidateSerializer(CreateWithFilesSerializer):
    dynamic = serializers.CharField(default="false")


class StageStartTriggerSerializer(BaseSerializer):
    plan_execution_id = serializers.IntegerField()


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StepModel
        exclude = []


class StepCreateSerializer(CreateWithFilesSerializer):
    stage_id = serializers.IntegerField()


class StepExecuteSerializer(BaseSerializer):
    stage_execution_id = serializers.IntegerField()


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RunModel
        exclude = []


class RunCreateSerializer(BaseSerializer):
    plan_id = serializers.IntegerField()
    worker_ids = serializers.ListField(child=serializers.IntegerField())


class RunCreateDetailSerializer(CreateDetailSerializer):
    plan_execution_ids = serializers.ListField(child=serializers.IntegerField())


class RunScheduleSerializer(BaseSerializer):
    start_time = serializers.CharField()


class RunPostponeSerializer(BaseSerializer):
    delta = serializers.CharField()


class PlanExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanExecutionModel
        exclude = []


class PlanExecutionListSerializer(ListSerializer):
    run_id = serializers.IntegerField(required=False, help_text="Run ID used to filter the results.")
    plan_model_id = serializers.IntegerField(required=False, help_text="Plan ID used to filter the results.")


class StageExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StageExecutionModel
        exclude = []


class StageExecutionReExecuteSerializer(BaseSerializer):
    immediately = serializers.BooleanField()


class StageExecutionListSerializer(ListSerializer):
    plan_execution_id = serializers.IntegerField(
        required=False, help_text="Plan execution ID used to filter the results."
    )
    stage_model_id = serializers.IntegerField(required=False, help_text="Stage ID used to filter the results.")


class StepExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StepExecutionModel
        exclude = []


class StepExecutionListSerializer(ListSerializer):
    stage_execution_id = serializers.IntegerField(
        required=False, help_text="Stage execution ID used to filter the results."
    )
    step_model_id = serializers.IntegerField(required=False, help_text="Step ID used to filter the results.")


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModel
        exclude = []


class WorkerCreateSerializer(BaseSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    force = serializers.BooleanField()


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SessionModel
        exclude = []


class ExecutionVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutionVariableModel
        exclude = []


class ExecutionVariableCreateSerializer(BaseSerializer):
    plan_execution_id = serializers.IntegerField()
    file = serializers.FileField()


class ExecutionVariableListSerializer(ListSerializer):
    plan_execution_id = serializers.IntegerField(
        required=False, help_text="Plan execution ID used to filter the results."
    )


class SuccessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SuccessorModel
        exclude = []


class CorrelationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CorrelationEventModel
        exclude = []


class PlanTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanTemplateModel
        exclude = []


class OutputMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OutputMappingModel
        exclude = []


class DependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DependencyModel
        exclude = []
