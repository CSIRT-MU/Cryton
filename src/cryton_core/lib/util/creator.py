from typing import Union

from cryton_core.lib.util import exceptions, logger
from cryton_core.lib.models import stage, plan, step, worker
from cryton_core.cryton_app.models import OutputMappingModel


def create_plan(template: dict) -> int:
    """
    Check if Plan structure is correct and add it to DB.
    :param template: Plan from file ({"plan": ... })
    :return:  Added Plan object ID
    :raises
        exceptions.ValidationError
        exceptions.PlanCreationFailedError
    """
    # Validate plan template.
    plan_dict = template.get("plan")
    is_plan_dynamic = plan_dict.get("dynamic")

    plan.Plan.validate(plan_dict, is_plan_dynamic)

    # Get defaults.
    plan_name = plan_dict.get("name")
    stages_list = plan_dict.pop("stages")

    # Create Plan object.
    plan_obj = plan.Plan(**plan_dict)
    plan_obj_id = plan_obj.model.id

    # Create Stages.
    for stage_dict in stages_list:
        try:
            stage_obj_id = create_stage(stage_dict, plan_obj_id)
            stage_dict.update({"stage_model_id": stage_obj_id})
        except Exception as ex:
            plan_obj.delete()
            raise exceptions.PlanCreationFailedError(message=ex, plan_name=plan_name)

    # Create Stage dependencies.
    for stage_dict in stages_list:
        stage_id = stage_dict.get("stage_model_id")
        stage_dependencies = stage_dict.get("depends_on", [])
        stage_obj = stage.Stage(stage_model_id=stage_id)

        for dependency_name in stage_dependencies:
            try:
                dependency_id = stage.StageModel.objects.get(name=dependency_name, plan_model_id=plan_obj_id).id
            except stage.StageModel.DoesNotExist as ex:
                plan_obj.delete()
                raise exceptions.DependencyDoesNotExist(message=ex, stage_name=dependency_name)

            stage_obj.add_dependency(dependency_id)

    logger.logger.info("plan created", plan_name=plan_obj.name, plan_id=plan_obj_id, status="success")

    return plan_obj_id


def create_stage(stage_dict: dict, plan_model_id: int) -> int:
    """
    Add Stage to DB.
    :param stage_dict: Stage dictionary
    :param plan_model_id: Plan ID
    :return: Added Stage object ID
    :raises
        exceptions.StageCreationFailedError
    """
    stage_dict.update({"plan_model_id": plan_model_id})
    steps_list = stage_dict.pop("steps")

    # Create Stage object.
    stage_obj = stage.Stage(**stage_dict)
    stage_obj_id = stage_obj.model.id

    # Create Steps.
    for step_dict in steps_list:
        step_obj_id = create_step(step_dict, stage_obj_id)
        step_dict.update({"step_model_id": step_obj_id})

    # Create Successors.
    for step_dict in steps_list:
        step_id = step_dict.get("step_model_id")
        step_successor_list = step_dict.get("next", [])
        step_obj = step.Step(step_model_id=step_id)

        # Set Step successors.
        for step_successor in step_successor_list:
            successors, s_type, s_values = (step_successor.get(key) for key in ["step", "type", "value"])
            if not isinstance(successors, list):
                successors = [successors]

            for successor_name in successors:
                create_successor(step_obj, stage_obj_id, successor_name, s_type, s_values)

    logger.logger.info("stage created", stage_name=stage_obj.name, stage_id=stage_obj_id, status="success")

    return stage_obj_id


def create_step(step_dict: dict, stage_model_id: int) -> int:
    """
    Add Step to DB.
    :param step_dict: Step dictionary
    :param stage_model_id: Stage ID
    :return: Added Step object ID
    """
    step_dict.update({"stage_model_id": stage_model_id})

    # Set 'is_final' flag.
    step_successor_list = step_dict.get("next", [])
    if len(step_successor_list) == 0:
        step_dict.update({"is_final": True})

    # Create Step object.
    step_obj = step.Step(**step_dict)
    step_model_id = step_obj.model.id

    # Create OutputMappings.
    output_mappings = step_dict.get("output_mapping", [])
    for output_mapping in output_mappings:
        create_output_mapping(output_mapping, step_model_id)

    logger.logger.info("step created", step_name=step_obj.name, step_id=step_model_id, status="success")

    return step_model_id


def create_successor(parent_step: step.Step, stage_id: int, successor_name: str, successor_type: str,
                     successor_values: Union[list, str]):
    """
    Add successor and its links between parent and successor Step to DB.
    :param parent_step: Parent Step
    :param stage_id: Stage ID
    :param successor_name: Successor's name
    :param successor_type: Successor's type
    :param successor_values: Successor's values (or just one)
    :return: None
    :raises:
        exceptions.InvalidSuccessorType
        exceptions.InvalidSuccessorValue
        exceptions.SuccessorCreationFailedError
    """
    try:
        successor_step_id = step.StepModel.objects.get(name=successor_name, stage_model_id=stage_id).id
    except step.StepModel.DoesNotExist as ex:
        raise exceptions.SuccessorCreationFailedError(message=ex, successor_name=successor_name)

    if not isinstance(successor_values, list):
        successor_values = [successor_values]

    for successor_value in successor_values:
        parent_step.add_successor(successor_step_id, successor_type, successor_value)


def create_output_mapping(output_mapping: dict, step_model_id: int):
    """
    Add output mapping for Step to DB.
    :param output_mapping: Output mapping
    :param step_model_id: Step ID
    :return: None
    """
    name_from = output_mapping.get("name_from")
    name_to = output_mapping.get("name_to")
    OutputMappingModel.objects.create(step_model_id=step_model_id, name_from=name_from, name_to=name_to)


def create_worker(name: str, description: str, force: bool = False) -> int:
    """
    Update prefix and add Worker to DB.
    :param name: Worker's name
    :param description: Worker's description
    :param force: If True, name won't have to be unique
    :return: Added Worker object ID
    """
    if name == "":
        raise exceptions.WrongParameterError(message="Parameter cannot be empty", param_name="name")

    elif not force and worker.WorkerModel.objects.filter(name=name).exists():
        raise exceptions.WrongParameterError(message="Inserted Worker with such parameter already exists",
                                             param_name="name")

    worker_obj = worker.Worker(name=name, description=description)
    return worker_obj.model.id
