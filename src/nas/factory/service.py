import os
from collections.abc import Iterator

from nas.core.runner import Runner
from nas.core.service import DockerService, Service
from nas.factory.secrets import Secrets
from nas.provider.abstract import DirectoryResource, Resource


class ServiceFactory:
    """
    Service Factory that dynamically creates new instances of services based on the provided resource type.
    The type of each created service instance depends on the characteristics of the resource.
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
