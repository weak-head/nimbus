from datetime import datetime as dt
from datetime import timedelta as td

import pytest
from mock import Mock, PropertyMock, patch

from nimbus.core import CompletedProcess, SubprocessRunner
from tests.helpers import MockDateTime


class TestSubprocessRunner:

    @patch("subprocess.run")
    @patch("nimbus.core.runner.datetime", MockDateTime)
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


class TestCompletedProcess:
    @pytest.mark.parametrize(
        ["exception", "exitcode", "expected"],
        [
            [None, 0, CompletedProcess.SUCCESS],
            [None, None, CompletedProcess.FAILED],
            [None, 1, CompletedProcess.FAILED],
            [None, 127, CompletedProcess.FAILED],
            [Exception(), 0, CompletedProcess.EXCEPTION],
            [Exception(), 2, CompletedProcess.EXCEPTION],
        ],
    )
    def test_status(self, exception, exitcode, expected):
        cp = CompletedProcess("", "", {})
        cp.exception = exception
        cp.exitcode = exitcode

        assert cp.status == expected

    @pytest.mark.parametrize(
        ["exception", "exitcode", "cmd", "started", "completed", "expected"],
        [
            [None, 0, "cmd", dt(2024, 1, 1), dt(2025, 1, 1), True],
            [None, 0, "cmd", dt(2025, 1, 1), dt(2024, 1, 1), True],
            [None, None, "cmd", dt(2024, 1, 1), dt(2025, 1, 1), False],
            [None, 1, "cmd", dt(2024, 1, 1), dt(2025, 1, 1), False],
            [Exception(), 0, "cmd", dt(2024, 1, 1), dt(2025, 1, 1), False],
            [Exception(), 3, "cmd", dt(2024, 1, 1), dt(2025, 1, 1), False],
            [None, None, None, dt(2024, 1, 1), dt(2025, 1, 1), False],
            [None, None, "cmd", None, dt(2025, 1, 1), False],
            [None, None, "cmd", dt(2024, 1, 1), None, False],
            [None, None, "cmd", None, None, False],
        ],
    )
    def test_success(self, exception, exitcode, cmd, started, completed, expected):
        cp = CompletedProcess(cmd, "", {})
        cp.exception = exception
        cp.exitcode = exitcode
        cp.started = started
        cp.completed = completed

        assert cp.success == expected

    @pytest.mark.parametrize(
        ["started", "completed", "expected"],
        [
            [None, None, None],
            [None, dt(2024, 1, 1), None],
            [dt(2024, 1, 1), None, None],
            [dt(2024, 1, 1, 10, 1, 30), dt(2024, 1, 1, 9, 1, 30), None],
            [dt(2024, 1, 1, 10, 1, 30), dt(2024, 1, 1, 11, 1, 30), td(hours=1)],
            [dt(2024, 1, 1, 10, 1, 30), dt(2025, 1, 2, 11, 1, 35), td(days=367, hours=1, seconds=5)],
        ],
    )
    def test_elapsed(self, started, completed, expected):
        cp = CompletedProcess("", "", {})
        cp.started = started
        cp.completed = completed

        assert cp.elapsed == expected
