from .fixtures import _Test


class TestBasic:
    template = "modules/empire/linux/template.yml"

    def test_run(self):
        t = _Test("worker", self.template)
        t.prepare()
        t.execute_run_command(["runs", "execute", "-S", str(t.run_id)], "executed", "FINISHED", 60)
        t.validate_report()
