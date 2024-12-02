from jsonschema import validate

from cryton.hive.utility.schemas import PLAN
from cryton.hive.utility.exceptions import StageCycleDetected, StageValidationError, ValidationError


class Validator:
    def __init__(self, scenario: dict):
        self._scenario = scenario

    def validate(self):
        try:
            self._validate_schema()
            self._validate(self._scenario)
        except Exception as ex:
            raise ValidationError(ex)

    def _validate_schema(self):
        validate(self._scenario, PLAN)

    def _validate(self, scenario: dict):
        # TODO: validate usage of steps/stages in output sharing eg. they exist
        stages: dict[str, dict] = dict()
        stage_dependencies: list[str] = list()
        steps: dict[str, dict] = dict()
        agent_names: list[str] = list()
        used_names: list[str] = ["parent"]
        is_dynamic = scenario.get("dynamic", False)

        # Allow zero stages only if the plan is dynamic
        if not is_dynamic and len(scenario["stages"]) == 0:
            raise ValueError("Plan must have at least one stage.")

        for stage_name, stage in scenario["stages"].items():
            stage_name: str
            stage: dict

            steps_graph = dict()
            init_steps_in_stage = set()
            steps_in_stage = set()
            successors_in_stage = set()

            # Check if stage name is already used
            if stage_name in used_names:
                raise NameError(f"Name {stage_name} is already used.")

            # Add dependencies' names
            if dependencies := stage.get("depends_on"):
                stage_dependencies += dependencies

            # Allow zero steps only if the plan is dynamic
            if not is_dynamic and len(stage["steps"]) == 0:
                raise ValueError("Stage must have at least one step.")

            used_names.append(stage_name)
            stages[stage_name] = stage

            # TODO: if the step is initial (is_init) there can't be parent prefix, add check to validation
            for step_name, step in stage["steps"].items():
                step_name: str
                step: dict

                # Get needed information for reachability check
                if step.get("is_init"):
                    init_steps_in_stage.add(step_name)
                succ_set = set()
                for succ_obj in step.get("next", []):
                    step_successors = succ_obj.get("step")
                    if not isinstance(step_successors, list):
                        step_successors = [step_successors]
                    succ_set.update(step_successors)
                    steps_graph.update({step_name: succ_set})
                successors_in_stage.update(succ_set)
                steps_in_stage.add(step_name)

                # Check if step name is already used
                if step_name in used_names:
                    raise NameError(f"Name {step_name} is already used.")

                # Check if agent name is already used
                if agent_name := step.get("agent_name"):
                    if agent_name in agent_names:
                        raise NameError(f"Name {agent_name} is already used.")
                    agent_names.append(agent_name)

                used_names.append(step_name)
                steps[step_name] = step

            # Check if there is at least one initial steps
            if not is_dynamic and len(init_steps_in_stage) == 0:
                raise StageValidationError(f"Stage {stage_name} has no initial steps.")

            # Check reachability
            reachable_steps = set()
            for init_step in init_steps_in_stage:
                try:
                    reachable_steps.update(self._dfs_reachable(set(), set(), steps_graph, init_step))
                except StageCycleDetected:
                    raise StageValidationError("Cycle detected in Stage", stage_name=stage_name)
            if steps_in_stage != reachable_steps:
                if unreachable_successors := reachable_steps.difference(steps_in_stage):
                    raise StageValidationError(
                        f"The following successors in stage {stage_name} are unreachable: {unreachable_successors}.",
                    )
                else:
                    raise StageValidationError(
                        f"The following steps in stage {stage_name} are unreachable: {steps_in_stage.difference(reachable_steps)}.",
                    )

            # Check that initial steps are not set as successors
            if invalid_steps := init_steps_in_stage.intersection(successors_in_stage):
                raise StageValidationError(f"The following initial steps are set as successors: {invalid_steps}.")

        # Check if stage dependencies exist
        for stage_dependency in stage_dependencies:
            if stage_dependency not in stages.keys():
                raise NameError(f"Stage {stage_dependency} is not defined.")

    def _dfs_reachable(self, visited: set, completed: set, nodes_pairs: dict, node: str) -> set:
        """
        Depth first search of reachable nodes
        :param visited: set of visited nodes
        :param completed: set of completed nodes
        :param nodes_pairs: stage successors representation ({parent: [successors]})
        :param node: current node
        :return:
        """
        if node in visited and node not in completed:
            raise StageCycleDetected("Stage cycle detected.")
        if node in completed:
            return completed
        visited.add(node)
        for neighbour in nodes_pairs.get(node, []):
            self._dfs_reachable(visited, completed, nodes_pairs, neighbour)
        completed.add(node)
        # completed and visited should be the same

        return completed
