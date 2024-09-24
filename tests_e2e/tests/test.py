import time
import click
import json
from typing import List, Dict

from tests_e2e.util import helpers, config
from tests_e2e.util.exceptions import CannotParseResponseError


class Test:
    """
    Base class for testing.
    """

    def __init__(self):
        self.description = ""
        self._executable: str = config.CRYTON_CLI_EXECUTABLE
        self.results = {}

    def run(self):
        """
        Prepares, runs tests and echoes the results.
        :return: None
        """
        click.echo()
        click.echo(self.description)
        click.echo()

        self.results["start_time"] = time.time()
        self._prepare()
        self._print_info("Settings", self.get_pre_info())

        self._run_tests()
        self.results["finish_time"] = time.time()
        self.results["test_duration"] = self.results["finish_time"] - self.results["start_time"]

        click.secho("Test successfully finished!", fg="green")
        self._print_info("Results", self.results)

    def _prepare(self):
        """
        Prepares everything in order to start the actual test(s).
        :return: None
        """

    @staticmethod
    def _print_info(header: str, to_print: Dict):
        """
        Pretty prints the information to the user.
        :param header: Information header
        :param to_print: Information to print
        :return: None
        """
        bad_keys = ["failed_steps"]
        click.echo()
        click.echo(f"{header}:")

        max_len = max([len(line_key) for line_key in to_print.keys()])
        for key, value in to_print.items():
            fg = "red" if key in bad_keys else None
            click.secho(f"{key}:{' ' * (max_len - len(key))} {value}", fg=fg)

        click.echo()

    def get_pre_info(self) -> Dict:
        """
        Gets pre-test information.
        :return: Information that will be printed to the user
        """

    def _run_tests(self):
        """
        Runs the tests.
        :return: None
        """

    def _cli_call(self, command: List[str]) -> str:
        """
        Calls CLI and parses the response.
        :param command: Command added to the CLI executable
        :return: Parsed response
        """
        cmd = [self._executable] + command
        result = helpers.execute_command(cmd)

        try:
            return result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            raise CannotParseResponseError(f"Couldn't parse the CLI response. Original result: {result.stdout}")

    def _cli_call_json(self, command: List[str]) -> Dict:
        """
        Calls CLI and parses the response.
        :param command: Command added to the CLI executable
        :return: Parsed response
        """
        cmd = [self._executable, "--debug"] + command
        result = helpers.execute_command(cmd)

        try:
            return json.loads(result.stdout.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as err:
            click.echo(f"\n{result.stdout.decode('utf-8')}\n")
            raise CannotParseResponseError(f"Couldn't parse the CLI response. Original exception: {err}")
