import pytest
from unittest.mock import Mock

from cryton_core.lib.models import stage, step
from cryton_core.lib.util import creator, exceptions


@pytest.mark.django_db
class TestCreator:
    def test_create_plan(self, mocker):
        mock_plan = mocker.patch("cryton_core.lib.util.creator.plan.Plan")
        mock_stage = mocker.patch("cryton_core.lib.util.creator.stage.Stage")
        mocker.patch("cryton_core.lib.util.creator.stage.StageModel")
        mock_create_stage = mocker.patch("cryton_core.lib.util.creator.create_stage")

        mock_plan.return_value.model.id = 0
        test_plan_dict = {"plan": {"name": "", "stages": [{"depends_on": [""]}]}}

        result = creator.create_plan(test_plan_dict)

        assert result == 0
        mock_plan.validate.assert_called()
        mock_create_stage.assert_called()
        mock_stage.return_value.add_dependency.assert_called()

    def test_create_plan_create_error(self, mocker):
        mock_plan = mocker.patch("cryton_core.lib.util.creator.plan.Plan")
        mock_create_stage = mocker.patch("cryton_core.lib.util.creator.create_stage")

        mock_create_stage.side_effect = RuntimeError
        test_plan_dict = {"plan": {"name": "", "stages": [{"depends_on": [""]}]}}

        with pytest.raises(exceptions.PlanCreationFailedError):
            creator.create_plan(test_plan_dict)

        mock_plan.validate.assert_called()

    def test_create_plan_dependency_error(self, mocker):
        mocker.patch("cryton_core.lib.util.creator.create_stage")
        mocker.patch("cryton_core.lib.util.creator.stage.Stage")
        mock_plan = mocker.patch("cryton_core.lib.util.creator.plan.Plan")
        mock_stage_model_get = mocker.patch("cryton_core.lib.util.creator.stage.StageModel.objects.get")
        mock_stage_model_get.side_effect = stage.StageModel.DoesNotExist

        test_plan_dict = {"plan": {"name": "", "stages": [{"depends_on": [""]}]}}

        with pytest.raises(exceptions.DependencyDoesNotExist):
            creator.create_plan(test_plan_dict)

        mock_plan.validate.assert_called()

    def test_create_stage(self, mocker):
        mock_stage = mocker.patch("cryton_core.lib.util.creator.stage.Stage")
        mock_create_step = mocker.patch("cryton_core.lib.util.creator.create_step")
        mocker.patch("cryton_core.lib.util.creator.step.Step")
        mock_create_successor = mocker.patch("cryton_core.lib.util.creator.create_successor")

        mock_stage.return_value.model.id = 0
        test_stage_dict = {"steps": [{"next": [{"step": "", "type": "", "value": ""}]}]}

        result = creator.create_stage(test_stage_dict, 0)

        assert result == 0
        mock_create_step.assert_called()
        mock_create_successor.assert_called()

    @pytest.mark.parametrize("test_step_dict",
                             [{"output_mapping": [""]},
                              {"output_mapping": [""], "next": ["", ""]}])
    def test_create_step(self, mocker, test_step_dict):
        mock_step = mocker.patch("cryton_core.lib.util.creator.step.Step")
        mock_create_mapping = mocker.patch("cryton_core.lib.util.creator.create_output_mapping")

        mock_step.return_value.model.id = 0

        result = creator.create_step(test_step_dict, 0)

        assert result == 0
        mock_create_mapping.assert_called()

    @pytest.mark.parametrize("test_values", ["", [""]])
    def test_create_successor(self, mocker, test_values):
        mocker.patch("cryton_core.lib.util.creator.step.StepModel.objects.get")
        mock_parent_step = Mock()

        creator.create_successor(mock_parent_step, 0, "", "", test_values)
        mock_parent_step.add_successor.assert_called()

    def test_create_successor_non_existent(self, mocker):
        mock_step_model_get = mocker.patch("cryton_core.lib.util.creator.step.StepModel.objects.get")
        mock_step_model_get.side_effect = step.StepModel.DoesNotExist

        with pytest.raises(exceptions.SuccessorCreationFailedError):
            creator.create_successor(Mock(), 0, "", "", "")

    def test_create_output_mapping(self, mocker):
        mock_mapping_create = mocker.patch("cryton_core.lib.util.creator.OutputMappingModel.objects.create")

        creator.create_output_mapping({"name_from": "", "name_to": ""}, 0)

        mock_mapping_create.assert_called()

    @pytest.mark.parametrize("w_name, w_description", [("test", "test"), ("test", "test")])
    def test_create_worker(self, mocker, w_name, w_description):
        mock_worker = mocker.patch("cryton_core.lib.util.creator.worker.Worker")
        mock_worker.return_value.model.id = 0

        result = creator.create_worker(w_name, w_description)

        assert result == 0

    @pytest.mark.parametrize("w_name, w_description", [("", ""), ])
    def test_create_worker_error(self, w_name, w_description):
        with pytest.raises(exceptions.WrongParameterError):
            creator.create_worker(w_name, w_description)
