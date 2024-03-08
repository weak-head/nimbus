from nas.core.runner import Runner
from nas.core.service import DockerService, Service
from nas.factory.secrets import Secrets
from nas.provider.service import ServiceResource


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

    def services(self, resource: ServiceResource) -> Service:
        if resource.kind == "docker-compose":
            secrets = self._secrets.service(resource.name)
            return DockerService(resource.name, resource.directory, secrets, self._runner)
        return None
