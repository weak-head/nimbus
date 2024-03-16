from __future__ import annotations

from abc import ABC, abstractmethod

from nas.core.runner import CompletedProcess, Runner


class Service(ABC):
    """
    Defines an abstract service.
    All services should follow the APIs defined by this class.
    """

    def __init__(self, name: str):
        self.name: str = name

    @abstractmethod
    def start(self) -> OperationStatus:
        """
        Start the service.
        """

    @abstractmethod
    def stop(self) -> OperationStatus:
        """
        Stop the service.
        """


class DockerService(Service):
    """
    A Dockerized service orchestrated using a docker-compose file.
    """

    def __init__(self, name: str, directory: str, env: dict[str, str], runner: Runner):
        super().__init__(name)
        self._directory = directory
        self._env = env
        self._runner = runner

    def _execute(self, operation: str, commands: list[str]) -> OperationStatus:
        status = OperationStatus(self.name, operation)
        for cmd in commands:
            proc = self._runner.execute(cmd, self._directory, self._env)
            status.processes.append(proc)
            if not proc.success:
                break
        return status

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

    def stop(self):
        return self._execute(
            "Stop",
            [
                "docker compose config --quiet",
                "docker compose down",
            ],
        )


class OperationStatus:
    """
    The outcome of the service operation.
    """

    def __init__(self, service: str, operation: str):
        self.service: str = service
        self.operation: str = operation
        self.processes: list[CompletedProcess] = []

    @property
    def success(self) -> bool:
        return all(proc.success for proc in self.processes)
