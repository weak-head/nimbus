from datetime import datetime as dt

from mock import Mock, PropertyMock, patch

from nimbuscli.core.execute.process import SubprocessRunner
from tests.helpers import MockDateTime


class TestSubprocessRunner:

    @patch("subprocess.run")
    @patch("nimbuscli.core.execute.process.datetime", MockDateTime)
    def test_execute(self, mock_run, monkeypatch):
        started_dt = dt(2024, 5, 10, 12, 30, 50)
        completed_dt = dt(2024, 5, 10, 12, 35, 55)
        MockDateTime.now_returns(started_dt, completed_dt)

        monkeypatch.setenv("SYS_KEY_1", "VALUE_1")
        monkeypatch.setenv("SYS_KEY_2", "VALUE_2")

        run_result = Mock()
        type(run_result).returncode = PropertyMock(return_value=12)
        type(run_result).stdout = PropertyMock(return_value="  stdout_abc  ")
        type(run_result).stderr = PropertyMock(return_value="  stderr_abc  ")
        mock_run.return_value = run_result

        cmd = "rar a -b -c -txv file folder"
        cwd = "/home/user/path"
        env = {"PROC_KEY": "PROC_VALUE"}
        expected_env = {
            "SYS_KEY_1": "VALUE_1",
            "SYS_KEY_2": "VALUE_2",
            **env,
        }

        runner = SubprocessRunner()
        proc = runner.execute(cmd, cwd, env)

        assert proc.cmd == cmd.split()
        assert proc.cwd == cwd
        assert proc.env == (proc.env | expected_env)
        assert proc.started == started_dt
        assert proc.completed == completed_dt
        assert proc.exitcode == 12
        assert proc.stdout == "stdout_abc"
        assert proc.stderr == "stderr_abc"

    @patch("subprocess.run")
    def test_execute_exception(self, mock_run):
        exc = Exception("Some exception")
        mock_run.side_effect = exc

        cmd = "rar a -b -c -txv file folder"
        cwd = "/home/user/path"
        env = {"PROC_KEY": "PROC_VALUE"}

        runner = SubprocessRunner()
        proc = runner.execute(cmd, cwd, env)

        assert proc.exception == exc
