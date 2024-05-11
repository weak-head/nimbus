import pytest
from mock import Mock, call

from nimbuscli.core.deploy.docker import DockerService


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
