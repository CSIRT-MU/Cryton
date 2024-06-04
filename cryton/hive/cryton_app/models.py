from django.db import models

from cryton.hive.utility import states as st
from cryton.hive.config.settings import UPLOAD_DIRECTORY_RELATIVE


class AdvancedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InstanceModel(AdvancedModel):
    name = models.TextField()

    class Meta:
        abstract = True


class ExecutionModel(AdvancedModel):
    state = models.TextField(default=st.PENDING)
    start_time = models.DateTimeField(null=True)
    pause_time = models.DateTimeField(null=True)
    finish_time = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class ExtendedExecutionModel(ExecutionModel):
    schedule_time = models.DateTimeField(null=True)
    aps_job_id = models.TextField()

    class Meta:
        abstract = True


class DescriptiveModel(InstanceModel):
    meta = models.JSONField(default=dict)

    class Meta:
        abstract = True


class PlanModel(DescriptiveModel):
    owner = models.TextField()
    settings = models.JSONField(default=dict)
    dynamic = models.BooleanField(default=False)


class StageModel(DescriptiveModel):
    plan_model = models.ForeignKey(PlanModel, on_delete=models.CASCADE, related_name="stages")
    trigger_type = models.TextField()
    trigger_args = models.JSONField()


class StepModel(DescriptiveModel):
    stage_model = models.ForeignKey(StageModel, on_delete=models.CASCADE, related_name="steps")
    step_type = models.TextField()
    arguments = models.JSONField()
    is_init = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    output_prefix = models.TextField()
    output = models.JSONField(default=dict)


class WorkerModel(InstanceModel):
    description = models.TextField()
    state = models.TextField(default=st.DOWN)


class RunModel(ExtendedExecutionModel):
    plan_model = models.ForeignKey(PlanModel, on_delete=models.CASCADE, related_name="runs")


class PlanExecutionModel(ExtendedExecutionModel):
    run = models.ForeignKey(RunModel, on_delete=models.CASCADE, related_name="plan_executions")
    plan_model = models.ForeignKey(PlanModel, on_delete=models.CASCADE, related_name="plan_executions")
    worker = models.ForeignKey(WorkerModel, related_name="plan_executions", on_delete=models.PROTECT)
    evidence_directory = models.TextField()


class StageExecutionModel(ExtendedExecutionModel):
    plan_execution = models.ForeignKey(PlanExecutionModel, on_delete=models.CASCADE, related_name="stage_executions")
    stage_model = models.ForeignKey(StageModel, on_delete=models.CASCADE, related_name="stage_executions")
    trigger_id = models.TextField()


class StepExecutionModel(ExecutionModel):
    stage_execution = models.ForeignKey(StageExecutionModel, on_delete=models.CASCADE, related_name="step_executions")
    step_model = models.ForeignKey(StepModel, on_delete=models.CASCADE, related_name="step_executions")
    result = models.TextField(default="")
    serialized_output = models.JSONField(default=dict)
    output = models.TextField(default="")
    valid = models.BooleanField(default=False)
    parent_id = models.IntegerField(null=True)


class SessionModel(InstanceModel):
    plan_execution = models.ForeignKey(PlanExecutionModel, on_delete=models.CASCADE, related_name="sessions")
    msf_id = models.TextField()


class ExecutionVariableModel(InstanceModel):
    plan_execution = models.ForeignKey(PlanExecutionModel, on_delete=models.CASCADE, related_name="execution_variables")
    value = models.JSONField()


class SuccessorModel(models.Model):
    type = models.TextField()
    value = models.TextField()
    parent = models.ForeignKey(StepModel, related_name="successors", on_delete=models.CASCADE)
    successor = models.ForeignKey(StepModel, related_name="parents", on_delete=models.CASCADE)


class CorrelationEventModel(models.Model):
    correlation_id = models.TextField()
    step_execution = models.ForeignKey(StepExecutionModel, on_delete=models.CASCADE, related_name="correlation_events")


class PlanTemplateModel(models.Model):
    file = models.FileField(upload_to=UPLOAD_DIRECTORY_RELATIVE)


class OutputMappingModel(models.Model):
    step_model = models.ForeignKey(StepModel, on_delete=models.CASCADE, related_name="output_mappings")
    name_from = models.TextField()
    name_to = models.TextField()


class DependencyModel(models.Model):
    stage_model = models.ForeignKey(StageModel, related_name="dependencies", on_delete=models.CASCADE)
    dependency = models.ForeignKey(StageModel, related_name="subjects_to", on_delete=models.CASCADE)
