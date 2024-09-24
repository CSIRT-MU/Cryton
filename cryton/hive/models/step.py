import json
from datetime import datetime
from typing import Union, Type, Optional
import re
import copy
import yaml
import amqpstorm
from jinja2 import nativetypes, StrictUndefined, UndefinedError

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.query import QuerySet
from django.core import exceptions as django_exc
from django.utils import timezone

from cryton.hive.cryton_app.models import (
    StepModel,
    StepExecutionModel,
    SuccessorModel,
    ExecutionVariableModel,
    CorrelationEventModel,
    StepOutputSettingsModel,
    OutputMappingModel,
    StageExecutionModel,
)

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import constants, exceptions, logger, states, util, rabbit_client
from cryton.hive.models import worker
from cryton.lib.utility.enums import Result

from dataclasses import dataclass, asdict


@dataclass
class StepReport:
    id: int
    name: str
    metadata: dict
    state: str
    start_time: datetime
    finish_time: datetime
    output: str
    serialized_output: dict
    result: str
    valid: bool


class Step:
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = StepModel.objects.get(id=model_id)

    @staticmethod
    def create_model(
        stage_id: int,
        name: str,
        module: str,
        is_init: bool,
        is_final: bool,
        arguments: dict,
        output_settings: dict,
        metadata: dict,
    ) -> StepModel:
        output_settings_model = StepOutputSettingsModel.objects.create(
            alias=output_settings.get("alias", ""), replace=output_settings.get("replace", {})
        )

        for mapping in output_settings.get("mapping", []):
            OutputMappingModel.objects.create(
                output_settings=output_settings_model, name_from=mapping["from"], name_to=mapping["to"]
            )

        return StepModel.objects.create(
            stage_id=stage_id,
            name=name,
            metadata=metadata,
            module=module,
            arguments=arguments,
            is_init=is_init,
            is_final=is_final,
            output_settings=output_settings_model,
        )

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[StepModel], StepModel]:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value: str):
        model = self.model
        model.name = value
        model.save()

    @property
    def is_init(self) -> bool:
        return self.model.is_init

    @is_init.setter
    def is_init(self, value: bool):
        model = self.model
        model.is_init = value
        model.save()

    @property
    def arguments(self) -> dict:
        return self.model.arguments

    @arguments.setter
    def arguments(self, value: dict):
        model = self.model
        model.arguments = value
        model.save()

    @property
    def meta(self) -> dict:
        return self.model.metadata

    @meta.setter
    def meta(self, value: dict):
        model = self.model
        model.metadata = value
        model.save()

    @property
    def execution_stats_list(self) -> QuerySet:
        """
        Returns StepExecutionStatsModel QuerySet. If the latest is needed, use '.latest()' on result.
        :return: QuerySet of StepExecutionStatsModel
        """
        return StepExecutionModel.objects.filter(step_id=self.model.id)

    @property
    def parents(self) -> QuerySet:
        return StepModel.objects.filter(
            id__in=SuccessorModel.objects.filter(successor_id=self.model.id).values_list("parent_id")
        )

    @property
    def successors(self) -> QuerySet:
        return StepModel.objects.filter(
            id__in=SuccessorModel.objects.filter(parent_id=self.model.id).values_list("successor_id")
        )

    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        Get list of StepInstances according to no or specified conditions
        :param kwargs: dict of parameters to filter by
        :return:
        """
        if kwargs:
            try:
                return StepModel.objects.filter(**kwargs)
            except django_exc.FieldError as ex:
                raise exceptions.WrongParameterError(message=ex)
        else:
            return StepModel.objects.all()

    def add_successor(self, successor_id: int, successor_type: str, successor_value: Optional[str]) -> int:
        """
        Check if successor's parameters are correct and save it.
        :param successor_id:
        :param successor_type: One of valid types
        :param successor_value: One of valid values for specified type
        :raises:
            InvalidSuccessorType
            InvalidSuccessorValue
        :return: SuccessorModel id
        """
        if successor_type == constants.ANY and successor_value is None:
            successor_value = ""

        successor = SuccessorModel(
            parent_id=self.model.id, successor_id=successor_id, type=successor_type, value=successor_value
        )
        successor.save()

        logger.logger.debug("Step successor created", step_id=self.model.id, step_successor_id=successor_id)

        return successor.id


class StepExecution:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        (optional) step_execution_id: int - for retrieving existing execution
        step_id: int - for creating new execution
        """
        step_execution_id = kwargs.get("step_execution_id")
        if step_execution_id is not None:
            try:
                self.model = StepExecutionModel.objects.get(id=step_execution_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.StepExecutionObjectDoesNotExist(
                    "StepExecutionStatsModel with id {} does not exist.".format(step_execution_id)
                )

        else:
            self.model = StepExecutionModel.objects.create(**kwargs)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[StepExecutionModel], StepExecutionModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: StepExecutionModel):
        self.__model = value

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            StepExecutionModel.objects.select_for_update().get(id=self.model.id)
            if states.StepStateMachine(self.model.id).validate_transition(self.state, value):
                logger.logger.debug(
                    "Step execution changed state",
                    step_execution_id=self.model.id,
                    state_from=self.state,
                    state_to=value,
                )
                model = self.model
                model.state = value
                model.save()

    @property
    def result(self) -> str:
        return self.model.result

    @result.setter
    def result(self, value: str):
        model = self.model
        model.result = value
        model.save()

    @property
    def output(self) -> str:
        return self.model.output

    @output.setter
    def output(self, value: str):
        model = self.model
        model.output = value
        model.save()

    @property
    def serialized_output(self) -> Union[list, dict]:
        return self.model.serialized_output

    @serialized_output.setter
    def serialized_output(self, value: Union[list, dict]):
        model = self.model
        model.serialized_output = value
        model.save()

    @property
    def start_time(self) -> Optional[datetime]:
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: Optional[datetime]):
        model = self.model
        model.start_time = value
        model.save()

    @property
    def finish_time(self) -> Optional[datetime]:
        return self.model.finish_time

    @finish_time.setter
    def finish_time(self, value: Optional[datetime]):
        model = self.model
        model.finish_time = value
        model.save()

    @property
    def valid(self) -> bool:
        return self.model.valid

    @valid.setter
    def valid(self, value: bool):
        model = self.model
        model.valid = value
        model.save()

    @property
    def parent(self) -> StepExecutionModel:
        return self.model.parent

    @parent.setter
    def parent(self, value: StepExecutionModel):
        model = self.model
        model.parent = value
        model.save()

    @staticmethod
    def filter(**kwargs) -> QuerySet:
        """
        Get list of StepExecutionStatsModel according to specified conditions.
        :param kwargs: dict of parameters to filter by
        :return: Desired QuerySet
        """
        if kwargs:
            try:
                return StepExecutionModel.objects.filter(**kwargs)
            except django_exc.FieldError as ex:
                raise exceptions.WrongParameterError(message=ex)
        else:
            return StepExecutionModel.objects.all()

    def validate(self) -> bool:
        """
        Validate cryton attack module arguments.
        :return:
        """
        logger.logger.debug("Validating Cryton module", step_id=self.model.step.id)
        target_queue = worker.Worker(self.model.stage_execution.plan_execution.worker.id).control_q_name
        message = {
            constants.EVENT_T: constants.EVENT_VALIDATE_MODULE,
            constants.EVENT_V: {
                constants.MODULE: self.model.step.module,
                constants.ARGUMENTS: self.model.step.arguments,  # TODO: won't be valid in case we use execution_variables, this is a bug!
            },
        }

        with rabbit_client.RpcClient() as rpc_client:
            response = rpc_client.call(target_queue, message)

        if response.get(constants.EVENT_V).get(constants.RESULT) == Result.OK:
            self.valid = True

        return self.valid

    def save_output(self, step_output: dict) -> None:
        """
        Save Step execution output to StepExecutionModel.
        :param step_output: dictionary with keys: output, serialized_output
        :return: None
        """
        if (serialized_output := step_output.get(constants.SERIALIZED_OUTPUT)) is not None:
            for mapping in self.model.step.output_settings.mappings.all():
                util.rename_key(serialized_output, mapping.name_from, mapping.name_to)

        model = self.model

        if serialized_output is not None:
            model.serialized_output = serialized_output
        if (output := step_output.get(constants.OUTPUT)) is not None:
            model.output = output

        model.save()

    def _update_dynamic_variables(self, arguments: dict) -> dict:
        """
        Update dynamic variables in mod_args (even with special $parent prefix)
        :param arguments: arguments that should be updated
        :return: Arguments updated for dynamic variables
        """
        logger.logger.debug("Updating step arguments with dynamic variables", step_execution_id=self.model.id)
        dynamic_variable_separator = self.model.step.stage.plan.settings.separator

        variable_definitions = util.get_dynamic_variables(arguments)
        prefixes = util.get_prefixes(variable_definitions, dynamic_variable_separator)
        variables: dict[str, dict] = dict()
        executions = StepExecutionModel.objects.filter(
            stage_execution__plan_execution=self.model.stage_execution.plan_execution
        ).order_by("finish_time")
        for prefix in prefixes:
            if prefix == "parent":
                variables.update({prefix: self.parent.serialized_output})
                continue

            prefix_variables = dict()
            for execution in executions.filter(step__name=prefix):
                prefix_variables.update(execution.serialized_output)
            for execution in executions.filter(step__output_settings__alias=prefix):
                prefix_variables.update(execution.serialized_output)
            if stage_ex := StageExecutionModel.objects.filter(
                stage__name=prefix, plan_execution=self.model.stage_execution.plan_execution
            ).first():
                prefix_variables.update(stage_ex.serialized_output)
            variables.update({prefix: prefix_variables})

        return util.fill_dynamic_variables(copy.deepcopy(arguments), variables, dynamic_variable_separator)

    @staticmethod
    def _update_arguments_with_execution_variables(arguments: dict, execution_variables: list) -> dict:
        """
        Fill Jinja variables in the arguments with execution variables.
        :param arguments: Arguments to fill
        :param execution_variables: Execution variables to fill the template (arguments) with
        :return: Filled arguments
        """
        parsed_execution_variables = {variable.get("name"): variable.get("value") for variable in execution_variables}

        env = nativetypes.NativeEnvironment(
            undefined=StrictUndefined,
            block_start_string=constants.BLOCK_START_STRING,
            block_end_string=constants.BLOCK_END_STRING,
            variable_start_string=constants.VARIABLE_START_STRING,
            variable_end_string=constants.VARIABLE_END_STRING,
            comment_start_string=constants.COMMENT_START_STRING,
            comment_end_string=constants.COMMENT_END_STRING,
        )
        arguments_template = env.from_string(yaml.safe_dump(arguments))

        try:
            return yaml.safe_load(arguments_template.render(**parsed_execution_variables))
        except (yaml.YAMLError, UndefinedError, TypeError) as ex:
            raise exceptions.StepValidationError(f"An error occurred while updating execution variables. {ex}.")

    def update_step_arguments(self, arguments: dict, plan_execution_id: Type[int]) -> dict:
        """
        Update Step arguments with execution and dynamic variables.
        :param arguments: Arguments to be updated
        :param plan_execution_id: ID of the parent step of the current step execution
        :return: Updated arguments with execution and dynamic variables
        """
        execution_vars = list(ExecutionVariableModel.objects.filter(plan_execution_id=plan_execution_id).values())

        if execution_vars:
            logger.logger.debug(
                "Updating step arguments with execution variables",
                step_execution_id=self.model.id,
                step_arguments=arguments,
                execution_vars=execution_vars,
            )
            try:
                arguments.update(self._update_arguments_with_execution_variables(arguments, execution_vars))
            except exceptions.StepValidationError as ex:
                logger.logger.error(str(ex))
                raise exceptions.MissingValueError(ex)

        # Update dynamic variables
        try:
            arguments.update(self._update_dynamic_variables(arguments))
        except Exception as ex:
            logger.logger.error(str(ex))
            raise exceptions.MissingValueError(f"Failed to update the dynamic variables. Original error: {ex}")

        logger.logger.debug("Step arguments updated", step_execution_id=self.model.id, step_arguments=arguments)
        return arguments

    def send_step_execution_request(
        self, rabbit_channel: amqpstorm.Channel, message_body: dict, reply_queue: str, target_queue: str
    ) -> None:
        """
        Sends RPC request to execute step using RabbitMQ.
        :param rabbit_channel: Rabbit channel
        :param message_body: data that should be sent to worker
        :param reply_queue: Queue that worker should reply to
        :param target_queue: Queue on which should data be sent to worker(for example)
        :return: None
        """
        logger.logger.debug(
            "Sending Step execution request", step_execution_id=self.model.id, message_body=message_body
        )
        with rabbit_client.RpcClient(rabbit_channel) as rpc_client:
            try:
                response = rpc_client.call(target_queue, message_body, custom_reply_queue=reply_queue)
            except exceptions.RpcTimeoutError as ex:
                self.state = states.ERROR
                self.process_error_state()
                logger.logger.error("Step execution failed", step_execution_id=self.model.id, error=str(ex))
                return

            self.state = states.RUNNING
            CorrelationEventModel.objects.create(
                correlation_id=rpc_client.correlation_id, step_execution_id=self.model.id
            )
            logger.logger.debug(
                "Received response from Step execution request ", step_execution_id=self.model.id, response=response
            )

    def _prepare_execution(self) -> [Type[int], worker.Worker]:
        """
        Execute necessary actions and return variables needed for individual execution of each type of StepExecution.
        :return: Plan execution id and worker instance for current Plan execution
        """
        states.StepStateMachine(self.model.id).validate_state(self.state, states.STEP_EXECUTE_STATES)
        logger.logger.debug("Executing Step", step_execution_id=self.model.id)

        plan_execution_id = self.model.stage_execution.plan_execution_id
        step_worker_obj = self.model.stage_execution.plan_execution.worker
        worker_obj = worker.Worker(step_worker_obj.id)

        # Set STARTING state
        self.start_time = timezone.now()
        self.state = states.STARTING

        return plan_execution_id, worker_obj

    def execute(self, rabbit_channel: amqpstorm.Channel = None) -> None:
        """
        Execute Step on worker specified in execution stats.
        :param rabbit_channel: Rabbit channel
        :return: None
        """
        logger.logger.debug("Starting Step execution", step_execution_id=self.model.id, step_name=self.model.step.name)
        plan_execution_id, worker_obj = self._prepare_execution()

        try:
            module_arguments = self.update_step_arguments(self.model.step.arguments, plan_execution_id)
        except exceptions.MissingValueError as ex:
            self.state = states.ERROR
            self.output = str(ex)
            self.process_error_state()
            return

        message_body = {
            constants.MODULE: self.model.step.module,
            constants.ARGUMENTS: module_arguments,
        }

        target_queue = worker_obj.attack_q_name
        reply_queue = SETTINGS.rabbit.queues.attack_response

        self.send_step_execution_request(rabbit_channel, message_body, reply_queue, target_queue)
        logger.logger.info(
            "Step executed", step_execution_id=self.model.id, step_name=self.model.step.name, status="success"
        )

    def report(self) -> dict:
        """
        Generate report containing output from Step Execution.
        :return: Step Execution report
        """
        report_obj = StepReport(
            id=self.model.id,
            name=self.model.step.name,
            metadata=self.model.step.metadata,
            state=self.state,
            start_time=self.start_time,
            finish_time=self.finish_time,
            result=self.result,
            serialized_output=self.serialized_output,
            output=self.output,
            valid=self.valid,
        )

        return asdict(report_obj)

    def get_successors_to_execute(self) -> QuerySet:
        """
        Get Successors based on evaluated dependency.

        :return: QuerySet of StepModel objects
        """
        # Get step successor from DB
        successor_ids = set()

        logger.logger.debug("Getting Step execution successors", step_execution_id=self.model.id)
        for successor in self.model.step.successors.all():
            successor_type = successor.type
            parent_value = getattr(self, successor_type) if successor_type != constants.ANY else None
            if successor_type == constants.ANY:
                successor_ids.add(successor.successor_id)

            elif successor_type in constants.REGEX_TYPES:
                if re.search(successor.value, str(parent_value)):
                    successor_ids.add(successor.successor_id)

            else:
                if successor.value == parent_value:
                    successor_ids.add(successor.successor_id)

        return StepModel.objects.filter(id__in=successor_ids)

    def ignore(self) -> None:
        """
        Set IGNORE state to Step Execution and to all of its successors.

        :return: None
        """
        # Stop recursion
        logger.logger.debug("Ignoring Step execution", step_execution_id=self.model.id)
        if self.state == states.IGNORED:
            return None
        # If any non SKIPPED parent exists (ignoring the one that called ignore())
        for parent_step in Step(self.model.step.id).parents:
            parent_step_exec_model = StepExecutionModel.objects.get(
                step=parent_step, stage_execution=self.model.stage_execution
            )
            parent_step_exec_obj = StepExecution(step_execution_id=parent_step_exec_model.id)
            # TODO: condition after 'or' may be adding too much runtime complexity here
            if (
                parent_step_exec_model.state not in states.STEP_FINAL_STATES
                or self.model.step in parent_step_exec_obj.get_successors_to_execute()
            ):
                return None

        # Set ignore state
        self.state = states.IGNORED
        logger.logger.debug("Step execution ignored", step_execution_id=self.model.id)
        # Execute for all successors
        for successor_step in Step(self.model.step.id).successors:
            step_ex_id = StepExecutionModel.objects.get(
                step=successor_step, stage_execution=self.model.stage_execution
            ).id
            step_ex_obj = StepExecution(step_execution_id=step_ex_id)
            step_ex_obj.ignore()

        return None

    def postprocess(self, ret_vals: dict) -> None:
        """
        Perform necessary things after executing Step like creating named sessions, update state, update successors
        and save Step Execution Output.

        :param ret_vals: output from Step Execution
        :return: None
        """
        logger.logger.debug("Postprocessing Step execution", step_execution_id=self.model.id)
        # Set final state, optionally save result
        result = ret_vals.get(constants.RESULT)
        self.finish_time = timezone.now()

        if result == Result.TERMINATED:
            self.state = states.TERMINATED
        elif result == Result.ERROR:
            self.state = states.ERROR
        else:
            self.state = states.FINISHED
            try:
                self.result = Result(result)
            except ValueError:
                self.result = Result.UNKNOWN

        if self.state == states.FINISHED:
            ret_vals[constants.OUTPUT], ret_vals[constants.SERIALIZED_OUTPUT] = self._alter_output(
                ret_vals.get(constants.OUTPUT), ret_vals.get(constants.SERIALIZED_OUTPUT)
            )

        # Store job output and error message
        self.save_output(ret_vals)

        # update Successors parents
        successor_list = self.get_successors_to_execute()

        for successor_step in successor_list:
            successor_step_execution_model = StepExecutionModel.objects.get(
                step_id=successor_step.id, stage_execution_id=self.model.stage_execution_id, state=states.PENDING
            )
            StepExecution(step_execution_id=successor_step_execution_model.id).parent = self.model

        logger.logger.debug("Step execution postprocess finished", step_execution_id=self.model.id)
        return None

    def _alter_output(self, output: str, serialized_output: dict) -> tuple[str, dict]:
        converted_serialized_output = json.dumps(serialized_output)
        replace_rules: dict[str, str] = self.model.step.output_settings.replace
        if replace_rules:
            for rule, replace_with in replace_rules.items():
                regex_rule = re.compile(rule)
                output = regex_rule.sub(replace_with, output)
                converted_serialized_output = regex_rule.sub(replace_with, converted_serialized_output)

        return output, json.loads(converted_serialized_output)

    def ignore_successors(self) -> None:
        """
        Ignor/skip all successor Steps of current Step Execution.
        :return: None
        """
        logger.logger.debug("Ignoring Step successors", step_execution_id=self.model.id)
        step_obj = Step(self.model.step.id)

        # Get all possible successors
        all_successor_list = StepModel.objects.filter(id__in=step_obj.model.successors.all().values_list("successor"))

        if self.state == states.FINISHED:
            # Get correct step successor from DB which are to be executed
            successor_list = self.get_successors_to_execute()
            # Set IGNORE steps (all successors which won't be executed and don't have parents
            successor_to_be_skipped = all_successor_list.difference(successor_list)
        else:
            successor_to_be_skipped = all_successor_list
        for successor_step in successor_to_be_skipped:
            try:
                successor_step_exec_id = StepExecutionModel.objects.get(
                    step_id=successor_step.id, stage_execution=self.model.stage_execution_id, state=states.PENDING
                ).id
            except ObjectDoesNotExist:
                # Does not exist or is not PENDING
                continue
            StepExecution(step_execution_id=successor_step_exec_id).ignore()
        return None

    def execute_successors(self) -> None:
        """
        Execute all successors of current Step Execution.
        :return: None
        """
        logger.logger.debug("Executing Step successors", step_execution_id=self.model.id)

        # Get correct step successor from DB which are to be executed
        successor_list = self.get_successors_to_execute()

        # Execute all successors
        for successor_step_model in successor_list:
            successor_step_execution_model = StepExecutionModel.objects.get(
                step_id=successor_step_model.id,
                stage_execution_id=self.model.stage_execution_id,
                state=states.PENDING,
            )
            successor_step_exec = StepExecution(step_execution_id=successor_step_execution_model.id)
            successor_step_exec.execute()
        return None

    def pause_successors(self) -> None:
        """
        Pause successor Steps of current Step Execution.
        :return: None
        """
        logger.logger.debug("Pausing Step successors", step_execution_id=self.model.id)
        # Set all successors to PAUSED, so they can be recognized/executed when unpaused
        successor_list = self.get_successors_to_execute()
        for step_obj in successor_list:
            successor_exec_id = StepExecutionModel.objects.get(
                stage_execution=self.model.stage_execution, step_id=step_obj.id
            ).id
            StepExecution(step_execution_id=successor_exec_id).state = states.PAUSED
            logger.logger.info(
                "Step successor paused", step_execution_id=self.model.id, successor_exec_id=successor_exec_id
            )

        return None

    def kill(self):
        """
        Kill current Step Execution on Worker.

        :return: Dictionary containing return_code and output
        """
        logger.logger.debug("Killing Step", step_id=self.model.step.id)
        states.StepStateMachine(self.model.id).validate_state(self.state, states.STEP_KILL_STATES)

        state_before = self.state
        self.state = states.TERMINATING

        if state_before == states.PAUSED:
            self.finish_time = timezone.now()
            self.state = states.TERMINATED
        else:
            worker_obj = worker.Worker(self.model.stage_execution.plan_execution.worker.id)
            correlation_id = self.model.correlation_events.first().correlation_id
            message = {
                constants.EVENT_T: constants.EVENT_KILL_STEP_EXECUTION,
                constants.EVENT_V: {"correlation_id": correlation_id},
            }

            with rabbit_client.RpcClient() as rpc_client:
                try:
                    response = rpc_client.call(worker_obj.control_q_name, message)
                except exceptions.RpcTimeoutError as ex:
                    logger.logger.error("Step execution not terminated", step_execution_id=self.model.id, error=str(ex))
                    return
                else:  # The state is set in the `post_process` method
                    response_value = response.get(constants.EVENT_V)
                    if response_value.get(constants.RESULT) != Result.OK:
                        logger.logger.warning(
                            "Step execution not terminated",
                            step_execution_id=self.model.id,
                            error=response_value.get("output"),
                        )
                        return

        logger.logger.info("Step execution terminated", step_execution_id=self.model.id)

    def re_execute(self) -> None:
        """
        Reset execution data and re-execute StepExecution.
        :return: None
        """
        states.StepStateMachine(self.model.id).validate_state(self.state, states.STEP_FINAL_STATES)
        self.reset_execution_data()
        self.execute()

    def reset_execution_data(self) -> None:
        """
        Reset changeable data to defaults.
        :return: None
        """
        logger.logger.debug("Resetting Step execution data", step_execution_id=self.model.id)
        states.StepStateMachine(self.model.id).validate_state(self.state, states.STEP_FINAL_STATES)

        with transaction.atomic():
            model = self.model
            StepExecutionModel.objects.select_for_update().get(id=model.id)

            model.state = states.PENDING
            model.start_time = None
            model.pause_time = None
            model.finish_time = None
            model.result = ""
            model.serialized_output = dict()
            model.output = ""
            model.valid = False
            model.parent = None
            model.save()

    def process_error_state(self) -> None:
        """
        If an error state is set, ignore successors and send an event that an error occurred.
        :return: None
        """
        self.ignore_successors()

        message = {
            constants.EVENT_T: constants.EVENT_STEP_EXECUTION_ERROR,
            constants.EVENT_V: {"step_execution_id": self.model.id},
        }
        with rabbit_client.Client() as client:
            client.send_message(SETTINGS.rabbit.queues.event_response, message)
