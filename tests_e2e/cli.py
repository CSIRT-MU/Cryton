import click
from os import path, get_terminal_size
from typing import List

from tests_e2e import tests
from tests_e2e.util import config


@click.group()
@click.version_option(message=f"%(prog)s, version %(version)s")
@click.option('-wa', '--worker-address', type=click.STRING, help="Worker's address")
@click.option('-wn', '--worker-name', type=click.STRING, help="Worker's name")
def cli(worker_address: str, worker_name: str) -> None:
    """
    A CLI for Cryton E2E.

    \f
    :return: None
    """


@cli.command('run-tests')
@click.option('-t', '--test', 'test_types', type=click.STRING, help='Choose what tests to run.', multiple=True)
def run_tests(test_types: List[str]):
    """
    Run E2E tests.

    \f
    :param test_types: What test(s) to run
    :return: None
    """
    terminal_width = get_terminal_size().columns
    section_separator = f"{'- '*(terminal_width//2-1)}\n\n"

    if not test_types:
        test_types = ["all"]
    click.echo(f"Tests to run: {test_types}.")
    click.echo(section_separator)

    default_workers = [{"name": config.WORKER_NAME, "description": "e2e tests - worker 1"}]
    default_inventory = path.join(config.E2E_DIRECTORY, "inventory.yml")
    default_execution_variables = default_inventory

    if "all" in test_types or "basic" in test_types:
        template = path.join(config.TEMPLATES_DIRECTORY, "basic/template.yml")
        tests.TestBasicExecution(template, default_workers, [default_inventory], None, 30).run()
        click.echo(section_separator)

    if "all" in test_types or "http_trigger" in test_types:
        template = path.join(config.TEMPLATES_DIRECTORY, "http-trigger/template.yml")
        tests.TestHTTPTriggerExecution(template, default_workers, [default_inventory], None, 30).run()
        click.echo(section_separator)

    if "all" in test_types or "msf_trigger" in test_types:
        template = path.join(config.TEMPLATES_DIRECTORY, "msf-trigger/template.yml")
        tests.TestMSFTriggerExecution(template, default_workers, [default_inventory], None, 30).run()
        click.echo(section_separator)

    if "all" in test_types or "empire" in test_types:
        template = path.join(config.TEMPLATES_DIRECTORY, "empire-agents/linux/template.yml")
        tests.TestEmpireExecution(template, default_workers, [default_inventory], None, 30).run()
        click.echo(section_separator)

    if "all" in test_types or "datetime_trigger" in test_types:
        template = path.join(config.TEMPLATES_DIRECTORY, "datetime-trigger/template.yml")
        tests.TestDatetimeTriggerExecution(template, default_workers, [default_inventory], None, 30).run()
        click.echo(section_separator)

    if "all" in test_types or "advanced" in test_types:
        template_advanced = path.join(config.TEMPLATES_DIRECTORY, "advanced/template.yml")
        tests.TestAdvancedExecution(template_advanced, default_workers, [default_inventory],
                                    [default_execution_variables], 30).run()
        click.echo(section_separator)

    if "all" in test_types or "control" in test_types:
        template = path.join(config.TEMPLATES_DIRECTORY, "advanced/template.yml")
        tests.TestAdvancedControl(template, default_workers, [default_inventory], None, 30).run()


@cli.command('run-custom')
@click.argument('template', type=click.Path(exists=True), required=True)
@click.option('-i', '--inventory-file', 'inventory_files', type=click.Path(exists=True), multiple=True,
              help="Inventory file used to fill the template. Can be used multiple times.")
@click.option('-e', '--execution-variable-file', 'execution_variable_files', type=click.Path(exists=True),
              multiple=True, help="Execution variable file used to fill the template. Can be used multiple times.")
@click.option('-w', '--worker-name', type=click.STRING, help="Worker to use.", default=config.WORKER_NAME)
@click.option('-T', '--timeout', type=click.INT, help='Set timeout for each check in the test.', default=30)
@click.option('-r', '--runs', 'number_of_runs', type=click.INT, default=1,
              help='How many times to run the test. Set `0` to run until error.')
def run_custom_template(template: str, timeout: int, inventory_files: List[str], execution_variable_files: List[str],
                        worker_name: str, number_of_runs: int):
    """
    Run a test with a custom TEMPLATE.
    TEMPLATE is path/to/your/template.

    \f
    :return: None
    """
    terminal_width = get_terminal_size().columns
    separator_visuals = '- ' * (terminal_width // 4 - 4)

    workers = [{"name": worker_name, "description": "e2e tests - custom worker"}]

    counter = 0
    failed_steps_counter = 0
    caught_exception = None
    try:
        while counter < number_of_runs or number_of_runs == 0:
            counter += 1
            run_separator = f"{separator_visuals}  {counter}   {separator_visuals}\n\n"

            try:
                t = tests.TestBasicExecution(template, workers, inventory_files, execution_variable_files, timeout)
                t.run()
            except Exception as ex:
                caught_exception = ex
                break

            if t.results.get("failed_steps") is not None:
                failed_steps_counter += 1

            click.echo(run_separator)

    except KeyboardInterrupt:
        pass

    click.echo(f"Number of executed runs: {counter}")

    fg = "red" if failed_steps_counter > 0 else None
    click.secho(f"Number of runs with any failed steps: {failed_steps_counter}", fg=fg)

    if caught_exception is not None:
        raise caught_exception


if __name__ == '__main__':
    cli()
