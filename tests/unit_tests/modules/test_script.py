import json
from unittest.mock import patch
from pytest_mock import MockerFixture
import pytest

from cryton.modules.script import mod


@pytest.mark.parametrize(
    "p_error, p_return_code",
    [
        ("test_error", -1),
        ("", 0)
    ]
)
def test_execute(mocker: MockerFixture, p_error, p_return_code):
    mod_arguments = {
        "script_path": "/tmp/test.py",
        "executable": "python3",
        "serialized_output": True,
        "timeout": 30,
    }
    mocker.patch("mod.validate")
    mocker.patch("os.path.exists", return_value=True)
    completed_process_mock = mocker.patch("subprocess.CompletedProcess")
    completed_process_mock.stdout.decode.return_value = json.dumps({"test": "output"})
    completed_process_mock.stderr.decode.return_value = p_error
    mocker.patch("subprocess.run", return_value=completed_process_mock)

    result = mod.execute(mod_arguments)
    completed_process_mock.check_returncode.assert_called_once()
    assert result == {
        "output": "STDOUT: {\"test\": \"output\"} \n STDERR: " + p_error,
        "serialized_output": {"test": "output"},
        "return_code": p_return_code
    }

    with patch("json.loads", side_effect=TypeError):
        result = mod.execute(mod_arguments)
        assert result == {
            "output": "STDOUT: {\"test\": \"output\"} \n STDERR: " + p_error +
                      "serialized_output_error: Output of the script is not valid JSON.",
            "serialized_output": {},
            "return_code": -1
        }
