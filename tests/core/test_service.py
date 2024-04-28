from datetime import timedelta as td

import pytest
from mock import Mock, call

from nimbus.core import DockerService, OperationStatus


class MockProc:

    def __init__(self, s=None, e=None):
        self._success = s
        self._elapsed = e

    @property
    def success(self):
        return self._success

    @property
    def elapsed(self):
        return self._elapsed


class TestDockerService:

    @pytest.mark.parametrize(
        ["statuses", "expected"],
        [
            [[True, True, True, True], [True, True, True, True]],
            [[False, True, True, True], [False]],
            [[True, True, True, False], [True, True, True, False]],
            [[True, False, True, False], [True, False]],
            [[False, True, True, True], [False]],
        ],
    )
    def test_execute(self, statuses, expected):
        mock_runner = Mock()
        mock_runner.execute.side_effect = [MockProc(s=s) for s in statuses]

        name = "NAME"
        directory = "DIRECTORY"
        env = {"KEY": "VALUE"}

        ds = DockerService(name, directory, env, mock_runner)
        result = ds.start()

        mock_runner.execute.assert_called()
        assert mock_runner.execute.call_count == len(expected)

        assert result.operation == "Start"
        assert result.service == name
        assert result.kind == "docker"
        assert len(result.processes) == len(expected)
        for ix, res in enumerate(result.processes):
            assert res.success == expected[ix]

    def test_start(self):
        mock_runner = Mock()
        mock_runner.execute.side_effect = [MockProc(s=True)] * 4

        name = "NAME"
        directory = "DIRECTORY"
        env = {"KEY": "VALUE"}

        ds = DockerService(name, directory, env, mock_runner)
        result = ds.start()

        assert result.operation == "Start"
        assert result.service == name
        assert result.kind == "docker"
        mock_runner.execute.assert_has_calls(
            [
                call("docker compose config --quiet", directory, env),
                call("docker compose pull", directory, env),
                call("docker compose down", directory, env),
                call("docker compose up --detach", directory, env),
            ]
        )

    def test_stop(self):
        mock_runner = Mock()
        mock_runner.execute.side_effect = [MockProc(s=True)] * 2

        name = "NAME"
        directory = "DIRECTORY"
        env = {"KEY": "VALUE"}

        ds = DockerService(name, directory, env, mock_runner)
        result = ds.stop()

        assert result.operation == "Stop"
        assert result.service == name
        assert result.kind == "docker"
        mock_runner.execute.assert_has_calls(
            [
                call("docker compose config --quiet", directory, env),
                call("docker compose down", directory, env),
            ]
        )


class TestOperationStatus:

    @pytest.mark.parametrize(
        "statuses",
        [
            [True],
            [False],
            [True, True, True],
            [True, False, True, False],
            [False, False, False],
        ],
    )
    def test_success(self, statuses):
        operation = OperationStatus("", "", "")
        for s in statuses:
            operation.processes.append(MockProc(s=s))

        assert operation.success == all(statuses)

    @pytest.mark.parametrize(
        ["durations", "expected"],
        [
            [
                [td(minutes=10)],
                td(minutes=10),
            ],
            [
                [td(minutes=10)] * 1000,
                td(minutes=10_000),
            ],
            [
                [td(minutes=10), td(minutes=3)],
                td(minutes=13),
            ],
            [
                [td(hours=1), td(minutes=10), td(seconds=3)],
                td(hours=1, minutes=10, seconds=3),
            ],
            [
                [td(minutes=17), td(minutes=10), td(seconds=3)],
                td(minutes=27, seconds=3),
            ],
        ],
    )
    def test_elapsed(self, durations, expected):
        operation = OperationStatus("", "", "")
        for d in durations:
            operation.processes.append(MockProc(e=d))

        assert operation.elapsed == expected
