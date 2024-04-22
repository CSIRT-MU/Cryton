import json
import subprocess

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# TODO: this module is only updated to work with the new rules, it's not reworked
#  - update validation (mainly descriptions)
#  - update check_requirements
#  - rework the module
#  - add tests
class Module(ModuleBase):
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `script` module.",
        "properties": {
            "script_path": {"type": "string"},
            "executable": {"type": "string"},
            "script_arguments": {"type": "string"},
            "serialize_output": {"type": "boolean"},
            "timeout": {"type": "integer"},
        },
        "required": ["script_path", "executable"],
        "additionalProperties": False,
    }

    def __init__(self, arguments: dict):
        super().__init__(arguments)

    def check_requirements(self) -> None:
        pass

    def execute(self) -> ModuleOutput:
        file_exec = self._arguments.get("script_path")
        special_args = self._arguments.get("script_arguments")
        serialize_output = self._arguments.get("serialize_output", False)
        timeout = self._arguments.get("timeout")
        executable = self._arguments.get("executable")

        if timeout is not None:
            try:
                timeout = int(timeout)
            except ValueError:
                self._data.output = "please check your timeout input"
                return self._data
        else:
            timeout = None

        cmd = [executable, file_exec]

        if special_args:
            special_args = str(special_args).split(" ")
            for each in special_args:
                cmd.append(str(each))

        try:
            process = subprocess.run(cmd, timeout=timeout, capture_output=True)
            process.check_returncode()
        except subprocess.TimeoutExpired:
            self._data.output = "Timeout expired"
            return self._data
        except subprocess.CalledProcessError as err:  # process exited with return code other than 0
            self._data.output = err.stderr.decode("utf-8")
            return self._data
        except Exception as err:
            self._data.output = str(err)
            return self._data

        process_stdout = process.stdout.decode("utf-8")
        print(process_stdout)
        if not (process_error := process.stderr.decode("utf-8")):
            self._data.result = Result.OK

        self._data.output = f"{process_stdout}\n{process_error}"

        if serialize_output:
            try:
                script_serialized_output = json.loads(process_stdout)
                self._data.serialized_output = script_serialized_output
            except (json.JSONDecodeError, TypeError):
                self._data.output += "serialized_output_error: Output of the script is not valid JSON."
                self._data.result = Result.FAIL

        return self._data
