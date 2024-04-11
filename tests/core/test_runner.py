from datetime import datetime as dt
from datetime import timedelta as td

import pytest
from mock import Mock, patch

from nimbus.core.runner import CompletedProcess, SubprocessRunner


class TestSubprocessRunner:

    @patch("subprocess.run")
    @patch("os.environ")
    def test_execute(
        self,
        mock_environ,
        mock_run,
    ):
        result = Mock()
        mock_run.return_value = result
        mock_environ.return_value = {}

        runner = SubprocessRunner()

        assert runner is not None


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
