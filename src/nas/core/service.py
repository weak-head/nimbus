from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Iterator

from nas.core.provider import DirectoryResource, Resource
from nas.core.runner import CompletedProcess, Runner
from nas.core.secrets import Secrets


class Service(ABC):
    """
    Defines an abstract service.
    All services should follow the APIs defined by this class.
    """

    @abstractmethod
    def start(self) -> OperationResult:
        """
        tbd
        """

    @abstractmethod
    def stop(self) -> OperationResult:
        """
        tbd
        """


class OperationResult:
    """
    tbd
    """

    def __init__(self, operation: str):
        self.operation: str = operation
        self.processes: list[CompletedProcess] = []

    @property
    def successful(self) -> bool:
        return all(proc.successful for proc in self.processes)


class ServiceFactory:
    """
    tbd
    """

    def __init__(self, runner: Runner, secrets: Secrets) -> None:
        self._runner = runner
        self._secrets = secrets

    def services(self, resource: Resource) -> Iterator[Service]:
        secrets = self._secrets.service(resource.name)
        if issubclass(type(resource), DirectoryResource):
            for path in resource.artifacts:
                if self._is_docker_service(path):
                    yield DockerService(resource.name, path, secrets, self._runner)

    def _is_docker_service(self, directory: str) -> bool:
        compose_files = [
            "docker-compose.yml",
            "docker-compose.yaml",
        ]
        return any(os.path.exists(os.path.join(directory, file) for file in compose_files))


class DockerService(Service):

    def __init__(self, name: str, folder: str, secrets: dict[str, str], runner: Runner):
        self._name = name
        self._folder = folder
        self._secrets = secrets
        self._runner = runner

    @abstractmethod
    def start(self) -> OperationResult:

        result = OperationResult("Start")

        for cmd in [
            "docker compose config --quiet",
            "docker compose pull",
            "docker compose down",
            "docker compose up --detach",
        ]:

            proc = self._runner.execute(cmd, self._folder)
            result.processes.append(proc)

            if not proc.successful:
                break

        return result

    @abstractmethod
    def stop(self):
        pass
