import pytest
from pytest_mock import MockFixture

from cryton_core.lib.util import exceptions, states, constants
from cryton_core.lib.util.logger import structlog


@pytest.fixture
def f_check_transition_validity(mocker: MockFixture):
    return mocker.patch('cryton_core.lib.util.states.StateMachine._check_transition_validity')


@pytest.fixture
def f_check_valid_state(mocker: MockFixture):
    return mocker.patch('cryton_core.lib.util.states.StateMachine._check_valid_state')


@pytest.fixture(autouse=True)
def f_logger(mocker: MockFixture):
    mocker.patch('cryton_core.lib.util.logger.logger', structlog.getLogger(constants.LOGGER_CRYTON_TESTING))


class TestStateMachine:
    def test_base_state_machine_init(self):
        ret = states.StateMachine(1, ['TEST'], [('TEST', 'TEST')])

        assert isinstance(ret, states.StateMachine)

    def test_check_transition_validity(self):
        machine = states.StateMachine(1, ['TEST', 'INVALID'], [('TEST', 'INVALID')])

        assert machine._check_transition_validity('TEST', 'INVALID') is True

    @pytest.mark.parametrize("p_state_from, p_state_to", [("INVALID", "TEST"), ("TEST", "INVALID")])
    def test_check_transition_validity_invalid_state_from(self, p_state_from, p_state_to):
        machine = states.StateMachine(1, ['TEST'], [('TEST', 'TEST')])
        
        with pytest.raises(exceptions.InvalidStateError):
            machine._check_transition_validity(p_state_from, p_state_to)

    def test_check_transition_validity_duplicate_transition(self):
        machine = states.StateMachine(1, ['TEST'], [('TEST', 'INVALID')])
        
        assert machine._check_transition_validity('TEST', 'TEST') is False

    def test_check_transition_validity_invalid_transition(self):
        machine = states.StateMachine(1, ['TEST', 'INVALID'], [('TEST', 'INVALID')])
        with pytest.raises(exceptions.StateTransitionError):
            machine._check_transition_validity('INVALID', 'TEST')

    def test_check_valid_state(self):
        state_list = ['TEST']
        machine = states.StateMachine(1, ['TEST'], [])
        assert machine._check_valid_state('TEST', state_list) is None

    def test_check_valid_state_empty_list(self):
        state_list = []
        machine = states.StateMachine(1, ['TEST'], [])
        assert machine._check_valid_state('TEST', state_list) is None

    def test_check_valid_state_invalid_state(self):
        state_list = ['TEST']
        machine = states.StateMachine(1, ['TEST'], [])
        with pytest.raises(exceptions.InvalidStateError):
            machine._check_valid_state('INVALID', state_list)


class TestRunStateMachine:
    def test_run_state_machine_init(self):
        ret = states.RunStateMachine(1)

        assert isinstance(ret, states.RunStateMachine)

    @pytest.mark.parametrize("p_valid_transition", [True, False])
    def test_run_state_machine_validate_transition_valid(self, f_check_transition_validity, p_valid_transition):
        f_check_transition_validity.return_value = p_valid_transition
        machine = states.RunStateMachine(1)
        
        assert machine.validate_transition('TEST', 'TEST') is p_valid_transition

    def test_run_state_machine_validate_transition_invalid_state(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.InvalidStateError('', 1, '', [])
        machine = states.RunStateMachine(1)
        with pytest.raises(exceptions.RunInvalidStateError):
            machine.validate_transition('TEST', 'TEST')

    def test_run_state_machine_validate_transition_invalid_transition(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.StateTransitionError('', 1, '', '', [])
        machine = states.RunStateMachine(1)
        
        with pytest.raises(exceptions.RunStateTransitionError):
            machine.validate_transition('TEST', 'TEST')

    def test_run_state_machine_validate_state(self, f_check_valid_state):
        f_check_valid_state.return_value = None
        state_list = ['TEST']
        machine = states.RunStateMachine(1)
        
        assert machine.validate_state('TEST', state_list) is None
    
    def test_run_state_machine_validate_state_invalid_state(self, f_check_valid_state):
        f_check_valid_state.side_effect = exceptions.InvalidStateError('', 1, '', [])
        state_list = ['TEST']
        machine = states.RunStateMachine(1)
        
        with pytest.raises(exceptions.RunInvalidStateError):
            machine.validate_state('INVALID', state_list)


class TestPlanStateMachine:

    def test_plan_state_machine_init(self):
        ret = states.PlanStateMachine(1)

        assert isinstance(ret, states.PlanStateMachine)
    
    def test_plan_state_machine_validate_transition_valid(self, f_check_transition_validity):
        f_check_transition_validity.return_value = True
        machine = states.PlanStateMachine(1)

        assert machine.validate_transition('TEST', 'TEST') is True
    
    def test_plan_state_machine_validate_transition_duplicate(self, f_check_transition_validity):
        f_check_transition_validity.return_value = False
        machine = states.PlanStateMachine(1)

        assert machine.validate_transition('TEST', 'TEST') is False
        
    def test_plan_state_machine_validate_transition_invalid_state(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.InvalidStateError('', 1, '', [])
        machine = states.PlanStateMachine(1)

        with pytest.raises(exceptions.PlanInvalidStateError):
            machine.validate_transition('TEST', 'TEST')
    
    def test_plan_state_machine_validate_transition_invalid_transition(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.StateTransitionError('', 1, '', '', [])
        machine = states.PlanStateMachine(1)

        with pytest.raises(exceptions.PlanStateTransitionError):
            machine.validate_transition('TEST', 'TEST')
    
    def test_plan_state_machine_validate_state(self, f_check_valid_state):
        f_check_valid_state.return_value = None
        state_list = ['TEST']
        machine = states.PlanStateMachine(1)

        assert machine.validate_state('TEST', state_list) is None

    def test_plan_state_machine_validate_state_invalid_state(self, f_check_valid_state):
        f_check_valid_state.side_effect = exceptions.InvalidStateError('', 1, '', [])
        state_list = ['TEST']
        machine = states.PlanStateMachine(1)

        with pytest.raises(exceptions.PlanInvalidStateError):
            machine.validate_state('INVALID', state_list)

    def test_stage_state_machine_init(self):
        ret = states.StageStateMachine(1)

        assert isinstance(ret, states.StageStateMachine)
    
    def test_stage_state_machine_validate_transition_valid(self, f_check_transition_validity):
        f_check_transition_validity.return_value = True
        machine = states.StageStateMachine(1)

        assert machine.validate_transition('TEST', 'TEST') is True

    def test_stage_state_machine_validate_transition_duplicate(self, f_check_transition_validity):
        f_check_transition_validity.return_value = False
        machine = states.StageStateMachine(1)

        assert machine.validate_transition('TEST', 'TEST') is False

    def test_stage_state_machine_validate_transition_invalid_state(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.InvalidStateError('', 1, '', [])
        machine = states.StageStateMachine(1)

        with pytest.raises(exceptions.StageInvalidStateError):
            machine.validate_transition('TEST', 'TEST')
    
    def test_stage_state_machine_validate_transition_invalid_transition(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.StateTransitionError('', 1, '', '', [])

        machine = states.StageStateMachine(1)

        with pytest.raises(exceptions.StageStateTransitionError):
            machine.validate_transition('TEST', 'TEST')
    
    def test_stage_state_machine_validate_state(self, f_check_valid_state):
        f_check_valid_state.return_value = None
        state_list = ['TEST']

        machine = states.StageStateMachine(1)

        assert machine.validate_state('TEST', state_list) is None

    def test_stage_state_machine_validate_state_invalid_state(self, f_check_valid_state):
        f_check_valid_state.side_effect = exceptions.InvalidStateError('', 1, '', [])
        state_list = ['TEST']

        machine = states.StageStateMachine(1)

        with pytest.raises(exceptions.StageInvalidStateError):
            machine.validate_state('INVALID', state_list)

    def test_step_state_machine_init(self):
        ret = states.StepStateMachine(1)

        assert isinstance(ret, states.StepStateMachine)
    
    def test_step_state_machine_validate_transition_valid(self, f_check_transition_validity):
        f_check_transition_validity.return_value = True
        machine = states.StepStateMachine(1)

        assert machine.validate_transition('TEST', 'TEST') is True

    def test_step_state_machine_validate_transition_duplicate(self, f_check_transition_validity):
        f_check_transition_validity.return_value = False
        machine = states.StepStateMachine(1)

        assert machine.validate_transition('TEST', 'TEST') is False

    def test_step_state_machine_validate_transition_invalid_state(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.InvalidStateError('', 1, '', [])
        machine = states.StepStateMachine(1)

        with pytest.raises(exceptions.StepInvalidStateError):
            machine.validate_transition('TEST', 'TEST')
            
    def test_step_state_machine_validate_transition_invalid_transition(self, f_check_transition_validity):
        f_check_transition_validity.side_effect = exceptions.StateTransitionError('', 1, '', '', [])
        machine = states.StepStateMachine(1)

        with pytest.raises(exceptions.StepStateTransitionError):
            machine.validate_transition('TEST', 'TEST')
    
    def test_step_state_machine_validate_state(self, f_check_valid_state):
        f_check_valid_state.return_value = None
        state_list = ['TEST']

        machine = states.StepStateMachine(1)

        assert machine.validate_state('TEST', state_list) is None
    
    def test_step_state_machine_validate_state_invalid_state(self, f_check_valid_state):
        f_check_valid_state.side_effect = exceptions.InvalidStateError('', 1, '', [])
        state_list = ['TEST']
        machine = states.StepStateMachine(1)

        with pytest.raises(exceptions.StepInvalidStateError):
            machine.validate_state('INVALID', state_list)
