# from unittest import TestCase
# from unittest.mock import patch, Mock
#
# from click.testing import CliRunner
#
# from cryton.worker.cli import cli
#
#
# class CliTest(TestCase):
#     def setUp(self):
#         self.runner = CliRunner()
#
#     def test_cli(self):
#         result = self.runner.invoke(cli)
#         self.assertEqual(0, result.exit_code)
#
#     @patch("cryton.worker.worker.Worker.start", Mock())
#     @patch("cryton.worker.util.util.install_modules_requirements")
#     def test_start(self, mock_install_requirements):
#         result = self.runner.invoke(cli, ["start", "--install-requirements"])
#         self.assertEqual(0, result.exit_code)
#         mock_install_requirements.assert_called()
