import json
from datetime import datetime
from typing import Type
import re
import copy
import yaml
import amqpstorm
from jinja2 import nativetypes, StrictUndefined, UndefinedError

from django.db import transaction
from django.utils import timezone

from cryton.hive.cryton_app.models import (
    StepModel,
    StepExecutionModel,
    CorrelationEventModel,
    StepOutputSettingsModel,
    OutputMappingModel,
    StageExecutionModel,
    SuccessorModel,
)

from cryton.hive.models.abstract import Instance, Execution
from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import constants, exceptions, logger, states, util, rabbit_client
from cryton.hive.models import worker
from cryton.lib.utility.enums import Result


class Step(Instance):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = StepModel.objects.get(id=model_id)
        self._logger = logger.logger.bind(step_id=model_id, name=self.model.name)

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
    def model(self) -> StepModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def name(self) -> str:
        return self.model.name

    @property
    def is_init(self) -> bool:
        return self.model.is_init

    @property
    def arguments(self) -> dict:
        return self.model.arguments

    @property
    def meta(self) -> dict:
        return self.model.metadata


class StepExecution(Execution):
    def __init__(self, model_id: int):
        """
        :param model_id: Model ID
        """
        self.__model = StepExecutionModel.objects.get(id=model_id)
        self._logger = logger.logger.bind(step_execution_id=model_id, name=self.model.step.name)

    @staticmethod
    def create_model(step_id: int, stage_execution_id: int) -> StepExecutionModel | Type[StepExecutionModel]:
        return StepExecutionModel.objects.create(step_id=step_id, stage_execution_id=stage_execution_id)

    @classmethod
    def prepare(cls, step_id: int, stage_execution_id: int) -> "StepExecution":
        model = cls.create_model(step_id, stage_execution_id)

        return StepExecution(model.id)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Type[StepExecutionModel] | StepExecutionModel:
        self.__model.refresh_from_db()
        return self.__model

    @property
    def state(self) -> str:
        return self.model.state

    @state.setter
    def state(self, value: str):
        with transaction.atomic():
            StepExecutionModel.objects.select_for_update().get(id=self.model.id)
            if states.StepStateMachine.validate_transition(self.state, value):
                self._logger.debug("step execution state updated", state_from=self.state, state_to=value)
                model = self.model
                model.state = value
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
    def serialized_output(self) -> list | dict:
        return self.model.serialized_output

    @serialized_output.setter
    def serialized_output(self, value: list | dict):
        model = self.model
        model.serialized_output = value
        model.save()

    @property
    def start_time(self) -> datetime | None:
        return self.model.start_time

    @start_time.setter
    def start_time(self, value: datetime | None):
        model = self.model
        model.start_time = value
        model.save()

    @property
    def finish_time(self) -> datetime | None:
        return self.model.finish_time

    @finish_time.setter
    def finish_time(self, value: datetime | None):
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

    def start(self, rabbit_channel: amqpstorm.Channel = None) -> None:
        """
        Start step execution.
        :param rabbit_channel: Rabbit channel to use
        :return: None
        """
        self._logger.debug("step execution starting")
        states.StepStateMachine.validate_state(self.state, states.STEP_EXECUTE_STATES)

        self.start_time = timezone.now()
        self.state = states.STARTING

        try:
            module_arguments = self.update_step_arguments()
        except exceptions.MissingValueError as ex:
            self.state = states.ERROR
            self.output = str(ex)
            self.process_error_state()
            return

        message_body = {constants.MODULE: self.model.step.module, constants.ARGUMENTS: module_arguments}
        target_queue = worker.Worker(self.model.stage_execution.plan_execution.worker.id).attack_queue
        reply_queue = SETTINGS.rabbit.queues.attack_response
        self._execute_on_worker(rabbit_channel, message_body, reply_queue, target_queue)
        self._logger.info("step execution started")

    def stop(self) -> None:
        """
        Stop step execution.
        :return: None
        """
        self._logger.debug("step execution stopping")
        states.StepStateMachine.validate_state(self.state, states.STEP_STOP_STATES)

        state_before = self.state
        self.state = states.STOPPING

        if state_before == states.PAUSED:
            self.finish_time = timezone.now()
            self.state = states.STOPPED
        else:
            worker_obj = worker.Worker(self.model.stage_execution.plan_execution.worker.id)
            correlation_id = self.model.correlation_events.first().correlation_id
            message = {
                constants.EVENT_T: constants.EVENT_STOP_STEP_EXECUTION,
                constants.EVENT_V: {"correlation_id": correlation_id},
            }

            with rabbit_client.RpcClient() as rpc_client:
                try:
                    response = rpc_client.call(worker_obj.control_queue, message)
                except exceptions.RpcTimeoutError as ex:
                    self._logger.error("cannot stop step execution", error=str(ex))
                    return
                else:  # The state is set in the `post_process` method
                    response_value = response.get(constants.EVENT_V)
                    if response_value.get(constants.RESULT) != Result.OK:
                        self._logger.warning("cannot stop step execution", error=response_value.get("output"))
                        return

        self._logger.info("step execution stopped")

    def finish(self):
        self._process_results()
        self._process_successors()

    def _process_results(self):
        pass

    def _process_successors(self):
        pass

    def report(self) -> dict:
        """
        Generate report containing output from Step Execution.
        :return: Step Execution report
        """
        report_obj = dict(
            id=self.model.id,
            name=self.model.step.name,
            metadata=self.model.step.metadata,
            state=self.state,
            start_time=self.start_time,
            finish_time=self.finish_time,
            serialized_output=self.serialized_output,
            output=self.output,
            valid=self.valid,
        )

        return report_obj

    def validate(self) -> bool:
        """
        Validate module arguments.
        :return:
        """
        self._logger.debug("step execution validating module")
        target_queue = worker.Worker(self.model.stage_execution.plan_execution.worker.id).control_queue
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

        self._logger.info("step execution module validated")
        return self.valid

    def _update_dynamic_variables(self, arguments: dict) -> dict:
        """
        Update dynamic variables in mod_args (even with special $parent prefix)
        :param arguments: arguments that should be updated
        :return: Arguments updated for dynamic variables
        """
        self._logger.debug("step execution updating arguments with dynamic variables")
        dynamic_variable_separator = self.model.step.stage.plan.settings.separator

        variable_definitions = util.get_dynamic_variables(arguments)
        prefixes = util.get_prefixes(variable_definitions, dynamic_variable_separator)
        variables: dict[str, dict] = dict()
        executions = StepExecutionModel.objects.filter(
            stage_execution__plan_execution=self.model.stage_execution.plan_execution,
            state__in=states.STEP_FINAL_STATES,
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

    def _update_execution_variables(self, arguments: dict, execution_variables: list) -> dict:
        """
        Fill Jinja variables in the arguments with execution variables.
        :param arguments: Arguments to fill
        :param execution_variables: Execution variables to fill the template (arguments) with
        :return: Filled arguments
        """
        self._logger.debug("step execution updating arguments with execution variables")
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

    def update_step_arguments(self) -> dict:
        """
        Update Step arguments with execution and dynamic variables.
        :return: Arguments updated with execution and dynamic variables
        """
        arguments = self.model.step.arguments
        execution_vars = list(self.model.stage_execution.plan_execution.execution_variables.all().values())

        if execution_vars:
            try:
                arguments.update(self._update_execution_variables(arguments, execution_vars))
            except exceptions.StepValidationError as ex:
                raise exceptions.MissingValueError(ex)

        # Update dynamic variables
        try:
            arguments.update(self._update_dynamic_variables(arguments))
        except Exception as ex:
            raise exceptions.MissingValueError(f"Failed to update the dynamic variables. Original error: {ex}")

        self._logger.debug("step execution step arguments updated", arguments=arguments)
        return arguments

    def _execute_on_worker(
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
        self._logger.debug("step execution executing on worker", message_body=message_body)
        with rabbit_client.RpcClient(rabbit_channel) as rpc_client:
            try:
                response = rpc_client.call(target_queue, message_body, custom_reply_queue=reply_queue)
            except exceptions.RpcTimeoutError as ex:
                self.state = states.ERROR
                self.process_error_state()
                self._logger.error("step execution module execution failed", error=str(ex))
                return

            self.state = states.RUNNING
            CorrelationEventModel.objects.create(correlation_id=rpc_client.correlation_id, step_execution=self.model)
            self._logger.debug("step execution module executed on worker", response=response)

    def _is_successor_executable(self, successor: SuccessorModel) -> bool:
        """
        Check if a successor is runnable by the current execution.
        :param successor: Possible successor
        :return: True in case the successor is eligible for execution
        """
        match successor.type:
            case constants.ANY:
                return True
            case constants.STATE:
                if successor.value.lower() == self.state.lower():
                    return True
            case constants.OUTPUT:
                if re.search(successor.value, self.output):
                    return True
            case constants.SERIALIZED_OUTPUT:
                if re.search(successor.value, str(self.serialized_output)):
                    return True

        return False

    def _get_executable_successors(self) -> set["StepExecution"]:
        """
        Get Successors that will be executed by the current execution.
        :return: Successors
        """
        self._logger.debug("step execution get executable successors")
        successors: set[StepExecution] = set()
        for successor_model in self.model.step.successors.all():
            if not self._is_successor_executable(successor_model):
                continue

            step = successor_model.successor
            step_execution = self.model.stage_execution.step_executions.filter(step=step, state=states.PENDING).first()
            if step_execution:
                successors.add(StepExecution(step_execution.id))

        return successors

    def ignore(self) -> None:
        """
        Set IGNORE state to Step Execution and to all of its successors.

        :return: None
        """
        self._logger.debug("step execution ignoring")
        if self.state == states.IGNORED:
            return

        # If any non SKIPPED parent exists (ignoring the one that called ignore())
        if self.model.parent:
            return

        if (
            self.model.stage_execution.step_executions.filter(step__in=self.model.step.parents.values("parent"))
            .exclude(state__in=states.STEP_FINAL_STATES)
            .exists()
        ):
            return

        self.state = states.IGNORED
        self._logger.debug("step execution ignored")
        # Try to ignore successors
        for successor_step in self.model.step.successors.all():
            step_ex_id = self.model.stage_execution.step_executions.get(step=successor_step).id
            step_ex_obj = StepExecution(step_ex_id)
            step_ex_obj.ignore()

    def postprocess(self, ret_vals: dict) -> None:
        """
        Perform necessary things after executing Step like creating named sessions, update state, update successors
        and save Step Execution Output.

        :param ret_vals: output from Step Execution
        :return: None
        """
        self._logger.debug("step execution postprocessing")
        self.finish_time = timezone.now()

        serialized_output = ret_vals[constants.SERIALIZED_OUTPUT]
        output = ret_vals[constants.OUTPUT]
        result = Result(ret_vals[constants.RESULT])

        match result:
            case Result.STOPPED:
                self.state = states.STOPPED
            case Result.ERROR:
                self.state = states.ERROR
            case Result.FAIL:
                self.state = states.FAILED
            case Result.OK:
                self.state = states.FINISHED
                output, serialized_output = self._alter_output(output, serialized_output)
                self._apply_output_mappings(serialized_output)

        self.serialized_output = serialized_output
        self.output = output

        # update Successors parents
        for successor in self._get_executable_successors():
            successor.parent = self.model

        self._logger.debug("step execution postprocess finished")

    def _apply_output_mappings(self, serialized_output: dict):
        for mapping in self.model.step.output_settings.mappings.all():
            util.rename_key(serialized_output, mapping.name_from, mapping.name_to)

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
        self._logger.debug("step execution ignoring step successors")
        all_successors = self.model.stage_execution.step_executions.filter(
            step__in=self.model.step.successors.values("successor"), state=states.PENDING
        )

        if self.state in [states.FINISHED, states.FAILED, states.ERROR]:
            executable_successors = [successor.model.id for successor in self._get_executable_successors()]
            successor_to_be_skipped = all_successors.exclude(id__in=executable_successors)
        else:
            successor_to_be_skipped = all_successors

        for successor in successor_to_be_skipped:
            StepExecution(successor.id).ignore()

    def start_successors(self) -> None:
        """
        Execute eligible successors.
        :return: None
        """
        self._logger.debug("step execution starting successors")
        for successor in self._get_executable_successors():
            successor.start()

    def pause_successors(self) -> None:
        """
        Set all successors' state to PAUSED, so they can be executed once resumed.
        :return: None
        """
        self._logger.debug("step execution pausing successors")
        for successor in self._get_executable_successors():
            successor.state = states.PAUSED
            self._logger.debug("step execution successor paused", successor_id=successor.model.id)

    def re_execute(self) -> None:
        """
        Reset execution data and re-execute StepExecution.
        :return: None
        """
        states.StepStateMachine.validate_state(self.state, states.STEP_FINAL_STATES)
        self.reset_execution_data()
        self.start()

    def reset_execution_data(self) -> None:
        """
        Reset changeable data to defaults.
        :return: None
        """
        self._logger.debug("step execution resetting data")
        states.StepStateMachine.validate_state(self.state, states.STEP_FINAL_STATES)

        with transaction.atomic():
            model = self.model
            StepExecutionModel.objects.select_for_update().get(id=model.id)

            model.state = states.PENDING
            model.start_time = None
            model.pause_time = None
            model.finish_time = None
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
