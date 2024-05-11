from __future__ import annotations

import logging

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.deploy.service import OperationStatus, Service
from nimbuscli.core.runner import Runner


class DockerService(Service):
    """
    A Dockerized service orchestrated using a docker-compose file.
    """

    def __init__(self, name: str, directory: str, env: dict[str, str], runner: Runner):
        super().__init__(name)
        self._directory = directory
        self._env = env
        self._runner = runner

    def __repr__(self) -> str:
        params = [
            f"name='{self._name}'",
            f"dir='{self._directory}'",
        ]
        return "DockerService(" + ", ".join(params) + ")"

    def _execute(self, operation: str, commands: list[str]) -> OperationStatus:
        status = OperationStatus(self.name, operation, "docker")
        for cmd in commands:
            proc = self._runner.execute(cmd, self._directory, self._env)
            status.processes.append(proc)
            if not proc.success:
                break
        return status

    @log_on_start(logging.INFO, "Starting {self._directory!s} service")
    @log_on_end(logging.INFO, "Started [{result.success!s}]: {self._directory!s}")
    def start(self) -> OperationStatus:
        return self._execute(
            "Start",
            [
                "docker compose config --quiet",
                "docker compose pull",
                "docker compose down",
                "docker compose up --detach",
            ],
        )

    @log_on_start(logging.INFO, "Stopping {self._directory!s} service")
    @log_on_end(logging.INFO, "Stopped [{result.success!s}]: {self._directory!s}")
    def stop(self):
        return self._execute(
            "Stop",
            [
                "docker compose config --quiet",
                "docker compose down",
            ],
        )
