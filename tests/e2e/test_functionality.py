import requests
import datetime
import yaml
from os.path import join

from .fixtures import _Test, trigger_msf_listener, create_inventory


class TestBasic:
    template = "functionality/basic/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()


class TestConditionalExecution:
    template = "functionality/conditional-execution/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()


class TestDeltaTrigger:
    template = "functionality/delta-trigger/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()


class TestExecutionVariables:
    template = "functionality/execution-variables/template.yml"
    execution_variables = "functionality/execution-variables/execution-variables.yml"

    def test_run(self):
        t = _Test("worker", self.template, execution_variables=join(_Test.EXAMPLES_DIRECTORY, self.execution_variables))
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()


class TestHTTPTrigger:
    template = "functionality/http-trigger/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "RUNNING")

        assert requests.get(f"http://{t.WORKER_ADDRESS}:8082/index?test=test").status_code == 200

        t.wait_for_run_state("FINISHED", 30)

        t.validate_report()


class TestMetasploitTrigger:
    template = "functionality/metasploit-trigger/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "RUNNING")

        trigger = trigger_msf_listener(t.WORKER_ADDRESS, 4444)

        t.wait_for_run_state("FINISHED", 30)

        t.validate_report()

        trigger.kill()


class TestOutputPostprocessing:
    template = "functionality/output-postprocessing/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()


class TestOutputSharing:
    template = "functionality/output-sharing/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()

    def test_all_run_controls(self):
        t = _Test("worker", self.template)
        t.prepare()

        t.execute_run_command(["runs", "show", str(t.run_id)], "id")
        t.execute_run_command(["runs", "validate-modules", str(t.run_id)], "validated")
        t.execute_run_command(["runs", "get-plan", str(t.run_id)], "detail")
        t.execute_run_command(["runs", "schedule", str(t.run_id), "2050-01-01", "20:00:00"], "scheduled", "SCHEDULED")
        t.execute_run_command(
            ["runs", "reschedule", str(t.run_id), "2050-01-01", "21:00:00"], "rescheduled", "SCHEDULED"
        )
        t.execute_run_command(["runs", "unschedule", str(t.run_id)], "unscheduled", "PENDING")
        t.execute_run_command(["runs", "execute", str(t.run_id)], "executed", "RUNNING", parse_the_response=False)
        t.execute_run_command(["runs", "pause", str(t.run_id)], "paused", "PAUSED")
        t.execute_run_command(["runs", "resume", str(t.run_id)], "resumed", "RUNNING")
        t.execute_run_command(["runs", "stop", str(t.run_id)], "stopped", "STOPPED")
        t.validate_report(
            "STOPPED",
            {pid: "STOPPED" for pid in t.plan_execution_ids},
            {"create-a-different-object": "STOPPED"},
            {"run-parent-command": "PENDING", "run-command-from-step": "PENDING", "run-command-from-alias": "PENDING"},
        )
        t.execute_run_command(["runs", "delete", str(t.run_id)], "", parse_the_response=False)


class TestTimeTrigger:
    template = "functionality/time-trigger/template.yml"

    def test_run(self):
        start_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=5)
        with open(join(_Test.EXAMPLES_DIRECTORY, self.template)) as f:
            original_template: dict = yaml.safe_load(f)
        original_template["stages"]["do-stuff-on-worker"]["arguments"] = {
            "timezone": "UTC",
            "hour": start_time.hour,
            "minute": start_time.minute,
            "second": start_time.second,
        }
        updated_template = create_inventory(original_template)

        t = _Test("worker", updated_template)
        t.prepare()

        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED")

        t.validate_report()
