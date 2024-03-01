# import schema
# from unittest.mock import patch, Mock
# import pytest
# from datetime import datetime
# import pytz
#
# from cryton.hive.utility import constants, exceptions, logger, states
# from cryton.hive.models import step, worker
# from cryton.hive.config.settings import SETTINGS
# from cryton.hive.cryton_app.models import StageModel, StepModel, PlanExecutionModel, StageExecutionModel, \
#     StepExecutionModel, ExecutionVariableModel, CorrelationEventModel, OutputMappingModel
#
# import yaml
# import os
# from django.utils import timezone
# from model_bakery import baker
#
# TESTS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#
#
# @pytest.mark.django_db
# class TestStepBase:
#     @pytest.fixture
#     def stage_model(self):
#         return baker.make(StageModel)
#
#     @pytest.fixture
#     def step_arguments(self, stage_model):
#         return {'name': 'test_step',
#                 'step_type': constants.STEP_TYPE_WORKER_EXECUTE,
#                 'stage_model_id': stage_model.id,
#                 'arguments': {constants.MODULE: "test_module",
#                               constants.MODULE_ARGUMENTS: {}}
#                 }
#
#     @pytest.fixture
#     def step_model(self, stage_model, step_arguments):
#         return baker.make(StepModel,
#                           stage_model=stage_model,
#                           **step_arguments)
#
#     @pytest.fixture
#     def step_model_2(self, stage_model, step_arguments):
#         step_arguments["name"] = "test_step_2"
#         return baker.make(StepModel,
#                           stage_model=stage_model,
#                           **step_arguments)
#
#     @pytest.fixture
#     def step_successor_arguments(self, stage_model):
#         return {'name': 'successor_step_1',
#                 'step_type': constants.STEP_TYPE_WORKER_EXECUTE,
#                 'stage_model_id': stage_model.id,
#                 'arguments': {constants.MODULE: "test_module",
#                               constants.MODULE_ARGUMENTS: {}}
#                 }
#
#     @pytest.fixture
#     def step_successor_model(self, stage_model, step_successor_arguments):
#         return baker.make(StepModel,
#                           stage_model=stage_model,
#                           **step_successor_arguments)
#
#     @pytest.fixture
#     def step_successor_model_2(self, stage_model, step_successor_arguments):
#         step_successor_arguments["name"] = 'successor_step_2'
#         return baker.make(StepModel,
#                           stage_model=stage_model,
#                           **step_successor_arguments)
#
#     @pytest.fixture
#     def step_successor_model_3(self, stage_model, step_successor_arguments):
#         step_successor_arguments["name"] = 'successor_step_3'
#         return baker.make(StepModel,
#                           stage_model=stage_model,
#                           **step_successor_arguments)
#
#     @pytest.fixture
#     def step_instance(self, step_model):
#         return step.Step(step_model_id=step_model.id)
#
#     @pytest.fixture
#     def step_instance_2(self, step_model_2):
#         return step.Step(step_model_id=step_model_2.id)
#
#     @pytest.fixture
#     def step_successor(self, step_successor_model):
#         return step.Step(step_model_id=step_successor_model.id)
#
#     @pytest.fixture
#     def step_successor_2(self, step_successor_model_2):
#         return step.Step(step_model_id=step_successor_model_2.id)
#
#     @pytest.fixture
#     def step_successor_3(self, step_successor_model_3):
#         return step.Step(step_model_id=step_successor_model_3.id)
#
#     @pytest.fixture
#     def agent_deploy_step_dict(self):
#         agent_deploy = open('{}/empire_agent_deploy_step.yaml'.format(TESTS_DIR))
#         return yaml.safe_load(agent_deploy)
#
#     @pytest.fixture
#     def empire_execution_step_dict(self):
#         empire_execute = open('{}/empire_execution_step.yaml'.format(TESTS_DIR))
#         return yaml.safe_load(empire_execute)
#
#     @pytest.fixture
#     def worker_execution_step_dict(self):
#         worker_execute = open('{}/worker_execution_step.yaml'.format(TESTS_DIR))
#         return yaml.safe_load(worker_execute)
#
#
# class TestStepExecutionBase(TestStepBase):
#     @pytest.fixture(autouse=True)
#     def auto_mock(self, mocker):
#         mocker.patch("time.sleep")
#         mocker.patch("cryton.hive.utility.states.StepStateMachine.validate_transition")
#         mocker.patch("cryton.hive.utility.states.StepStateMachine.validate_state")
#
#     @pytest.fixture
#     def plan_execution_model(self):
#         return baker.make(PlanExecutionModel)
#
#     @pytest.fixture
#     def stage_execution_model(self, plan_execution_model):
#         return baker.make(StageExecutionModel, plan_execution=plan_execution_model)
#
#     @pytest.fixture()
#     def plan_execution_id(self, stage_execution_model):
#         return stage_execution_model.plan_execution_id
#
#     @pytest.fixture
#     def step_execution_model(self, stage_execution_model, step_model):
#         return baker.make(StepExecutionModel, stage_execution=stage_execution_model, step_model=step_model)
#
#     @pytest.fixture
#     def step_execution_model_2(self, stage_execution_model, step_model_2):
#         return baker.make(StepExecutionModel, stage_execution=stage_execution_model, step_model=step_model_2)
#
#     @pytest.fixture
#     def step_successor_execution_model(self, step_execution_model, stage_execution_model, step_successor_model):
#         return baker.make(StepExecutionModel, stage_execution=stage_execution_model, step_model=step_successor_model,
#                           parent_id=step_execution_model.id)
#
#     @pytest.fixture
#     def step_successor_execution_model_2(self, stage_execution_model, step_successor_model_2):
#         return baker.make(StepExecutionModel, stage_execution=stage_execution_model, step_model=step_successor_model_2)
#
#     @pytest.fixture
#     def step_successor_execution_model_3(self, stage_execution_model, step_successor_model_3):
#         return baker.make(StepExecutionModel, stage_execution=stage_execution_model, step_model=step_successor_model_3)
#
#     @pytest.fixture
#     def step_execution(self, step_execution_model, stage_execution_model):
#         return step.StepExecutionWorkerExecute(step_execution_id=step_execution_model.id)
#
#     @pytest.fixture
#     def step_execution_2(self, step_execution_model_2, stage_execution_model):
#         return step.StepExecutionWorkerExecute(step_execution_id=step_execution_model_2.id)
#
#     @pytest.fixture
#     def step_execution_successor(self, step_successor_execution_model):
#         return step.StepExecutionWorkerExecute(step_execution_id=step_successor_execution_model.id)
#
#     @pytest.fixture
#     def step_execution_successor_2(self, step_successor_execution_model_2):
#         return step.StepExecutionWorkerExecute(step_execution_id=step_successor_execution_model_2.id)
#
#     @pytest.fixture
#     def step_execution_successor_3(self, step_successor_execution_model_3):
#         return step.StepExecutionWorkerExecute(step_execution_id=step_successor_execution_model_3.id)
#
#     @pytest.fixture
#     def worker_instance(self, plan_execution_model):
#         worker_instance = worker.Worker(worker_model_id=plan_execution_model.worker.id)
#         worker_instance.name = "test_worker"
#         return worker_instance
#
#
# @patch('cryton.hive.utility.logger.logger', logger.structlog.getLogger('cryton-core-debug'))
# class TestStepBasic(TestStepBase):
#     def test_step_init_delete(self, step_instance):
#         step_model_id = step_instance.model.id
#
#         assert isinstance(step_model_id, int)
#         step_instance.delete()
#         with pytest.raises(exceptions.StepObjectDoesNotExist):
#             step.Step(step_model_id=step_model_id)
#
#     def test_step_init_from_id(self, step_instance):
#         step_model = baker.make(StepModel)
#
#         step.Step(step_model_id=step_model.id)
#
#         with pytest.raises(exceptions.StepObjectDoesNotExist):
#             step.Step(step_model_id=int(step_model.id) + 1)
#
#     def test_properties(self, step_instance):
#         temp_stage_model = baker.make(StageModel)
#
#         step_instance.stage_model_id = temp_stage_model.id
#         assert step_instance.stage_model_id == temp_stage_model.id
#
#     def test_properties_arguments(self, step_instance):
#         step_instance.arguments = {}
#         assert step_instance.arguments == {}
#
#     def test_properties_is_init(self, step_instance):
#         step_instance.is_init = False
#         assert step_instance.is_init is False
#
#     def test_properties_is_final(self, step_instance):
#         step_instance.is_final = False
#         assert step_instance.is_final is False
#
#     def test_properties_name(self, step_instance):
#         step_instance.name = 'some-name'
#         assert step_instance.name == 'some-name'
#
#     def test_properties_type(self, step_instance):
#         step_instance.step_type = 'some-type'
#         assert step_instance.step_type == 'some-type'
#
#     def test_properties_output_prefix(self, step_instance):
#         step_instance.output_prefix = 'some-type'
#         assert step_instance.output_prefix == 'some-type'
#
#     def test_properties_successors(self, step_instance, step_successor, stage_model):
#         step_instance.add_successor(step_successor.model.id, successor_type=constants.RESULT,
#                                     successor_value=constants.RESULT_OK)
#         assert isinstance(step_instance.successors, step.QuerySet)
#         assert step_instance.successors[0].name == step_successor.name
#
#     def test_step_init_from_file(self, stage_model):
#         f_in = open('{}/worker_execution_step.yaml'.format(TESTS_DIR))
#         step_yaml = yaml.safe_load(f_in)
#         step_yaml.update({'stage_model_id': stage_model.id})
#         step_instance = step.Step(**step_yaml)
#
#         assert isinstance(step_instance.model.id, int)
#
#     def test_step_delete(self, step_instance):
#         step_id = step_instance.model.id
#         step_instance.delete()
#         with pytest.raises(exceptions.StepObjectDoesNotExist):
#             step.Step(step_model_id=step_id)
#
#     def test_step_list(self, step_instance, stage_model):
#         StepModel.objects.all().delete()
#         step.Step(name='test_step',
#                   step_type=constants.STEP_TYPE_WORKER_EXECUTE,
#                   stage_model_id=stage_model.id,
#                   is_init=True,
#                   arguments={})
#
#         assert len(step.Step.filter()) == 1
#         assert len(step.Step.filter(stage_model_id=-1)) == 0
#         assert len(step.Step.filter(stage_model_id=stage_model.id)) == 1
#         assert len(step.Step.filter(is_init=False)) == 0
#         assert len(step.Step.filter(is_init=True)) == 1
#         with pytest.raises(exceptions.WrongParameterError):
#             assert len(step.Step.filter(non_existent=False)) == 0
#
#     def test_validate_ssh_connection(self, step_instance):
#         ssh_connection_dict = {
#             "target": "target1",
#             "username": "test",
#             "password": "test",
#             "port": 22
#         }
#
#         step.Step.validate_ssh_connection(ssh_connection_dict)
#
#     def test_validate_next_parameter(self, step_instance):
#         next_dict = {
#             "type": "result",
#             "value": "OK",
#             "step": "test_step"
#         }
#
#         step.Step.validate_next_parameter(next_dict)
#
#     def test_ssh_connection_validaton_error(self, step_instance):
#         step_arguments = {
#             constants.MODULE: "module_name",
#             constants.MODULE_ARGUMENTS: {},
#             constants.SSH_CONNECTION: {
#                 "target": "target1",
#                 "username": "test",
#                 "password": "test",
#                 "ssh_key": "test",
#                 "port": 22
#             }
#         }
#
#         with pytest.raises(schema.SchemaError):
#             step.StepWorkerExecute.validate(step_arguments)
#
#     def test_validate_worker_execution(self, worker_execution_step_dict):
#         step.StepWorkerExecute.validate(step_arguments=worker_execution_step_dict[constants.ARGUMENTS])
#         worker_execution_step_dict[constants.ARGUMENTS].pop("module")
#
#         with pytest.raises(schema.SchemaError):
#             step.StepWorkerExecute.validate(step_arguments=worker_execution_step_dict[constants.ARGUMENTS])
#
#     def test_validate_empire_execution(self, empire_execution_step_dict):
#         step.StepEmpireExecute.validate(step_arguments=empire_execution_step_dict[constants.ARGUMENTS])
#         empire_execution_step_dict[constants.ARGUMENTS].pop("module")
#
#         with pytest.raises(schema.SchemaError) as err:
#             step.StepEmpireExecute.validate(step_arguments=empire_execution_step_dict)
#
#         assert err.value.code == "Wrong combination of arguments, please see documentation"
#
#     def test_validate_agent_deploy(self, agent_deploy_step_dict):
#         step.StepEmpireAgentDeploy.validate(step_arguments=agent_deploy_step_dict[constants.ARGUMENTS])
#         agent_deploy_step_dict[constants.ARGUMENTS].pop("stager_type")
#
#         with pytest.raises(schema.SchemaError):
#             step.StepEmpireAgentDeploy.validate(step_arguments=agent_deploy_step_dict)
#
#     def test_getter(self, worker_execution_step_dict, stage_model):
#         worker_execution_step_dict.update({'stage_model_id': stage_model.id})
#         step_instance = step.Step(**worker_execution_step_dict)
#
#         assert step_instance.model.stage_model.id == stage_model.id
#
#
# class TestStepSuccessors(TestStepExecutionBase):
#
#     def test_add_successor(self, step_instance, step_successor):
#         step_instance.add_successor(step_successor.model.id, constants.RESULT, constants.RESULT_OK)
#
#         with pytest.raises(exceptions.InvalidSuccessorType):
#             step_instance.add_successor(step_successor.model.id, 'bad_type', constants.RESULT_OK)
#
#         with pytest.raises(exceptions.InvalidSuccessorValue):
#             step_instance.add_successor(step_successor.model.id, constants.RESULT, 'bad value')
#
#     def test_parents(self, step_instance, step_successor):
#         step_instance.add_successor(step_successor.model.id, constants.RESULT, constants.RESULT_OK)
#         assert [step_instance.model] == list(step_successor.parents)
#
#     def test_successors(self, step_instance, step_successor):
#         step_instance.add_successor(step_successor.model.id, constants.RESULT, constants.RESULT_OK)
#         assert [step_successor.model] == list(step_instance.successors)
#
#     @pytest.mark.parametrize("p_successor_type, p_successor_value, p_step_execution_result",
#                              [(constants.RESULT, constants.RESULT_OK, constants.RESULT_OK),
#                               (constants.ANY, None, 'FAIL'),
#                               (constants.OUTPUT, "test", "testresult"),
#                               (constants.SERIALIZED_OUTPUT, "test", {"test": "result"})])
#     def test_get_successors(self, step_instance, step_successor, step_execution, p_successor_type, p_successor_value,
#                             p_step_execution_result):
#         step_instance.add_successor(step_successor.model.id, p_successor_type, p_successor_value)
#         step_execution.result = p_step_execution_result
#         if p_successor_type != constants.ANY:
#             setattr(step_execution, p_successor_type, p_step_execution_result)
#         successors = step_execution.get_successors_to_execute()
#         assert len(successors) == 1
#         assert step_successor.model.id == step_execution.get_successors_to_execute().first().id
#
#     def test_pause_successors(self, mocker, step_execution, step_execution_successor, step_successor_model):
#         mocker.patch("cryton.hive.models.step.StepExecution.get_successors_to_execute", return_value=[step_successor_model])
#
#         step_execution.pause_successors()
#         assert step_execution_successor.state == states.PAUSED
#
#     def test_ignore(self, step_instance, step_successor, stage_execution_model, step_execution,
#                     step_execution_successor, mocker):
#         mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.get_successors_to_execute")
#         step_instance.add_successor(step_successor.model.id, 'output', 'test')
#
#         step_execution.ignore()
#
#         assert step_execution.state == states.IGNORED
#         assert step_execution_successor.state == states.IGNORED
#
#     def test_ignore_with_multiple_parents(self, step_instance, step_instance_2, step_successor,
#                                           step_execution, step_execution_2, step_execution_successor, mocker):
#         mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.get_successors_to_execute")
#         step_instance.add_successor(step_successor.model.id, 'output', 'test')
#         step_instance_2.add_successor(step_successor.model.id, 'output', 'test')
#
#         step_execution.state = states.FINISHED
#         step_execution_2.state = states.RUNNING
#
#         step_execution_successor.ignore()
#
#         assert step_execution_successor.state == states.PENDING
#
#     def test_ignore_with_multiple_parents_finished(self, step_instance, step_instance_2, step_successor,
#                                                    step_execution, step_execution_2, step_execution_successor, mocker):
#         mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.get_successors_to_execute",
#                      return_value=[step_execution_successor.model.id])
#         step_instance.add_successor(step_successor.model.id, 'output', 'test')
#         step_instance_2.add_successor(step_successor.model.id, 'output', 'test')
#
#         step_execution.state = states.FINISHED
#         step_execution.output = "wrong"
#         step_execution_2.state = states.FINISHED
#         step_execution_2.output = "testoutput"
#
#         step_execution_successor.ignore()
#
#         assert step_execution_successor.state == states.PENDING
#
#     def test_ignore_adversaries(self, mocker, step_instance, step_successor, step_successor_2, step_successor_3,
#                                 step_execution, step_execution_successor, step_execution_successor_2,
#                                 step_execution_successor_3, stage_execution_model):
#         mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.execute")
#
#         step_instance.add_successor(step_successor.model.id, 'output', 'test')
#         step_instance.add_successor(step_successor_2.model.id, constants.RESULT, constants.RESULT_OK)
#         step_successor.add_successor(step_successor_3.model.id, constants.RESULT, constants.RESULT_OK)
#         step_successor_2.add_successor(step_successor_3.model.id, constants.RESULT, constants.RESULT_OK)
#
#         step_execution.output = "test"
#         step_execution_successor.result = constants.RESULT_OK
#         step_execution_successor_2.ignore()
#
#         assert step_execution_successor_2.state != states.IGNORED
#
#         step_execution.state = states.RUNNING
#         step_execution.state = states.FINISHED
#
#         step_execution_successor_2.ignore()
#
#         assert step_execution_successor_2.state == states.IGNORED
#         assert step_execution_successor_3.state != states.IGNORED
#
#     def test_ignore_successors(self, mocker, step_instance, step_successor, step_successor_2, step_successor_3,
#                                step_execution, step_execution_successor, step_execution_successor_2,
#                                step_execution_successor_3, stage_execution_model):
#         mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.execute")
#         # mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.get_successors_to_execute")
#
#         step_instance.add_successor(step_successor.model.id, 'output', 'test')
#         step_instance.add_successor(step_successor_2.model.id, constants.RESULT, constants.RESULT_OK)
#         step_successor.add_successor(step_successor_3.model.id, constants.RESULT, constants.RESULT_OK)
#         step_successor_2.add_successor(step_successor_3.model.id, constants.RESULT, constants.RESULT_OK)
#
#         step_execution.state = states.RUNNING
#         step_execution.state = states.FINISHED
#         step_execution.output = "fail_output"
#         step_execution.result = constants.RESULT_FAIL
#         step_execution.ignore_successors()
#
#         assert step_execution_successor.state == states.IGNORED
#         assert step_execution_successor_2.state == states.IGNORED
#         assert step_execution_successor_3.state == states.IGNORED
#
#     def test_execute_successors(self, mocker, step_instance, step_successor, step_successor_2, step_successor_3,
#                                 step_execution, step_execution_successor, step_execution_successor_2,
#                                 step_execution_successor_3, stage_execution_model):
#         mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.execute")
#         step_instance.add_successor(step_successor.model.id, 'output', 'test')
#         step_instance.add_successor(step_successor_2.model.id, constants.RESULT, constants.RESULT_OK)
#         step_successor.add_successor(step_successor_3.model.id, constants.RESULT, constants.RESULT_OK)
#         step_successor_2.add_successor(step_successor_3.model.id, constants.RESULT, constants.RESULT_OK)
#
#         step_execution.state = states.RUNNING
#         step_execution.state = states.FINISHED
#         step_execution.output = "test"
#         step_execution.result = constants.RESULT_FAIL
#
#         step_execution.execute_successors()
#         step_execution.ignore_successors()
#
#         assert step_execution_successor.state == states.PENDING
#         assert step_execution_successor_2.state == states.IGNORED
#         assert step_execution_successor_3.state == states.PENDING
#
#
# class TestStepExecution(TestStepExecutionBase):
#     def test_init_delete(self, step_execution):
#         step_ex_model_id = step_execution.model.id
#
#         step_execution.delete()
#         with pytest.raises(exceptions.StepExecutionObjectDoesNotExist):
#             step.StepExecution(step_execution_id=step_ex_model_id)
#
#     def test_properties_state(self, step_execution):
#         step_execution.state = 'FINISHED'
#         assert step_execution.state == 'FINISHED'
#
#     def test_properties_result(self, step_execution):
#         step_execution.result = constants.RESULT
#         assert step_execution.result == constants.RESULT
#
#     def test_properties_output(self, step_execution):
#         step_execution.output = 'test_output'
#         assert step_execution.output == 'test_output'
#
#     def test_properties_serialized_output(self, step_execution):
#         step_execution.serialized_output = {'test_md_out_key': 'test_output'}
#         assert step_execution.serialized_output == {'test_md_out_key': 'test_output'}
#
#     def test_properties_start_time(self, step_execution):
#         cur_time = timezone.now()
#         step_execution.start_time = cur_time
#         assert step_execution.start_time == cur_time
#
#     def test_properties_finish_time(self, step_execution):
#         cur_time = timezone.now()
#         step_execution.finish_time = cur_time
#         assert step_execution.finish_time == cur_time
#
#     def test_properties_valid(self, step_execution):
#         step_execution.valid = True
#         assert step_execution.valid is True
#
#     def test_filter(self, step_execution):
#         step_ex_list = step.StepExecution.filter(id=step_execution.model.id)
#         assert isinstance(step_ex_list, step.QuerySet)
#
#         # all
#         step_ex_list = step.StepExecution.filter()
#         assert isinstance(step_ex_list, step.QuerySet)
#
#         # wrong field
#         with pytest.raises(exceptions.WrongParameterError):
#             step.StepExecution.filter(non_ex_param='test')
#
#     def test_step_init_from_id(self, stage_execution_model):
#         step_exec_model = baker.make(StepExecutionModel, **{'stage_execution_id': stage_execution_model.id})
#
#         step.StepExecution(step_execution_id=step_exec_model.id)
#
#         with pytest.raises(exceptions.StepExecutionObjectDoesNotExist):
#             step.StepExecution(step_execution_id=int(step_exec_model.id) + 1)
#
#     def test__update_dynamic_variables(self, mocker, step_execution, step_execution_successor):
#         mocker.patch("cryton.hive.utility.util.get_dynamic_variables", return_value=["$parent.username"])
#         get_prefixes = mocker.patch("cryton.hive.utility.util.get_prefixes", return_value=["parent"])
#         fill_dynamic_variables = mocker.patch("cryton.hive.utility.util.fill_dynamic_variables",
#                                               return_value={"username": "test_user"})
#
#         step_execution.serialized_output = {"username": "test_user"}
#         updated_arguments = step_execution_successor._update_dynamic_variables({"username": "$parent.username"},
#                                                                                step_execution.model.id)
#         with pytest.raises(RuntimeError) as exc:
#             step_execution_successor._update_dynamic_variables({"username": "$parent.username"}, None)
#         assert str(exc.value) == "Parent must be specified for $parent prefix."
#
#         get_prefixes.assert_called_with(["$parent.username"], '.')
#         fill_dynamic_variables.assert_called_with({"username": "$parent.username"},
#                                                   {"parent": {"username": "test_user"}}, '.')
#
#         assert updated_arguments == {"username": "test_user"}
#
#     def test__update_arguments_with_execution_variables(self, mocker, step_execution):
#         execution_vars = [{"name": "test_name", "value": "test_value"}]
#         updated_arguments = step_execution._update_arguments_with_execution_variables(
#             {"test_variable": "{{test_name}}"}, execution_vars
#         )
#
#         assert updated_arguments == {"test_variable": "test_value"}
#
#     def test_update_step_arguments(self, mocker, step_execution, step_execution_successor, plan_execution_id):
#         step_execution_successor.parent_id = step_execution.model.id
#         ex_var_detail = baker.make(ExecutionVariableModel, id=1, plan_execution_id=plan_execution_id, name="test_name",
#                                    value="test_value").__dict__
#         ex_var_detail.pop('_state')
#
#         update_execution_variables = mocker.patch(
#             "cryton.hive.models.step.StepExecution._update_arguments_with_execution_variables",
#             return_value={"test_variable": "test_value", "username": "$parent.username"})
#         update_dynamic_variables = mocker.patch("cryton.hive.models.step.StepExecution._update_dynamic_variables",
#                                                 return_value={"test_variable": "test_value", "username": "test_name"})
#
#         arguments_to_be_updated = {"test_variable": "{{test_name}}", "username": "$parent.username"}
#         execution_variables = [ex_var_detail]
#
#         updated_arguments = step_execution_successor.update_step_arguments(arguments_to_be_updated,
#                                                                            plan_execution_id)
#
#         update_execution_variables.assert_called_with(arguments_to_be_updated, execution_variables)
#         update_dynamic_variables.assert_called_with(arguments_to_be_updated, step_execution_successor.parent_id)
#
#         assert updated_arguments == {"test_variable": "test_value", "username": "test_name"}
#
#     def test_return_msf_session_id_use_named_session(self, mocker, step_execution, step_instance, plan_execution_id):
#         step_instance.arguments = {"use_named_session": "test_session"}
#         mocker.patch("cryton.hive.models.session.get_msf_session_id", return_value="1")
#
#         return_msf_session_id = step_execution.get_msf_session_id(step_instance,
#                                                                   plan_execution_id)
#         assert return_msf_session_id == "1"
#
#     def test_return_msf_session_id_session_not_open(self, mocker, step_execution, step_instance, plan_execution_id):
#         step_instance.arguments = {"use_named_session": "test_session"}
#         step_execution.process_error_state = Mock()
#
#         with pytest.raises(exceptions.SessionIsNotOpen) as exc:
#             error_msg = {'message': "No session with specified name open",
#                          'session_name': "test_session",
#                          'plan_execution_id': plan_execution_id, 'step_id': step_instance.model.id}
#
#             mocker.patch("cryton.hive.models.session.get_msf_session_id",
#                          side_effect=exceptions.SessionObjectDoesNotExist(message=""))
#             step_execution.get_msf_session_id(step_instance, plan_execution_id)
#
#             assert step_execution.state == states.ERROR
#             assert error_msg == exc.value.message
#
#     def test_return_msf_session_id_use_any_session(self, mocker, step_execution, step_instance, plan_execution_id):
#         step_instance.arguments = {"use_any_session_to_target": "test_session"}
#
#         mocker.patch("cryton.hive.models.session.get_session_ids", return_value=["1"])
#         return_msf_session_id = step_execution.get_msf_session_id(step_instance,
#                                                                   plan_execution_id)
#
#         assert return_msf_session_id == "1"
#
#     def test_return_msf_session_id_no_session_object(self, mocker, step_execution, step_instance, plan_execution_id):
#         step_instance.arguments = {"use_any_session_to_target": "test_session"}
#         step_execution.process_error_state = Mock()
#
#         with pytest.raises(exceptions.SessionIsNotOpen) as exc:
#             mocker.patch("cryton.hive.models.session.get_session_ids", return_value=[])
#
#             error_msg = {
#                 "message": "No session to desired target open", "session_name": None, "session_id": None,
#                 "plan_execution_id": plan_execution_id, "step_id": step_instance.model.id, "plan_id": None,
#                 "target": None,
#                 "target_id": None
#             }
#
#             step_execution.get_msf_session_id(step_instance, plan_execution_id)
#
#             assert step_execution.state == states.ERROR
#             assert exc.value.message == error_msg
#
#     def test_send_step_execution_request(self, mocker, step_execution):
#         rpc_mock = mocker.patch("cryton.hive.models.step.rabbit_client.RpcClient")
#         rpc_mock.return_value.__enter__.return_value.call.return_value = {'event_v': {'return_code': 0}}
#         rpc_mock.return_value.__enter__.return_value.correlation_id = "1"
#         create_correlation_event = mocker.patch("cryton.hive.models.step.CorrelationEventModel.objects.create")
#
#         message_body = {"test_body_key": "test_body_value"}
#         target_queue = "test_target_queue"
#         reply_queue = "test_reply_queue"
#
#         step_execution.send_step_execution_request(rpc_mock.channel, message_body, reply_queue, target_queue)
#
#         create_correlation_event.assert_called_with(correlation_id="1", step_execution_id=step_execution.model.id)
#         rpc_mock.return_value.__enter__.return_value.call.assert_called_with(target_queue, message_body,
#                                                                              custom_reply_queue=reply_queue)
#
#     def test_send_step_execution_request_timeout(self, mocker, step_execution):
#         rpc_mock = mocker.patch("cryton.hive.models.step.rabbit_client.RpcClient")
#         rpc_mock.return_value.__enter__.return_value.call.side_effect = exceptions.RpcTimeoutError("")
#         rpc_mock.return_value.__enter__.return_value.correlation_id = "1"
#         step_execution.process_error_state = Mock()
#
#         message_body = {"test_body_key": "test_body_value"}
#         target_queue = "test_target_queue"
#         reply_queue = "test_reply_queue"
#
#         step_execution.send_step_execution_request(rpc_mock.channel, message_body, reply_queue, target_queue)
#
#         rpc_mock.return_value.__enter__.return_value.call.assert_called_with(target_queue, message_body,
#                                                                              custom_reply_queue=reply_queue)
#         step_execution.process_error_state.assert_called_once()
#
#     @pytest.mark.parametrize(
#         ("p_module_output", "p_saved_output_in_db"),
#         [
#             ({'serialized_output': 'test_serialized_output', 'output': 'test_output'},
#              {'serialized_output': 'test_serialized_output', 'output': 'test_output'}),
#             ({'serialized_output': None, 'output': None},
#              {'serialized_output': {}, 'output': ''}),
#         ])
#     def test_save_output(self, step_execution, p_module_output, p_saved_output_in_db):
#         step_execution.save_output(p_module_output)
#
#         assert step_execution.model.serialized_output == p_saved_output_in_db.get('serialized_output')
#         assert step_execution.model.output == p_saved_output_in_db.get('output')
#
#     def test_save_output_with_mappings(self, step_execution, step_model, stage_execution_model):
#         output = {'serialized_output': {'test': 1, 'best': 2}}
#         OutputMappingModel.objects.create(step_model=step_model, name_from='best', name_to='crest')
#         step_execution.save_output(output)
#         expected = {'test': 1, 'crest': 2}
#
#         assert step_execution.serialized_output == expected
#
#     def test_report(self):
#         step_ex_model = baker.make(StepExecutionModel, **{'state': 'FINISHED'})
#         step_execution = step.StepExecution(step_execution_id=step_ex_model.id)
#         report_dict = step_execution.report()
#
#         assert isinstance(report_dict, dict)
#         assert report_dict.get('state') == 'FINISHED'
#
#     # TODO: move to integration tests?
#     # def test_serialized_output_sharing(self, stage_model, step_model, step_successor_model, step_instance,
#     #                          step_successor, step_execution, step_execution_successor):
#     #
#     #     successor_module_args = {'password': '$parent.password', 'username': '$parent.username',
#     #                              'test_custom': '$custom.output'}
#     #     parent_serialized_output = {'username': 'test_username', 'password': 'root', 'output': 123}
#     #     expected_msg_body = {'password': 'root', 'username': 'test_username', 'test_custom': 123}
#     #
#     #     step_model.output_prefix = 'custom'
#     #     step_model.save()
#     #     step_successor_model.arguments[constants.MODULE_ARGUMENTS] = successor_module_args
#     #
#     #     # Add successor
#     #     step_instance.add_successor(step_successor_model.id, successor_type=constants.RESULT,
#     #                                 successor_value=constants.RESULT_OK)
#     #
#     #     step_execution.serialized_output = parent_serialized_output
#     #     step_execution_successor.parent_id = step_execution.model.id
#     #
#     #     updated_arguments = step_execution_successor._update_dynamic_variables(successor_module_args,
#     #                                                                            step_execution.model.id)
#     #
#     #     assert updated_arguments == expected_msg_body
#
#     def test_kill(self, mocker, step_execution):
#         rpc_mock = mocker.patch("cryton.hive.models.step.rabbit_client.RpcClient")
#         rpc_mock.return_value.__enter__.return_value.call.return_value = {'event_v': {'return_code': 0}}
#         mock_logger: Mock = mocker.patch("cryton.hive.utility.logger.logger")
#         step_execution.state = 'RUNNING'
#         baker.make(CorrelationEventModel, step_execution_id=step_execution.model.id)
#
#         step_execution.kill()
#         mock_logger.info.assert_called_once()
#
#     def test_re_execute(self, mocker, step_execution):
#         mocker.patch("cryton.hive.models.step.StepExecution.reset_execution_data")
#         execution = mocker.patch("cryton.hive.models.step.StepExecutionWorkerExecute.execute")
#
#         step_execution.re_execute()
#         execution.assert_called()
#
#     def test_reset_execution_data(self, step_execution, step_execution_model):
#         step_execution_model.state = 'test_state'
#         step_execution_model.start_time = datetime.now(tz=pytz.utc)
#         step_execution_model.pause_time = datetime.now(tz=pytz.utc)
#         step_execution_model.finish_time = datetime.now(tz=pytz.utc)
#         step_execution_model.result = 'test_result'
#         step_execution_model.serialized_output = 'test_serialized_output'
#         step_execution_model.output = 'test_output'
#         step_execution_model.valid = True
#         step_execution_model.parent_id = 1
#         step_execution_model.save()
#
#         step_execution.reset_execution_data()
#
#         assert step_execution.state == states.PENDING
#         assert step_execution.start_time is None
#         assert step_execution.finish_time is None
#         assert step_execution.result == ""
#         assert step_execution.serialized_output == {}
#         assert step_execution.output == ""
#         assert step_execution.valid is False
#         assert step_execution.parent_id is None
#
#     def test__prepare_execution(self, mocker, step_instance, stage_execution_model, plan_execution_id):
#         worker_instance = mocker.patch("cryton.hive.models.step.worker.Worker")
#
#         # creating StepExecution because step_execution fixture is from StepExecutionWorkerExecute class and method
#         # in testing is called on super()
#         step_execution = step.StepExecution(step_model_id=step_instance.model.id,
#                                             stage_execution_id=stage_execution_model.id)
#
#         prepare_execution = step_execution._prepare_execution()
#
#         assert prepare_execution == (plan_execution_id, worker_instance.return_value)
#
#     def test_postprocess(self, mocker, step_execution, plan_execution_id, step_model, plan_execution_model):
#         step_model.arguments.update({"create_named_session": "test_session"})
#         step_model.save()
#         plan_execution_model.evidence_directory = "test_dir"
#         plan_execution_model.save()
#
#         create_session = mocker.patch("cryton.hive.models.step.session.create_session")
#         save_output = mocker.patch("cryton.hive.models.step.StepExecution.save_output")
#         mocker.patch("cryton.hive.models.step.timezone.now", return_value=datetime(2022, 1, 1, 12, 26, 2,
#                                                                                        tzinfo=pytz.utc))
#
#         return_values = {constants.RETURN_CODE: constants.CODE_OK, "serialized_output": {"session_id": "1"}}
#
#         step_execution.postprocess(return_values)
#         create_session.assert_called_with(plan_execution_id, "1", "test_session")
#         assert step_execution.result == constants.RESULT_OK
#         assert step_execution.finish_time == datetime(2022, 1, 1, 12, 26, 2, tzinfo=pytz.utc)
#         assert step_execution.state == states.FINISHED
#         save_output.assert_called_with({
#             constants.RETURN_CODE: constants.CODE_OK, "serialized_output": {"session_id": "1"}})
#
#
# class TestStepExecutionWorkerExecute(TestStepExecutionBase):
#     @pytest.fixture()
#     def step_instance(self, stage_model):
#         step_arguments = {'name': 'test_step',
#                           'step_type': constants.STEP_TYPE_WORKER_EXECUTE,
#                           'stage_model_id': stage_model.id,
#                           'is_init': True,
#                           'arguments': {constants.MODULE: "module_name",
#                                         constants.MODULE_ARGUMENTS: {}}
#                           }
#         return step.StepWorkerExecute(**step_arguments)
#
#     @pytest.fixture()
#     def step_execution(self, step_instance, stage_execution_model):
#         return step.StepExecutionWorkerExecute(step_model_id=step_instance.model.id,
#                                                stage_execution_id=stage_execution_model.id)
#
#     def test_validate(self, step_instance, mocker, step_execution, plan_execution_model, worker_instance):
#         mock_rpc_client = mocker.patch("cryton.hive.models.step.rabbit_client.RpcClient")
#         mock_rpc_client.return_value.__enter__.return_value.call \
#             .return_value = {constants.EVENT_V: {constants.RETURN_CODE: 0}}
#
#         resp = step_execution.validate()
#
#         assert resp is True
#
#     def test_execute(self, mocker, step_instance, step_execution, plan_execution_id, worker_instance):
#         rabbit_channel = Mock()
#         _prepare_execution = mocker.patch("cryton.hive.models.step.StepExecution._prepare_execution",
#                                           return_value=[plan_execution_id, worker_instance])
#         update_step_arguments = mocker.patch("cryton.hive.models.step.StepExecution.update_step_arguments",
#                                              return_value={})
#         return_msf_session_id = mocker.patch("cryton.hive.models.step.StepExecution.get_msf_session_id",
#                                              return_value="1")
#         send_step_execution_request = mocker.patch(
#             "cryton.hive.models.step.StepExecution.send_step_execution_request",
#             return_value="1")
#
#         step_execution.execute(rabbit_channel)
#
#         update_step_arguments.assert_called_with(step_instance.module_arguments, plan_execution_id)
#         return_msf_session_id.assert_called_with(step_execution.step_instance, plan_execution_id)
#         send_step_execution_request.assert_called_with(rabbit_channel,
#                                                        {
#                                                            constants.STEP_TYPE: step_instance.step_type,
#                                                            constants.ARGUMENTS: {
#                                                                constants.MODULE: "module_name",
#                                                                constants.MODULE_ARGUMENTS: {constants.SESSION_ID: "1"}
#                                                            }
#                                                        },
#                                                        SETTINGS.rabbit.queues.attack_response,
#                                                        worker_instance.attack_q_name
#                                                        )
#
#
# class TestStepExecutionEmpireExecute(TestStepExecutionBase):
#     @pytest.fixture()
#     def step_instance(self, stage_model):
#         step_arguments = {
#             'name': 'test_step',
#             'step_type': constants.STEP_TYPE_EMPIRE_EXECUTE,
#             'stage_model_id': stage_model.id,
#             'is_init': True,
#             'arguments': {
#                 constants.USE_AGENT: "test_agent",
#                 constants.MODULE: "module_name"
#             }
#         }
#         return step.StepEmpireExecute(**step_arguments)
#
#     @pytest.fixture()
#     def step_execution(self, step_instance, stage_execution_model):
#         return step.StepExecutionEmpireExecute(step_model_id=step_instance.model.id,
#                                                stage_execution_id=stage_execution_model.id)
#
#     def test_step_type_does_not_exist(self):
#         with pytest.raises(exceptions.StepTypeDoesNotExist):
#             step.StepType["wrong_step_type"].value()
#
#     def test_execute(self, mocker, step_instance, step_execution, plan_execution_id, worker_instance):
#         rabbit_channel = Mock()
#         _prepare_execution = mocker.patch("cryton.hive.models.step.StepExecution._prepare_execution",
#                                           return_value=[plan_execution_id, worker_instance])
#         update_step_arguments = mocker.patch("cryton.hive.models.step.StepExecution.update_step_arguments",
#                                              return_value=step_instance.arguments)
#         send_step_execution_request = mocker.patch(
#             "cryton.hive.models.step.StepExecution.send_step_execution_request",
#             return_value="1")
#
#         step_execution.execute(rabbit_channel)
#
#         update_step_arguments.assert_called_with(step_instance.arguments, plan_execution_id)
#         send_step_execution_request.assert_called_with(rabbit_channel,
#                                                        {
#                                                            constants.STEP_TYPE: step_instance.step_type,
#                                                            constants.ARGUMENTS: {
#                                                                constants.USE_AGENT: "test_agent",
#                                                                constants.MODULE: "module_name"
#                                                            }
#                                                        },
#                                                        SETTINGS.rabbit.queues.attack_response,
#                                                        worker_instance.attack_q_name
#                                                        )
#
#
# class TestStepExecutionEmpireAgentDeploy(TestStepExecutionBase):
#     @pytest.fixture()
#     def step_instance(self, stage_model):
#         step_arguments = {'name': 'test_step',
#                           'step_type': constants.STEP_TYPE_DEPLOY_AGENT,
#                           'stage_model_id': stage_model.id,
#                           'is_init': True,
#                           'arguments': {}
#                           }
#         return step.StepEmpireAgentDeploy(**step_arguments)
#
#     @pytest.fixture()
#     def step_execution(self, step_instance, stage_execution_model):
#         return step.StepExecutionEmpireAgentDeploy(step_model_id=step_instance.model.id,
#                                                    stage_execution_id=stage_execution_model.id)
#
#     def test_execute(self, mocker, step_instance, step_execution, plan_execution_id, worker_instance):
#         rabbit_channel = Mock()
#         _prepare_execution = mocker.patch("cryton.hive.models.step.StepExecution._prepare_execution",
#                                           return_value=[plan_execution_id, worker_instance])
#         update_step_arguments = mocker.patch("cryton.hive.models.step.StepExecution.update_step_arguments",
#                                              return_value={})
#         return_msf_session_id = mocker.patch("cryton.hive.models.step.StepExecution.get_msf_session_id",
#                                              return_value="1")
#         send_step_execution_request = mocker.patch(
#             "cryton.hive.models.step.StepExecution.send_step_execution_request",
#             return_value="1")
#
#         step_execution.execute(rabbit_channel)
#
#         update_step_arguments.assert_called_with(step_instance.arguments,
#                                                  plan_execution_id)
#
#         return_msf_session_id.assert_called_with(step_execution.step_instance, plan_execution_id)
#
#         send_step_execution_request.assert_called_with(rabbit_channel,
#                                                        {
#                                                            constants.STEP_TYPE: step_instance.step_type,
#                                                            constants.ARGUMENTS: {constants.SESSION_ID: "1"}
#                                                        },
#                                                        SETTINGS.rabbit.queues.agent_response,
#                                                        worker_instance.agent_q_name
#                                                        )
