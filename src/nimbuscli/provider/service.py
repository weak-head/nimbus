from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbuscli.core.deploy import DockerService, Service
from nimbuscli.core.execute import Runner
from nimbuscli.provider.resource import Provider, Resource
from nimbuscli.provider.secret import Secrets


class ServiceResource(Resource):

    def __init__(self, name: str, kind: str, directory: str):
        super().__init__(name)
        self.kind: str = kind
        self.directory: str = directory


class ServiceProvider(Provider[ServiceResource]):
    """
    This class provides a recursive mechanism for
    discovering services within all parent folders.
    By traversing through parent folders, it facilitates
    the identification and interaction with services,
    """

    def __init__(self, directories: list[str]):
        self._directories: list[str] = directories
        self._compose_files = [
            "compose.yml",
            "compose.yaml",
            "docker-compose.yml",
            "docker-compose.yaml",
        ]

    def __repr__(self) -> str:
        params = [
            f"dirs={self._directories!r}",
        ]
        return "ServiceProvider(" + ", ".join(params) + ")"

    def _resources(self) -> Iterator[ServiceResource]:
        for directory in self._directories:
            yield from self._discover(Path(directory).expanduser())

    def _discover(self, path: Path) -> Iterator[ServiceResource]:
        if not path.is_dir():
            return

        match kind := self._get_kind(path):
            case "docker-compose":
                yield ServiceResource(
                    path.name,
                    kind,
                    path.as_posix(),
                )

            case None:
                for obj in path.iterdir():
                    yield from self._discover(obj)

    def _get_kind(self, path: Path) -> str:
        if any(path.joinpath(file).exists() for file in self._compose_files):
            return "docker-compose"
        return None


class ServiceFactory:
    """
    Service Factory that dynamically creates new instances
    of a service based on the provided service kind.
    The type of each created service instance depends on
    the characteristics of the resource.
    """

    def __init__(self, runner: Runner, secrets: Secrets) -> None:
        self._runner = runner
        self._secrets = secrets

    def __repr__(self) -> str:
        params = [
            f"runner='{self._runner.__class__.__name__}'",
            f"secrets='{self._secrets.__class__.__name__}'",
        ]
        return "ServiceFactory(" + ", ".join(params) + ")"

    @log_on_start(logging.DEBUG, "Creating Service: {resource.name!s} [{resource.kind!s}]")
    @log_on_end(logging.DEBUG, "Created Service: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Service: {e!r}", on_exceptions=Exception)
    def create_service(self, resource: ServiceResource) -> Service:
        match resource.kind:
            case "docker-compose":
                return DockerService(
                    resource.name,
                    resource.directory,
                    self._secrets.env(resource.name),
                    self._runner,
                )

            case _:
                return None
