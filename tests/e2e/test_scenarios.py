from .fixtures import _Test


class TestBasic:
    template = "functionality/basic/template.yml"

    def test_run(self):
        t = _Test("worker", "scenarios/playground/template.yml", "scenarios/playground/inventory.yml")
        t.prepare()
        t.execute_run_command(["runs", "execute", str(t.run_id)], "executed", "FINISHED", 240, False)
        t.validate_report()
