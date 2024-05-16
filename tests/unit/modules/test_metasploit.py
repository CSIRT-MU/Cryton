from unittest.mock import Mock
from pytest_mock import MockerFixture
import pytest
from dataclasses import asdict

from cryton.modules.metasploit.module import Module, ModuleOutput, Result


class TestModuleMetasploit:
    path = "cryton.modules.metasploit.module"

    @pytest.fixture
    def f_msf_client(self, mocker: MockerFixture):
        return mocker.patch(f"{self.path}.MetasploitClientUpdated")

    @pytest.mark.parametrize(
        "p_arguments",
        [
            {"module_name": "test", "datastore": {"option": "value"}, "timeout": 1},
            {"module_name": "test"},
            {"commands": ["test"]},
            {"commands": ["test"], "timeout": 1},
        ],
    )
    def test_schema(self, p_arguments: dict):
        Module.validate_arguments(p_arguments)

    # @pytest.mark.parametrize(
    #     "p_arguments",
    #     [
    #         {},
    #         {"non_existent": "placeholder"},
    #         {"module_name": "test", "non_existent": "placeholder"},
    #         {"commands": ["test"], "non_existent": "placeholder"},
    #         {"module_name": "test", "commands": ["test"]},
    #         {"timeout": 1},
    #     ],
    # )
    # def test_schema_error(self, p_arguments: dict):
    #     with pytest.raises(Exception):
    #         Module.validate_arguments(p_arguments)

    def test_check_requirements(self, f_msf_client):
        assert Module({}).check_requirements() is None

    def test_execute(self, f_msf_client, mocker: MockerFixture):
        mock__get_commands = mocker.patch(f"{self.path}.Module._get_commands", return_value=["test"])
        mock__run_commands = mocker.patch(f"{self.path}.Module._run_commands", return_value="test")
        mock__parse_results = mocker.patch(f"{self.path}.Module._parse_results")

        result = Module({}).execute()

        assert asdict(result) == asdict(ModuleOutput())
        mock__get_commands.assert_called_once()
        mock__run_commands.assert_called_once_with(["test"])
        mock__parse_results.assert_called_once_with("test")

    @pytest.mark.parametrize(
        "p_arguments, p_commands",
        [
            ({"commands": ["test"]}, ["test"]),
            (
                {"module_name": "test", "datastore": {"a": "x", "payload": "test", "b": 1}},
                ["use test", "set PAYLOAD test", "set A x", "set B 1", "run -z"],
            ),
        ],
    )
    def test__get_commands(self, p_arguments, p_commands, f_msf_client):
        assert Module(p_arguments)._get_commands() == p_commands

    def test__run_commands(self, f_msf_client):
        mock_msf_console = Mock()
        mock_msf_console.execute.return_value = "output"
        f_msf_client.return_value.consoles.create.return_value = mock_msf_console

        assert Module({})._run_commands(["test", "test2"]) == "output"
        mock_msf_console.execute.assert_called_once_with("test\ntest2", None)
        mock_msf_console.destroy.assert_called_once()

    @pytest.mark.parametrize(
        "p_output, p_serialized_output, p_result",
        [
            (
                "\n[*] Command shell session 1 opened (127.0.0.1:4446 -> 127.0.0.1:39188) at 2024-05-07 16:23:59\n",
                {"session_id": 1},
                Result.OK,
            ),
            ("\nExploit failed (error)\n", {}, Result.FAIL),
            ("\n[*] Exploit completed, but no session was created.\n", {}, Result.FAIL),
            ("Other than error", {}, Result.OK),
        ],
    )
    def test__parse_results(self, p_output, p_serialized_output, p_result, f_msf_client):
        module = Module({})
        module._parse_results(p_output)

        assert module._data.output == p_output
        assert module._data.serialized_output == p_serialized_output
        assert module._data.result == p_result
