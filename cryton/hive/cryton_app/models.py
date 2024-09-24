from django.db import models

from cryton.hive.utility import states
from cryton.hive.config.settings import UPLOAD_DIRECTORY_RELATIVE


class TimedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InstanceModel(TimedModel):
    name = models.TextField()

    class Meta:
        abstract = True


class ExecutionModel(TimedModel):
    state = models.TextField(default=states.PENDING)
    start_time = models.DateTimeField(null=True)
    pause_time = models.DateTimeField(null=True)
    finish_time = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class SchedulableExecutionModel(ExecutionModel):
    schedule_time = models.DateTimeField(null=True)
    job_id = models.TextField()

    class Meta:
        abstract = True


class DescriptiveModel(InstanceModel):
    metadata = models.JSONField()

    class Meta:
        abstract = True


class OutputModel(models.Model):
    serialized_output = models.JSONField(default=dict)  # TODO: serialized_output -> output?
    output = models.TextField(default="")  # TODO: output -> debug_output?

    class Meta:
        abstract = True


class PlanSettings(models.Model):
    separator = models.TextField()


class PlanModel(DescriptiveModel):
    settings = models.OneToOneField(PlanSettings, models.CASCADE)
    dynamic = models.BooleanField(default=False)


class StageModel(DescriptiveModel):
    plan = models.ForeignKey(PlanModel, models.CASCADE, related_name="stages")
    type = models.TextField()
    arguments = models.JSONField()


class StepOutputSettingsModel(models.Model):
    alias = models.TextField()
    replace = models.JSONField()


class OutputMappingModel(models.Model):
    output_settings = models.ForeignKey(StepOutputSettingsModel, models.CASCADE, related_name="mappings")
    name_from = models.TextField()
    name_to = models.TextField()


class StepModel(DescriptiveModel):
    stage = models.ForeignKey(StageModel, models.CASCADE, related_name="steps")
    is_init = models.BooleanField()
    is_final = models.BooleanField()
    output_settings = models.OneToOneField(StepOutputSettingsModel, models.CASCADE)
    module = models.TextField()
    arguments = models.JSONField()


class WorkerModel(InstanceModel):
    description = models.TextField()
    state = models.TextField(default=states.DOWN)


class RunModel(SchedulableExecutionModel):
    plan = models.ForeignKey(PlanModel, models.CASCADE, related_name="runs")


class PlanExecutionModel(SchedulableExecutionModel):
    run = models.ForeignKey(RunModel, models.CASCADE, related_name="plan_executions")
    plan = models.ForeignKey(PlanModel, models.CASCADE, related_name="plan_executions")
    worker = models.ForeignKey(WorkerModel, models.PROTECT, related_name="plan_executions")
    evidence_directory = models.TextField()


class StageExecutionModel(SchedulableExecutionModel, OutputModel):
    plan_execution = models.ForeignKey(PlanExecutionModel, models.CASCADE, related_name="stage_executions")
    stage = models.ForeignKey(StageModel, models.CASCADE, related_name="stage_executions")
    trigger_id = models.TextField()


class StepExecutionModel(ExecutionModel, OutputModel):
    stage_execution = models.ForeignKey(StageExecutionModel, models.CASCADE, related_name="step_executions")
    step = models.ForeignKey(StepModel, models.CASCADE, related_name="step_executions")
    result = models.TextField(default="")
    valid = models.BooleanField(default=False)
    parent = models.ForeignKey("self", models.CASCADE, null=True)


class ExecutionVariableModel(InstanceModel):
    plan_execution = models.ForeignKey(PlanExecutionModel, models.CASCADE, related_name="execution_variables")
    value = models.JSONField()


class SuccessorModel(models.Model):
    type = models.TextField()
    value = models.TextField()
    parent = models.ForeignKey(StepModel, models.CASCADE, related_name="successors")
    successor = models.ForeignKey(StepModel, models.CASCADE, related_name="parents")


class CorrelationEventModel(models.Model):
    correlation_id = models.TextField()
    step_execution = models.ForeignKey(StepExecutionModel, models.CASCADE, related_name="correlation_events")


class PlanTemplateModel(models.Model):
    file = models.FileField(upload_to=UPLOAD_DIRECTORY_RELATIVE)


class StageDependencyModel(models.Model):
    stage = models.ForeignKey(StageModel, models.CASCADE, related_name="dependencies")
    dependency = models.ForeignKey(StageModel, models.CASCADE, related_name="subjects_to")
