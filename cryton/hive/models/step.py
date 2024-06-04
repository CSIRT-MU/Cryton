import json
from datetime import datetime
from typing import Union, Type, Optional
import re
import copy
import yaml
import amqpstorm
from schema import Schema, Optional as SchemaOptional, SchemaError, Or, And
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
    OutputMappingModel,
    CorrelationEventModel,
)

from cryton.hive.config.settings import SETTINGS
from cryton.hive.utility import constants, exceptions, logger, states, util, rabbit_client
from cryton.hive.models import worker, session
from cryton.hive.utility.exceptions import StepTypeDoesNotExist
from enum import EnumMeta, Enum
from cryton.lib.utility.enums import Result

from dataclasses import dataclass, asdict


@dataclass
class StepReport:
    id: int
    name: str
    meta: dict
    state: str
    start_time: datetime
    finish_time: datetime
    output: str
    serialized_output: dict
    result: str
    valid: bool


class Step:

    def __init__(self, **kwargs):
        """

        :param kwargs:
                 step_model_id: int = None,
                 stage_model_id: int = None,
                 arguments: str = None,
                 is_init: bool = None,
                 name: str = None
                 step_type: str = None
        """
        step_model_id = kwargs.get("step_model_id")
        if step_model_id:
            try:
                self.model = StepModel.objects.get(id=step_model_id)
            except django_exc.ObjectDoesNotExist:
                raise exceptions.StepObjectDoesNotExist("PlanModel with id {} does not exist.".format(step_model_id))

        else:
            step_obj_arguments = copy.deepcopy(kwargs)
            step_obj_arguments.pop(constants.NEXT, None)
            step_obj_arguments.pop("output_mapping", None)
            # Set default prefix as step name
            if step_obj_arguments.get("output_prefix") is None:
                step_obj_arguments.update({"output_prefix": step_obj_arguments.get("name")})
            self.model = StepModel.objects.create(**step_obj_arguments)

    def delete(self):
        self.model.delete()

    @property
    def model(self) -> Union[Type[StepModel], StepModel]:
        self.__model.refresh_from_db()
        return self.__model

    @model.setter
    def model(self, value: StepModel):
        self.__model = value

    @property
    def stage_model_id(self) -> Union[Type[int], int]:
        return self.model.stage_model_id

    @stage_model_id.setter
    def stage_model_id(self, value: int):
        model = self.model
        model.stage_model_id = value
        model.save()

    @property
    def name(self) -> str:
        return self.model.name

    @name.setter
    def name(self, value: str):
        model = self.model
        model.name = value
        model.save()

    @property
    def step_type(self) -> str:
        return self.model.step_type

    @step_type.setter
    def step_type(self, value: str):
        model = self.model
        model.step_type = value
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
    def is_final(self) -> bool:
        return self.model.is_final

    @is_final.setter
    def is_final(self, value: bool):
        model = self.model
        model.is_final = value
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
    def output_prefix(self) -> str:
        return self.model.output_prefix

    @output_prefix.setter
    def output_prefix(self, value: bool):
        model = self.model
        model.output_prefix = value
        model.save()

    @property
    def meta(self) -> dict:
        return self.model.meta

    @meta.setter
    def meta(self, value: dict):
        model = self.model
        model.meta = value
        model.save()

    @property
    def output(self) -> dict:
        return self.model.output

    @property
    def execution_stats_list(self) -> QuerySet:
        """
        Returns StepExecutionStatsModel QuerySet. If the latest is needed, use '.latest()' on result.
        :return: QuerySet of StepExecutionStatsModel
        """
        return StepExecutionModel.objects.filter(step_model_id=self.model.id)

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

    @classmethod
    def validate(cls, step_dict) -> bool:
        """
        Validate a step dictionary
        :raises:
            exceptions.StepValidationError
        :return: True
        """

        forbidden_output_prefixes = ["parent"]
        for step_object in StepModel.objects.all():
            forbidden_output_prefixes.append(step_object.name)

        conf_schema = Schema(
            {
                "name": str,
                SchemaOptional("meta"): dict,
                constants.STEP_TYPE: str,
                SchemaOptional("is_init"): bool,
                constants.ARGUMENTS: dict,
                SchemaOptional("next"): list,
                SchemaOptional("output_mapping"): [{"name_from": str, "name_to": str}],
                SchemaOptional("output_prefix"): And(
                    str,
                    lambda x: (x not in forbidden_output_prefixes and ("." not in x and "&" not in x)),
                    error="This output_prefix is not allowed",
                ),
                SchemaOptional("output"): dict,
            }
        )

        try:
            logger.logger.debug("Validating step", step_name=step_dict.get("name"))
            conf_schema.validate(step_dict)
            StepType[step_dict[constants.STEP_TYPE]].value.validate(step_dict[constants.ARGUMENTS])

            if "next" in step_dict.keys():
                for value_of_next in step_dict["next"]:
                    cls.validate_next_parameter(value_of_next)
        except (SchemaError, StepTypeDoesNotExist) as ex:
            raise exceptions.StepValidationError(ex, step_name=step_dict.get("name"))

        logger.logger.debug("Step validated", step_name=step_dict.get("name"))
        return True

    @classmethod
    def validate_ssh_connection(cls, ssh_connection_dict):
        """
        Validate ssh_connection dictionary

        :raises:
            exceptions.StepValidationError
        :return: True
        """

        conf_schema = Schema(
            Or(
                {
                    "target": str,
                    SchemaOptional("username"): str,
                    SchemaOptional(
                        Or(
                            "password",
                            "ssh_key",
                            only_one=True,
                            error="Arguments 'password' and 'ssh_key' cannot be used together",
                        )
                    ): str,
                    SchemaOptional("port"): int,
                }
            )
        )

        conf_schema.validate(ssh_connection_dict)

    @classmethod
    def validate_next_parameter(cls, next_dict):
        conf_schema = Schema(
            Or(
                {
                    "type": And(str, lambda x: x in constants.SUCCESSOR_TYPES_WITHOUT_ANY),
                    "value": Or(str, [str]),
                    "step": Or(str, [str]),
                },
                {"type": And(str, lambda x: x == "any"), "step": Or(str, [str])},
            )
        )

        conf_schema.validate(next_dict)

        if next_dict["type"] == constants.RESULT and next_dict["value"] not in Result:
            raise SchemaError("Invalid value for type 'result' in the parameter 'next'")

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
        logger.logger.debug("Adding step successor", step_id=self.model.id, step_successor_id=successor_id)
        if successor_type not in constants.VALID_SUCCESSOR_TYPES:
            raise exceptions.InvalidSuccessorType(
                "Unknown successor type. Choose one of valid types: {}".format(constants.VALID_SUCCESSOR_TYPES),
                successor_type,
            )

        if successor_type == constants.RESULT and successor_value not in Result:
            raise exceptions.InvalidSuccessorValue(
                "Unknown successor value. Choose one of valid types: {}".format(Result.values()), successor_value
            )

        if successor_type == constants.ANY and successor_value is None:
            successor_value = ""

        successor = SuccessorModel(
            parent_id=self.model.id, successor_id=successor_id, type=successor_type, value=successor_value
        )
        successor.save()

        logger.logger.debug("Step successor created", step_id=self.model.id, step_successor_id=successor_id)

        return successor.id


class StepWorkerExecute(Step):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.module_name = self.arguments[constants.MODULE]
        self.module_arguments = self.arguments[constants.MODULE_ARGUMENTS]

    @classmethod
    def validate(cls, step_arguments):
        """
        Validate arguments in 'worker/execute' step_type
        """
        worker_exec_valid_schema = Schema(
            Or(
                {
                    constants.MODULE: str,
                    constants.MODULE_ARGUMENTS: dict,
                    SchemaOptional(constants.CREATE_NAMED_SESSION): str,
                    SchemaOptional(constants.USE_ANY_SESSION_TO_TARGET): str,
                },
                {
                    constants.MODULE: str,
                    constants.MODULE_ARGUMENTS: dict,
                    SchemaOptional(constants.CREATE_NAMED_SESSION): str,
                    SchemaOptional(constants.USE_NAMED_SESSION): str,
                },
                only_one=True,
            )
        )

        worker_exec_valid_schema.validate(step_arguments)

        if constants.SSH_CONNECTION in step_arguments:
            cls.validate_ssh_connection(step_arguments[constants.SSH_CONNECTION])


class StepEmpireAgentDeploy(Step):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def validate(cls, step_arguments):
        """
        Validate arguments in 'empire/agent-deploy' step type
        """
        agent_deploy_valid_schema = Schema(
            Or(
                {
                    constants.LISTENER_NAME: str,
                    SchemaOptional(constants.LISTENER_PORT): int,
                    SchemaOptional(constants.LISTENER_OPTIONS): dict,
                    SchemaOptional(constants.LISTENER_TYPE): str,
                    constants.STAGER_TYPE: str,
                    SchemaOptional(constants.STAGER_OPTIONS): dict,
                    constants.AGENT_NAME: And(str, lambda n: n.isalnum(), error="Invalid agent_name format"),
                    SchemaOptional(
                        Or(constants.USE_NAMED_SESSION, constants.USE_ANY_SESSION_TO_TARGET, only_one=True)
                    ): str,
                },
                {
                    constants.LISTENER_NAME: str,
                    SchemaOptional(constants.LISTENER_PORT): int,
                    SchemaOptional(constants.LISTENER_OPTIONS): dict,
                    SchemaOptional(constants.LISTENER_TYPE): str,
                    constants.STAGER_TYPE: str,
                    SchemaOptional(constants.STAGER_OPTIONS): dict,
                    constants.AGENT_NAME: And(str, lambda n: n.isalnum(), error="Invalid agent_name format"),
                    SchemaOptional(constants.SESSION_ID): int,
                },
                {
                    constants.LISTENER_NAME: str,
                    SchemaOptional(constants.LISTENER_PORT): int,
                    SchemaOptional(constants.LISTENER_OPTIONS): dict,
                    SchemaOptional(constants.LISTENER_TYPE): str,
                    constants.STAGER_TYPE: str,
                    SchemaOptional(constants.STAGER_OPTIONS): dict,
                    constants.AGENT_NAME: And(str, lambda n: n.isalnum(), error="Invalid agent_name format"),
                    SchemaOptional(constants.SSH_CONNECTION): dict,
                },
                only_one=True,
            )
        )

        agent_deploy_valid_schema.validate(step_arguments)

        if constants.SSH_CONNECTION in step_arguments:
            cls.validate_ssh_connection(step_arguments[constants.SSH_CONNECTION])


class StepEmpireExecute(Step):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def validate(cls, step_arguments):
        """
        Validate arguments in 'empire/execute' step type
        """
        empire_exec_valid_schema = Schema(
            Or(
                {
                    constants.USE_AGENT: And(str, lambda n: n.isalnum(), error="Invalid agent name format"),
                    constants.SHELL_COMMAND: str,
                },
                {
                    constants.USE_AGENT: And(str, lambda n: n.isalnum(), error="Invalid agent name format"),
                    constants.MODULE: str,
                    SchemaOptional(constants.MODULE_ARGUMENTS): dict,
                },
                only_one=True,
            ),
            error="Wrong combination of arguments, please see documentation",
        )

        empire_exec_valid_schema.validate(step_arguments)


class StepExecution:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        (optional) step_execution_id: int - for retrieving existing execution
        step_model_id: int - for creating new execution
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
    def parent_id(self) -> int:
        return self.model.parent_id

    @parent_id.setter
    def parent_id(self, value: int):
        model = self.model
        model.parent_id = value
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

    def validate(self):
        """
        Validates Step Execution.

        :return:
        """
        pass

    def save_output(self, step_output: dict) -> None:
        """
        Save Step execution output to StepExecutionModel.

        :param step_output: dictionary with keys: output, serialized_output
        :return: None
        """
        if (serialized_output := step_output.get(constants.SERIALIZED_OUTPUT)) is not None:
            output_mappings = OutputMappingModel.objects.filter(step_model=self.model.step_model)
            for output_mapping in output_mappings:
                util.rename_key(serialized_output, output_mapping.name_from, output_mapping.name_to)

        model = self.model

        if serialized_output is not None:
            model.serialized_output = serialized_output
        if (output := step_output.get(constants.OUTPUT)) is not None:
            model.output = output

        model.save()

    def _update_dynamic_variables(self, arguments: dict, parent_step_ex_id: Optional[int]) -> dict:
        """
        Update dynamic variables in mod_args (even with special $parent prefix)
        :param arguments: arguments that should be updated
        :param parent_step_ex_id: ID of the parent step of the current step execution
        :return: Arguments updated for dynamic variables
        """
        logger.logger.debug(
            "Updating step arguments with dynamic variables", step_execution_id=self.model.id, step_arguments=arguments
        )

        # Get list of dynamic variables
        vars_list = util.get_dynamic_variables(arguments)

        dynamic_variable_separator = self.model.step_model.stage_model.plan_model.settings.get(
            constants.SEPARATOR, constants.SEPARATOR_DEFAULT_VALUE
        )
        # Get their prefixes
        prefixes = util.get_prefixes(vars_list, dynamic_variable_separator)
        vars_dict = dict()
        is_parent = False

        for prefix in prefixes:
            # If prefix is parent, get parents prefix
            if prefix == "parent":
                if parent_step_ex_id is None:
                    raise RuntimeError("Parent must be specified for $parent prefix.")
                is_parent = True
                prefix = StepExecutionModel.objects.get(id=parent_step_ex_id).step_model.output_prefix

            tmp_dict = dict()

            for step_ex in StepExecutionModel.objects.filter(
                step_model__output_prefix=prefix,
                stage_execution__plan_execution=self.model.stage_execution.plan_execution,
            ):
                if step_ex.serialized_output:
                    tmp_dict.update(step_ex.serialized_output)
            # Change parents prefix back to 'parent' for updating dictionary to substitute
            if is_parent:
                prefix = "parent"
                is_parent = False
            vars_dict.update({prefix: tmp_dict})

        updated_arguments = util.fill_dynamic_variables(copy.deepcopy(arguments), vars_dict, dynamic_variable_separator)
        return updated_arguments

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
            arguments.update(self._update_dynamic_variables(arguments, self.parent_id))
        except Exception as ex:
            logger.logger.error(str(ex))
            raise exceptions.MissingValueError(f"Failed to update the dynamic variables. Original error: {ex}")

        logger.logger.debug("Step arguments updated", step_execution_id=self.model.id, step_arguments=arguments)
        return arguments

    @staticmethod
    def get_msf_session_id(step_obj: Step, plan_execution_id: Type[int]) -> Optional[str]:
        """
        Check if there should be used any session stored in database and get its session_id.
        :param step_obj: Step instance of current Step Execution
        :param plan_execution_id: Plan Execution ID of current Step Execution.
        :return: MSF Session id
        """
        step_arguments = step_obj.arguments
        use_named_session = step_arguments.get(constants.USE_NAMED_SESSION)
        use_any_session_to_target = step_arguments.get(constants.USE_ANY_SESSION_TO_TARGET)

        if use_named_session is not None:
            # Throws SessionObjectDoesNotExist
            try:
                return session.get_msf_session_id(use_named_session, plan_execution_id)
            except exceptions.SessionObjectDoesNotExist:
                err_msg = {
                    "message": "No session with specified name open",
                    "session_name": use_named_session,
                    "plan_execution_id": plan_execution_id,
                    "step_id": step_obj.model.id,
                }
                logger.logger.error(**err_msg)
                raise exceptions.SessionIsNotOpen(**err_msg)

        elif use_any_session_to_target is not None:
            # Get last session
            try:
                session_msf_id_lst = session.get_session_ids(use_any_session_to_target, plan_execution_id)
            except exceptions.RpcTimeoutError:
                session_msf_id_lst = []

            if len(session_msf_id_lst) == 0:
                err_msg = {
                    "message": "No session to desired target open",
                    "session_name": None,
                    "plan_execution_id": plan_execution_id,
                    "step_id": step_obj.model.id,
                }
                logger.logger.error(**err_msg)
                raise exceptions.SessionIsNotOpen(**err_msg)
            return session_msf_id_lst[-1]

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
        worker_obj = worker.Worker(worker_model_id=step_worker_obj.id)

        # Set STARTING state
        self.start_time = timezone.now()
        self.state = states.STARTING

        return plan_execution_id, worker_obj

    def execute(self):
        """
        Execute current Step Execution.

        :return:
        """
        pass

    def report(self) -> dict:
        """
        Generate report containing output from Step Execution.
        :return: Step Execution report
        """
        report_obj = StepReport(
            id=self.model.id,
            name=self.model.step_model.name,
            meta=self.model.step_model.meta,
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
        for successor in self.model.step_model.successors.all():
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
        for parent_step in Step(step_model_id=self.model.step_model.id).parents:
            parent_step_exec_model = StepExecutionModel.objects.get(
                step_model=parent_step, stage_execution=self.model.stage_execution
            )
            parent_step_exec_obj = StepExecution(step_execution_id=parent_step_exec_model.id)
            # TODO: condition after 'or' may be adding too much runtime complexity here
            if (
                parent_step_exec_model.state not in states.STEP_FINAL_STATES
                or self.model.step_model in parent_step_exec_obj.get_successors_to_execute()
            ):
                return None

        # Set ignore state
        self.state = states.IGNORED
        logger.logger.debug("Step execution ignored", step_execution_id=self.model.id)
        # Execute for all successors
        for successor_step in Step(step_model_id=self.model.step_model.id).successors:
            step_ex_id = StepExecutionModel.objects.get(
                step_model=successor_step, stage_execution=self.model.stage_execution
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
        step_obj = Step(step_model_id=self.model.step_model.id)

        # Check if any named session should be created:
        create_named_session = step_obj.arguments.get(constants.CREATE_NAMED_SESSION)
        if create_named_session is not None:
            try:
                msf_session_id = ret_vals[constants.SERIALIZED_OUTPUT][constants.SESSION_ID]
            except (KeyError, TypeError):
                ret_vals[constants.RESULT] = Result.FAIL
                logger.logger.warning("Module didn't return a session id", step_execution_id=self.model.id)
            else:
                session.create_session(
                    self.model.stage_execution.plan_execution_id, msf_session_id, create_named_session
                )

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
            self._alter_output(ret_vals.get(constants.OUTPUT), ret_vals.get(constants.SERIALIZED_OUTPUT))

        # Store job output and error message
        self.save_output(ret_vals)

        # update Successors parents
        successor_list = self.get_successors_to_execute()

        for successor_step in successor_list:
            successor_step_execution_model = StepExecutionModel.objects.get(
                step_model_id=successor_step.id, stage_execution_id=self.model.stage_execution_id, state=states.PENDING
            )
            StepExecution(step_execution_id=successor_step_execution_model.id).parent_id = self.model.id

        logger.logger.debug("Step execution postprocess finished", step_execution_id=self.model.id)
        return None

    def _alter_output(self, output: str, serialized_output: dict) -> tuple[str, dict]:
        converted_serialized_output = json.dumps(serialized_output)
        replace_rules: dict[str, str] = self.model.step_model.output.get("replace")
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
        step_obj = Step(step_model_id=self.model.step_model.id)

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
                    step_model_id=successor_step.id, stage_execution=self.model.stage_execution_id, state=states.PENDING
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
                step_model_id=successor_step_model.id,
                stage_execution_id=self.model.stage_execution_id,
                state=states.PENDING,
            )
            successor_step_exec = StepExecutionType[successor_step_model.step_type].value(
                step_execution_id=successor_step_execution_model.id
            )
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
                stage_execution=self.model.stage_execution, step_model_id=step_obj.id
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
        logger.logger.debug("Killing Step", step_id=self.model.step_model_id)
        states.StepStateMachine(self.model.id).validate_state(self.state, states.STEP_KILL_STATES)

        state_before = self.state
        self.state = states.TERMINATING

        if state_before == states.PAUSED:
            self.finish_time = timezone.now()
            self.state = states.TERMINATED
        else:
            worker_obj = worker.Worker(worker_model_id=self.model.stage_execution.plan_execution.worker.id)
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
            model.parent_id = None
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


class StepExecutionWorkerExecute(StepExecution):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step_instance = StepWorkerExecute(step_model_id=self.model.step_model.id)

    def validate(self) -> bool:
        """
        Validate cryton attack module arguments.

        :return:
        """
        logger.logger.debug("Validating Cryton module", step_id=self.model.step_model_id)
        target_queue = worker.Worker(worker_model_id=self.model.stage_execution.plan_execution.worker.id).control_q_name
        message = {
            constants.EVENT_T: constants.EVENT_VALIDATE_MODULE,
            constants.EVENT_V: {
                "module": self.step_instance.module_name,
                "module_arguments": self.step_instance.module_arguments,
            },
        }

        with rabbit_client.RpcClient() as rpc_client:
            response = rpc_client.call(target_queue, message)

        if response.get(constants.EVENT_V).get(constants.RESULT) == Result.OK:
            self.valid = True

        return self.valid

    def execute(self, rabbit_channel: amqpstorm.Channel = None) -> None:
        """
        Execute Step on worker specified in execution stats.
        :param rabbit_channel: Rabbit channel
        :return: None
        """
        logger.logger.debug(
            "Starting Step execution", step_execution_id=self.model.id, step_name=self.step_instance.name
        )
        plan_execution_id, worker_obj = self._prepare_execution()

        try:
            module_arguments = self.update_step_arguments(self.step_instance.module_arguments, plan_execution_id)
            session_id = self.get_msf_session_id(self.step_instance, plan_execution_id)
        except (exceptions.SessionIsNotOpen, exceptions.MissingValueError) as ex:
            self.state = states.ERROR
            self.output = str(ex)
            self.process_error_state()
            return

        if session_id:
            module_arguments[constants.SESSION_ID] = session_id

        if (session_id := module_arguments.get(constants.SESSION_ID)) is not None:
            module_arguments[constants.SESSION_ID] = int(session_id)

        message_body = {
            constants.STEP_TYPE: self.step_instance.step_type,
            constants.ARGUMENTS: {
                constants.MODULE: self.step_instance.module_name,
                constants.MODULE_ARGUMENTS: module_arguments,
            },
        }

        target_queue = worker_obj.attack_q_name
        reply_queue = SETTINGS.rabbit.queues.attack_response

        self.send_step_execution_request(rabbit_channel, message_body, reply_queue, target_queue)
        logger.logger.info(
            "Step executed", step_execution_id=self.model.id, step_name=self.step_instance.name, status="success"
        )


class StepExecutionEmpireExecute(StepExecution):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step_instance = StepEmpireExecute(step_model_id=self.model.step_model.id)

    def execute(self, rabbit_channel: amqpstorm.Channel = None) -> None:
        """
        Execute Step on worker specified in execution stats.
        :param rabbit_channel: Rabbit channel
        :return: None
        """
        plan_execution_id, worker_obj = self._prepare_execution()

        try:
            step_arguments = self.update_step_arguments(self.step_instance.arguments, plan_execution_id)
        except exceptions.MissingValueError as ex:
            self.state = states.ERROR
            self.output = str(ex)
            self.process_error_state()
            return

        message_body = {
            constants.STEP_TYPE: self.step_instance.step_type,
            constants.ARGUMENTS: step_arguments,
        }

        target_queue = worker_obj.attack_q_name
        reply_queue = SETTINGS.rabbit.queues.attack_response

        self.send_step_execution_request(rabbit_channel, message_body, reply_queue, target_queue)
        logger.logger.info(
            "Step executed", step_execution_id=self.model.id, step_name=self.step_instance.name, status="success"
        )

    def validate(self):
        """
        Validates StepExecutionEmpireExecute.

        :return:
        """
        self.valid = True


class StepExecutionEmpireAgentDeploy(StepExecution):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step_instance = StepEmpireAgentDeploy(step_model_id=self.model.step_model.id)

    def execute(self, rabbit_channel: amqpstorm.Channel = None) -> None:
        """
        Execute Step on worker specified in execution stats.
        :param rabbit_channel: Rabbit channel
        :return: None
        """
        plan_execution_id, worker_obj = self._prepare_execution()

        try:
            step_arguments = self.update_step_arguments(self.step_instance.arguments, plan_execution_id)
            session_id = self.get_msf_session_id(self.step_instance, plan_execution_id)
        except (exceptions.SessionIsNotOpen, exceptions.MissingValueError) as ex:
            self.state = states.ERROR
            self.output = str(ex)
            self.process_error_state()
            return

        if session_id:
            step_arguments[constants.SESSION_ID] = session_id

        if (session_id := step_arguments.get(constants.SESSION_ID)) is not None:
            step_arguments[constants.SESSION_ID] = int(session_id)

        message_body = {constants.STEP_TYPE: self.step_instance.step_type, constants.ARGUMENTS: step_arguments}

        target_queue = worker_obj.agent_q_name
        reply_queue = SETTINGS.rabbit.queues.agent_response

        self.send_step_execution_request(rabbit_channel, message_body, reply_queue, target_queue)
        logger.logger.info(
            "Step executed", step_execution_id=self.model.id, step_name=self.step_instance.name, status="success"
        )

    def validate(self):
        """
        Validates StepExecutionEmpireAgentDeploy.

        :return:
        """
        self.valid = True


class StepTypeMeta(EnumMeta):
    """
    Overrides base metaclass of Enum in order to support custom exception when accessing not present item.
    """

    step_types = {
        constants.STEP_TYPE_WORKER_EXECUTE: "worker_execute",
        constants.STEP_TYPE_EMPIRE_EXECUTE: "empire_execute",
        constants.STEP_TYPE_DEPLOY_AGENT: "empire_agent_deploy",
    }

    def __getitem__(self, item):
        try:
            return super().__getitem__(StepTypeMeta.step_types[item])
        except KeyError:
            raise StepTypeDoesNotExist(item, constants.STEP_TYPES_LIST)


class StepType(Enum, metaclass=StepTypeMeta):
    empire_agent_deploy = StepEmpireAgentDeploy
    worker_execute = StepWorkerExecute
    empire_execute = StepEmpireExecute


class StepExecutionType(Enum, metaclass=StepTypeMeta):
    empire_agent_deploy = StepExecutionEmpireAgentDeploy
    worker_execute = StepExecutionWorkerExecute
    empire_execute = StepExecutionEmpireExecute
