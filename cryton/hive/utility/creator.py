from cryton.hive.utility import logger
from cryton.hive.models import Plan, Stage, Step
from cryton.hive.cryton_app.models import StageDependencyModel, PlanModel, StageModel, SuccessorModel, StepModel


def create_plan(template: dict) -> int:
    """
    Parse filled template into plan.
    We are expecting validated and sanitized data.
    :param template: Plan from file ({"name": ... })
    :return:  Added Plan object ID
    :raises
        exceptions.PlanCreationFailedError
    """
    plan = Plan.create_model(
        template["name"], template.get("settings", {}), template.get("dynamic", False), template.get("metadata", {})
    )
    create_stages(plan, template.get("stages", {}))
    logger.logger.info("plan created", name=plan.name, id=plan.id)

    return plan.id


def create_stages(plan: PlanModel, stages: dict) -> list[int]:
    stage_dependencies: dict = {}
    for stage_name, stage_data in stages.items():
        stage_obj = create_stage(plan.id, stage_name, stage_data)
        stage_dependencies[stage_obj.id] = stage_data.get("depends_on", [])

        create_steps(stage_obj, stage_data.get("steps", {}))

    create_dependencies(plan, stage_dependencies)

    return list(stage_dependencies.keys())


def create_dependencies(plan: PlanModel, stage_dependencies: dict):
    plan_stages = StageModel.objects.filter(plan=plan)
    for stage_id, dependencies in stage_dependencies.items():
        if not dependencies:
            continue
        for dependency in dependencies:
            StageDependencyModel.objects.create(
                stage_id=stage_id, dependency=plan_stages.get(plan=plan, name=dependency)
            )


def create_stage(plan_id: int, name: str, data: dict):
    return Stage.create_model(
        plan_id, name, data.get("type", "immediate"), data.get("arguments", {}), data.get("metadata", {})
    )


def create_steps(stage: StageModel, steps: dict) -> list[int]:
    step_successors = {}
    for step_name, step_data in steps.items():
        step = create_step(stage.id, step_name, step_data)
        step_successors[step.id] = step_data.get("next", [])

    create_successors(stage, step_successors)

    return list(step_successors.keys())


def create_successors(stage: StageModel, step_successors: dict):
    stage_steps = StepModel.objects.filter(stage=stage)
    for step_parent_id, options in step_successors.items():
        for option in options:
            successors = option["step"]
            if not isinstance(successors, list):
                successors = [successors]
            for successor in successors:
                SuccessorModel.objects.create(
                    type=option["type"],
                    parent_id=step_parent_id,
                    successor=stage_steps.get(name=successor),
                    value=option.get("value", ""),
                )


def create_step(stage_id: int, name: str, data: dict):
    return Step.create_model(
        stage_id,
        name,
        data["module"],
        data.get("is_init", False),
        True if not data.get("next", []) else False,
        data.get("arguments", {}),
        data.get("output", {}),
        data.get("metadata", {}),
    )
